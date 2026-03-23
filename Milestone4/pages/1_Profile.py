import streamlit as st
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_token import logout

st.set_page_config(page_title="FitPlan Pro – Profile", page_icon="⚡", layout="wide")

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

uname = st.session_state.get("username", "Athlete")

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@700;800;900&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&display=swap');
::-webkit-scrollbar{width:5px;}
::-webkit-scrollbar-track{background:rgba(255,255,255,0.04);}
::-webkit-scrollbar-thumb{background:rgba(229,9,20,0.40);border-radius:3px;}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stSidebarNav"],section[data-testid="stSidebar"]{display:none!important;}

:root{--red:#E50914;--ease:cubic-bezier(0.22,1,0.36,1);}

html,body,.stApp,[data-testid="stAppViewContainer"]{
  font-family:'DM Sans',sans-serif!important;color:#fff!important;
}

/* ══ BACKGROUND — blurred gym photo with heavy dark overlay ══ */
[data-testid="stAppViewContainer"]::before{
  content:'';position:fixed;inset:0;z-index:0;
  background:url('https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=1920&q=85&auto=format&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.4')
    center 40% / cover no-repeat;
  filter:blur(8px) brightness(0.28) saturate(0.6);
  transform:scale(1.06);
}
[data-testid="stAppViewContainer"]{
  background:linear-gradient(160deg,
    rgba(2,1,8,0.82) 0%,
    rgba(4,2,10,0.70) 40%,
    rgba(2,1,8,0.85) 100%) !important;
  position:relative;
}
[data-testid="stAppViewContainer"]>section>div.block-container{
  max-width:900px!important;margin:0 auto!important;
  padding:0 28px 100px!important;position:relative;z-index:2;
}

/* ══ TOPNAV ══ */
.topnav{
  position:sticky;top:0;z-index:100;
  display:flex;align-items:center;justify-content:space-between;
  padding:18px 0 14px;
  background:linear-gradient(180deg,rgba(2,1,8,0.97) 70%,transparent 100%);
  backdrop-filter:blur(30px);margin-bottom:4px;
  border-bottom:1px solid rgba(229,9,20,0.10);
}
.nav-logo{
  font-family:'Bebas Neue',sans-serif;font-size:1.9rem;letter-spacing:5px;
  color:var(--red);text-shadow:0 0 28px rgba(229,9,20,0.5);
}

/* ══ GLASS CARDS ══ */
[data-testid="stVerticalBlockBorderWrapper"]{
  background:rgba(8,4,18,0.82)!important;
  border:2px solid rgba(229,9,20,0.45)!important;
  border-radius:20px!important;
  backdrop-filter:blur(40px) saturate(1.6) brightness(1.05)!important;
  -webkit-backdrop-filter:blur(40px) saturate(1.6) brightness(1.05)!important;
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,0.10),
    inset 0 0 40px rgba(0,0,0,0.40),
    0 0 0 1px rgba(229,9,20,0.12),
    0 24px 70px rgba(0,0,0,0.75)!important;
  transition:border-color 0.35s,box-shadow 0.35s,transform 0.35s!important;
  padding:32px 36px 28px!important;
  margin-bottom:16px!important;
  position:relative;overflow:hidden;
  animation:breathe 5s ease-in-out infinite;
}
/* Red top scan line on cards */
[data-testid="stVerticalBlockBorderWrapper"]::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1.5px;
  background:linear-gradient(90deg,transparent,rgba(229,9,20,0.45) 30%,rgba(255,80,80,0.25) 50%,rgba(229,9,20,0.45) 70%,transparent);
  z-index:1;
}
@keyframes breathe{
  0%,100%{box-shadow:inset 0 1px 0 rgba(255,255,255,0.10),inset 0 0 40px rgba(0,0,0,0.40),0 0 0 1px rgba(229,9,20,0.12),0 24px 70px rgba(0,0,0,0.75);}
  50%{box-shadow:inset 0 1px 0 rgba(255,255,255,0.12),inset 0 0 40px rgba(0,0,0,0.40),0 0 0 1px rgba(229,9,20,0.25),0 28px 80px rgba(0,0,0,0.82),0 0 50px rgba(229,9,20,0.08);}
}

/* ══ LABELS ══ */
[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span,
.stTextInput>label,.stNumberInput>label,.stSelectbox>label,
.stMultiSelect>label,.stCheckbox>label,.stRadio>label{
  color:#fff!important;font-size:1.05rem!important;font-weight:700!important;
  letter-spacing:2px!important;text-transform:uppercase!important;
  text-shadow:0 1px 12px rgba(0,0,0,0.99)!important;opacity:1!important;
}

/* ══ INPUTS ══ */
/* ══ GLASS INPUTS — nuclear targeting all containers ══ */
input, textarea,
.stTextInput input, .stTextInput>div>div>input,
.stNumberInput input, .stNumberInput>div>div>input,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input{
  background:rgba(8,5,20,0.55)!important;
  border:2px solid rgba(229,9,20,0.45)!important;
  color:#fff!important;border-radius:10px!important;
  font-family:'DM Sans',sans-serif!important;font-size:0.95rem!important;
  backdrop-filter:blur(32px)!important;
  -webkit-backdrop-filter:blur(32px)!important;
  box-shadow:
    0 0 0 1px rgba(229,9,20,0.08),
    inset 0 1px 0 rgba(255,255,255,0.06),
    0 4px 16px rgba(0,0,0,0.40)!important;
  transition:all 0.25s!important;
}
input:hover, .stTextInput input:hover, .stNumberInput input:hover{
  background:rgba(12,6,24,0.70)!important;
  border-color:rgba(229,9,20,0.60)!important;
  box-shadow:
    0 0 16px rgba(229,9,20,0.25),
    0 0 4px rgba(229,9,20,0.15),
    inset 0 1px 0 rgba(255,255,255,0.08),
    0 4px 20px rgba(0,0,0,0.50)!important;
}
input:focus, .stTextInput input:focus, .stNumberInput input:focus{
  background:rgba(14,6,26,0.80)!important;
  border-color:rgba(229,9,20,0.90)!important;
  box-shadow:
    0 0 24px rgba(229,9,20,0.40),
    0 0 8px rgba(229,9,20,0.20),
    0 0 0 3px rgba(229,9,20,0.12),
    inset 0 1px 0 rgba(255,255,255,0.10),
    0 4px 24px rgba(0,0,0,0.55)!important;
  outline:none!important;
}

/* ══ GLASS SELECTS ══ */
.stSelectbox>div>div,
.stMultiSelect>div>div,
[data-testid="stSelectbox"]>div>div,
[data-baseweb="select"]>div{
  background:rgba(8,5,20,0.55)!important;
  border:2px solid rgba(229,9,20,0.45)!important;
  color:#fff!important;border-radius:10px!important;
  backdrop-filter:blur(32px)!important;
  -webkit-backdrop-filter:blur(32px)!important;
  box-shadow:
    0 0 0 1px rgba(229,9,20,0.08),
    inset 0 1px 0 rgba(255,255,255,0.06),
    0 4px 16px rgba(0,0,0,0.40)!important;
  transition:all 0.25s!important;
}
.stSelectbox>div>div:hover,.stMultiSelect>div>div:hover,
[data-baseweb="select"]>div:hover{
  border-color:rgba(229,9,20,0.65)!important;
  box-shadow:
    0 0 20px rgba(229,9,20,0.30),
    inset 0 1px 0 rgba(255,255,255,0.08),
    0 4px 20px rgba(0,0,0,0.50)!important;
}

/* ══ Number input step buttons ══ */
.stNumberInput [data-testid="stNumberInputStepDown"],
.stNumberInput [data-testid="stNumberInputStepUp"],
[data-testid="stNumberInputStepDown"],
[data-testid="stNumberInputStepUp"]{
  background:rgba(229,9,20,0.20)!important;
  border:2px solid rgba(229,9,20,0.55)!important;
  color:#fff!important;border-radius:6px!important;
}
.stNumberInput [data-testid="stNumberInputStepDown"]:hover,
.stNumberInput [data-testid="stNumberInputStepUp"]:hover{
  background:rgba(229,9,20,0.45)!important;
  box-shadow:0 0 10px rgba(229,9,20,0.40)!important;
}

/* ══ Override white form background ══ */
[data-testid="stForm"]{
  background:transparent!important;
  border:none!important;
}
section[data-testid="stFormSubmitButton"] button,
[data-testid="baseButton-secondaryFormSubmit"]{
  width:100%!important;
}

/* ══ BUTTONS ══ */
.stButton>button{
  background:linear-gradient(135deg,rgba(229,9,20,0.85),rgba(160,0,10,0.90))!important;
  border:2px solid rgba(229,9,20,0.65)!important;
  color:#fff!important;border-radius:10px!important;
  font-family:'Barlow Condensed',sans-serif!important;
  font-size:1.05rem!important;font-weight:700!important;
  letter-spacing:2px!important;text-transform:uppercase!important;
  box-shadow:0 0 18px rgba(229,9,20,0.40),0 4px 16px rgba(229,9,20,0.20)!important;
  transition:all 0.22s cubic-bezier(0.34,1.56,0.64,1)!important;
  min-height:52px!important;
}
.stButton>button:hover{
  background:linear-gradient(135deg,#E50914,#c0000c)!important;
  transform:translateY(-2px) scale(1.02)!important;
  box-shadow:0 0 32px rgba(229,9,20,0.65),0 8px 28px rgba(229,9,20,0.35)!important;
}
/* Primary pulsing save button */
[data-testid="baseButton-secondaryFormSubmit"],.stFormSubmitButton>button,
section[data-testid="stFormSubmitButton"]>div>button{
  background:linear-gradient(135deg,#E50914,#b0000a)!important;
  border:2px solid rgba(229,9,20,0.65)!important;
  color:#fff!important;border-radius:10px!important;
  font-family:'Barlow Condensed',sans-serif!important;
  font-size:1.1rem!important;font-weight:800!important;
  letter-spacing:3px!important;text-transform:uppercase!important;
  min-height:56px!important;width:100%!important;
  animation:btn-pulse 2.5s ease-in-out infinite!important;
}
@keyframes btn-pulse{
  0%,100%{box-shadow:0 0 18px rgba(229,9,20,0.45),0 4px 18px rgba(229,9,20,0.25);}
  50%{box-shadow:0 0 36px rgba(229,9,20,0.80),0 6px 30px rgba(229,9,20,0.50);}
}
[data-testid="baseButton-secondaryFormSubmit"]:hover,.stFormSubmitButton>button:hover{
  animation:none!important;
  box-shadow:0 0 44px rgba(229,9,20,0.90),0 10px 36px rgba(229,9,20,0.55)!important;
  transform:translateY(-2px)!important;
}

/* Primary action button — Generate Plan */
.gen-btn .stButton>button{
  background:linear-gradient(135deg,#E50914,#c0000c)!important;
  border-color:rgba(229,9,20,0.5)!important;color:#fff!important;
  animation:glow-pulse 2.4s ease-in-out infinite!important;
}
@keyframes glow-pulse{
  0%,100%{box-shadow:0 0 18px rgba(229,9,20,0.45),0 4px 18px rgba(229,9,20,0.25);}
  50%{box-shadow:0 0 32px rgba(229,9,20,0.75),0 6px 28px rgba(229,9,20,0.45);}
}
.gen-btn .stButton>button:hover{
  animation:none!important;filter:brightness(1.12)!important;
  box-shadow:0 0 40px rgba(229,9,20,0.80)!important;transform:translateY(-2px)!important;
}
/* Regen button — orange warning style */
[data-testid="stButton"]:has(button[key="regen_form_btn_profile"]) button,
div:has(> [data-testid="baseButton-secondary"][kind="secondary"][key="regen_form_btn_profile"]) button{
  background:linear-gradient(135deg,rgba(234,88,12,0.90),rgba(194,65,12,0.95))!important;
  border:1.5px solid rgba(249,115,22,0.65)!important;color:#fff!important;
  border-radius:10px!important;font-weight:700!important;font-size:0.85rem!important;
  letter-spacing:0.5px!important;
  box-shadow:0 0 16px rgba(234,88,12,0.45)!important;transition:all 0.22s!important;
  animation:regen-pulse 2.2s ease-in-out infinite!important;
}
@keyframes regen-pulse{
  0%,100%{box-shadow:0 0 14px rgba(234,88,12,0.45);}
  50%{box-shadow:0 0 28px rgba(234,88,12,0.80);}
}

/* ══ CHECKBOX ══ */
.stCheckbox [data-testid="stCheckbox"] span{
  border-color:rgba(229,9,20,0.50)!important;
}
[data-testid="stCheckbox"]:hover [data-testid="stCheckbox"] span{
  border-color:var(--red)!important;
}

/* ══ SECTION HEADER ══ */
.sec-hdr{
  display:flex;align-items:center;gap:10px;
  font-size:0.85rem;font-weight:700;letter-spacing:3.5px;
  text-transform:uppercase;color:rgba(255,255,255,0.90);
  margin:28px 0 14px;
}
.sec-hdr::before{content:'';width:20px;height:1.5px;background:var(--red);flex-shrink:0;border-radius:1px;}
.sec-hdr::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,rgba(255,255,255,0.06),transparent);}

/* ══ BMI BADGE ══ */
.bmi-pill{
  display:inline-flex;align-items:center;gap:8px;
  padding:8px 18px;border-radius:100px;
  background:rgba(229,9,20,0.10);border:2px solid rgba(229,9,20,0.40);
  font-size:0.80rem;font-weight:700;letter-spacing:1px;margin-top:12px;color:rgba(255,255,255,0.80);
}

hr{border-color:rgba(255,255,255,0.90)!important;margin:20px 0!important;}
div[data-testid="stHorizontalBlock"]{gap:12px!important;}

/* ═══ UX OVERHAUL: VISIBILITY & READABILITY ════════════════════════════════ */
html,body,.stApp,.stMarkdown,p,div,span,label{text-shadow:0 2px 6px rgba(0,0,0,0.98)!important;}
[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] p{color:#fff!important;font-size:1.05rem!important;font-weight:700!important;text-shadow:0 2px 8px rgba(0,0,0,0.99)!important;}
.stCheckbox>label,.stCheckbox>label p{color:#fff!important;font-weight:700!important;font-size:1.05rem!important;text-shadow:0 2px 8px rgba(0,0,0,0.99)!important;}
.stTabs [data-baseweb="tab"]{color:rgba(255,255,255,0.92)!important;font-size:0.95rem!important;font-weight:700!important;text-shadow:0 2px 6px rgba(0,0,0,0.95)!important;}
.stExpander details summary{color:#fff!important;font-size:1.05rem!important;font-weight:700!important;text-shadow:0 2px 6px rgba(0,0,0,0.95)!important;}
.stMarkdown p,.stMarkdown li{color:#fff!important;font-size:1.05rem!important;line-height:1.75!important;text-shadow:0 2px 8px rgba(0,0,0,0.99)!important;}
.cal-cell{background:rgba(0,0,0,0.85)!important;border:1.5px solid rgba(255,255,255,0.28)!important;}
.cal-cell.today-cell{background:rgba(229,9,20,0.40)!important;border:2.5px solid #E50914!important;}
.cal-cell.done-cell{background:rgba(34,197,94,0.32)!important;border:2px solid rgba(34,197,94,0.75)!important;}
.cal-num{color:#fff!important;font-size:0.80rem!important;font-weight:800!important;text-shadow:0 2px 6px rgba(0,0,0,0.99)!important;}
.cal-dow{color:rgba(255,255,255,0.95)!important;font-size:0.80rem!important;font-weight:800!important;}
.act-day{color:#fff!important;font-size:0.80rem!important;font-weight:800!important;text-shadow:0 2px 6px rgba(0,0,0,0.99)!important;}
.g-panel{background:rgba(8,4,2,0.88)!important;backdrop-filter:blur(32px)!important;-webkit-backdrop-filter:blur(32px)!important;}
</style>
""", unsafe_allow_html=True)

# ── Nuclear popover dark fix (Streamlit renders dropdowns outside .stApp) ─────
st.markdown("""
<style>
[data-baseweb="popover"],[data-baseweb="popover"] *{background-color:#0d0818!important;color:#fff!important;}
[data-baseweb="popover"]{border:2px solid rgba(229,9,20,0.37)!important;border-radius:14px!important;box-shadow:0 20px 60px rgba(0,0,0,0.92)!important;}
[data-baseweb="menu"]{background:#0d0818!important;}
[data-baseweb="menu"] ul,[data-baseweb="menu"] li{background:#0d0818!important;color:rgba(255,255,255,0.80)!important;}
li[role="option"]{background:#0d0818!important;color:rgba(255,255,255,0.78)!important;font-family:'DM Sans',sans-serif!important;padding:10px 14px!important;margin:1px 6px!important;border-radius:8px!important;cursor:pointer!important;}
li[role="option"]:hover{background:rgba(229,9,20,0.18)!important;color:#fff!important;}
li[aria-selected="true"]{background:rgba(229,9,20,0.25)!important;color:#fff!important;}
[data-baseweb="menu"]>div>div:first-child{background:#0d0818!important;border-bottom:1px solid rgba(255,255,255,0.06)!important;color:rgba(255,255,255,0.90)!important;font-size:0.75rem!important;padding:8px 14px!important;}
[data-baseweb="tag"]{background:rgba(229,9,20,0.18)!important;border:2px solid rgba(229,9,20,0.47)!important;border-radius:6px!important;margin:2px!important;}
[data-baseweb="tag"] span{color:#fff!important;}
div[data-baseweb="multi-select"]{background:rgba(255,255,255,0.06)!important;}
div[data-baseweb="multi-select"]>div{background:rgba(255,255,255,0.06)!important;color:#fff!important;}
div[data-baseweb="multi-select"] input{background:transparent!important;color:#fff!important;}
div[data-baseweb="select"] div div{background:transparent!important;color:#fff!important;}

/* ═══ UX OVERHAUL: VISIBILITY & READABILITY ════════════════════════════════ */
html,body,.stApp,.stMarkdown,p,div,span,label{text-shadow:0 2px 6px rgba(0,0,0,0.98)!important;}
[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] p{color:#fff!important;font-size:1.05rem!important;font-weight:700!important;text-shadow:0 2px 8px rgba(0,0,0,0.99)!important;}
.stCheckbox>label,.stCheckbox>label p{color:#fff!important;font-weight:700!important;font-size:1.05rem!important;text-shadow:0 2px 8px rgba(0,0,0,0.99)!important;}
.stTabs [data-baseweb="tab"]{color:rgba(255,255,255,0.92)!important;font-size:0.95rem!important;font-weight:700!important;text-shadow:0 2px 6px rgba(0,0,0,0.95)!important;}
.stExpander details summary{color:#fff!important;font-size:1.05rem!important;font-weight:700!important;text-shadow:0 2px 6px rgba(0,0,0,0.95)!important;}
.stMarkdown p,.stMarkdown li{color:#fff!important;font-size:1.05rem!important;line-height:1.75!important;text-shadow:0 2px 8px rgba(0,0,0,0.99)!important;}
.cal-cell{background:rgba(0,0,0,0.85)!important;border:1.5px solid rgba(255,255,255,0.28)!important;}
.cal-cell.today-cell{background:rgba(229,9,20,0.40)!important;border:2.5px solid #E50914!important;}
.cal-cell.done-cell{background:rgba(34,197,94,0.32)!important;border:2px solid rgba(34,197,94,0.75)!important;}
.cal-num{color:#fff!important;font-size:0.80rem!important;font-weight:800!important;text-shadow:0 2px 6px rgba(0,0,0,0.99)!important;}
.cal-dow{color:rgba(255,255,255,0.95)!important;font-size:0.80rem!important;font-weight:800!important;}
.act-day{color:#fff!important;font-size:0.80rem!important;font-weight:800!important;text-shadow:0 2px 6px rgba(0,0,0,0.99)!important;}
.g-panel{background:rgba(8,4,2,0.88)!important;backdrop-filter:blur(32px)!important;-webkit-backdrop-filter:blur(32px)!important;}
</style>
""", unsafe_allow_html=True)

# ── NAV ───────────────────────────────────────────────────────────────────────
nc1, nc2, nc3, nc4 = st.columns([3,2,2,2])
with nc1:
    st.markdown("<div class='nav-logo'>⚡ FITPLAN PRO</div>", unsafe_allow_html=True)
with nc2:
    if st.session_state.get("structured_days"):
        if st.button("🏠 Home", use_container_width=True, key="prof_dash"):
            if not st.session_state.get("workout_plan"):
                st.session_state.workout_plan = "\n".join([f"## Day {d.get('day',i+1)}" for i,d in enumerate(st.session_state.get("structured_days",[]))])
            st.switch_page("pages/2_Dashboard.py")
with nc3:
    if st.session_state.get("structured_days"):
        if st.button("⚡ Workout", use_container_width=True, key="prof_wp"):
            st.switch_page("pages/3_Workout_Plan.py")
with nc4:
    if st.button("🚪 Sign Out", use_container_width=True, key="prof_so2"):
        logout(uname)
        for k in ["logged_in","username","auth_token","user_data","workout_plan","structured_days","dietary_type","full_plan_data","plan_id","plan_start","plan_duration","plan_for","force_regen","tracking","_plan_checked","_db_loaded_dash","_auto_redirect","_diet_chosen","_needs_rerun","_db_streak","edit_profile_mode","_login_db_err"]:
            st.session_state.pop(k, None)
        st.switch_page("app.py")

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── On login: load profile + plan from DB ────────────────────────────────────
if not st.session_state.get("_plan_checked"):
    st.session_state._plan_checked = True
    # Step 1: Load user profile from DB (always — ensures fresh data after re-login)
    try:
        from utils.db import get_user_profile
        saved_profile = get_user_profile(uname)
        if saved_profile:
            st.session_state.user_data = saved_profile
    except Exception as _pe:
        import traceback; traceback.print_exc()
    # Step 2: Load active plan from DB
    try:
        from utils.db import get_active_plan
        existing = get_active_plan(uname)
        # Always clear stale session plan before loading fresh
        if existing and existing.get("days") and len(existing["days"]) > 0:
            for _k in ["structured_days","full_plan_data","workout_plan","plan_id","dietary_type","plan_start"]:
                st.session_state.pop(_k, None)
        if existing and existing.get("days"):
            days = existing["days"]
            structured = []
            for d in days:
                day_obj = {
                    "day":          d.get("day_number", 1),
                    "is_rest_day":  d.get("is_rest_day", False),
                    "muscle_group": d.get("muscle_group", "Full Body"),
                    "workout":      d.get("workout_json", []),
                    "dietary":      d.get("dietary_json", {}),
                    "pre_stretch":  d.get("pre_stretch_json", []),
                    "post_stretch": d.get("post_stretch_json", []),
                }
                structured.append(day_obj)
            structured.sort(key=lambda x: x["day"])
            st.session_state.structured_days = structured
            st.session_state.full_plan_data  = structured
            st.session_state.dietary_type    = existing.get("dietary_type","veg")
            st.session_state.plan_id         = existing.get("plan_id","")
            # Build text version
            st.session_state.workout_plan    = "\n".join([f"## Day {d['day']} - {d['muscle_group']}" for d in structured])
            st.session_state.plan_for        = uname
            st.session_state._auto_redirect  = True  # plan loaded → go to dashboard
    except Exception:
        pass
    # Also redirect if only profile was loaded (no plan yet → dashboard will route to plan gen)
    if not st.session_state.get("_auto_redirect") and st.session_state.get("user_data"):
        st.session_state._auto_redirect = True

# ── Auto-redirect logic ───────────────────────────────────────────────────────
if st.session_state.get("_auto_redirect"):
    st.session_state.pop("_auto_redirect", None)
    st.switch_page("pages/2_Dashboard.py")  # always redirect — profile + plan are loaded

# ── Load existing user_data from session ──────────────────────────────────────
ud = st.session_state.get("user_data", {})
edit_mode = st.session_state.get("edit_profile_mode", False)
has_plan  = bool(st.session_state.get("structured_days"))

# ══════════════════════════════════════════════════════════════════════════════
# PROFILE FORM — shown if no data yet OR in edit mode
# ══════════════════════════════════════════════════════════════════════════════
if not ud or edit_mode:
    st.markdown(
        f"<div style='background:linear-gradient(135deg,rgba(229,9,20,0.10),rgba(229,9,20,0.04));"
        f"border:2px solid rgba(229,9,20,0.35);border-radius:18px;padding:24px 32px;margin-bottom:22px;"
        f"position:relative;overflow:hidden'>"
        f"<div style='position:absolute;top:0;left:0;right:0;height:2px;"
        f"background:linear-gradient(90deg,transparent,#E50914,transparent)'></div>"
        f"<div style='font-size:0.85rem;font-weight:700;letter-spacing:4px;text-transform:uppercase;"
        f"color:rgba(229,9,20,0.80);margin-bottom:6px'>Welcome Back</div>"
        f"<div style='font-family:Bebas Neue,sans-serif;font-size:2.6rem;letter-spacing:3px;"
        f"color:#fff;line-height:1;text-shadow:0 0 30px rgba(229,9,20,0.30)'>"
        f"WELCOME, <span style='color:#E50914'>{uname.upper()}!</span></div>"
        f"<div style='font-size:1.00rem;color:rgba(255,255,255,0.90);margin-top:8px'>"
        f"Fill in your body details to generate your personalised AI fitness plan.</div></div>",
        unsafe_allow_html=True
    )

    with st.form("profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            age    = st.number_input("Age", min_value=10, max_value=100, value=int(ud.get("age",25)))
            height = st.number_input("Height (cm)", min_value=100, max_value=250, value=int(ud.get("height",170)))
        with c2:
            gender = st.selectbox("Gender", ["Male","Female","Other"], index=["Male","Female","Other"].index(ud.get("gender","Male")))
            weight = st.number_input("Weight (kg)", min_value=30, max_value=250, value=int(ud.get("weight",70)))
        c3, c4 = st.columns(2)
        with c3:
            level  = st.selectbox("Fitness Level", ["Beginner","Intermediate","Advanced"],
                                  index=["Beginner","Intermediate","Advanced"].index(ud.get("level","Beginner")))
        with c4:
            goal   = st.selectbox("Fitness Goal", ["Weight Loss","Build Muscle","General Fitness"],
                                  index=["Weight Loss","Build Muscle","General Fitness"].index(ud.get("goal","Weight Loss")))
        c5, c6 = st.columns(2)
        with c5:
            dpw    = st.selectbox("Training Days/Week", [3,4,5,6,7], index=[3,4,5,6,7].index(int(ud.get("days_per_week",5))))
        with c6:
            months = st.selectbox("Program Length", [1,2,3], index=[1,2,3].index(int(ud.get("months",1))), format_func=lambda x: f"{x} month{'s' if x>1 else ''}")

        home_eq = st.multiselect("🏠 Home & Basic Equipment", [
            "Dumbbells","Adjustable Dumbbells","Resistance Bands","Pull-up Bar",
            "Dip Station","Bench","Kettlebell","Jump Rope","Push-up Handles",
            "Ab Roller","Yoga Mat","Foam Roller","TRX / Suspension Bands",
            "Battle Ropes","Medicine Ball"
        ], default=ud.get("home_eq",[]))
        gym_eq  = st.multiselect("🏋️ Commercial Gym Equipment", [
            "Barbell + Rack","EZ Curl Bar","Cable Machine","Smith Machine",
            "Lat Pulldown","Seated Cable Row","Leg Press","Leg Curl Machine",
            "Leg Extension Machine","Chest Fly Machine","Pec Deck",
            "Incline / Decline Bench","Preacher Curl Bench","Dip Machine",
            "Treadmill","Elliptical","Rowing Machine","Stationary Bike",
            "Stair Climber","Assisted Pull-up Machine"
        ], default=ud.get("gym_eq",[]))
        no_eq   = st.checkbox("🤸 Bodyweight Only — no equipment needed", value=ud.get("no_eq", False))

        submitted = st.form_submit_button("💾 SAVE PROFILE & CONTINUE →", use_container_width=True)

    # Regenerate button — outside form so it always shows
    has_plan = bool(st.session_state.get("structured_days"))
    if has_plan:
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        regen_col1, regen_col2 = st.columns([1,1])
        with regen_col1:
            st.markdown("""
            <div style='background:rgba(229,9,20,0.06);border:1px solid rgba(229,9,20,0.25);
              border-radius:12px;padding:12px 16px;font-size:0.80rem;color:rgba(255,255,255,0.90);
              line-height:1.5'>
              <b style='color:rgba(229,9,20,0.80)'>&#128260; Regenerate Plan</b><br>
              Clears your current plan and generates a brand new one with your updated profile settings.
            </div>
            """, unsafe_allow_html=True)
        with regen_col2:
            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
            if st.button("🔄 REGENERATE PLAN", use_container_width=True, key="regen_form_btn_profile"):
                # Clear all plan data
                for _k in ["workout_plan","structured_days","dietary_type","full_plan_data",
                            "plan_id","_diet_chosen","force_regen","_db_loaded_dash",
                            "_notes_loaded","_plan_checked"]:
                    st.session_state.pop(_k, None)
                st.session_state.force_regen = True
                # Try to delete from DB too
                try:
                    from utils.db import delete_active_plan
                    delete_active_plan(uname)
                except Exception:
                    pass
                st.success("Plan cleared! Redirecting to generate your new plan...")
                st.switch_page("pages/3_Workout_Plan.py")
    else:
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background:rgba(229,9,20,0.06);border:1px solid rgba(229,9,20,0.15);
          border-radius:10px;padding:10px 14px;font-size:0.75rem;color:rgba(255,255,255,0.90);
          text-align:center'>
          &#128221; Fill in your profile above and click Save to generate your personalised plan
        </div>
        """, unsafe_allow_html=True)

    if submitted:
        total_days = dpw * 4 * months  # no cap — 3 months × 7 days = 84 max
        equipment  = [] if no_eq else list(set(home_eq + gym_eq))
        profile = {
            "name": uname, "age": age, "gender": gender,
            "height": height, "weight": weight,
            "level": level, "goal": goal,
            "days_per_week": dpw, "months": months,
            "total_days": total_days, "equipment": equipment,
            "home_eq": home_eq, "gym_eq": gym_eq, "no_eq": no_eq,
        }
        st.session_state.user_data = profile
        # Save profile to DB
        try:
            from utils.db import save_user_profile
            save_user_profile(uname, profile)
        except Exception:
            pass
        st.session_state.edit_profile_mode = False
        st.toast("✅ Profile saved!", icon="👤")
        # If regenerating, clear old plan from DB
        if st.session_state.get("force_regen"):
            try:
                from utils.db import delete_active_plan
                delete_active_plan(uname)
                for _k in ["structured_days","dietary_type","full_plan_data","plan_id","_diet_chosen","workout_plan"]:
                    st.session_state.pop(_k, None)
            except Exception:
                pass
            st.switch_page("pages/3_Workout_Plan.py")
        else:
            # New profile saved — go to dashboard (which will route to plan gen if needed)
            st.switch_page("pages/2_Dashboard.py")

    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PROFILE DISPLAY — shown when data exists
# ══════════════════════════════════════════════════════════════════════════════
else:
    from prompt_builder import calculate_bmi, bmi_category
    bmi     = calculate_bmi(ud["weight"], ud["height"])
    bmi_cat = bmi_category(bmi)

    st.markdown(
        f"<div style='background:linear-gradient(135deg,rgba(229,9,20,0.10),rgba(229,9,20,0.04));"
        f"border:2px solid rgba(229,9,20,0.35);border-radius:18px;padding:24px 32px;margin-bottom:22px;"
        f"position:relative;overflow:hidden'>"
        f"<div style='position:absolute;top:0;left:0;right:0;height:2px;"
        f"background:linear-gradient(90deg,transparent,#E50914,transparent)'></div>"
        f"<div style='font-size:0.85rem;font-weight:700;letter-spacing:4px;text-transform:uppercase;"
        f"color:rgba(229,9,20,0.80);margin-bottom:6px'>Your Profile</div>"
        f"<div style='font-family:Bebas Neue,sans-serif;font-size:2.6rem;letter-spacing:3px;"
        f"color:#fff;line-height:1;text-shadow:0 0 30px rgba(229,9,20,0.30)'>"
        f"WELCOME, <span style='color:#E50914'>{uname.upper()}!</span></div>"
        f"<div style='font-size:1.00rem;color:rgba(255,255,255,0.90);margin-top:8px'>"
        f"Here's your body stats and active plan summary.</div></div>",
        unsafe_allow_html=True
    )

    st.markdown(f"""
    <div class='card'>
      <div class='card-title'>👤 Your Profile</div>
      <div style='display:grid;grid-template-columns:repeat(3,1fr);gap:16px'>
        {"".join([
          f"<div style='background:rgba(12,6,24,0.82);border:1.5px solid rgba(229,9,20,0.35);border-radius:14px;padding:18px;text-align:center;backdrop-filter:blur(20px);box-shadow:inset 0 1px 0 rgba(255,255,255,0.08),0 8px 32px rgba(0,0,0,0.60)'>"
          f"<div style='font-size:0.85rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:rgba(255,255,255,0.90);margin-bottom:6px'>{lbl}</div>"
          f"<div style='font-family:Bebas Neue,sans-serif;font-size:1.8rem;color:#fff;letter-spacing:1px'>{val}</div>"
          f"<div style='font-size:1.00rem;color:rgba(255,255,255,0.90)'>{unit}</div></div>"
          for lbl,val,unit in [
            ("Age", ud['age'], "years"),
            ("Height", ud['height'], "cm"),
            ("Weight", ud['weight'], "kg"),
            ("BMI", f"{bmi:.1f}", bmi_cat),
            ("Level", ud['level'], "fitness"),
            ("Goal", ud['goal'].replace(' ','<br>'), ""),
          ]
        ])}
      </div>
      <div style='margin-top:14px;display:flex;gap:10px;flex-wrap:wrap'>
        <div style='font-size:0.80rem;color:rgba(255,255,255,0.90)'>📅 {ud['days_per_week']} days/week · {ud['months']} month{'s' if ud['months']>1 else ''} · {ud['total_days']} total days</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Plan status + Regenerate ───────────────────────────────────────────────
    if has_plan:
        plan_days = len(st.session_state.structured_days)
        diet_str  = ("🌿 Vegetarian" if st.session_state.get("dietary_type")=="veg"
                     else ("🍗 Non-Vegetarian" if st.session_state.get("dietary_type")=="nonveg"
                           else "🍽️ Flexible"))
        dpw_s   = str(ud.get("days_per_week", 5))
        months_s = str(ud.get("months", 1))
        st.markdown(
            "<div style='background:rgba(34,197,94,0.08);border:1.5px solid rgba(34,197,94,0.30);"
            "border-radius:14px;padding:16px 22px;margin-bottom:14px;display:flex;"
            "align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px'>"
            "<div><div style='font-size:0.85rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;"
            "color:rgba(34,197,94,0.75);margin-bottom:4px'>&#10003; Active Plan</div>"
            "<div style='font-size:1.05rem;font-weight:600;color:#fff'>"
            + str(plan_days) + "-day plan &middot; " + diet_str + "</div></div>"
            "<div style='font-size:0.75rem;color:rgba(255,255,255,0.90)'>"
            + dpw_s + " days/week &middot; " + months_s + " month(s)</div></div>",
            unsafe_allow_html=True
        )

        # Navigation
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            if st.button("🏠 Dashboard", use_container_width=True, key="pdisp_dash"):
                st.switch_page("pages/2_Dashboard.py")
        with b2:
            if st.button("⚡ Workout Plan", use_container_width=True, key="pdisp_wp"):
                st.switch_page("pages/3_Workout_Plan.py")
        with b3:
            if st.button("🥗 Diet Plan", use_container_width=True, key="pdisp_diet"):
                st.switch_page("pages/4_Diet_Plan.py")
        with b4:
            if st.button("✏️ Edit Profile", use_container_width=True, key="pdisp_edit"):
                st.session_state.edit_profile_mode = True
                st.rerun()

        # REGENERATE PLAN section
        st.markdown(
            "<div style='background:rgba(229,9,20,0.07);border:1.5px solid rgba(229,9,20,0.28);"
            "border-radius:16px;padding:20px 24px;margin-top:16px;position:relative;overflow:hidden'>"
            "<div style='position:absolute;top:0;left:0;right:0;height:2px;"
            "background:linear-gradient(90deg,transparent,#E50914,transparent)'></div>"
            "<div style='font-size:0.85rem;font-weight:700;letter-spacing:3px;text-transform:uppercase;"
            "color:rgba(229,9,20,0.80);margin-bottom:6px'>&#128260; Don&#39;t Like Your Plan?</div>"
            "<div style='font-family:Bebas Neue,sans-serif;font-size:1.4rem;letter-spacing:2px;"
            "color:#fff;margin-bottom:8px'>Regenerate Your Plan</div>"
            "<div style='font-size:0.80rem;color:rgba(255,255,255,0.90);line-height:1.55;margin-bottom:16px'>"
            "Not satisfied with the exercises or meals? Get a completely new AI-generated "
            + str(plan_days) + "-day workout + diet plan. Your tracking history is preserved.</div>"
            "</div>",
            unsafe_allow_html=True
        )
        rc1, rc2 = st.columns([1,1])
        with rc1:
            st.markdown(
                "<div style='background:rgba(12,6,24,0.82);border:1.5px solid rgba(229,9,20,0.30);"
                "border-radius:10px;padding:12px 14px;font-size:1.05rem;color:rgba(255,255,255,0.95);line-height:1.6;"
                "backdrop-filter:blur(20px);box-shadow:inset 0 1px 0 rgba(255,255,255,0.06),0 8px 28px rgba(0,0,0,0.55)'>"
                "&#9888;&#65039; This <b style='color:rgba(229,9,20,0.80)'>permanently deletes</b> your "
                "current plan and AI generates a fresh one with your profile settings.</div>",
                unsafe_allow_html=True
            )
        with rc2:
            if not st.session_state.get("_regen_confirm"):
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                if st.button("🔄 REGENERATE PLAN", use_container_width=True, key="regen_show_confirm"):
                    st.session_state._regen_confirm = True
                    st.rerun()
            else:
                st.markdown(
                    "<div style='font-size:1.00rem;font-weight:700;color:rgba(229,9,20,0.90);"
                    "text-align:center;margin-bottom:8px;padding-top:4px'>"
                    "&#9888;&#65039; Are you sure? This cannot be undone.</div>",
                    unsafe_allow_html=True
                )
                yc, nc = st.columns(2)
                with yc:
                    if st.button("✅ Yes, Regenerate!", use_container_width=True, key="regen_yes"):
                        for _k in ["workout_plan","structured_days","dietary_type","full_plan_data",
                                   "plan_id","_diet_chosen","force_regen","_db_loaded_dash",
                                   "_notes_loaded","_plan_checked","_regen_confirm"]:
                            st.session_state.pop(_k, None)
                        st.session_state.force_regen = True
                        try:
                            from utils.db import delete_active_plan
                            delete_active_plan(uname)
                        except Exception: pass
                        st.toast("🔄 Generating your new plan...", icon="⚡")
                        st.switch_page("pages/3_Workout_Plan.py")
                with nc:
                    if st.button("❌ Cancel", use_container_width=True, key="regen_no"):
                        st.session_state._regen_confirm = False
                        st.rerun()

    else:
        st.markdown(
            "<div style='background:rgba(229,9,20,0.07);border:1px solid rgba(229,9,20,0.22);"
            "border-radius:14px;padding:16px 22px;margin-bottom:14px;text-align:center;"
            "font-size:1.00rem;color:rgba(255,255,255,0.90)'>"
            "No active plan yet. Generate your personalised AI plan below.</div>",
            unsafe_allow_html=True
        )
        b1, b2 = st.columns(2)
        with b1:
            st.markdown("<div class='gen-btn'>", unsafe_allow_html=True)
            if st.button("⚡ GENERATE PLAN", use_container_width=True, key="pdisp_gen"):
                st.switch_page("pages/3_Workout_Plan.py")
            st.markdown("</div>", unsafe_allow_html=True)
        with b2:
            if st.button("✏️ Edit Profile", use_container_width=True, key="pdisp_edit2"):
                st.session_state.edit_profile_mode = True
                st.rerun()
