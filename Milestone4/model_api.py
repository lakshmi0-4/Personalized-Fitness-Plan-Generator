"""
model_api.py — Fast AI plan generation for FitPlan Pro.

Uses llama-3.1-8b-instant (131,072 TPM free tier) for speed.
Generates full plan in ONE API call — no chunking needed.
Typical time: 10-20 seconds for a 20-day plan.
"""

import os, time, json, re


# ══════════════════════════════════════════════════════════════════════════════
# Groq API call
# ══════════════════════════════════════════════════════════════════════════════

def query_model(prompt, max_tokens=8000, model="llama-3.1-8b-instant"):
    """Single Groq call. Uses 8b-instant by default (131k TPM — very fast)."""
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY not set.\n"
            "1. Go to https://console.groq.com\n"
            "2. Create API Key (gsk_...)\n"
            "3. HuggingFace > Settings > Secrets > GROQ_API_KEY"
        )
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": (
                    "You are a certified personal trainer and nutritionist. "
                    "Output ONLY valid JSON arrays. No text before or after. "
                    "Be specific with exercise names, quantities, and food items."
                )},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return resp.choices[0].message.content
    except Exception as e:
        err = str(e)
        if "401" in err or "invalid_api_key" in err.lower():
            raise ValueError("Invalid Groq API key. Check https://console.groq.com/keys") from None
        if "429" in err or "rate_limit" in err.lower():
            raise ValueError("Rate limit hit. Wait 30s and retry.") from None
        if "model_not_found" in err.lower() or "model" in err.lower():
            raise ValueError(f"Model error: {err}") from None
        raise


# ══════════════════════════════════════════════════════════════════════════════
# JSON repair
# ══════════════════════════════════════════════════════════════════════════════

def _repair_json(text):
    if not text:
        return None
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = re.sub(r"```", "", text).strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    # Try to extract array
    m = re.search(r"(\[.*\])", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            text = m.group(1)
    # Repair truncated JSON
    stack, in_str, escape, result = [], False, False, []
    for ch in text:
        if escape:
            escape = False; result.append(ch); continue
        if ch == "\\" and in_str:
            escape = True; result.append(ch); continue
        if ch == '"' and not escape:
            in_str = not in_str; result.append(ch); continue
        if in_str:
            result.append(ch); continue
        if ch in "{[":
            stack.append(ch); result.append(ch)
        elif ch in "}]":
            if stack: stack.pop()
            result.append(ch)
        else:
            result.append(ch)
    if in_str: result.append('"')
    joined = "".join(result).rstrip().rstrip(",")
    for opener in reversed(stack):
        joined += "}" if opener == "{" else "]"
    try:
        return json.loads(joined)
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════════════
# Defaults
# ══════════════════════════════════════════════════════════════════════════════

_PRE_VIDEOS = [
    "https://www.youtube.com/embed/R0mMyV5OtcM",
    "https://www.youtube.com/embed/sTxC3J3gQEU",
    "https://www.youtube.com/embed/CBzmVKDKOko",
]
_POST_VIDEOS = [
    "https://www.youtube.com/embed/Qyd_guFDMh4",
    "https://www.youtube.com/embed/L_xrDAtykMI",
    "https://www.youtube.com/embed/v7AYKMP6rOE",
]

def _default_dietary(dtype):
    if dtype == "veg":
        return {"breakfast":"Oats with banana, chia seeds and honey (1 cup oats)",
                "lunch":    "Brown rice (1 cup) with mixed dal and seasonal vegetables",
                "dinner":   "Paneer curry (100g) with 2 multigrain rotis and salad",
                "snacks":   "Handful mixed nuts, 1 fruit and green tea"}
    return {"breakfast":"3 boiled eggs with 2 whole wheat toast and black coffee",
            "lunch":    "Grilled chicken breast (150g) with brown rice and salad",
            "dinner":   "Baked fish (150g) with steamed broccoli and sweet potato",
            "snacks":   "Boiled eggs (2) and 20 almonds"}

def _default_pre(day_num):
    v = _PRE_VIDEOS[day_num % len(_PRE_VIDEOS)]
    return [
        {"name":"Arm Circles",    "duration":"30s","video_url":v},
        {"name":"Leg Swings",     "duration":"30s","video_url":v},
        {"name":"Hip Circles",    "duration":"30s","video_url":v},
        {"name":"Jumping Jacks",  "duration":"30s","video_url":v},
    ]

def _default_post(day_num):
    v = _POST_VIDEOS[day_num % len(_POST_VIDEOS)]
    return [
        {"name":"Quad Stretch",      "duration":"40s","video_url":v},
        {"name":"Hamstring Stretch", "duration":"40s","video_url":v},
        {"name":"Child's Pose",      "duration":"45s","video_url":v},
        {"name":"Chest Stretch",     "duration":"30s","video_url":v},
    ]

_FALLBACK_WORKOUTS = [
    [{"name":"Push-ups","sets":3,"reps":"12","rest":"60s","timer":60,"notes":"Elbows at 45 deg"},
     {"name":"Tricep Dips","sets":3,"reps":"10","rest":"60s","timer":60,"notes":"Elbows close"},
     {"name":"Shoulder Taps","sets":3,"reps":"20","rest":"45s","timer":45,"notes":"Hips stable"},
     {"name":"Pike Push-ups","sets":3,"reps":"8","rest":"60s","timer":60,"notes":"Hips high"},
     {"name":"Plank","sets":3,"reps":"30s","rest":"45s","timer":30,"notes":"Straight line"}],
    [{"name":"Squats","sets":4,"reps":"15","rest":"60s","timer":60,"notes":"Knees over toes"},
     {"name":"Reverse Lunges","sets":3,"reps":"12","rest":"60s","timer":60,"notes":"90 degree knee"},
     {"name":"Glute Bridges","sets":3,"reps":"20","rest":"45s","timer":45,"notes":"Squeeze at top"},
     {"name":"Jump Squats","sets":3,"reps":"12","rest":"75s","timer":60,"notes":"Soft landing"},
     {"name":"Calf Raises","sets":3,"reps":"25","rest":"30s","timer":30,"notes":"Full ROM"}],
    [{"name":"Burpees","sets":3,"reps":"10","rest":"75s","timer":75,"notes":"Controlled drop"},
     {"name":"High Knees","sets":3,"reps":"30s","rest":"45s","timer":30,"notes":"Drive knees high"},
     {"name":"Mountain Climbers","sets":3,"reps":"30","rest":"45s","timer":45,"notes":"Fast alt"},
     {"name":"Box Jumps","sets":3,"reps":"8","rest":"75s","timer":60,"notes":"Soft landing"},
     {"name":"Jumping Jacks","sets":3,"reps":"40","rest":"30s","timer":30,"notes":"Full ext"}],
    [{"name":"Bicycle Crunches","sets":3,"reps":"20","rest":"45s","timer":45,"notes":"Exhale twist"},
     {"name":"Leg Raises","sets":3,"reps":"15","rest":"45s","timer":45,"notes":"Lower back flat"},
     {"name":"Russian Twists","sets":3,"reps":"20","rest":"45s","timer":45,"notes":"Feet off floor"},
     {"name":"Plank","sets":3,"reps":"45s","rest":"45s","timer":45,"notes":"Hollow body"},
     {"name":"Dead Bug","sets":3,"reps":"12","rest":"30s","timer":30,"notes":"Slow extend"}],
]
_MUSCLE_GROUPS = [
    "Upper Body Push","Lower Body","Upper Body Pull",
    "Core & Cardio","Full Body Compound","Shoulders & Arms",
    "Lower Body Posterior",
]

def _fallback_day(dn, dtype):
    is_rest = (dn % 7 == 0)
    return {
        "day":          dn,
        "is_rest_day":  is_rest,
        "muscle_group": "Rest & Recovery" if is_rest else _MUSCLE_GROUPS[(dn-1) % len(_MUSCLE_GROUPS)],
        "workout":      [] if is_rest else _FALLBACK_WORKOUTS[(dn-1) % len(_FALLBACK_WORKOUTS)],
        "dietary":      _default_dietary(dtype),
        "pre_stretch":  _default_pre(dn),
        "post_stretch": _default_post(dn),
    }


# ══════════════════════════════════════════════════════════════════════════════
# Validation
# ══════════════════════════════════════════════════════════════════════════════

def _validate_day(day, dn, dtype):
    day["day"] = dn
    day.setdefault("is_rest_day",  False)
    day.setdefault("muscle_group", _MUSCLE_GROUPS[(dn-1) % len(_MUSCLE_GROUPS)])
    if not isinstance(day.get("workout"), list):
        day["workout"] = []
    for ex in day["workout"]:
        if not isinstance(ex, dict): continue
        ex.setdefault("name",  "Exercise")
        ex.setdefault("sets",  3)
        ex.setdefault("reps",  "12")
        ex.setdefault("rest",  "60s")
        ex.setdefault("notes", "Maintain form")
        try:
            ex["timer"] = int(str(ex.get("timer", ex.get("rest","60").replace("s",""))).replace("s",""))
        except Exception:
            ex["timer"] = 60
    if not isinstance(day.get("dietary"), dict) or not any(day.get("dietary",{}).values()):
        day["dietary"] = _default_dietary(dtype)
    for m in ["breakfast","lunch","dinner","snacks"]:
        day["dietary"].setdefault(m, "Balanced nutritious meal")
    if not isinstance(day.get("pre_stretch"), list) or not day.get("pre_stretch"):
        day["pre_stretch"] = _default_pre(dn)
    if not isinstance(day.get("post_stretch"), list) or not day.get("post_stretch"):
        day["post_stretch"] = _default_post(dn)
    # Add video URLs if missing
    for s in day.get("pre_stretch", []):
        s.setdefault("video_url", _PRE_VIDEOS[dn % len(_PRE_VIDEOS)])
    for s in day.get("post_stretch", []):
        s.setdefault("video_url", _POST_VIDEOS[dn % len(_POST_VIDEOS)])
    return day


def _to_text(days):
    lines = []
    for d in days:
        dn = d.get("day", 1)
        mg = d.get("muscle_group", "Full Body")
        if d.get("is_rest_day"):
            lines.append(f"## Day {dn} - Rest Day\n\nRest and recover.\n")
            continue
        lines.append(f"## Day {dn} - {mg}")
        for ex in d.get("workout", []):
            lines.append(f"- {ex.get('name')} - {ex.get('sets')}x{ex.get('reps')} (rest {ex.get('rest')})")
        diet = d.get("dietary", {})
        for meal in ["breakfast","lunch","dinner","snacks"]:
            if diet.get(meal):
                lines.append(f"  {meal.title()}: {diet[meal]}")
        lines.append("")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN — Single fast API call
# ══════════════════════════════════════════════════════════════════════════════

def query_model_chunked(name, gender, height, weight, goal, fitness_level,
                        equipment, days_per_week=5, months=1,
                        dietary_type="veg", progress_callback=None):
    """
    Generate complete workout + diet plan in ONE fast API call.
    Uses llama-3.1-8b-instant (131,072 TPM) — typically 10-20 seconds.
    Falls back to llama-3.3-70b-versatile if 8b fails.
    Returns: (full_plan_text, structured_days_list, bmi, bmi_cat)
    """
    from prompt_builder import calculate_bmi, bmi_category, bmi_advice
    bmi        = calculate_bmi(weight, height)
    bmi_cat    = bmi_category(bmi)
    total_days = days_per_week * 4 * months  # no cap — max 84 (7d × 4w × 3mo)
    eq_str     = ", ".join(equipment) if equipment else "Bodyweight only"
    diet_label = "Vegetarian" if dietary_type == "veg" else "Non-Vegetarian"
    diet_rule  = "NO meat/fish/eggs" if dietary_type == "veg" else "Include meat/fish/eggs every meal"

    # Which days are rest days
    rest_days = set()
    for week in range(months * 4 + 1):
        for offset in range(days_per_week + 1, 8):
            d = week * 7 + offset
            if 1 <= d <= total_days:
                rest_days.add(d)

    # Muscle group per day
    muscles = [
        "Upper Body Push","Lower Body","Upper Body Pull",
        "Core & Cardio","Full Body Compound","Shoulders & Arms",
        "Lower Body Posterior",
    ]

    # Build compact day specs
    day_specs = []
    for d in range(1, total_days + 1):
        if d in rest_days:
            day_specs.append(f"{d}:REST")
        else:
            day_specs.append(f"{d}:{muscles[(d-1) % len(muscles)]}")

    intensity = {
        "Beginner":     "2-3 sets, 90s rest, basic moves only",
        "Intermediate": "3-4 sets, 60s rest, progressive overload",
        "Advanced":     "4-5 sets, 45s rest, supersets allowed",
    }.get(fitness_level, "3 sets, 60s rest")

    goal_tip = {
        "Weight Loss":     "high reps 15-20, short rest, cardio circuits",
        "Build Muscle":    "moderate reps 8-12, compound lifts, protein surplus",
        "General Fitness": "balanced 10-15 reps, mix strength and cardio",
    }.get(goal, "balanced training")

    if progress_callback:
        progress_callback(1, 1, 0, total_days, status=f"Generating your {total_days}-day plan...")

    # ── COMPACT PROMPT ────────────────────────────────────────────────────────
    prompt = f"""Generate a {total_days}-day personalised fitness plan as a JSON array.

User: {name},{gender},{height}cm,{weight}kg,BMI:{bmi:.1f}({bmi_cat}),Goal:{goal}({goal_tip}),Level:{fitness_level}({intensity}),Equipment:{eq_str},Diet:{diet_label}({diet_rule})

Days to generate: {", ".join(day_specs)}
REST days have is_rest_day=true and empty workout array but still have dietary plan.

Return a JSON array of {total_days} objects. Each object:
{{"day":N,"is_rest_day":false,"muscle_group":"...","workout":[{{"name":"ExerciseName","sets":3,"reps":"12","rest":"60s","timer":60,"notes":"form tip"}},...5 exercises],"dietary":{{"breakfast":"food+qty","lunch":"food+qty","dinner":"food+qty","snacks":"food"}},"pre_stretch":[{{"name":"stretch","duration":"30s","video_url":"https://www.youtube.com/embed/R0mMyV5OtcM"}}],"post_stretch":[{{"name":"stretch","duration":"40s","video_url":"https://www.youtube.com/embed/Qyd_guFDMh4"}}]}}

Rules:
- Use ONLY equipment: {eq_str}
- {diet_rule} — be specific with food names and quantities
- Vary exercises each day — no repeats across days
- Adjust sets/reps/rest for {fitness_level} level
- Output ONLY the JSON array, nothing else"""

    # ── ATTEMPT with fast model first, fallback to powerful model ─────────────
    # ── Chunk strategy: 20 days per call for reliability ─────────────────────
    CHUNK_SIZE = 20
    all_days   = []
    last_err   = None
    n_chunks   = max(1, -(-total_days // CHUNK_SIZE))  # ceiling division

    for chunk_idx in range(n_chunks):
        chunk_start = chunk_idx * CHUNK_SIZE + 1
        chunk_end   = min(chunk_start + CHUNK_SIZE - 1, total_days)
        chunk_days_needed = chunk_end - chunk_start + 1

        # Update progress
        if progress_callback:
            pct = int((chunk_start - 1) / total_days * 90)
            progress_callback(chunk_idx+1, n_chunks, chunk_start-1, total_days,
                status=f"Generating days {chunk_start}–{chunk_end} of {total_days}...")

        # Which days in this chunk are rest days
        chunk_rest = {d for d in rest_days if chunk_start <= d <= chunk_end}

        # Muscle group per day for this chunk
        chunk_muscles = {
            d: muscles[(d-1) % len(muscles)]
            for d in range(chunk_start, chunk_end+1)
            if d not in chunk_rest
        }

        # Build day specs for prompt
        day_specs = []
        for d in range(chunk_start, chunk_end+1):
            if d in rest_days:
                day_specs.append(f"{d}:REST")
            else:
                day_specs.append(f"{d}:{chunk_muscles.get(d,'Full Body')}")

        # Build chunk prompt
        avoid = ""
        if all_days:
            used = [ex.get("name","") for day in all_days[-5:] for ex in day.get("workout",[])]
            used = [n for n in used if n][:15]
            if used:
                avoid = f"\nAvoid repeating these exercises from previous days: {', '.join(used)}"

        # Progressive overload: calculate which week this chunk is in
        week_num = (chunk_start - 1) // days_per_week + 1
        overload_note = ""
        if week_num == 2:
            overload_note = " WEEK 2: Add 1 rep to each exercise compared to week 1."
        elif week_num == 3:
            overload_note = " WEEK 3: Add 1 set OR increase reps by 2 compared to week 2."
        elif week_num >= 4:
            overload_note = f" WEEK {week_num}: Increase intensity — add 1 set, increase reps by 2-3, reduce rest by 10s."

        chunk_prompt = f"""Generate days {chunk_start} to {chunk_end} of a {total_days}-day fitness plan. Output ONLY a JSON array of {chunk_days_needed} objects.

User: {name},{gender},{height}cm,{weight}kg,BMI:{bmi:.1f}({bmi_cat}),Goal:{goal}({goal_tip}),Level:{fitness_level}({intensity}),Equipment:{eq_str},Diet:{diet_label}({diet_rule})

Days: {", ".join(day_specs)}
REST days: is_rest_day=true, workout=[], include dietary plan.{avoid}{overload_note}

Each object: {{"day":N,"is_rest_day":false,"muscle_group":"...","workout":[{{"name":"Exercise","sets":3,"reps":"12","rest":"60s","timer":60,"notes":"form tip"}},...5 exercises],"dietary":{{"breakfast":"food+qty","lunch":"food+qty","dinner":"food+qty","snacks":"food"}},"pre_stretch":[{{"name":"stretch","duration":"30s","video_url":"https://www.youtube.com/embed/R0mMyV5OtcM"}}],"post_stretch":[{{"name":"stretch","duration":"40s","video_url":"https://www.youtube.com/embed/Qyd_guFDMh4"}}]}}

Rules: Only use equipment: {eq_str}. {diet_rule}. Vary exercises from previous days. {fitness_level} intensity. Output ONLY the JSON array."""

        # Try models
        chunk_parsed = None
        models_to_try = [
            ("llama-3.1-8b-instant",    8000),
            ("llama-3.3-70b-versatile", 6000),
        ]
        for model_name, max_tok in models_to_try:
            for attempt in range(2):
                try:
                    raw = query_model(chunk_prompt, max_tokens=max_tok, model=model_name)
                    chunk_parsed = _repair_json(raw)
                    if chunk_parsed and isinstance(chunk_parsed, list) and len(chunk_parsed) > 0:
                        break
                    if attempt == 0:
                        time.sleep(2)
                except ValueError as e:
                    last_err = e
                    if "rate_limit" in str(e).lower():
                        if progress_callback:
                            progress_callback(chunk_idx+1, n_chunks, chunk_start-1, total_days,
                                status="Rate limit — waiting 30s...")
                        time.sleep(30)
                    if attempt == 0:
                        time.sleep(3); continue
                    break
                except Exception as e:
                    last_err = e
                    if attempt == 0:
                        time.sleep(3); continue
                    break
            if chunk_parsed and isinstance(chunk_parsed, list) and len(chunk_parsed) > 0:
                break

        # Build lookup by day number
        parsed_map = {}
        if chunk_parsed:
            for p in chunk_parsed:
                if isinstance(p, dict) and p.get("day"):
                    parsed_map[int(p["day"])] = p

        # Build structured days for this chunk
        for dn in range(chunk_start, chunk_end + 1):
            raw_day = (parsed_map.get(dn) or
                      (chunk_parsed[dn - chunk_start] if chunk_parsed and (dn - chunk_start) < len(chunk_parsed) else None) or
                      _fallback_day(dn, dietary_type))
            if not isinstance(raw_day, dict):
                raw_day = _fallback_day(dn, dietary_type)
            if dn in rest_days:
                raw_day["is_rest_day"]  = True
                raw_day["workout"]      = []
                raw_day["muscle_group"] = "Rest & Recovery"
            all_days.append(_validate_day(raw_day, dn, dietary_type))

        # Small pause between chunks to avoid rate limits
        if chunk_idx < n_chunks - 1:
            time.sleep(1)

    if progress_callback:
        progress_callback(n_chunks, n_chunks, total_days, total_days, status="✅ Plan Ready!")

    return _to_text(all_days), all_days, bmi, bmi_cat 