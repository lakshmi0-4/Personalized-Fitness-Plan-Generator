"""
utils/db.py — All Supabase + SQLite database operations for FitPlan Pro.
Handles: plans, plan_days, daily_progress, streaks.
Falls back to SQLite if Supabase is not configured.
"""

import os, json, time, uuid, sqlite3
import requests

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()
DB_PATH      = "/tmp/fitplan_plans.db"

USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_KEY)


# ══════════════════════════════════════════════════════════════════════════════
# SQLite setup (fallback)
# ══════════════════════════════════════════════════════════════════════════════

def _init_sqlite():
    """Create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            plan_id      TEXT PRIMARY KEY,
            username     TEXT NOT NULL,
            created_at   REAL,
            dietary_type TEXT,
            total_days   INTEGER,
            is_active    INTEGER DEFAULT 1
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS plan_days (
            id                TEXT PRIMARY KEY,
            plan_id           TEXT,
            day_number        INTEGER,
            muscle_group      TEXT,
            is_rest_day       INTEGER DEFAULT 0,
            workout_json      TEXT,
            dietary_json      TEXT,
            pre_stretch_json  TEXT,
            post_stretch_json TEXT
        )
    """)
    # Add columns if upgrading existing DB
    try:
        c.execute("ALTER TABLE plan_days ADD COLUMN muscle_group TEXT DEFAULT 'Full Body'")
    except Exception:
        pass
    try:
        c.execute("ALTER TABLE plan_days ADD COLUMN is_rest_day INTEGER DEFAULT 0")
    except Exception:
        pass

    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_progress (
            id               TEXT PRIMARY KEY,
            username         TEXT,
            plan_id          TEXT,
            day_number       INTEGER,
            date             TEXT,
            workout_checks   TEXT,
            dietary_checks   TEXT,
            day_completed    INTEGER DEFAULT 0,
            completed_at     REAL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS streaks (
            username            TEXT PRIMARY KEY,
            current_streak      INTEGER DEFAULT 0,
            longest_streak      INTEGER DEFAULT 0,
            last_completed_date TEXT,
            streak_history      TEXT DEFAULT '[]',
            opted_in            INTEGER DEFAULT 0,
            display_name        TEXT DEFAULT '',
            goal                TEXT DEFAULT ''
        )
    """)
    for _col_def in [
        "ALTER TABLE streaks ADD COLUMN opted_in INTEGER DEFAULT 0",
        "ALTER TABLE streaks ADD COLUMN display_name TEXT DEFAULT ''",
        "ALTER TABLE streaks ADD COLUMN goal TEXT DEFAULT ''",
    ]:
        try: c.execute(_col_def)
        except Exception: pass

    # ── INDEXES for query performance ─────────────────────────────────────
    for _idx in [
        "CREATE INDEX IF NOT EXISTS idx_plans_username ON plans(username)",
        "CREATE INDEX IF NOT EXISTS idx_plan_days_plan_id ON plan_days(plan_id)",
        "CREATE INDEX IF NOT EXISTS idx_daily_progress_user_plan ON daily_progress(username,plan_id)",
        "CREATE INDEX IF NOT EXISTS idx_streaks_username ON streaks(username)",
    ]:
        try: c.execute(_idx)
        except Exception: pass

    conn.commit()
    conn.close()


_init_sqlite()


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

def _headers():
    return {
        "apikey":        SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type":  "application/json",
        "Prefer":        "return=representation"
    }


def _sb_get(table, filters=""):
    """GET from Supabase."""
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/{table}?{filters}",
        headers=_headers(), timeout=10
    )
    return r.json() if r.ok else []


def _sb_post(table, data, upsert=False):
    """POST / upsert to Supabase."""
    h = _headers()
    if upsert:
        h["Prefer"] = "resolution=merge-duplicates,return=representation"
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=h, json=data, timeout=10
    )
    return r.ok


def _sb_patch(table, filters, data):
    """PATCH (update) Supabase rows."""
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{filters}",
        headers=_headers(), json=data, timeout=10
    )
    return r.ok


# ══════════════════════════════════════════════════════════════════════════════
# PLAN OPERATIONS
# ══════════════════════════════════════════════════════════════════════════════

def save_plan(username, dietary_type, total_days, days_data):
    """
    Save a newly generated plan + all day data.
    Deactivates any previous active plan for this user.
    Returns: plan_id (str)
    """
    plan_id = str(uuid.uuid4())

    if USE_SUPABASE:
        # Deactivate old plans
        _sb_patch("plans", f"username=eq.{username}&is_active=eq.true",
                  {"is_active": False})

        # Insert new plan
        _sb_post("plans", {
            "plan_id":      plan_id,
            "username":     username,
            "created_at":   time.time(),
            "dietary_type": dietary_type,
            "total_days":   total_days,
            "is_active":    True
        })

        # Insert each day
        for day_num, day in enumerate(days_data, 1):
            _sb_post("plan_days", {
                "id":                str(uuid.uuid4()),
                "plan_id":           plan_id,
                "day_number":        day_num,
                "muscle_group":      day.get("muscle_group", "Full Body"),
                "is_rest_day":       day.get("is_rest_day", False),
                "workout_json":      json.dumps(day.get("workout", [])),
                "dietary_json":      json.dumps(day.get("dietary", {})),
                "pre_stretch_json":  json.dumps(day.get("pre_stretch", [])),
                "post_stretch_json": json.dumps(day.get("post_stretch", []))
            })

    else:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Deactivate old plans
        c.execute("UPDATE plans SET is_active=0 WHERE username=?", (username,))

        # Insert new plan
        c.execute(
            "INSERT INTO plans VALUES (?,?,?,?,?,?)",
            (plan_id, username, time.time(), dietary_type, total_days, 1)
        )

        # Insert each day (with muscle_group and is_rest_day)
        for day_num, day in enumerate(days_data, 1):
            c.execute(
                "INSERT INTO plan_days VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    str(uuid.uuid4()), plan_id, day_num,
                    day.get("muscle_group", "Full Body"),
                    int(day.get("is_rest_day", False)),
                    json.dumps(day.get("workout", [])),
                    json.dumps(day.get("dietary", {})),
                    json.dumps(day.get("pre_stretch", [])),
                    json.dumps(day.get("post_stretch", []))
                )
            )

        conn.commit()
        conn.close()

    return plan_id


def get_active_plan(username):
    """
    Get user's current active plan with all days.
    Returns dict with plan metadata + days list, or None.
    """
    if USE_SUPABASE:
        plans = _sb_get("plans",
                        f"username=eq.{username}&is_active=eq.true&limit=1")
        if not plans:
            return None
        plan = plans[0]

        days = _sb_get("plan_days",
                       f"plan_id=eq.{plan['plan_id']}&order=day_number.asc")
        plan["days"] = days

    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute(
            "SELECT * FROM plans WHERE username=? AND is_active=1 LIMIT 1",
            (username,)
        )
        row = c.fetchone()
        if not row:
            conn.close()
            return None

        plan = dict(row)
        c.execute(
            "SELECT * FROM plan_days WHERE plan_id=? ORDER BY day_number ASC",
            (plan["plan_id"],)
        )
        rows = [dict(r) for r in c.fetchall()]
        # Ensure day_number field exists
        for row in rows:
            row.setdefault("day_number", row.get("day_number", 1))
        plan["days"] = rows
        conn.close()

    # Add human-readable date
    import datetime
    try:
        ts = plan.get("created_at", 0)
        plan["created_at_date"] = datetime.datetime.fromtimestamp(ts).date().isoformat() if ts else datetime.date.today().isoformat()
    except Exception:
        plan["created_at_date"] = datetime.date.today().isoformat()

    # Parse JSON strings in days
    for day in plan.get("days", []):
        for field in ["workout_json", "dietary_json",
                      "pre_stretch_json", "post_stretch_json"]:
            if isinstance(day.get(field), str):
                try:
                    day[field] = json.loads(day[field])
                except Exception:
                    day[field] = [] if field != "dietary_json" else {}

    return plan


def delete_active_plan(username):
    """Deactivate (soft-delete) the user's current plan."""
    if USE_SUPABASE:
        _sb_patch("plans", f"username=eq.{username}&is_active=eq.true",
                  {"is_active": False})
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "UPDATE plans SET is_active=0 WHERE username=?", (username,)
        )
        conn.commit()
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# PROGRESS OPERATIONS
# ══════════════════════════════════════════════════════════════════════════════

def save_progress(username, plan_id, day_number, workout_checks, dietary_checks):
    """
    Save checkbox progress for a specific day.
    Returns: True if day is fully completed, False otherwise.
    """
    from datetime import date as _date
    today = str(_date.today())

    all_workout = all(workout_checks.values()) if workout_checks else False
    all_dietary = all(dietary_checks.values()) if dietary_checks else False
    day_completed = all_workout and all_dietary

    row_id = f"{username}_{plan_id}_{day_number}"

    payload = {
        "id":              row_id,
        "username":        username,
        "plan_id":         plan_id,
        "day_number":      day_number,
        "date":            today,
        "workout_checks":  json.dumps(workout_checks),
        "dietary_checks":  json.dumps(dietary_checks),
        "day_completed":   day_completed,
        "completed_at":    time.time() if day_completed else None
    }

    if USE_SUPABASE:
        _sb_post("daily_progress", payload, upsert=True)
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT OR REPLACE INTO daily_progress
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            row_id, username, plan_id, day_number, today,
            json.dumps(workout_checks), json.dumps(dietary_checks),
            int(day_completed),
            time.time() if day_completed else None
        ))
        conn.commit()
        conn.close()

    return day_completed


def get_progress(username, plan_id, day_number):
    """
    Get saved checkbox state for a specific day.
    Returns dict: {workout_checks, dietary_checks, day_completed}
    """
    if USE_SUPABASE:
        rows = _sb_get(
            "daily_progress",
            f"username=eq.{username}&plan_id=eq.{plan_id}"
            f"&day_number=eq.{day_number}&limit=1"
        )
        row = rows[0] if rows else None
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            "SELECT * FROM daily_progress WHERE username=? AND plan_id=? AND day_number=?",
            (username, plan_id, day_number)
        )
        r = c.fetchone()
        row = dict(r) if r else None
        conn.close()

    if not row:
        return {"workout_checks": {}, "dietary_checks": {}, "day_completed": False}

    return {
        "workout_checks": json.loads(row.get("workout_checks") or "{}"),
        "dietary_checks": json.loads(row.get("dietary_checks") or "{}"),
        "day_completed":  bool(row.get("day_completed", False))
    }


def get_all_progress(username, plan_id):
    """
    Get progress for ALL days of a plan.
    Returns list of progress dicts.
    """
    if USE_SUPABASE:
        rows = _sb_get(
            "daily_progress",
            f"username=eq.{username}&plan_id=eq.{plan_id}&order=day_number.asc"
        )
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            "SELECT * FROM daily_progress WHERE username=? AND plan_id=? ORDER BY day_number ASC",
            (username, plan_id)
        )
        rows = [dict(r) for r in c.fetchall()]
        conn.close()

    result = []
    for row in rows:
        result.append({
            "day_number":     row["day_number"],
            "workout_checks": json.loads(row.get("workout_checks") or "{}"),
            "dietary_checks": json.loads(row.get("dietary_checks") or "{}"),
            "day_completed":  bool(row.get("day_completed", False)),
            "date":           row.get("date", "")
        })
    return result


# ══════════════════════════════════════════════════════════════════════════════
# STREAK OPERATIONS
# ══════════════════════════════════════════════════════════════════════════════

def get_streak(username):
    """
    Get current streak data for a user.
    Returns dict: {current_streak, longest_streak, last_completed_date, streak_history}
    """
    if USE_SUPABASE:
        rows = _sb_get("streaks", f"username=eq.{username}&limit=1")
        row = rows[0] if rows else None
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM streaks WHERE username=?", (username,))
        r = c.fetchone()
        row = dict(r) if r else None
        conn.close()

    if not row:
        return {
            "username":            username,
            "current_streak":      0,
            "longest_streak":      0,
            "last_completed_date": None,
            "streak_history":      []
        }

    return {
        "username":            row["username"],
        "current_streak":      row.get("current_streak", 0),
        "longest_streak":      row.get("longest_streak", 0),
        "last_completed_date": row.get("last_completed_date"),
        "streak_history":      json.loads(row.get("streak_history") or "[]")
    }


def save_streak(streak_data):
    """
    Save/update streak data for a user.
    streak_data must contain 'username'.
    """
    payload = {
        "username":            streak_data["username"],
        "current_streak":      streak_data.get("current_streak", 0),
        "longest_streak":      streak_data.get("longest_streak", 0),
        "last_completed_date": streak_data.get("last_completed_date"),
        "streak_history":      json.dumps(streak_data.get("streak_history", [])),
        "opted_in":            int(streak_data.get("opted_in", False)),
        "display_name":        streak_data.get("display_name", ""),
        "goal":                streak_data.get("goal", ""),
    }

    if USE_SUPABASE:
        _sb_post("streaks", payload, upsert=True)
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT OR REPLACE INTO streaks
            (username,current_streak,longest_streak,last_completed_date,streak_history,opted_in,display_name,goal)
            VALUES (?,?,?,?,?,?,?,?)
        """, (
            payload["username"], payload["current_streak"], payload["longest_streak"],
            payload["last_completed_date"], payload["streak_history"],
            payload["opted_in"], payload["display_name"], payload["goal"]
        ))
        conn.commit()
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# USER PROFILE OPERATIONS
# ══════════════════════════════════════════════════════════════════════════════

def _init_profile_table():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            username     TEXT PRIMARY KEY,
            name         TEXT,
            age          INTEGER,
            gender       TEXT,
            height       REAL,
            weight       REAL,
            fitness_level TEXT,
            goal         TEXT,
            days_per_week INTEGER,
            months       INTEGER,
            total_days   INTEGER,
            equipment    TEXT,
            home_eq      TEXT,
            gym_eq       TEXT,
            no_eq        INTEGER DEFAULT 0,
            updated_at   REAL
        )
    """)
    conn.commit()
    conn.close()

_init_profile_table()


def save_user_profile(username, profile_data):
    """Save user profile to DB. Upsert."""
    payload = {
        "username":      username,
        "name":          profile_data.get("name", ""),
        "age":           profile_data.get("age", 25),
        "gender":        profile_data.get("gender", "Male"),
        "height":        profile_data.get("height", 170),
        "weight":        profile_data.get("weight", 70),
        "fitness_level": profile_data.get("level", "Beginner"),
        "goal":          profile_data.get("goal", "General Fitness"),
        "days_per_week": profile_data.get("days_per_week", 5),
        "months":        profile_data.get("months", 1),
        "total_days":    profile_data.get("total_days", 20),
        "equipment":     json.dumps(profile_data.get("equipment", [])),
        "home_eq":       json.dumps(profile_data.get("home_eq", [])),
        "gym_eq":        json.dumps(profile_data.get("gym_eq", [])),
        "no_eq":         int(profile_data.get("no_eq", False)),
        "updated_at":    time.time(),
    }
    if USE_SUPABASE:
        import urllib.parse, urllib.request
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=representation"
        }
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/user_profiles",
            data=data, headers=headers, method="POST"
        )
        try:
            urllib.request.urlopen(req, timeout=10)
        except Exception:
            pass
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT OR REPLACE INTO user_profiles
            (username,name,age,gender,height,weight,fitness_level,goal,
             days_per_week,months,total_days,equipment,home_eq,gym_eq,no_eq,updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            payload["username"], payload["name"], payload["age"],
            payload["gender"], payload["height"], payload["weight"],
            payload["fitness_level"], payload["goal"],
            payload["days_per_week"], payload["months"], payload["total_days"],
            payload["equipment"], payload["home_eq"], payload["gym_eq"],
            payload["no_eq"], payload["updated_at"]
        ))
        conn.commit()
        conn.close()


def get_user_profile(username):
    """Load user profile from DB. Returns dict or None."""
    if USE_SUPABASE:
        import urllib.request, urllib.parse
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
        }
        url = f"{SUPABASE_URL}/rest/v1/user_profiles?username=eq.{urllib.parse.quote(username)}&select=*&limit=1"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=8) as r:
                rows = json.loads(r.read().decode())
                row = rows[0] if rows else None
        except Exception:
            row = None
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM user_profiles WHERE username=?", (username,))
        r = c.fetchone()
        row = dict(r) if r else None
        conn.close()

    if not row:
        return None

    return {
        "name":         row.get("name", ""),
        "age":          row.get("age", 25),
        "gender":       row.get("gender", "Male"),
        "height":       row.get("height", 170),
        "weight":       row.get("weight", 70),
        "level":        row.get("fitness_level", "Beginner"),
        "goal":         row.get("goal", "General Fitness"),
        "days_per_week":row.get("days_per_week", 5),
        "months":       row.get("months", 1),
        "total_days":   row.get("total_days", 20),
        "equipment":    json.loads(row.get("equipment") or "[]"),
        "home_eq":      json.loads(row.get("home_eq") or "[]"),
        "gym_eq":       json.loads(row.get("gym_eq") or "[]"),
        "no_eq":        bool(row.get("no_eq", False)),
    }


# ══════════════════════════════════════════════════════════════════════════════
# WEIGHT LOG
# ══════════════════════════════════════════════════════════════════════════════

def _init_weight_log():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS weight_log (
            id         TEXT PRIMARY KEY,
            username   TEXT NOT NULL,
            date       TEXT NOT NULL,
            weight_kg  REAL NOT NULL
        )
    """)
    conn.commit(); conn.close()

_init_weight_log()


def save_weight_log(username, date_str, weight_kg):
    row_id = f"{username}_{date_str}"
    if USE_SUPABASE:
        _sb_post("weight_log", {
            "id": row_id, "username": username,
            "date": date_str, "weight_kg": weight_kg
        }, upsert=True)
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT OR REPLACE INTO weight_log VALUES (?,?,?,?)",
                     (row_id, username, date_str, weight_kg))
        conn.commit(); conn.close()


def get_weight_log(username, limit=60):
    if USE_SUPABASE:
        rows = _sb_get("weight_log",
            f"username=eq.{username}&order=date.asc&limit={limit}")
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = [dict(r) for r in conn.execute(
            "SELECT * FROM weight_log WHERE username=? ORDER BY date ASC LIMIT ?",
            (username, limit)).fetchall()]
        conn.close()
    return [{"date": r["date"], "weight_kg": r["weight_kg"]} for r in rows]


# ══════════════════════════════════════════════════════════════════════════════
# WORKOUT NOTES
# ══════════════════════════════════════════════════════════════════════════════

def _init_workout_notes():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS workout_notes (
            id           TEXT PRIMARY KEY,
            username     TEXT NOT NULL,
            plan_id      TEXT NOT NULL,
            day_number   INTEGER NOT NULL,
            exercise_idx INTEGER NOT NULL,
            note         TEXT DEFAULT ''
        )
    """)
    conn.commit(); conn.close()

_init_workout_notes()


def save_workout_note(username, plan_id, day_number, exercise_idx, note):
    row_id = f"{username}_{plan_id}_{day_number}_{exercise_idx}"
    if USE_SUPABASE:
        _sb_post("workout_notes", {
            "id": row_id, "username": username, "plan_id": plan_id,
            "day_number": day_number, "exercise_idx": exercise_idx, "note": note
        }, upsert=True)
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT OR REPLACE INTO workout_notes VALUES (?,?,?,?,?,?)",
                     (row_id, username, plan_id, day_number, exercise_idx, note))
        conn.commit(); conn.close()


def get_workout_notes(username, plan_id, day_number):
    """Returns dict: {exercise_idx: note_text}"""
    if USE_SUPABASE:
        rows = _sb_get("workout_notes",
            f"username=eq.{username}&plan_id=eq.{plan_id}&day_number=eq.{day_number}")
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = [dict(r) for r in conn.execute(
            "SELECT * FROM workout_notes WHERE username=? AND plan_id=? AND day_number=?",
            (username, plan_id, day_number)).fetchall()]
        conn.close()
    return {r["exercise_idx"]: r["note"] for r in rows if r.get("note")}


# ══════════════════════════════════════════════════════════════════════════════
# WATER TRACKER
# ══════════════════════════════════════════════════════════════════════════════

def _init_water_tracker():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS water_tracker (
            id       TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            date     TEXT NOT NULL,
            glasses  INTEGER DEFAULT 0
        )
    """)
    conn.commit(); conn.close()

_init_water_tracker()


def save_water(username, date_str, glasses):
    row_id = f"{username}_{date_str}"
    if USE_SUPABASE:
        _sb_post("water_tracker", {
            "id": row_id, "username": username,
            "date": date_str, "glasses": glasses
        }, upsert=True)
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT OR REPLACE INTO water_tracker VALUES (?,?,?,?)",
                     (row_id, username, date_str, glasses))
        conn.commit(); conn.close()


def get_water(username, date_str):
    if USE_SUPABASE:
        rows = _sb_get("water_tracker",
            f"username=eq.{username}&date=eq.{date_str}&limit=1")
        return rows[0]["glasses"] if rows else 0
    else:
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute(
            "SELECT glasses FROM water_tracker WHERE username=? AND date=?",
            (username, date_str)).fetchone()
        conn.close()
        return row[0] if row else 0


# ══════════════════════════════════════════════════════════════════════════════
# PERSONAL RECORDS
# ══════════════════════════════════════════════════════════════════════════════

def _init_personal_records():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS personal_records (
            id         TEXT PRIMARY KEY,
            username   TEXT NOT NULL,
            exercise   TEXT NOT NULL,
            value      REAL NOT NULL,
            unit       TEXT DEFAULT 'reps',
            date       TEXT NOT NULL,
            note       TEXT DEFAULT ''
        )
    """)
    conn.commit(); conn.close()

_init_personal_records()


def save_personal_record(username, exercise, value, unit, date_str, note=""):
    row_id = str(uuid.uuid4())
    payload = {"id": row_id, "username": username, "exercise": exercise,
               "value": value, "unit": unit, "date": date_str, "note": note}
    if USE_SUPABASE:
        _sb_post("personal_records", payload)
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO personal_records VALUES (?,?,?,?,?,?,?)",
                     (row_id, username, exercise, value, unit, date_str, note))
        conn.commit(); conn.close()


def get_personal_records(username):
    if USE_SUPABASE:
        rows = _sb_get("personal_records",
                       f"username=eq.{username}&order=date.asc")
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = [dict(r) for r in conn.execute(
            "SELECT * FROM personal_records WHERE username=? ORDER BY date ASC",
            (username,)).fetchall()]
        conn.close()
    return rows


def delete_personal_record(record_id):
    if USE_SUPABASE:
        import requests as _req
        _req.delete(f"{SUPABASE_URL}/rest/v1/personal_records?id=eq.{record_id}",
                    headers=_headers(), timeout=10)
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("DELETE FROM personal_records WHERE id=?", (record_id,))
        conn.commit(); conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# BODY MEASUREMENTS
# ══════════════════════════════════════════════════════════════════════════════

def _init_measurements():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS body_measurements (
            id       TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            date     TEXT NOT NULL,
            chest    REAL,
            waist    REAL,
            hips     REAL,
            arms     REAL,
            thighs   REAL
        )
    """)
    conn.commit(); conn.close()

_init_measurements()


def save_measurements(username, date_str, chest, waist, hips, arms, thighs):
    row_id = f"{username}_{date_str}"
    payload = {"id": row_id, "username": username, "date": date_str,
               "chest": chest, "waist": waist, "hips": hips,
               "arms": arms, "thighs": thighs}
    if USE_SUPABASE:
        _sb_post("body_measurements", payload, upsert=True)
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT OR REPLACE INTO body_measurements VALUES (?,?,?,?,?,?,?,?)",
                     (row_id, username, date_str, chest, waist, hips, arms, thighs))
        conn.commit(); conn.close()


def get_measurements(username, limit=20):
    if USE_SUPABASE:
        rows = _sb_get("body_measurements",
                       f"username=eq.{username}&order=date.asc&limit={limit}")
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = [dict(r) for r in conn.execute(
            "SELECT * FROM body_measurements WHERE username=? ORDER BY date ASC LIMIT ?",
            (username, limit)).fetchall()]
        conn.close()
    return rows


# ══════════════════════════════════════════════════════════════════════════════
# CHAT HISTORY
# ══════════════════════════════════════════════════════════════════════════════

def _init_chat():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id         TEXT PRIMARY KEY,
            username   TEXT NOT NULL,
            role       TEXT NOT NULL,
            content    TEXT NOT NULL,
            created_at REAL
        )
    """)
    conn.commit(); conn.close()

_init_chat()


def save_chat_message(username, role, content):
    row_id = str(uuid.uuid4())
    if USE_SUPABASE:
        _sb_post("chat_history", {"id": row_id, "username": username,
                  "role": role, "content": content, "created_at": time.time()})
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO chat_history VALUES (?,?,?,?,?)",
                     (row_id, username, role, content, time.time()))
        conn.commit(); conn.close()


def get_chat_messages_raw(username, limit=50):
    """Get raw chat messages directly from chat_history table (used internally)."""
    if USE_SUPABASE:
        rows = _sb_get("chat_history",
                       f"username=eq.{username}&order=created_at.asc&limit={limit}")
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = [dict(r) for r in conn.execute(
            "SELECT * FROM chat_history WHERE username=? ORDER BY created_at ASC LIMIT ?",
            (username, limit)).fetchall()]
        conn.close()
    return [{"role": r["role"], "content": r["content"]} for r in rows]


def clear_chat_history(username):
    if USE_SUPABASE:
        import requests as _req
        _req.delete(f"{SUPABASE_URL}/rest/v1/chat_history?username=eq.{username}",
                    headers=_headers(), timeout=10)
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("DELETE FROM chat_history WHERE username=?", (username,))
        conn.commit(); conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# SAVE CHAT HISTORY (bulk — replaces per-message save for AI Coach fix #8)
# ══════════════════════════════════════════════════════════════════════════════
def save_chat_history(username, messages):
    """Save full chat history (list of {role,content} dicts)."""
    import json
    payload = json.dumps(messages)
    if USE_SUPABASE:
        _sb_post("user_settings", {"username": username,
                  "setting_key": "chat_history", "setting_value": payload})
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                username TEXT, setting_key TEXT, setting_value TEXT,
                PRIMARY KEY (username, setting_key))
        """)
        conn.execute(
            "INSERT OR REPLACE INTO user_settings VALUES (?,?,?)",
            (username, "chat_history", payload))
        conn.commit(); conn.close()


def get_chat_history(username, limit=20):
    """Load full chat history."""
    import json
    val = get_user_setting(username, "chat_history")
    if val:
        try:
            msgs = json.loads(val)
            return msgs[-limit:] if msgs else []
        except Exception:
            pass
    return []


# ══════════════════════════════════════════════════════════════════════════════
# USER SETTINGS (key-value store — supplements, preferences, etc.)
# ══════════════════════════════════════════════════════════════════════════════
def _init_user_settings():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            username    TEXT NOT NULL,
            setting_key TEXT NOT NULL,
            setting_value TEXT,
            updated_at  REAL,
            PRIMARY KEY (username, setting_key)
        )
    """)
    conn.commit(); conn.close()

_init_user_settings()


def save_user_setting(username, key, value):
    if USE_SUPABASE:
        _sb_post("user_settings", {
            "username": username, "setting_key": key,
            "setting_value": str(value), "updated_at": time.time()})
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT OR REPLACE INTO user_settings VALUES (?,?,?,?)",
            (username, key, str(value), time.time()))
        conn.commit(); conn.close()


def get_user_setting(username, key, default=None):
    if USE_SUPABASE:
        rows = _sb_get("user_settings",
                       f"username=eq.{username}&setting_key=eq.{key}&limit=1")
        if rows: return rows[0].get("setting_value", default)
    else:
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute(
            "SELECT setting_value FROM user_settings WHERE username=? AND setting_key=?",
            (username, key)).fetchone()
        conn.close()
        if row: return row[0]
    return default


# ══════════════════════════════════════════════════════════════════════════════
# PROGRESS PHOTOS (Fix #10 — persist photos across sessions)
# ══════════════════════════════════════════════════════════════════════════════
def _init_progress_photos():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS progress_photos (
            id         TEXT PRIMARY KEY,
            username   TEXT NOT NULL,
            photo_date TEXT,
            label      TEXT,
            b64        TEXT,
            mime       TEXT,
            created_at REAL
        )
    """)
    conn.commit(); conn.close()

_init_progress_photos()


def save_progress_photo(username, photo_dict):
    row_id = str(uuid.uuid4())
    if USE_SUPABASE:
        _sb_post("progress_photos", {
            "id": row_id, "username": username,
            "photo_date": photo_dict.get("date",""),
            "label": photo_dict.get("label",""),
            "b64": photo_dict.get("b64",""),
            "mime": photo_dict.get("mime","image/jpeg"),
            "created_at": time.time()})
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO progress_photos VALUES (?,?,?,?,?,?,?)",
                     (row_id, username, photo_dict.get("date",""),
                      photo_dict.get("label",""), photo_dict.get("b64",""),
                      photo_dict.get("mime","image/jpeg"), time.time()))
        conn.commit(); conn.close()


def get_progress_photos(username, limit=50):
    if USE_SUPABASE:
        rows = _sb_get("progress_photos",
                       f"username=eq.{username}&order=created_at.asc&limit={limit}")
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = [dict(r) for r in conn.execute(
            "SELECT * FROM progress_photos WHERE username=? ORDER BY created_at ASC LIMIT ?",
            (username, limit)).fetchall()]
        conn.close()
    return [{"date":r.get("photo_date",""),
             "label":r.get("label",""),
             "b64":r.get("b64",""),
             "mime":r.get("mime","image/jpeg")} for r in rows]


def delete_progress_photo(username, photo_date, label):
    if USE_SUPABASE:
        import requests as _req
        _req.delete(f"{SUPABASE_URL}/rest/v1/progress_photos"
                    f"?username=eq.{username}&photo_date=eq.{photo_date}&label=eq.{label}",
                    headers=_headers(), timeout=10)
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("DELETE FROM progress_photos WHERE username=? AND photo_date=? AND label=?",
                     (username, photo_date, label))
        conn.commit(); conn.close()


# ── COMPATIBILITY ALIASES — fixes wrong function names used in pages ──────────
def get_water_intake(username, date_str):
    """Alias for get_water() — fixes wrong name in 4_Diet_Plan.py"""
    return get_water(username, date_str)

def save_water_intake(username, date_str, glasses):
    """Alias for save_water() — fixes wrong name in 4_Diet_Plan.py"""
    return save_water(username, date_str, glasses)

def save_personal_records(username, records_dict):
    """Alias — fixes wrong bulk-save call in 6_records.py.
    records_dict = {exercise_name: [{value, unit, date}, ...]}
    """
    from datetime import date as _d
    today = _d.today().isoformat()
    for ex_name, entries in records_dict.items():
        if entries:
            e = entries[-1]
            save_personal_record(
                username, ex_name,
                e.get("value", 0), e.get("unit", "reps"),
                e.get("date", today), e.get("note", "")
            )

def get_body_measurements(username, limit=20):
    """Alias for get_measurements() — fixes wrong name in 6_records.py"""
    return get_measurements(username, limit)

def save_body_measurements(username, meas_list):
    """Alias — fixes wrong call in 6_records.py.
    meas_list = list of measurement entry dicts
    """
    from datetime import date as _d
    today = _d.today().isoformat()
    if meas_list:
        entry = meas_list[-1]
        m = entry.get("measurements", {})
        save_measurements(
            username,
            entry.get("date", today),
            m.get("Chest (cm)", 0), m.get("Waist (cm)", 0),
            m.get("Hips (cm)", 0), m.get("Left Arm (cm)", 0),
            m.get("Left Thigh (cm)", 0)
        )