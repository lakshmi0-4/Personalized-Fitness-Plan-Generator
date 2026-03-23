# utils/__init__.py — FitPlan Pro utility package
# Exposes all helper functions directly from the utils package
# Usage: from utils import save_plan, get_active_plan, update_streak etc.

from utils.db import (
    save_plan,
    get_active_plan,
    delete_active_plan,
    save_progress,
    get_progress,
    get_all_progress,
    get_streak,
    save_streak,
)

from utils.progress_tracker import (
    build_workout_checks,
    build_dietary_checks,
    merge_checks,
    load_day_progress,
    toggle_workout_item,
    toggle_dietary_item,
    mark_day_complete,
    unmark_day,
    get_plan_stats,
    get_today_day_number,
    get_completion_heatmap,
)

from utils.streak_manager import (
    update_streak,
    get_streak_display,
    check_streak_milestone,
)

from utils.plan_manager import (
    build_combined_prompt,
    parse_plan_response,
    generate_full_plan,
)

from utils.workout_components import (
    render_safety_cautions,
    render_exercise_timer,
    render_stretch_videos,
    render_full_workout_day,
)

__all__ = [
    # db
    "save_plan",
    "get_active_plan",
    "delete_active_plan",
    "save_progress",
    "get_progress",
    "get_all_progress",
    "get_streak",
    "save_streak",
    # progress_tracker
    "build_workout_checks",
    "build_dietary_checks",
    "merge_checks",
    "load_day_progress",
    "toggle_workout_item",
    "toggle_dietary_item",
    "mark_day_complete",
    "unmark_day",
    "get_plan_stats",
    "get_today_day_number",
    "get_completion_heatmap",
    # streak_manager
    "update_streak",
    "get_streak_display",
    "check_streak_milestone",
    # plan_manager
    "build_combined_prompt",
    "parse_plan_response",
    "generate_full_plan",
    # workout_components
    "render_safety_cautions",
    "render_exercise_timer",
    "render_stretch_videos",
    "render_full_workout_day",
] 
