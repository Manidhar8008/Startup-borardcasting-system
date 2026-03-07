import argparse
import json
import logging
import os
from collections import defaultdict
from pathlib import Path
from typing import Iterable, List

from dotenv import load_dotenv

from analytics_engine import engagement_tracker
from automation import scheduler
from brain_input import brain_parser
from decision_engine import approval_queue, topic_selector
from distribution import publisher_router
from founder_agent import thinking_agent, research_agent, content_agent, distribution_agent, analytics_agent
from content_engine import generator
from network_engine import content_transformer
from ai_core import knowledge_model, topic_predictor
from ai_core import performance_learner

ROOT = Path(__file__).resolve().parent
LOGS_DIR = ROOT / "logs"


def setup_logging():
    LOGS_DIR.mkdir(exist_ok=True)
    fmt = "%(asctime)s %(name)s %(levelname)s %(message)s"
    logging.basicConfig(level=logging.INFO, format=fmt)

    for name, logfile in {
        "research": LOGS_DIR / "research.log",
        "publishing": LOGS_DIR / "publishing.log",
        "engine": LOGS_DIR / "engine.log",
    }.items():
        handler = logging.FileHandler(logfile)
        handler.setFormatter(logging.Formatter(fmt))
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.propagate = False


def determine_content_type(brand: str, content_length: str) -> str:
    mapping = {
        "janani_ai": {"long": "long_form", "short": "thread"},
        "mw_ai_data_systems": {"long": "case_study", "short": "insight"},
        "mw_ai_news": {"long": "explainer", "short": "thread"},
        "mw_ai_edu": {"long": "tutorial", "short": "short_explainer"},
    }
    return mapping.get(brand, {}).get(content_length, "insight")


def store_ideas(queue: approval_queue.ApprovalQueue, ideas: Iterable[dict]):
    existing_titles = {i.get("title", "").lower() for i in queue.list_ideas()}
    for idea in ideas:
        title = (idea.get("title") or "").lower()
        if title and title in existing_titles:
            continue
        queue.add_idea(idea)


def show_approval_queue(queue: approval_queue.ApprovalQueue):
    pending = queue.list_ideas("pending")
    if not pending:
        print("No pending ideas.")
        return
    print("Pending ideas:")
    for idea in pending:
        print(f"- {idea['id']}: {idea.get('title')} (source: {idea.get('source')})")


def generate_drafts_from_approved(brand: str, queue: approval_queue.ApprovalQueue):
    # delegate to content_agent
    return content_agent.draft_from_approved(brand)


def transform_core_to_distribution(core_brand: str, drafts):
    """Create derivative drafts for distribution brands from core-brand drafts."""
    if core_brand not in {"janani_ai", "mw_ai_data_systems"}:
        return 0

    created = 0
    news_queue = approval_queue.ApprovalQueue("mw_ai_news")
    edu_queue = approval_queue.ApprovalQueue("mw_ai_edu")

    for draft in drafts:
        base_text = draft.get("draft", "")
        topic = draft.get("topic", "")

        news_thread = content_transformer.generate_twitter_thread(base_text, brand="mw_ai_news")
        news_caption = content_transformer.generate_instagram_caption(base_text, brand="mw_ai_news")
        news_text = "\n".join(news_thread.get("thread", []))
        news_queue.add_draft(
            {
                "brand": "mw_ai_news",
                "topic": f"{topic} (news)",
                "draft": news_text or news_caption.get("caption", ""),
                "content_type": "thread",
                "content_length": "short",
            }
        )
        created += 1

        edu_script = content_transformer.generate_youtube_script(base_text, brand="mw_ai_edu")
        edu_queue.add_draft(
            {
                "brand": "mw_ai_edu",
                "topic": f"{topic} (edu)",
                "draft": edu_script.get("script", ""),
                "content_type": "tutorial",
                "content_length": "long",
            }
        )
        created += 1
    return created


def publish_drafts(brand: str, *, dry_run: bool = True):
    results = distribution_agent.publish_ready(brand, dry_run=dry_run)
    for res in results:
        topic = res.get("draft")
        metrics = {"platform": ",".join(res.get("channels", [])), "brand": brand, "score": 1}
        analytics_agent.record_publication(topic, metrics)
    performance_learner.learn()
    return results


def review_cli(brand: str):
    queue = approval_queue.ApprovalQueue(brand)
    pending = queue.list_ideas("pending")
    if not pending:
        print("No pending ideas to review.")
        return

    for idea in pending:
        print(f"\n{idea['id']} :: {idea.get('title')}\n{idea.get('summary')}")
        choice = input("[a]pprove / [r]eject / [s]kip: ").strip().lower()
        if choice == "a":
            queue.set_idea_status(idea["id"], "approved")
        elif choice == "r":
            reason = input("Reason for rejection: ").strip() or "manual"
            queue.set_idea_status(idea["id"], "rejected", reason=reason)
        else:
            continue
    print("Review complete.")


def run_pipeline(brand: str, *, offline: bool = False, limit: int = 5):
    queue = approval_queue.ApprovalQueue(brand)

    # Thinking agent ingests any new founder inputs (non-destructive)
    thinking_agent.ingest_founder_inputs()
    knowledge_model.build_snapshot()

    # Research agent collects signals
    research_items = research_agent.gather(brand, offline=offline)
    predicted = topic_predictor.suggest_topics(brand, research_items)
    combined_items = list(research_items) + predicted
    ranked = topic_selector.rank_topics(combined_items, brand, limit=limit)

    ideas = []
    for idx, item in enumerate(ranked):
        content_length = topic_selector.pick_content_length(brand, idx)
        content_type = determine_content_type(brand, content_length)
        ideas.append(
            {
                "title": item.get("title"),
                "summary": item.get("summary"),
                "source": item.get("source"),
                "brand": brand,
                "content_length": content_length,
                "content_type": content_type,
            }
        )
    store_ideas(queue, ideas)
    show_approval_queue(queue)

    drafts = generate_drafts_from_approved(brand, queue)
    transform_core_to_distribution(brand, drafts)


def schedule_cli():
    print(json.dumps(scheduler.default_schedule(), indent=2))


def think_cli():
    counts = thinking_agent.ingest_founder_inputs()
    for brand, count in counts.items():
        print(f"Ingested {count} ideas for {brand}")


def parse_args():
    parser = argparse.ArgumentParser(description="Startup Broadcasting Engine")
    parser.add_argument("command", nargs="?", default="run", help="think | run | review | publish | schedule")
    parser.add_argument("brand", nargs="?", default="janani_ai", help="Brand to target")
    parser.add_argument("--offline", action="store_true", help="Use offline stubs")
    parser.add_argument("--dry-run", dest="dry_run", action="store_true", help="Do not hit live APIs")
    parser.add_argument("--limit", type=int, default=5, help="How many ideas per brand")
    return parser.parse_args()


def main():
    load_dotenv()
    setup_logging()
    args = parse_args()

    dry_run = args.dry_run or os.getenv("DRY_RUN", "true").lower() == "true"

    if args.command == "think":
        think_cli()
    elif args.command == "review":
        review_cli(args.brand)
        drafts = generate_drafts_from_approved(args.brand, approval_queue.ApprovalQueue(args.brand))
        transform_core_to_distribution(args.brand, drafts)
    elif args.command == "publish":
        publish_drafts(args.brand, dry_run=dry_run)
    elif args.command == "schedule":
        schedule_cli()
    else:
        run_pipeline(args.brand, offline=args.offline, limit=args.limit)
        if not dry_run:
            publish_drafts(args.brand, dry_run=dry_run)


if __name__ == "__main__":
    main()
