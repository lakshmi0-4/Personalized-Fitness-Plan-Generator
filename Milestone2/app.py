import streamlit as st
from prompt_builder import build_prompt
from model_api import query_model

st.set_page_config(page_title="FitPlan AI", page_icon="💪", layout="centered")

# ---------- DARK CSS ----------

st.markdown("""
<style>

/* Background */

.stApp {
    background: linear-gradient(to right,#0f2027,#203a43,#2c5364);
}

/* Text */

html, body, [class*="css"] {
    color: white !important;
}

/* Title */

h1 {
    text-align:center;
    color:#00eaff !important;
    font-size:42px;
}

/* Inputs */

input {
    background-color:#1e1e1e !important;
    border-radius:10px !important;
    border:2px solid #00eaff !important;
    color:white !important;
}

/* Dropdown */

div[data-baseweb="select"]>div{
    background-color:#1e1e1e !important;
    border-radius:10px !important;
    border:2px solid #00eaff !important;
    color:white !important;
}

/* Button */

.stButton>button{
    background-color:#00eaff !important;
    color:black !important;
    border-radius:12px !important;
    font-size:18px !important;
    padding:10px 25px !important;
}

/* Button Hover */

.stButton>button:hover{
    background-color:#00c8d7 !important;
}

/* Clean Result Box */

.resultbox{
    background:#1e1e1e;
    padding:15px 20px 20px 20px;
    border-radius:15px;
    border-left:5px solid #00eaff;
    box-shadow:0px 4px 12px rgba(0,0,0,0.4);
    margin-top:10px;
}

/* REMOVE TOP SPACE */

.resultbox p:first-child{
    margin-top:0px !important;
}

</style>
""", unsafe_allow_html=True)

# ---------- Title ----------

st.markdown("<h1>💪 FitPlan AI</h1>", unsafe_allow_html=True)
st.subheader("AI Personalized Workout Generator")

# ---------- Lists ----------

goals_list = [
"Build Muscle",
"Weight Loss",
"Strength Gain",
"Abs Building",
"Flexible"
]

equipment_list = [
"Dumbbells",
"Resistance Band",
"Yoga Mat",
"No Equipment",
"Treadmill",
"Cycle",
"Skipping Rope"
]

fitness_levels = [
"Beginner",
"Intermediate",
"Advanced"
]

# ---------- Form ----------

with st.form("fitness_form"):

    name = st.text_input("Name")

    age = st.number_input(
        "Age",
        min_value=10,
        max_value=80
    )

    gender = st.selectbox(
        "Gender",
        ["Male","Female"]
    )

    height = st.number_input(
        "Height (cm)",
        min_value=0.0
    )

    weight = st.number_input(
        "Weight (kg)",
        min_value=0.0
    )

    goal = st.selectbox(
        "Fitness Goal",
        goals_list
    )

    st.write("Available Equipment")

    selected_equipment=[]

    for eq in equipment_list:
        if st.checkbox(eq):
            selected_equipment.append(eq)

    level = st.radio(
        "Fitness Level",
        fitness_levels
    )

    submit = st.form_submit_button(
        "Generate Workout Plan"
    )

# ---------- Result ----------

if submit:

    if name=="":
        st.error("Enter Name")

    elif height==0 or weight==0:
        st.error("Enter Height and Weight")

    else:

        prompt,bmi,bmi_status = build_prompt(
            name,
            age,
            gender,
            height,
            weight,
            goal,
            level,
            selected_equipment
        )

        st.success("Profile Generated")

        st.write("## User Profile")

        st.markdown('<div class="resultbox">', unsafe_allow_html=True)

        st.write("Name:",name)
        st.write("Age:",age)
        st.write("BMI:",round(bmi,2))
        st.write("Category:",bmi_status)
        st.write("Goal:",goal)
        st.write("Level:",level)

        st.markdown('</div>', unsafe_allow_html=True)

        st.write("## 🏋️ AI 5-Day Workout Plan")

        with st.spinner("Generating Plan..."):
            plan = query_model(prompt)

        st.markdown('<div class="resultbox">', unsafe_allow_html=True)

        st.write(plan)

        st.markdown('</div>', unsafe_allow_html=True)
