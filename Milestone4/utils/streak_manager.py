"""
utils/streak_manager.py — Streak calculation and update logic for FitPlan Pro.
Streak increases when user completes a full day (all workout + diet checkboxes).
Streak resets if a day is missed.
"""

from datetime import date, timedelta
from utils.db import get_streak, save_streak


def update_streak(username, day_completed: bool) -> int:
    """
    Update streak based on whether today's plan was fully completed.

    Rules:
    - day_completed=True  → increment streak (if consecutive) or start new one
    - day_completed=False → if today was previously completed, decrement streak
    - Missed yesterday    → streak resets to 0 on next completion

    Returns: updated current_streak (int)
    """
    today     = str(date.today())
    yesterday = str(date.today() - timedelta(days=1))

    streak = get_streak(username)
    history = streak.get("streak_history", [])
    last    = streak.get("last_completed_date")

    if day_completed:
        # Add today to history if not already there
        if today not in history:
            history.append(today)
            history.sort()

        if last == yesterday:
            # Consecutive day — extend streak
            streak["current_streak"] += 1
        elif last == today:
            # Already counted today — no change
            pass
        else:
            # Missed one or more days — start fresh
            streak["current_streak"] = 1

        streak["last_completed_date"] = today
        streak["longest_streak"] = max(
            streak.get("longest_streak", 0),
            streak["current_streak"]
        )

    else:
        # User unchecked something — today is no longer complete
        if last == today and today in history:
            history.remove(today)
            streak["current_streak"] = max(0, streak["current_streak"] - 1)
            streak["last_completed_date"] = history[-1] if history else None

    streak["streak_history"] = history
    save_streak(streak)

    return streak["current_streak"]


def get_streak_display(username):
    """
    Get formatted streak info for display in the UI.
    Returns dict ready to pass to the dashboard.
    """
    streak = get_streak(username)

    current = streak.get("current_streak", 0)
    longest = streak.get("longest_streak", 0)
    last    = streak.get("last_completed_date")
    history = streak.get("streak_history", [])

    today     = str(date.today())
    yesterday = str(date.today() - timedelta(days=1))

    # Determine if streak is at risk (yesterday not completed)
    if current > 0 and last not in [today, yesterday]:
        status = "broken"
        current = 0  # reset display — streak was broken
        # Actually update DB too
        _reset_streak(username, streak)
    elif last == today:
        status = "active"
    elif last == yesterday:
        status = "at_risk"   # complete today to keep streak alive
    else:
        status = "inactive"

    return {
        "current_streak": current,
        "longest_streak": longest,
        "last_completed":  last,
        "status":          status,
        "completed_days":  len(history),
        "emoji":           _streak_emoji(current)
    }


def _reset_streak(username, streak):
    """Internal: reset broken streak in DB."""
    streak["current_streak"] = 0
    save_streak(streak)


def _streak_emoji(streak_count):
    """Return an appropriate emoji based on streak length."""
    if streak_count == 0:
        return "💤"
    elif streak_count < 3:
        return "🔥"
    elif streak_count < 7:
        return "🔥🔥"
    elif streak_count < 14:
        return "🔥🔥🔥"
    elif streak_count < 30:
        return "⚡🔥"
    else:
        return "🏆🔥"


def check_streak_milestone(streak_count):
    """
    Return a milestone message if user hit a notable streak.
    Returns: str message or None
    """
    milestones = {
        3:   "3-day streak! You're building a habit! 💪",
        7:   "One full week! Incredible consistency! 🏅",
        14:  "Two weeks strong! You're unstoppable! ⚡",
        21:  "21 days — habits are officially formed! 🧠",
        30:  "30-day streak! Elite level dedication! 🏆",
        50:  "50 days! You're a fitness legend! 🌟",
        100: "100 DAYS! Absolute monster! 👑"
    }
    return milestones.get(streak_count) 