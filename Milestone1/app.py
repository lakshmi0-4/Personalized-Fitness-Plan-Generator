import streamlit as st

st.set_page_config(page_title="FitPlan AI", page_icon="💪", layout="centered")

st.title("💪 FitPlan AI")
st.subheader("Personalized Fitness Profile Form")

st.write("Enter your details to calculate BMI and fitness category.")
st.divider()

# Input options
goals_list = ["Build Muscle", "Weight Loss", "Strength Gain", "Abs Building", "Flexible"]

equipment_list = [
    "Dumbbells", "Resistance Band", "Yoga Mat", "No Equipment",
    "Inclined Bench", "Treadmill", "Cycle", "Skipping Rope",
    "Hand Gripper", "Pullups Bar", "Weight Plates", "Hula Hoop Ring", "Bosu Ball"
]

fitness_levels = ["Beginner", "Intermediate", "Advanced"]

# Form
with st.form("fitness_form"):

    st.header("📝 Personal Information")
    name = st.text_input("Name *")
    height_cm = st.number_input("Height (in cm) *", min_value=0.0, step=1.0)
    weight_kg = st.number_input("Weight (in kg) *", min_value=0.0, step=1.0)

    st.header("🏋️ Fitness Details")
    goal = st.selectbox("Fitness Goal", goals_list)

    st.write("Available Equipment (Select multiple):")
    selected_equipment = []
    for eq in equipment_list:
        if st.checkbox(eq):
            selected_equipment.append(eq)

    level = st.radio("Fitness Level", fitness_levels)

    submit = st.form_submit_button("Calculate BMI")

# BMI Calculation + Validation
if submit:
    if name.strip() == "":
        st.error("❌ Name is required.")
    elif height_cm <= 0:
        st.error("❌ Height must be greater than 0.")
    elif weight_kg <= 0:
        st.error("❌ Weight must be greater than 0.")
    else:
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        bmi = round(bmi, 2)

        # BMI Category
        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Normal"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obese"

        st.success("✅ BMI Calculated Successfully!")

        st.subheader("📌 Result")
        st.write(f"**Name:** {name}")
        st.write(f"**Height:** {height_cm} cm ({round(height_m, 2)} m)")
        st.write(f"**Weight:** {weight_kg} kg")
        st.write(f"**BMI:** {bmi}")
        st.write(f"**Category:** {category}")

        st.subheader("🏆 Fitness Profile")
        st.write(f"**Goal:** {goal}")
        st.write(f"**Fitness Level:** {level}")

        st.write("**Equipment Selected:**")
        if len(selected_equipment) == 0:
            st.write("✅ No Equipment Selected")
        else:
            for eq in selected_equipment:
                st.write(f"✅ {eq}")
