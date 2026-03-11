import streamlit as st
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_token import logout

st.set_page_config(page_title="FitPlan Pro – Profile", page_icon="⚡", layout="wide")

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

uname = st.session_state.get("username", "Athlete")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&display=swap');

/* ━━━ GLOBAL DARK THEME ━━━ */
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stSidebarNav"],section[data-testid="stSidebar"]{display:none!important;}

html,body,.stApp,[data-testid="stAppViewContainer"]{
  background:#141414!important;
  color:#fff!important;
  font-family:'DM Sans',sans-serif!important;
}
[data-testid="stAppViewContainer"]>section>div.block-container{
  max-width:860px!important;margin:0 auto!important;
  padding:0 24px 60px!important;
}

/* ━━━ TOPNAV ━━━ */
.topnav{
  position:sticky;top:0;z-index:100;
  display:flex;align-items:center;justify-content:space-between;
  padding:18px 0 16px;
  background:linear-gradient(180deg,#141414 85%,transparent 100%);
  margin-bottom:8px;
}
.nav-logo{
  font-family:'Bebas Neue',sans-serif;
  font-size:1.8rem;letter-spacing:4px;color:#E50914;
  text-shadow:0 0 20px rgba(229,9,20,0.35);
}
.nav-user{
  font-size:0.82rem;color:rgba(255,255,255,0.5);
}
.nav-user strong{color:#fff;}

/* ━━━ PAGE HERO ━━━ */
.page-hero{
  padding:32px 0 28px;
  border-bottom:1px solid rgba(255,255,255,0.06);
  margin-bottom:32px;
}
.page-hero-title{
  font-family:'Bebas Neue',sans-serif;
  font-size:clamp(2rem,5vw,3.2rem);
  letter-spacing:2px;color:#fff;
  line-height:1;
}
.page-hero-title em{color:#E50914;font-style:normal;}
.page-hero-sub{
  font-size:0.9rem;color:rgba(255,255,255,0.45);
  margin-top:8px;font-weight:300;letter-spacing:0.3px;
}

/* ━━━ SECTION HEADER ━━━ */
.section-hdr{
  display:flex;align-items:center;gap:10px;
  font-size:0.68rem;font-weight:600;letter-spacing:3px;
  text-transform:uppercase;color:rgba(255,255,255,0.4);
  margin-bottom:14px;margin-top:28px;
}
.section-hdr::before{content:'';width:24px;height:1px;background:#E50914;flex-shrink:0;}

/* ━━━ STREAMLIT INPUT OVERRIDES — Dark Netflix style ━━━ */
div[data-baseweb="input"],
div[data-baseweb="textarea"]{
  background:rgba(255,255,255,0.1)!important;
  border:1.5px solid rgba(255,255,255,0.18)!important;
  border-radius:4px!important;
  transition:border-color 0.2s, background 0.2s!important;
}
div[data-baseweb="input"]:focus-within,
div[data-baseweb="textarea"]:focus-within{
  background:rgba(255,255,255,0.13)!important;
  border-color:rgba(255,255,255,0.7)!important;
  box-shadow:none!important;
}
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea{
  background:transparent!important;
  color:#fff!important;
  font-family:'DM Sans',sans-serif!important;
  font-size:0.95rem!important;
}
div[data-baseweb="input"] input::placeholder{color:rgba(255,255,255,0.3)!important;}

/* Number input buttons */
div[data-baseweb="input"] button{
  color:rgba(255,255,255,0.5)!important;
}
div[data-baseweb="input"] button:hover{
  color:#fff!important;background:rgba(255,255,255,0.08)!important;
}

/* Select */
div[data-baseweb="select"]>div{
  background:rgba(255,255,255,0.1)!important;
  border:1.5px solid rgba(255,255,255,0.18)!important;
  border-radius:4px!important;color:#fff!important;
}
div[data-baseweb="select"]>div:focus-within{
  border-color:rgba(255,255,255,0.7)!important;
}
div[data-baseweb="select"] span{color:#fff!important;}
div[data-baseweb="popover"]{background:#1f1f1f!important;border:1px solid rgba(255,255,255,0.1)!important;}
li[role="option"]{color:#fff!important;}
li[role="option"]:hover{background:rgba(255,255,255,0.08)!important;}
li[aria-selected="true"]{background:rgba(229,9,20,0.2)!important;}

/* Multiselect */
div[data-baseweb="multi-select"]>div{
  background:rgba(255,255,255,0.1)!important;
  border:1.5px solid rgba(255,255,255,0.18)!important;
  border-radius:4px!important;
}
span[data-baseweb="tag"]{
  background:rgba(229,9,20,0.25)!important;
  border:1px solid rgba(229,9,20,0.4)!important;
  border-radius:3px!important;
}
span[data-baseweb="tag"] span{color:#fff!important;}

/* Labels */
.stTextInput label,.stNumberInput label,.stSelectbox label,
.stMultiSelect label,.stSlider label{
  color:rgba(255,255,255,0.5)!important;
  font-size:0.7rem!important;font-weight:600!important;
  letter-spacing:2px!important;text-transform:uppercase!important;
  margin-bottom:6px!important;
}

/* ━━━ SUBMIT BUTTON ━━━ */
.stButton>button{
  background:#E50914!important;color:#fff!important;
  border:none!important;border-radius:4px!important;
  font-family:'DM Sans',sans-serif!important;
  font-size:1rem!important;font-weight:700!important;
  padding:14px 40px!important;
  letter-spacing:0.5px!important;
  transition:all 0.2s!important;
  box-shadow:0 4px 20px rgba(229,9,20,0.3)!important;
  width:100%!important;
}
.stButton>button:hover{
  background:#f6121d!important;
  box-shadow:0 6px 28px rgba(229,9,20,0.5)!important;
  transform:translateY(-1px)!important;
}

/* Logout button override */
.logout-btn .stButton>button{
  background:transparent!important;
  border:1.5px solid rgba(255,255,255,0.3)!important;
  color:rgba(255,255,255,0.7)!important;
  padding:8px 20px!important;
  font-size:0.8rem!important;
  width:auto!important;
  box-shadow:none!important;
}
.logout-btn .stButton>button:hover{
  border-color:rgba(255,255,255,0.7)!important;
  color:#fff!important;
  background:rgba(255,255,255,0.06)!important;
  transform:none!important;
  box-shadow:none!important;
}

/* ━━━ DIVIDER ━━━ */
hr{border:none!important;border-top:1px solid rgba(255,255,255,0.07)!important;margin:24px 0!important;}

/* ━━━ ERROR / INFO ━━━ */
.stAlert{border-radius:4px!important;}
[data-testid="stNotification"]{background:rgba(232,124,3,0.15)!important;border:1px solid rgba(232,124,3,0.3)!important;}
</style>
""", unsafe_allow_html=True)

# ── TOPNAV ──
col_logo, col_user, col_logout = st.columns([3, 4, 2])
with col_logo:
    st.markdown("<div class='nav-logo'>⚡ FitPlan Pro</div>", unsafe_allow_html=True)
with col_user:
    st.markdown(f"<div style='padding-top:8px;text-align:center'><span style='font-size:0.82rem;color:rgba(255,255,255,0.5)'>👋 Welcome, <strong style='color:#fff'>{uname}</strong></span></div>", unsafe_allow_html=True)
with col_logout:
    st.markdown("<div class='logout-btn'>", unsafe_allow_html=True)
    if st.button("Sign Out"):
        logout(st.session_state.get("username",""))
        for k in ["logged_in","username","auth_token","user_data","workout_plan","plan_for"]:
            st.session_state.pop(k, None)
        st.switch_page("app.py")
    st.markdown("</div>", unsafe_allow_html=True)

# ── HERO ──
st.markdown("""
<div class='page-hero'>
  <div class='page-hero-title'>YOUR FITNESS<br><em>STARTS HERE.</em></div>
  <div class='page-hero-sub'>Fill in your profile and we'll generate a personalised 5-day AI workout plan.</div>
</div>
""", unsafe_allow_html=True)

# ── FORM ──
st.markdown("<div class='section-hdr'>Personal Info</div>", unsafe_allow_html=True)

name = st.text_input("Full Name", placeholder="e.g. Karthik", label_visibility="visible")

c1, c2, c3, c4 = st.columns(4)
with c1:
    age = st.number_input("Age", min_value=15, max_value=80, step=1, value=25)
with c2:
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
with c3:
    height_cm = st.number_input("Height (cm)", min_value=100, max_value=250, step=1, value=170)
with c4:
    weight_kg = st.number_input("Weight (kg)", min_value=30, max_value=300, step=1, value=70)

st.markdown("<div class='section-hdr'>Goals & Equipment</div>", unsafe_allow_html=True)

c5, c6 = st.columns(2)
with c5:
    goal = st.selectbox("Fitness Goal", [
        "Build Muscle","Weight Loss","Strength Gain",
        "Abs Building","Flexibility and Mobility"
    ])
with c6:
    level = st.selectbox("Fitness Level", ["Beginner","Intermediate","Advanced"])

equipment = st.multiselect(
    "Available Equipment",
    ["Dumbbells","Resistance Band","Yoga Mat","Bench",
     "Pullup Bar","Barbell","Kettlebell","Treadmill"],
    default=[]
)

st.markdown("<br>", unsafe_allow_html=True)

if st.button("⚡  Generate My Workout Plan"):
    if not name.strip():
        st.error("Please enter your full name.")
        st.stop()
    st.session_state.user_data = {
        "name": name.strip(), "age": age, "gender": gender,
        "height": height_cm, "weight": weight_kg,
        "goal": goal, "level": level, "equipment": equipment
    }
    st.session_state.pop("workout_plan", None)
    st.session_state.pop("plan_for", None)
    st.switch_page("pages/2_Workout_Plan.py")
