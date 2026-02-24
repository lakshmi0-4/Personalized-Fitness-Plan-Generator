def calculate_bmi(weight, height):

    height_m = height / 100
    return weight / (height_m ** 2)


def bmi_category(bmi):

    if bmi < 18.5:
        return "Underweight"

    elif bmi < 25:
        return "Normal Weight"

    elif bmi < 30:
        return "Overweight"

    else:
        return "Obese"


# IMPORTANT: AGE ADDED HERE

def build_prompt(name, age, gender, height, weight, goal, fitness_level, equipment):

    bmi = calculate_bmi(weight, height)

    bmi_status = bmi_category(bmi)

    equipment_list = ", ".join(equipment) if equipment else "No Equipment"

    prompt = f"""
Create a simple 5-day workout plan.

User Info:

Name: {name}
Age: {age}
Gender: {gender}
BMI: {bmi:.2f} ({bmi_status})
Goal: {goal}
Level: {fitness_level}
Equipment: {equipment_list}

Day 1:
Exercises with sets and reps

Day 2:
Exercises with sets and reps

Day 3:
Exercises with sets and reps

Day 4:
Exercises with sets and reps

Day 5:
Exercises with sets and reps

Stop after Day 5.
"""

    return prompt, bmi, bmi_status
