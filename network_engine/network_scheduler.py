"""Higher-level scheduling helpers for the network engine."""
from datetime import datetime
from automation import scheduler


def network_schedule():
    plan = scheduler.default_schedule()
    plan["daily_idea_generation"] = {
        "name": "daily_idea_generation",
        "cron": "0 5 * * *",
        "next_run": scheduler.next_run(5).isoformat() + "Z",
    }
    plan["daily_short_distribution"] = {
        "name": "daily_short_distribution",
        "cron": "0 9 * * *",
        "next_run": scheduler.next_run(9).isoformat() + "Z",
    }
    return plan


def should_transform_core_to_distribution(last_updated: datetime) -> bool:
    # Placeholder: transform if a core article is newer than 1 day.
    return (datetime.utcnow() - last_updated).days < 1
