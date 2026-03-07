"""Simple scheduler helpers (stub, not a real cron)."""
from datetime import datetime, timedelta
from typing import Dict


def next_run(hour_utc: int, *, day_offset: int = 0) -> datetime:
    now = datetime.utcnow()
    target = now.replace(hour=hour_utc, minute=0, second=0, microsecond=0) + timedelta(days=day_offset)
    if target <= now:
        target += timedelta(days=1)
    return target


def schedule_daily(hour_utc: int) -> Dict:
    target = next_run(hour_utc)
    return {
        "name": "daily_research",
        "cron": f"0 {hour_utc} * * *",
        "next_run": target.isoformat() + "Z",
    }


def schedule_weekly(day_of_week: int, hour_utc: int) -> Dict:
    now = datetime.utcnow()
    day_diff = (day_of_week - now.weekday()) % 7
    target = next_run(hour_utc, day_offset=day_diff)
    return {
        "name": "weekly_long_form",
        "cron": f"0 {hour_utc} * * {day_of_week}",
        "next_run": target.isoformat() + "Z",
    }


def schedule_daily_ideas(hour_utc: int) -> Dict:
    target = next_run(hour_utc)
    return {
        "name": "daily_idea_generation",
        "cron": f"0 {hour_utc} * * *",
        "next_run": target.isoformat() + "Z",
    }


def schedule_daily_distribution(hour_utc: int) -> Dict:
    target = next_run(hour_utc)
    return {
        "name": "daily_short_distribution",
        "cron": f"0 {hour_utc} * * *",
        "next_run": target.isoformat() + "Z",
    }


def schedule_weekly_edu_video(day_of_week: int, hour_utc: int) -> Dict:
    now = datetime.utcnow()
    day_diff = (day_of_week - now.weekday()) % 7
    target = next_run(hour_utc, day_offset=day_diff)
    return {
        "name": "weekly_educational_video",
        "cron": f"0 {hour_utc} * * {day_of_week}",
        "next_run": target.isoformat() + "Z",
    }


def schedule_daily_thinking(hour_utc: int) -> Dict:
    target = next_run(hour_utc)
    return {
        "name": "daily_founder_thinking",
        "cron": f"0 {hour_utc} * * *",
        "next_run": target.isoformat() + "Z",
    }


def default_schedule() -> Dict[str, Dict]:
    # Monday=0 ... Sunday=6
    return {
        "daily_research": schedule_daily(hour_utc=3),
        "weekly_long_form": schedule_weekly(day_of_week=6, hour_utc=4),
        "daily_founder_thinking": schedule_daily_thinking(hour_utc=4),
        "daily_idea_generation": schedule_daily_ideas(hour_utc=5),
        "daily_short_distribution": schedule_daily_distribution(hour_utc=9),
        "weekly_educational_video": schedule_weekly_edu_video(day_of_week=2, hour_utc=7),
    }
