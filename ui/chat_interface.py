"""JAN Chat Interface: interactive CLI loop (v3 — Gemini powered)."""
import sys
from core.jan_manager import JanManager

BANNER = r"""
     ██╗ █████╗ ███╗   ██╗
     ██║██╔══██╗████╗  ██║
     ██║███████║██╔██╗ ██║
██   ██║██╔══██║██║╚██╗██║
╚█████╔╝██║  ██║██║ ╚████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝

  JAN AI Media Manager  |  Brand: {brand}
  LLM: {llm}  |  9 Platforms  |  Workflow Mode: ON
  Type 'help' or:  multiply AI agents
"""

HELP_TEXT = """
━━━  CONTENT MULTIPLICATION  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  multiply <topic>       1 idea → 22 assets across 9 platforms

━━━  WORKFLOW (one command does everything)  ━━━━━━━━━━━━━━━━━━
  <message>              Type naturally — JAN auto-detects workflows

  Examples:
    create 3 reels about AI agents
    write 2 linkedin posts on LLM fine tuning
    make a tutorial on building RAG pipelines
    research prompt engineering trends

━━━  STEP-BY-STEP COMMANDS  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  morning briefing       Read notes + score topics + LLM plan + learning
  research <topic>       Research a topic (live: RSS + Perplexity)
  plan today             Build scored + LLM content plan
  generate drafts        Gemini drafts (Hook / Insight / Example / CTA)
  publish drafts         Simulate publishing → records topic memory
  topic insights         Top / recent / recommended topics

━━━  SYSTEM  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  status                 Pipeline + memory + LLM provider state
  brand <name>           Switch brand
  help                   This menu
  exit                   Quit JAN
"""


def print_separator():
    print("\n" + "━" * 60)


def _thinking(msg: str):
    print(f"\n  ⟳  {msg}", flush=True)


def _get_llm_info() -> str:
    try:
        from ai_core.llm_router import get_active_provider
        return get_active_provider()
    except Exception:
        return "ollama"


def run(brand: str = "janani_ai"):
    jan = JanManager(brand=brand)
    llm = _get_llm_info()
    print(BANNER.format(brand=jan.brand, llm=llm))

    while True:
        try:
            raw = input("JAN ▶  ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye! 👋")
            sys.exit(0)

        if not raw:
            continue

        full_cmd = raw.lower().strip()
        parts    = raw.split(maxsplit=1)
        cmd      = parts[0].lower()
        arg      = parts[1] if len(parts) > 1 else ""

        print_separator()

        # ── Exit ──────────────────────────────────────────────────────────────
        if cmd in ("exit", "quit"):
            print("Goodbye! 👋")
            sys.exit(0)

        # ── Help ──────────────────────────────────────────────────────────────
        elif cmd == "help":
            print(HELP_TEXT)

        # ── Multiply ─────────────────────────────────────────────────────────
        elif cmd == "multiply":
            if not arg:
                print("⚠️  Usage: multiply <topic>\n   Example: multiply AI agents for startups")
            else:
                _thinking(f"Multiplying across 9 platforms: \"{arg}\" ...")
                print(jan.multiply(arg))

        # ── Workflow shortcut: do <message> ───────────────────────────────────
        elif cmd == "do":
            if not arg:
                print(
                    "⚠️  Usage: do <message>\n"
                    "   Example: do create 3 reels about AI agents"
                )
            else:
                _thinking(f"Interpreting: \"{arg}\" ...")
                print(jan.execute_workflow(arg))

        # ── Morning briefing ──────────────────────────────────────────────────
        elif full_cmd == "morning briefing":
            _thinking("Reading notes + scoring topics + learning + building strategy ...")
            print(jan.morning_briefing())

        # ── Research ──────────────────────────────────────────────────────────
        elif cmd == "research":
            if not arg:
                print("⚠️  Usage: research <topic>")
            else:
                _thinking(f"Researching: {arg} ...")
                print(jan.research(arg))

        # ── Plan ──────────────────────────────────────────────────────────────
        elif full_cmd == "plan today":
            _thinking("Scoring topics + building LLM plan ...")
            print(jan.plan_today())

        # ── Generate ──────────────────────────────────────────────────────────
        elif full_cmd == "generate drafts":
            _thinking("Writing drafts with Gemini ...")
            print(jan.generate_drafts())

        # ── Publish ───────────────────────────────────────────────────────────
        elif full_cmd == "publish drafts":
            _thinking("Simulating publish + recording topic memory ...")
            print(jan.publish_drafts(dry_run=True))

        # ── Topic insights ────────────────────────────────────────────────────
        elif full_cmd == "topic insights":
            print(jan.topic_insights())

        # ── Status ────────────────────────────────────────────────────────────
        elif cmd == "status":
            print(jan.status())

        # ── Brand switch ──────────────────────────────────────────────────────
        elif cmd == "brand":
            if not arg:
                print(f"Current brand: {jan.brand}")
            else:
                jan = JanManager(brand=arg)
                print(f"✅ Switched to brand: {arg}")

        # ── Fallback: Natural Language Workflow ───────────────────────────────
        else:
            _thinking(f"Interpreting: \"{raw}\" ...")
            print(jan.execute_workflow(raw))

        print_separator()
