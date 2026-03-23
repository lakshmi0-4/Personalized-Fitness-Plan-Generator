"""
utils/plan_manager.py — Plan generation, prompt building, and response parsing.
Generates combined workout + dietary plan via Groq API in chunks.
Robust JSON parsing handles truncated/malformed model responses.
"""

import json, re, time


# ══════════════════════════════════════════════════════════════════════════════
# Prompt builder
# ══════════════════════════════════════════════════════════════════════════════

def build_combined_prompt(user_data, dietary_type, start_day, chunk_size):
    """
    Build a prompt that generates both workout + dietary plan for a chunk of days.
    Returns: prompt string
    """
    end_day    = start_day + chunk_size - 1
    diet_label = "Vegetarian" if dietary_type == "veg" else "Non-Vegetarian"
    eq_list    = ", ".join(user_data.get("equipment", [])) or "No equipment (bodyweight only)"

    intensity_map = {
        "Beginner":     "2-3 sets, light-moderate weight, 90s rest, focus on form",
        "Intermediate": "3-4 sets, moderate-heavy weight, 60-75s rest",
        "Advanced":     "4-5 sets, heavy compounds, 45-60s rest, supersets ok",
    }
    intensity = intensity_map.get(user_data.get("level", "Beginner"),
                                  "3 sets, 60s rest")

    return f"""You are a certified fitness trainer and nutritionist.
Generate a {diet_label} workout and diet plan for Days {start_day} to {end_day} only.

USER:
- Name: {user_data.get('name','User')}, Age: {user_data.get('age',25)}
- Goal: {user_data.get('goal','General Fitness')}, Level: {user_data.get('level','Beginner')}
- Equipment: {eq_list}
- Diet: {diet_label}, intensity: {intensity}

OUTPUT EXACTLY this JSON array (no extra text, no markdown, no explanation):
[
  {{
    "day": {start_day},
    "muscle_group": "Upper Body",
    "workout": [
      {{
        "name": "Push-ups",
        "sets": 3,
        "reps": "12",
        "rest": "60s",
        "timer": 60,
        "notes": "Keep core tight, elbows at 45 degrees"
      }}
    ],
    "dietary": {{
      "breakfast": "Oats with banana and honey",
      "lunch": "Grilled chicken with brown rice and vegetables",
      "dinner": "Dal with roti and salad",
      "snacks": "Handful of mixed nuts and a fruit"
    }},
    "pre_stretch": [
      {{
        "name": "Arm circles",
        "duration": "30s",
        "video_url": "https://www.youtube.com/embed/HDiHMHBpHBQ"
      }}
    ],
    "post_stretch": [
      {{
        "name": "Chest stretch",
        "duration": "30s",
        "video_url": "https://www.youtube.com/embed/qULTwquOuT4"
      }}
    ]
  }}
]

Rules:
- Output ONLY the JSON array. Absolutely no text before or after.
- Generate exactly {chunk_size} day object(s): days {start_day} through {end_day}.
- Each workout must have 5-7 exercises appropriate for {user_data.get('level','Beginner')}.
- Use {eq_list} only for exercises.
- {"Use ONLY vegetarian ingredients." if dietary_type == "veg" else "Include non-vegetarian protein sources."}
- Vary muscle groups each day.
- Timer value = exercise duration in seconds (e.g. plank=30, jumping jacks=45, rest=60).
- Make sure the JSON is complete and properly closed with ]"""


# ══════════════════════════════════════════════════════════════════════════════
# Response parser — robust against truncation
# ══════════════════════════════════════════════════════════════════════════════

def _repair_truncated_json(text):
    """
    Attempt to repair a truncated JSON array by closing open structures.
    This handles the "Unexpected end of JSON input" error.
    """
    text = text.strip()

    # Remove markdown code fences if present
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to extract JSON array from surrounding text
    match = re.search(r'(\[.*\])', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            text = match.group(1)

    # Repair truncated JSON — close any open structures
    repaired = _close_json(text)
    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        return None


def _close_json(s):
    """
    Close any unclosed brackets/braces in a JSON string.
    Handles truncated model responses.
    """
    # Track open structures
    stack   = []
    in_str  = False
    escape  = False
    result  = []

    for i, ch in enumerate(s):
        if escape:
            escape = False
            result.append(ch)
            continue

        if ch == '\\' and in_str:
            escape = True
            result.append(ch)
            continue

        if ch == '"' and not escape:
            in_str = not in_str
            result.append(ch)
            continue

        if in_str:
            result.append(ch)
            continue

        if ch in '{[':
            stack.append(ch)
            result.append(ch)
        elif ch in '}]':
            if stack:
                stack.pop()
            result.append(ch)
        else:
            result.append(ch)

    # If we're in a string, close it
    if in_str:
        result.append('"')

    # Close any open key-value that's incomplete
    joined = ''.join(result).rstrip().rstrip(',')

    # Close remaining open structures in reverse order
    for opener in reversed(stack):
        if opener == '{':
            joined += '}'
        elif opener == '[':
            joined += ']'

    return joined


def parse_plan_response(text):
    """
    Parse model response into list of day dicts.
    Returns: list of day dicts, or [] on complete failure.
    """
    if not text:
        return []

    parsed = _repair_truncated_json(text)

    if parsed is None:
        return []

    if isinstance(parsed, list):
        return [_validate_day(d) for d in parsed if isinstance(d, dict)]

    if isinstance(parsed, dict):
        return [_validate_day(parsed)]

    return []


def _validate_day(day):
    """
    Ensure a day dict has all required fields with sensible defaults.
    """
    return {
        "day":          day.get("day", 1),
        "muscle_group": day.get("muscle_group", "Full Body"),
        "workout":      _validate_workout(day.get("workout", [])),
        "dietary":      _validate_dietary(day.get("dietary", {})),
        "pre_stretch":  day.get("pre_stretch", _default_pre_stretch()),
        "post_stretch": day.get("post_stretch", _default_post_stretch())
    }


def _validate_workout(workout):
    """Ensure each exercise has required fields."""
    if not isinstance(workout, list):
        return []
    valid = []
    for ex in workout:
        if not isinstance(ex, dict):
            continue
        valid.append({
            "name":  ex.get("name", "Exercise"),
            "sets":  ex.get("sets", 3),
            "reps":  str(ex.get("reps", "12")),
            "rest":  ex.get("rest", "60s"),
            "timer": int(ex.get("timer", 60)),
            "notes": ex.get("notes", "Focus on proper form")
        })
    return valid


def _validate_dietary(dietary):
    """Ensure dietary dict has all meal slots."""
    if not isinstance(dietary, dict):
        return {
            "breakfast": "Oats with fruits",
            "lunch":     "Rice with vegetables and protein",
            "dinner":    "Light meal with salad",
            "snacks":    "Fruits and nuts"
        }
    return {
        "breakfast": dietary.get("breakfast", "Balanced breakfast"),
        "lunch":     dietary.get("lunch",     "Balanced lunch"),
        "dinner":    dietary.get("dinner",    "Light dinner"),
        "snacks":    dietary.get("snacks",    "Healthy snacks")
    }


def _default_pre_stretch():
    return [
        {"name": "Arm Circles",        "duration": "30s",
         "video_url": "https://www.youtube.com/embed/HDiHMHBpHBQ"},
        {"name": "Leg Swings",         "duration": "30s",
         "video_url": "https://www.youtube.com/embed/HDiHMHBpHBQ"},
        {"name": "Hip Rotations",      "duration": "30s",
         "video_url": "https://www.youtube.com/embed/HDiHMHBpHBQ"}
    ]


def _default_post_stretch():
    return [
        {"name": "Quad Stretch",       "duration": "30s",
         "video_url": "https://www.youtube.com/embed/qULTwquOuT4"},
        {"name": "Hamstring Stretch",  "duration": "30s",
         "video_url": "https://www.youtube.com/embed/qULTwquOuT4"},
        {"name": "Child's Pose",       "duration": "45s",
         "video_url": "https://www.youtube.com/embed/qULTwquOuT4"}
    ]


# ══════════════════════════════════════════════════════════════════════════════
# Main generation function
# ══════════════════════════════════════════════════════════════════════════════

def generate_full_plan(user_data, dietary_type, total_days,
                       progress_callback=None):
    """
    Generate a complete day-by-day workout + diet plan via Groq.
    Splits into chunks of 2 days to avoid token cutoff.

    progress_callback(chunk_num, total_chunks, days_done) — optional

    Returns: list of day dicts (validated)
    """
    from model_api import query_model

    CHUNK_SIZE   = 2   # 2 days per chunk — safe limit to avoid truncation
    all_days     = []
    total_chunks = max(1, (total_days + CHUNK_SIZE - 1) // CHUNK_SIZE)
    chunk_num    = 0

    for start in range(1, total_days + 1, CHUNK_SIZE):
        chunk_num += 1
        chunk_size = min(CHUNK_SIZE, total_days - start + 1)

        if progress_callback:
            progress_callback(chunk_num, total_chunks, start - 1)

        prompt = build_combined_prompt(user_data, dietary_type, start, chunk_size)

        # Retry up to 3 times
        parsed_days = []
        for attempt in range(3):
            try:
                # Use higher max_tokens to avoid truncation
                response = query_model(prompt, max_tokens=2500)
                parsed_days = parse_plan_response(response)

                if parsed_days:
                    break
                else:
                    # Empty parse — retry with explicit reminder
                    if attempt < 2:
                        time.sleep(2)
                        continue

            except ValueError as e:
                err = str(e)
                if "rate limit" in err.lower() and attempt < 2:
                    time.sleep(65)
                    continue
                raise
            except Exception:
                if attempt < 2:
                    time.sleep(5)
                    continue
                raise

        # If parsing still failed, create placeholder days
        if not parsed_days:
            for d in range(chunk_size):
                parsed_days.append(_build_fallback_day(start + d))

        # Fix day numbers in case model returned wrong ones
        for i, day in enumerate(parsed_days):
            day["day"] = start + i

        all_days.extend(parsed_days[:chunk_size])

        # Pause between chunks (free tier rate limit)
        if start + CHUNK_SIZE <= total_days:
            time.sleep(1)

    if progress_callback:
        progress_callback(total_chunks, total_chunks, total_days)

    return all_days


def _build_fallback_day(day_number):
    """Build a generic fallback day if model parsing fails completely."""
    workouts_by_day = {
        1: [
            {"name": "Push-ups",       "sets": 3, "reps": "12", "rest": "60s", "timer": 60, "notes": "Elbows at 45°"},
            {"name": "Squats",         "sets": 3, "reps": "15", "rest": "60s", "timer": 60, "notes": "Knees over toes"},
            {"name": "Plank",          "sets": 3, "reps": "30s","rest": "45s", "timer": 30, "notes": "Straight line"},
            {"name": "Lunges",         "sets": 3, "reps": "10", "rest": "60s", "timer": 60, "notes": "Step forward"},
            {"name": "Mountain Climbers","sets":3, "reps":"20", "rest": "45s", "timer": 45, "notes": "Fast pace"},
        ],
        2: [
            {"name": "Jumping Jacks",  "sets": 3, "reps": "30", "rest": "45s", "timer": 45, "notes": "Full extension"},
            {"name": "Burpees",        "sets": 3, "reps": "10", "rest": "75s", "timer": 60, "notes": "Controlled drop"},
            {"name": "High Knees",     "sets": 3, "reps": "30s","rest": "45s", "timer": 30, "notes": "Drive knees up"},
            {"name": "Bicycle Crunches","sets":3, "reps":"20", "rest": "45s", "timer": 45, "notes": "Twist fully"},
            {"name": "Wall Sit",       "sets": 3, "reps": "30s","rest": "60s", "timer": 30, "notes": "90 degree angle"},
        ]
    }
    workout = workouts_by_day.get((day_number - 1) % 2 + 1,
                                  workouts_by_day[1])

    return {
        "day":          day_number,
        "muscle_group": "Full Body",
        "workout":      workout,
        "dietary":      _validate_dietary({}),
        "pre_stretch":  _default_pre_stretch(),
        "post_stretch": _default_post_stretch()
    } 