import streamlit as st

st.set_page_config(page_title="FitPlan AI", page_icon="💪", layout="centered")

# ------------------ CSS for Background + Dark Text + Light Inputs ------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #ffe6f0, #e6f7ff);
}

/* Force all text to dark */
html, body, [class*="css"]  {
    color: black !important;
}

/* Labels */
label, .stTextInput label, .stNumberInput label, .stSelectbox label, 
.stRadio label, .stCheckbox label {
    color: black !important;
    font-weight: 600;
}

/* Header text */
h1, h2, h3, h4, h5, h6, p, span, div {
    color: black !important;
}

/* Selectbox + Input boxes light shade */
div[data-baseweb="select"] > div {
    background-color: #f8f8ff !important;
    border: 2px solid #ffb6c1 !important;
    border-radius: 10px !important;
    color: black !important;
}

/* Dropdown options */
ul[role="listbox"] {
    background-color: #ffffff !important;
    color: black !important;
}

/* Number input + text input */
input {
    background-color: #f8f8ff !important;
    border: 2px solid #ffb6c1 !important;
    border-radius: 10px !important;
    color: black !important;
}

/* Button light shade */
.stButton > button, div.stFormSubmitButton > button {
    background-color: #ffb6c1 !important;
    color: black !important;
    border-radius: 12px !important;
    font-size: 18px !important;
    font-weight: bold !important;
    border: none !important;
    padding: 10px 25px !important;
}

/* Button hover */
.stButton > button:hover, div.stFormSubmitButton > button:hover {
    background-color: #ff91a4 !important;
    color: white !important;
}

/* Form Box */
.box {
    background-color: white;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
}

/* Result Box */
.result {
    background-color: white;
    padding: 20px;
    border-radius: 15px;
    border-left: 8px solid #ff2d55;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
    margin-top: 20px;
}

/* Title */
.title {
    text-align: center;
    font-size: 45px;
    font-weight: 900;
    color: #ff2d55 !important;
}
.sub {
    text-align: center;
    font-size: 18px;
    font-weight: 600;
    color: #444 !important;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ------------------ Title ------------------
st.markdown('<div class="title">💪 FitPlan AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Personalized Fitness Profile Form</div>', unsafe_allow_html=True)

# ------------------ Lists ------------------
goals_list = ["Build Muscle", "Weight Loss", "Strength Gain", "Abs Building", "Flexible"]

equipment_list = [
    "Dumbbells", "Resistance Band", "Yoga Mat", "No Equipment",
    "Inclined Bench", "Treadmill", "Cycle", "Skipping Rope",
    "Hand Gripper", "Pullups Bar", "Weight Plates", "Hula Hoop Ring", "Bosu Ball"
]

fitness_levels = ["Beginner", "Intermediate", "Advanced"]

# ------------------ Form UI ------------------
st.markdown('<div class="box">', unsafe_allow_html=True)

with st.form("fitness_form"):

    st.header("📝 Personal Information")
    name = st.text_input("👤 Name *")
    height_cm = st.number_input("📏 Height (in cm) *", min_value=0.0, step=1.0)
    weight_kg = st.number_input("⚖️ Weight (in kg) *", min_value=0.0, step=1.0)

    st.header("🏋️ Fitness Details")
    goal = st.selectbox("🎯 Fitness Goal", goals_list)

    st.write("🏋️ Available Equipment (Select multiple):")
    selected_equipment = []
    for eq in equipment_list:
        if st.checkbox(eq):
            selected_equipment.append(eq)

    level = st.radio("📊 Fitness Level", fitness_levels)

    submit = st.form_submit_button("🚀 Calculate BMI")

st.markdown('</div>', unsafe_allow_html=True)

# ------------------ BMI Calculation ------------------
if submit:
    if name.strip() == "":
        st.error("❌ Name is required.")
    elif height_cm <= 0:
        st.error("❌ Height must be greater than 0.")
    elif weight_kg <= 0:
        st.error("❌ Weight must be greater than 0.")
    else:
        height_m = height_cm / 100
        bmi = round(weight_kg / (height_m ** 2), 2)

        if bmi < 18.5:
            category = "Underweight 🟡"
        elif bmi < 25:
            category = "Normal 🟢"
        elif bmi < 30:
            category = "Overweight 🟠"
        else:
            category = "Obese 🔴"

        st.success("✅ BMI Calculated Successfully!")

        st.markdown(f"""
        <div class="result">
            <h2>📌 Result</h2>
            <p><b>Name:</b> {name}</p>
            <p><b>Height:</b> {height_cm} cm ({round(height_m, 2)} m)</p>
            <p><b>Weight:</b> {weight_kg} kg</p>
            <p><b>BMI:</b> {bmi}</p>
            <p><b>Category:</b> {category}</p>
            <hr>
            <p><b>Goal:</b> {goal}</p>
            <p><b>Fitness Level:</b> {level}</p>
            <p><b>Equipment Selected:</b> {", ".join(selected_equipment) if selected_equipment else "No Equipment Selected"}</p>
        </div>
        """, unsafe_allow_html=True)
