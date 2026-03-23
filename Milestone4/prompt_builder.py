def calculate_bmi(weight, height):
    h = height / 100
    return weight / (h * h)

def bmi_category(bmi):
    if bmi < 18.5:  return "Underweight"
    elif bmi < 25:  return "Normal Weight"
    elif bmi < 30:  return "Overweight"
    else:           return "Obese"

def bmi_advice(category):
    return {
        "Underweight":   "focus on caloric surplus, compound lifts, and muscle building. Avoid excessive cardio.",
        "Normal Weight": "maintain current weight while building lean muscle and improving cardiovascular fitness.",
        "Overweight":    "incorporate cardio-strength circuits to burn fat while preserving muscle mass.",
        "Obese":         "prioritise low-impact cardio, mobility work, and progressive resistance training.",
    }.get(category, "train consistently and progressively.")

def build_prompt(name, gender, height, weight, goal, fitness_level, equipment,
                 days_per_week=5, months=1):
    bmi       = calculate_bmi(weight, height)
    bmi_cat   = bmi_category(bmi)
    eq_list   = ", ".join(equipment) if equipment else "Bodyweight only (no equipment)"
    advice    = bmi_advice(bmi_cat)
    total_days = days_per_week * 4 * months   # weeks per month × months
    # Cap at 30 for safety (model output length)
    total_days = min(total_days, 30)

    intensity_map = {
        "Beginner":     "2–3 working sets, moderate weight, longer rest (90s). Prioritise form over load.",
        "Intermediate": "3–4 working sets, progressive overload, 60–75s rest.",
        "Advanced":     "4–5 working sets, heavy compound movements, 45–60s rest, supersets where appropriate.",
    }
    intensity = intensity_map.get(fitness_level, "3 sets, 60s rest.")

    # Build the day-structure part of the format instruction
    day_example = "\n".join([
        f"## Day {i+1} - [Muscle Group / Focus]"
        "\n\n**Warm-Up (5 min)**"
        "\n- Exercise 1: sets x reps"
        "\n- Exercise 2: sets x reps"
        "\n\n**Main Workout**"
        "\n- Exercise 1 — sets x reps (rest 60s)"
        "\n- Exercise 2 — sets x reps (rest 60s)"
        "\n- Exercise 3 — sets x reps (rest 60s)"
        "\n- Exercise 4 — sets x reps (rest 60s)"
        "\n- Exercise 5 — sets x reps (rest 60s)"
        "\n\n**Cool-Down (3 min)**"
        "\n- Stretch 1"
        "\n- Stretch 2\n"
        for i in range(min(total_days, 3))  # show 3 day examples in prompt
    ])

    prompt = f"""You are an elite certified personal trainer and sports scientist.
Create a complete, professional {total_days}-day personalised workout plan
({days_per_week} training days per week × {months} month{'s' if months>1 else ''}).

━━━ CLIENT PROFILE ━━━
Name           : {name}
Gender         : {gender}
Height / Weight: {height} cm / {weight} kg
BMI            : {bmi:.1f} ({bmi_cat})
Primary Goal   : {goal}
Fitness Level  : {fitness_level}
Equipment      : {eq_list}
Plan Duration  : {days_per_week} days/week for {months} month{'s' if months>1 else ''} = {total_days} workout days total

━━━ PROGRAMMING NOTES ━━━
• BMI guidance  : {advice}
• Intensity     : {intensity}
• Equipment     : Only use the equipment listed above. Substitute with bodyweight if needed.
• Progression   : Each week should slightly increase intensity, volume or complexity vs the previous week.
• Rest days     : Build rest days into the weekly cycle naturally (user trains {days_per_week} days/week).

━━━ REQUIRED OUTPUT FORMAT ━━━
Use EXACTLY this structure for ALL {total_days} days:

## Day 1 - [Muscle Group / Focus]

**Warm-Up (5 min)**
- Exercise 1: sets x reps
- Exercise 2: sets x reps

**Main Workout**
- Exercise 1 — sets x reps (rest 60s)
- Exercise 2 — sets x reps (rest 60s)
- Exercise 3 — sets x reps (rest 60s)
- Exercise 4 — sets x reps (rest 60s)
- Exercise 5 — sets x reps (rest 60s)

**Cool-Down (3 min)**
- Stretch 1
- Stretch 2

[Continue this exact structure for Day 2 through Day {total_days}]

━━━ FINAL SECTION ━━━
End with ONE personalised motivational paragraph addressed directly to {name}.

━━━ RULES ━━━
1. Day headers must start with "## Day N -"
2. Include sets × reps for every exercise (e.g. 3 x 12 reps)
3. Rest periods in parentheses after each exercise
4. No exercises unsafe for {fitness_level} level
5. Ensure variety across all days — don't repeat same muscle groups back-to-back
6. Be specific — no vague instructions
7. Generate ALL {total_days} days — do not stop early
"""
    return prompt, bmi, bmi_cat