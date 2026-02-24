import streamlit as st
from prompt_builder import build_prompt
from model_api import query_model

st.set_page_config(page_title="FitPlan AI", page_icon="💪", layout="centered")

# ---------- CSS ----------

st.markdown("""
<style>

/* Background */

.stApp {
background: linear-gradient(135deg,#141e30,#243b55);
color:white;
}

/* Title */

.title{
text-align:center;
font-size:42px;
font-weight:bold;
color:#00eaff;
margin-bottom:0px;
}

.subtitle{
text-align:center;
font-size:18px;
color:#cccccc;
margin-bottom:30px;
}

/* Glass Card */

.card{
background: rgba(255,255,255,0.05);
padding:25px;
border-radius:18px;
box-shadow:0px 6px 25px rgba(0,0,0,0.4);
margin-top:15px;
}

/* Inputs */

input{
background:#111 !important;
color:white !important;
border-radius:10px !important;
border:1px solid #00eaff !important;
}

/* Dropdown */

div[data-baseweb="select"]>div{
background:#111 !important;
color:white !important;
border-radius:10px !important;
border:1px solid #00eaff !important;
}

/* Button */

.stButton>button{
background:linear-gradient(90deg,#00eaff,#00c8d7);
color:black;
font-size:18px;
border-radius:12px;
padding:10px 25px;
font-weight:bold;
border:none;
}

.stButton>button:hover{
background:linear-gradient(90deg,#00c8d7,#00eaff);
}

/* Section titles */

.section{
font-size:24px;
font-weight:bold;
color:#00eaff;
margin-top:10px;
}

</style>
""", unsafe_allow_html=True)

# ---------- Title ----------

st.markdown('<div class="title">💪 FitPlan AI</div>',unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI Personalized Workout Generator</div>',unsafe_allow_html=True)

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

# ---------- FORM ----------

st.markdown('<div class="card">',unsafe_allow_html=True)

with st.form("fitness_form"):

    st.markdown('<div class="section">Personal Details</div>',unsafe_allow_html=True)

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

    st.markdown('<div class="section">Fitness Details</div>',unsafe_allow_html=True)

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

    submit = st.form_submit_button("Generate Workout Plan")

st.markdown('</div>',unsafe_allow_html=True)

# ---------- RESULT ----------

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

        st.success("Plan Generated Successfully")

        # Profile Card

        st.markdown('<div class="card">',unsafe_allow_html=True)

        st.markdown('<div class="section">User Profile</div>',unsafe_allow_html=True)

        st.write("Name:",name)
        st.write("Age:",age)
        st.write("BMI:",round(bmi,2))
        st.write("Category:",bmi_status)
        st.write("Goal:",goal)
        st.write("Level:",level)

        st.markdown('</div>',unsafe_allow_html=True)

        st.markdown('<div class="card">',unsafe_allow_html=True)

        st.markdown('<div class="section">AI Workout Plan</div>',unsafe_allow_html=True)

        with st.spinner("Generating AI Plan..."):
            plan = query_model(prompt)

        st.write(plan)

        st.markdown('</div>',unsafe_allow_html=True)
