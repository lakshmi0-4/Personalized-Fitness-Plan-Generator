"""
utils/progress_tracker.py — Daily progress tracking logic for FitPlan Pro.
Handles: checkbox state management, completion detection, stats calculation.
"""

from utils.db import save_progress, get_progress, get_all_progress
from utils.streak_manager import update_streak


# ══════════════════════════════════════════════════════════════════════════════
# Checkbox state helpers
# ══════════════════════════════════════════════════════════════════════════════

def build_workout_checks(exercises):
    """
    Build initial empty checkbox dict from exercise list.
    exercises: list of dicts with 'name' key
    Returns: {"Push-ups": False, "Squats": False, ...}
    """
    return {ex["name"]: False for ex in exercises if "name" in ex}


def build_dietary_checks(dietary):
    """
    Build initial empty checkbox dict from dietary dict.
    dietary: {"breakfast": "...", "lunch": "...", ...}
    Returns: {"breakfast": False, "lunch": False, ...}
    """
    return {meal: False for meal in dietary if dietary[meal]}


def merge_checks(existing, new_keys):
    """
    Merge saved checkbox state with current exercise/meal list.
    Preserves saved True/False values; adds False for new keys.
    """
    merged = {}
    for key in new_keys:
        merged[key] = existing.get(key, False)
    return merged


# ══════════════════════════════════════════════════════════════════════════════
# Core tracking functions
# ══════════════════════════════════════════════════════════════════════════════

def load_day_progress(username, plan_id, day_number, exercises, dietary):
    """
    Load saved progress for a day and merge with current plan data.
    Returns: (workout_checks, dietary_checks, day_completed)
    """
    saved = get_progress(username, plan_id, day_number)

    workout_keys = [ex["name"] for ex in exercises if "name" in ex]
    dietary_keys = list(dietary.keys()) if dietary else []

    workout_checks = merge_checks(saved["workout_checks"], workout_keys)
    dietary_checks = merge_checks(saved["dietary_checks"], dietary_keys)

    return workout_checks, dietary_checks, saved["day_completed"]


def toggle_workout_item(username, plan_id, day_number,
                        exercise_name, checked,
                        current_workout_checks, current_dietary_checks):
    """
    Toggle a single workout checkbox and save to DB.
    Returns: (updated_workout_checks, day_completed, new_streak)
    """
    current_workout_checks[exercise_name] = checked

    day_completed = save_progress(
        username, plan_id, day_number,
        current_workout_checks, current_dietary_checks
    )

    new_streak = update_streak(username, day_completed)
    return current_workout_checks, day_completed, new_streak


def toggle_dietary_item(username, plan_id, day_number,
                        meal_name, checked,
                        current_workout_checks, current_dietary_checks):
    """
    Toggle a single dietary checkbox and save to DB.
    Returns: (updated_dietary_checks, day_completed, new_streak)
    """
    current_dietary_checks[meal_name] = checked

    day_completed = save_progress(
        username, plan_id, day_number,
        current_workout_checks, current_dietary_checks
    )

    new_streak = update_streak(username, day_completed)
    return current_dietary_checks, day_completed, new_streak


def mark_day_complete(username, plan_id, day_number,
                      exercises, dietary):
    """
    Mark ALL items in a day as complete at once.
    Returns: (workout_checks, dietary_checks, new_streak)
    """
    workout_checks = {ex["name"]: True for ex in exercises if "name" in ex}
    dietary_checks = {meal: True for meal in dietary if dietary[meal]}

    save_progress(username, plan_id, day_number, workout_checks, dietary_checks)
    new_streak = update_streak(username, True)

    return workout_checks, dietary_checks, new_streak


def unmark_day(username, plan_id, day_number, exercises, dietary):
    """
    Unmark ALL items in a day (reset to unchecked).
    Returns: (workout_checks, dietary_checks)
    """
    workout_checks = {ex["name"]: False for ex in exercises if "name" in ex}
    dietary_checks = {meal: False for meal in dietary if dietary[meal]}

    save_progress(username, plan_id, day_number, workout_checks, dietary_checks)
    update_streak(username, False)

    return workout_checks, dietary_checks


# ══════════════════════════════════════════════════════════════════════════════
# Stats / Summary
# ══════════════════════════════════════════════════════════════════════════════

def get_plan_stats(username, plan_id, total_days):
    """
    Calculate overall plan completion stats.
    Returns dict with summary numbers.
    """
    all_progress = get_all_progress(username, plan_id)

    completed_days = sum(1 for p in all_progress if p["day_completed"])

    total_workout_tasks = 0
    done_workout_tasks  = 0
    total_dietary_tasks = 0
    done_dietary_tasks  = 0

    for p in all_progress:
        wc = p["workout_checks"]
        dc = p["dietary_checks"]

        total_workout_tasks += len(wc)
        done_workout_tasks  += sum(1 for v in wc.values() if v)
        total_dietary_tasks += len(dc)
        done_dietary_tasks  += sum(1 for v in dc.values() if v)

    total_tasks = total_workout_tasks + total_dietary_tasks
    done_tasks  = done_workout_tasks  + done_dietary_tasks

    return {
        "completed_days":       completed_days,
        "total_days":           total_days,
        "pending_days":         total_days - completed_days,
        "progress_pct":         round((completed_days / total_days * 100), 1) if total_days else 0,
        "total_workout_tasks":  total_workout_tasks,
        "done_workout_tasks":   done_workout_tasks,
        "total_dietary_tasks":  total_dietary_tasks,
        "done_dietary_tasks":   done_dietary_tasks,
        "total_tasks":          total_tasks,
        "done_tasks":           done_tasks,
        "overall_task_pct":     round((done_tasks / total_tasks * 100), 1) if total_tasks else 0
    }


def get_today_day_number(plan_created_at, days_per_week=5):
    """
    Calculate which day of the plan today corresponds to.
    Based on days since plan creation and training frequency.
    Returns: day_number (1-indexed), or 1 if before start.
    """
    from datetime import datetime, timezone
    import math

    now = datetime.now(timezone.utc).timestamp()
    days_elapsed = (now - plan_created_at) / 86400  # seconds per day

    # Account for rest days: only training days count
    # e.g. 5 days/week = train Mon-Fri, rest Sat-Sun
    training_day = math.floor(days_elapsed * (days_per_week / 7)) + 1
    return max(1, int(training_day))


def get_completion_heatmap(username, plan_id, total_days):
    """
    Build a completion status list for calendar/heatmap display.
    Returns: list of dicts [{day_number, status, date}]
    status: 'completed' | 'partial' | 'pending'
    """
    all_progress = get_all_progress(username, plan_id)
    progress_map = {p["day_number"]: p for p in all_progress}

    heatmap = []
    for day in range(1, total_days + 1):
        p = progress_map.get(day)
        if not p:
            status = "pending"
        elif p["day_completed"]:
            status = "completed"
        else:
            wc = p["workout_checks"]
            dc = p["dietary_checks"]
            any_done = any(wc.values()) or any(dc.values())
            status = "partial" if any_done else "pending"

        heatmap.append({
            "day_number": day,
            "status":     status,
            "date":       p["date"] if p else None
        })

    return heatmap 