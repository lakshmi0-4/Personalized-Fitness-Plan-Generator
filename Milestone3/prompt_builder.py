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
        "Obese":         "prioritise low-impact cardio, mobility work, and progressive resistance training."
    }.get(category, "train consistently and progressively.")

def build_prompt(name, gender, height, weight, goal, fitness_level, equipment):
    bmi       = calculate_bmi(weight, height)
    bmi_cat   = bmi_category(bmi)
    eq_list   = ", ".join(equipment) if equipment else "Bodyweight only (no equipment)"
    advice    = bmi_advice(bmi_cat)
    intensity_map = {
        "Beginner":     "2–3 working sets, moderate weight, longer rest (90s). Prioritise form over load.",
        "Intermediate": "3–4 working sets, progressive overload, 60–75s rest.",
        "Advanced":     "4–5 working sets, heavy compound movements, 45–60s rest, supersets where appropriate."
    }
    intensity = intensity_map.get(fitness_level, "3 sets, 60s rest.")

    prompt = f"""You are an elite certified personal trainer and sports scientist.
Create a complete, professional 5-day personalised workout plan.
━━━ CLIENT PROFILE ━━━
Name           : {name}
Gender         : {gender}
Height / Weight: {height} cm / {weight} kg
BMI            : {bmi:.1f} ({bmi_cat})
Primary Goal   : {goal}
Fitness Level  : {fitness_level}
Equipment      : {eq_list}
━━━ PROGRAMMING NOTES ━━━
• BMI guidance  : {advice}
• Intensity     : {intensity}
• Equipment     : Only use the equipment listed above. Substitute with bodyweight if needed.
━━━ REQUIRED OUTPUT FORMAT ━━━
Use EXACTLY this structure for all 5 days:
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
[Repeat the above structure for Day 2 through Day 5]
━━━ FINAL SECTION ━━━
End with ONE personalised motivational paragraph addressed directly to {name}.
━━━ RULES ━━━
1. Day headers must start with "## Day N -"
2. Include sets × reps for every exercise (e.g. 3 x 12 reps)
3. Rest periods in parentheses after each exercise
4. No exercises unsafe for {fitness_level} level
5. Ensure variety across all 5 days
6. Be specific — no vague instructions
"""
    return prompt, bmi, bmi_cat
