# -*- coding: utf-8 -*-
"""Achievement badges engine — checks conditions and awards badges."""
from datetime import date, timedelta

BADGES = [
    # (id, icon, title, description, condition_key)
    ("first_workout",  "🏋️", "First Rep",        "Completed your very first workout",           "workouts_done >= 1"),
    ("three_day",      "🔥", "On Fire",           "3-day workout streak",                        "streak >= 3"),
    ("seven_day",      "⚡", "Week Warrior",      "7-day workout streak — one full week!",       "streak >= 7"),
    ("fourteen_day",   "💪", "Two Week Grind",    "14 consecutive workout days",                 "streak >= 14"),
    ("thirty_day",     "🏆", "Month Master",      "30-day streak — you're unstoppable!",         "streak >= 30"),
    ("first_meal",     "🥗", "Clean Eater",       "Logged your first complete meal day",         "meals_done >= 4"),
    ("water_goal",     "💧", "Hydration Hero",    "Hit your 8-glass water goal",                 "water_glasses >= 8"),
    ("first_pr",       "📈", "Personal Best",     "Set your first personal record",              "total_prs >= 1"),
    ("five_prs",       "🥇", "Record Breaker",    "Set 5 personal records",                      "total_prs >= 5"),
    ("first_photo",    "📸", "Transformation Starts", "Uploaded your first progress photo",      "photos >= 1"),
    ("halfway",        "🎯", "Halfway There",     "Completed 50% of your plan",                  "plan_pct >= 50"),
    ("plan_done",      "🎖️", "Plan Complete",     "Finished your entire fitness plan!",          "plan_pct >= 100"),
    ("ten_workouts",   "💥", "Double Digits",     "Completed 10 total workouts",                 "workouts_done >= 10"),
    ("twenty_five",    "🌟", "Quarter Century",   "25 workouts done — elite territory",          "workouts_done >= 25"),
    ("ai_chat",        "🤖", "AI Powered",        "Had your first AI coaching session",          "ai_chats >= 1"),
    ("meal_streak_7",  "🥦", "Clean Week",        "Logged meals for 7 days in a row",            "meal_streak >= 7"),
    ("weight_logged",  "⚖️",  "Scale Watcher",    "Logged your body weight",                     "weight_logs >= 1"),
    ("measurements",   "📏", "Body Check",        "Logged body measurements",                    "measurements >= 1"),
]

def compute_stats(uname, session_state):
    """Compute all stats needed to evaluate badge conditions."""
    sdays      = session_state.get("structured_days", [])
    tracking   = session_state.get("tracking", {})
    plan_dur   = max(len(sdays), 1)

    workouts_done = sum(1 for v in tracking.values() if v.get("status") == "done")
    streak        = session_state.get("_db_streak", 0)
    plan_pct      = int(workouts_done / plan_dur * 100)

    # Count meals done
    meals_done = 0
    for i, sd in enumerate(sdays[:7]):
        dn = sd.get("day", i+1)
        for meal in ["breakfast","lunch","dinner","snacks"]:
            if session_state.get(f"meal_d{dn}_{meal}", False):
                meals_done += 1

    # Water
    today = date.today().isoformat()
    water_glasses = session_state.get(f"water_{uname}_{today}", 0)

    # PRs
    prs       = session_state.get("personal_records", {})
    total_prs = sum(len(v) for v in prs.values())

    # Photos
    photos = len(session_state.get("progress_photos", []))

    # AI chats
    ai_chats = len(session_state.get("chat_messages", []))

    # Meal streak (days with all 4 meals logged)
    meal_streak = 0
    check_date  = date.today()
    for _ in range(30):
        _dn = None
        _ps = date.fromisoformat(session_state.get("plan_start", today))
        _off = (check_date - _ps).days
        if 0 <= _off < len(sdays):
            _dn = sdays[_off].get("day", _off+1)
        if _dn and all(session_state.get(f"meal_d{_dn}_{m}", False)
                       for m in ["breakfast","lunch","dinner","snacks"]):
            meal_streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    # Weight logs / measurements
    weight_logs   = len(session_state.get("_wlog_history", []))
    measurements  = len(session_state.get("body_measurements", []))

    return {
        "workouts_done": workouts_done,
        "streak":        streak,
        "plan_pct":      plan_pct,
        "meals_done":    meals_done,
        "water_glasses": water_glasses,
        "total_prs":     total_prs,
        "photos":        photos,
        "ai_chats":      ai_chats,
        "meal_streak":   meal_streak,
        "weight_logs":   weight_logs,
        "measurements":  measurements,
    }


def get_earned_badges(stats):
    """Return list of earned badge dicts."""
    earned = []
    for bid, icon, title, desc, cond in BADGES:
        try:
            if eval(cond, {}, stats):
                earned.append({"id":bid,"icon":icon,"title":title,"desc":desc})
        except Exception:
            pass
    return earned


def get_next_badge(stats):
    """Return the next badge the user is closest to earning."""
    for bid, icon, title, desc, cond in BADGES:
        try:
            if not eval(cond, {}, stats):
                return {"id":bid,"icon":icon,"title":title,"desc":desc,"cond":cond}
        except Exception:
            pass
    return None


def render_badges_html(earned, compact=False):
    """Return HTML string for badge display."""
    if not earned:
        return ("<div style='text-align:center;padding:20px;color:rgba(255,255,255,0.35);"
                "font-size:0.82rem'>Complete workouts to earn your first badge! 🏅</div>")

    if compact:
        # Small icons only
        icons = "".join(
            "<span title='" + b["title"] + "' style='font-size:1.4rem;cursor:default'>" + b["icon"] + "</span>"
            for b in earned
        )
        return f"<div style='display:flex;gap:6px;flex-wrap:wrap;align-items:center'>{icons}</div>"

    cards = ""
    for b in earned:
        cards += (
            f"<div style='background:rgba(229,9,20,0.12);border:1.5px solid rgba(229,9,20,0.35);"
            f"border-radius:12px;padding:14px 16px;text-align:center;min-width:120px;"
            f"flex:1;max-width:150px'>"
            f"<div style='font-size:2rem;margin-bottom:6px'>{b['icon']}</div>"
            f"<div style='font-size:0.72rem;font-weight:700;color:#fff;margin-bottom:3px'>{b['title']}</div>"
            f"<div style='font-size:0.60rem;color:rgba(255,255,255,0.45);line-height:1.4'>{b['desc']}</div>"
            f"</div>"
        )
    return (f"<div style='display:flex;flex-wrap:wrap;gap:10px;justify-content:flex-start'>"
            f"{cards}</div>")