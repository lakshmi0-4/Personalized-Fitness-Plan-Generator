# -*- coding: utf-8 -*-
import streamlit as st
import os, sys
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_token import logout
from bg_utils import apply_bg

st.set_page_config(page_title="FitPlan Pro - Diet Plan", page_icon="🥗", layout="wide")
if not st.session_state.get("logged_in"): st.switch_page("app.py")
if "user_data" not in st.session_state: st.switch_page("pages/1_Profile.py")

uname     = st.session_state.get("username", "Athlete")
data      = st.session_state.user_data
sdays     = st.session_state.get("structured_days", [])
plan_id   = st.session_state.get("plan_id", "")
today_str = date.today().isoformat()
dietary_type = st.session_state.get("dietary_type", "veg")

# Pick background based on dietary type
if dietary_type == "nonveg":
    bg_url = "https://images.unsplash.com/photo-1544025162-d76538b2a681?w=1800&q=80&auto=format&fit=crop"
    accent = "#f97316"; accent_rgb = "249,115,22"
elif dietary_type == "both":
    bg_url = "https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=1800&q=80&auto=format&fit=crop"
    accent = "#facc15"; accent_rgb = "250,204,21"
else:  # veg default
    bg_url = "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=1800&q=80&auto=format&fit=crop"
    accent = "#22c55e"; accent_rgb = "34,197,94"

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@700;800;900&family=DM+Sans:opsz,wght@9..40,400;9..40,600;9..40,700&display=swap');
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stSidebarNav"],section[data-testid="stSidebar"]{display:none!important;}
html,body,.stApp{background:transparent!important;color:#fff!important;font-family:'DM Sans',sans-serif!important;}
[data-testid="stAppViewContainer"]>section>div.block-container{
  max-width:1200px!important;margin:0 auto!important;padding:0 32px 80px!important;}
[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] p{color:rgba(255,255,255,0.80)!important;}
.stButton>button{background:linear-gradient(135deg,rgba(229,9,20,0.85),rgba(160,0,10,0.90))!important;
  border:none!important;color:#fff!important;border-radius:8px!important;
  font-family:'DM Sans',sans-serif!important;font-size:0.82rem!important;font-weight:700!important;
  box-shadow:0 4px 16px rgba(229,9,20,0.35)!important;transition:all 0.20s!important;}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 6px 24px rgba(229,9,20,0.60)!important;}
.stTabs [data-baseweb="tab-list"]{background:rgba(0,0,0,0.40)!important;border-radius:10px!important;
  padding:4px!important;border:1px solid rgba(255,255,255,0.12)!important;backdrop-filter:blur(10px)!important;}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:rgba(255,255,255,0.90)!important;
  border-radius:7px!important;font-size:0.75rem!important;font-weight:600!important;border:none!important;padding:8px 14px!important;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,rgba(229,9,20,0.85),rgba(160,0,10,0.90))!important;
  color:#fff!important;box-shadow:0 3px 12px rgba(229,9,20,0.45)!important;}
.stCheckbox>label{color:#fff!important;}
.stExpander{background:rgba(0,0,0,0.65)!important;
  border:1.5px solid rgba(255,255,255,0.18)!important;
  border-radius:14px!important;backdrop-filter:blur(14px)!important;
  box-shadow:0 4px 20px rgba(0,0,0,0.40)!important;}
.stExpander:hover{border-color:rgba(229,9,20,0.45)!important;}
.stExpander [data-testid="stExpanderToggleIcon"]{color:#fff!important;}
.stExpander details summary{
  color:#fff!important;font-weight:700!important;font-size:0.88rem!important;
  letter-spacing:0.3px!important;padding:14px 18px!important;}
.stExpander details summary:hover{color:#E50914!important;}
.stExpander details[open] summary{color:#E50914!important;}
/* Inner content of expander */
.stExpander details .stExpanderDetails{
  padding:0 18px 14px!important;background:transparent!important;}
div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stButton"] > button{
  background:rgba(0,0,0,0.40)!important;border:1.5px solid rgba(229,9,20,0.50)!important;
  color:#fff!important;border-radius:9px!important;font-size:0.68rem!important;
  font-weight:700!important;padding:6px 8px!important;height:36px!important;
  min-height:36px!important;backdrop-filter:blur(10px)!important;box-shadow:none!important;}
div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stButton"] > button:hover{
  background:rgba(229,9,20,0.30)!important;border-color:rgba(229,9,20,0.85)!important;transform:translateY(-1px)!important;}
div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stButton"]:last-child > button{
  background:rgba(229,9,20,0.35)!important;border:1.5px solid #E50914!important;}
.nav-logo-txt{font-family:'Bebas Neue',sans-serif;font-size:1.5rem;letter-spacing:5px;
  color:#E50914;text-shadow:0 0 20px rgba(229,9,20,0.50);line-height:1;}
.meal-card{background:rgba(0,0,0,0.45);border:1.5px solid rgba(255,255,255,0.12);
  border-radius:14px;padding:16px 20px;margin-bottom:10px;position:relative;
  overflow:hidden;backdrop-filter:blur(10px);}
.meal-label{font-size:0.72rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;
  margin-bottom:8px;display:flex;align-items:center;justify-content:space-between;}
.meal-text{font-size:0.90rem;color:rgba(255,255,255,0.88);line-height:1.65;}
.swap-mini .stButton>button{background:rgba(229,9,20,0.15)!important;
  border:1px solid rgba(229,9,20,0.40)!important;color:rgba(255,255,255,0.85)!important;
  font-size:0.65rem!important;font-weight:700!important;padding:3px 10px!important;
  height:auto!important;border-radius:6px!important;box-shadow:none!important;
  text-transform:uppercase!important;letter-spacing:0.5px!important;}
.swap-mini .stButton>button:hover{background:rgba(229,9,20,0.35)!important;transform:none!important;}
.water-card{background:rgba(0,0,0,0.50);border:1.5px solid rgba(96,165,250,0.35);
  border-radius:16px;padding:18px 22px;margin-bottom:16px;backdrop-filter:blur(12px);}
.feature-card{background:rgba(0,0,0,0.45);border:1.5px solid rgba(255,255,255,0.12);
  border-radius:14px;padding:20px 18px;height:100%;backdrop-filter:blur(10px);
  transition:border-color 0.2s;}
.feature-card:hover{border-color:rgba(229,9,20,0.45);}
.feature-card-title{font-size:0.72rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;
  color:rgba(229,9,20,0.85);margin-bottom:12px;display:flex;align-items:center;gap:6px;}
.prog-bar-bg{height:5px;background:rgba(255,255,255,0.10);border-radius:3px;overflow:hidden;margin-top:6px;}
/* ── VISIBILITY FIXES ─────────────────────────────────────────────────────── */
/* Keep background image visible — only darken card interiors, not the whole page */
[data-testid="stAppViewContainer"]>section>div.block-container{
  background:transparent!important;
  border-radius:0!important;
  padding:0 24px 80px!important;
}
/* Meal cards — much darker background */
.meal-card{background:rgba(0,0,0,0.78)!important;
  border:1.5px solid rgba(255,255,255,0.22)!important;}
.meal-text{color:#fff!important;font-size:0.92rem!important;
  text-shadow:0 1px 4px rgba(0,0,0,0.90)!important;}
.meal-label span{text-shadow:0 1px 4px rgba(0,0,0,0.90)!important;}
/* Water card */
.water-card{background:rgba(0,0,0,0.78)!important;
  border:1.5px solid rgba(96,165,250,0.45)!important;}
/* Feature cards */
.feature-card{background:rgba(0,0,0,0.78)!important;
  border:1.5px solid rgba(255,255,255,0.20)!important;}
/* Right column nutrition card */
div[data-testid="stVerticalBlock"] > div > div > div[style*="rgba(0,0,0,0.45)"]{
  background:rgba(0,0,0,0.80)!important;}
/* General text contrast */
html,body,.stApp,.stMarkdown,p,div,span{
  text-shadow:0 1px 3px rgba(0,0,0,0.80)!important;}
/* Checkbox label */
.stCheckbox>label{color:#fff!important;font-weight:600!important;
  text-shadow:0 1px 4px rgba(0,0,0,0.90)!important;}
/* Section labels */
.feature-card-title{color:rgba(229,9,20,0.95)!important;
  text-shadow:0 1px 4px rgba(0,0,0,0.90)!important;}
/* Grocery list items */
.feature-card div[style*="border-bottom"]{
  color:#fff!important;font-weight:500!important;}
/* Tab text */
.stTabs [data-baseweb="tab"]{color:rgba(255,255,255,0.75)!important;
  text-shadow:0 1px 3px rgba(0,0,0,0.80)!important;}
/* ── GLASSY INPUTS ─────────────────────────────────────────────────────────── */
.stNumberInput>div>div>input,
.stTextInput>div>div>input,
.stTextArea>div>div>textarea {
  background:rgba(0,0,0,0.75)!important;
  border:1.5px solid rgba(255,255,255,0.22)!important;
  color:#fff!important;border-radius:14px!important;
  backdrop-filter:blur(12px)!important;
  box-shadow:0 2px 12px rgba(0,0,0,0.30)!important;}
.stNumberInput>div>div>input:focus,
.stTextInput>div>div>input:focus {
  border-color:rgba(229,9,20,0.60)!important;
  background:rgba(255,255,255,0.12)!important;
  box-shadow:0 0 0 3px rgba(229,9,20,0.15)!important;}
.stNumberInput [data-testid="stNumberInputStepUp"],
.stNumberInput [data-testid="stNumberInputStepDown"] {
  background:rgba(229,9,20,0.22)!important;border:none!important;
  color:#fff!important;border-radius:8px!important;}
[data-baseweb="select"]>div {
  background:rgba(0,0,0,0.75)!important;
  border:1.5px solid rgba(255,255,255,0.22)!important;
  border-radius:14px!important;backdrop-filter:blur(12px)!important;color:#fff!important;}
[data-baseweb="select"] span,[data-baseweb="select"] div{color:#fff!important;}
[data-baseweb="popover"] [role="option"]{background:rgba(5,20,8,0.97)!important;color:#fff!important;}
[data-baseweb="popover"] [role="option"]:hover{background:rgba(34,197,94,0.18)!important;}
/* Checkbox */
.stCheckbox>label{color:#fff!important;font-weight:500!important;}
[data-testid="stWidgetLabel"] p{color:rgba(255,255,255,0.82)!important;font-weight:600!important;}
</style>""", unsafe_allow_html=True)

# Apply background image via bg_utils
_overlay_map = {
    "nonveg": "rgba(40,15,4,0.52)",
    "both":   "rgba(20,35,8,0.52)",
    "veg":    "rgba(0,30,5,0.52)",
}
apply_bg(bg_url, overlay=_overlay_map.get(dietary_type, "rgba(0,0,0,0.48)"))

# NAV
st.markdown("<div style='padding:8px 0;margin-bottom:16px'>", unsafe_allow_html=True)
_n = st.columns([1.6,1,1,1,1,1,1,1.2])
with _n[0]: st.markdown("<div class='nav-logo-txt'>&#9889; FITPLAN PRO</div>", unsafe_allow_html=True)
with _n[1]:
    if st.button("Home",    key="dp_db", use_container_width=True): st.switch_page("pages/2_Dashboard.py")
with _n[2]:
    if st.button("Workout", key="dp_wp", use_container_width=True): st.switch_page("pages/3_Workout_Plan.py")
with _n[3]:
    if st.button("Diet",    key="dp_dp", use_container_width=True): st.switch_page("pages/4_Diet_Plan.py")
with _n[4]:
    if st.button("AI Coach",key="dp_ai", use_container_width=True):
        try: st.switch_page("pages/5_ai_coach.py")
        except Exception as e: st.warning(str(e))
with _n[5]:
    if st.button("Records", key="dp_rc", use_container_width=True):
        try: st.switch_page("pages/6_records.py")
        except Exception as e: st.warning(str(e))
with _n[6]:
    if st.button("Photos",  key="dp_ph", use_container_width=True):
        try: st.switch_page("pages/7_progress_photos.py")
        except Exception as e: st.warning(str(e))
with _n[7]:
    if st.button("Sign Out",key="dp_so", use_container_width=True):
        logout(uname)
        for _k in ["logged_in","username","auth_token","user_data","workout_plan","structured_days",
                   "dietary_type","full_plan_data","plan_id","plan_start","plan_duration","plan_for",
                   "force_regen","tracking","_plan_checked","_db_loaded_dash","_auto_redirect",
                   "_diet_chosen","_needs_rerun","_db_streak","edit_profile_mode"]:
            st.session_state.pop(_k, None)
        st.switch_page("app.py")
st.markdown("</div>", unsafe_allow_html=True)

# HERO
diet_icons = {"veg":"&#127807;","nonveg":"&#127829;","both":"&#127807;&#127829;"}
diet_names = {"veg":"Vegetarian","nonveg":"Non-Vegetarian","both":"Flexible"}
d_icon = diet_icons.get(dietary_type, "&#127807;")
d_name = diet_names.get(dietary_type, "Vegetarian")
uname_up = uname.upper()
st.markdown(
    "<div style='background:rgba(0,0,0,0.55);border:1.5px solid rgba(" + accent_rgb + ",0.40);"
    "border-radius:20px;padding:28px 36px;margin-bottom:20px;backdrop-filter:blur(14px);"
    "position:relative;overflow:hidden'>"
    "<div style='position:absolute;top:0;left:0;right:0;height:2px;"
    "background:linear-gradient(90deg,transparent," + accent + ",transparent)'></div>"
    "<div style='font-size:0.72rem;font-weight:700;letter-spacing:4px;text-transform:uppercase;"
    "color:rgba(" + accent_rgb + ",0.80);margin-bottom:8px'>" + d_icon + " Personalised Nutrition Plan</div>"
    "<div style='font-family:Barlow Condensed,sans-serif;font-size:clamp(1.8rem,4vw,3rem);"
    "font-weight:900;text-transform:uppercase;color:#fff;line-height:1;margin-bottom:10px'>"
    + uname_up + "'s <span style=\"color:" + accent + "\">Diet Plan</span></div>"
    "<div style='font-size:0.82rem;color:rgba(255,255,255,0.90)'>"
    + d_name + " meal plan for " + str(len(sdays)) + " days</div>"
    "</div>",
    unsafe_allow_html=True
)

if not sdays:
    st.markdown(
        "<div style='text-align:center;padding:60px 20px'>"
        "<div style='font-size:3rem;margin-bottom:14px'>🥗</div>"
        "<div style='font-family:Bebas Neue,sans-serif;font-size:1.8rem;color:#E50914;"
        "letter-spacing:2px;margin-bottom:8px'>No Plan Found</div>"
        "<div style='font-size:0.85rem;color:rgba(255,255,255,0.90);margin-bottom:24px'>"
        "Generate your personalised plan first from the Profile page.</div>"
        "</div>",
        unsafe_allow_html=True
    )
    if st.button("👤 Go to Profile", use_container_width=False):
        st.switch_page("pages/1_Profile.py")
    st.stop()

# Make sure dietary_type is always set
if not st.session_state.get("dietary_type"):
    st.session_state.dietary_type = "veg"
    dietary_type = "veg"

# WATER TRACKER
water_key = "water_" + uname + "_" + today_str
if water_key not in st.session_state:
    try:
        from utils.db import get_water as get_water_intake
        st.session_state[water_key] = get_water_intake(uname, today_str)
    except Exception:
        st.session_state[water_key] = 0

glasses   = st.session_state[water_key]
goal_w    = 8
pct_w     = min(int(glasses / goal_w * 100), 100)
fill_col  = "#22c55e" if glasses >= goal_w else "#60a5fa"

glass_html = ""
for gi in range(goal_w):
    filled = gi < glasses
    bg  = "rgba(34,197,94,0.35)" if filled else "rgba(255,255,255,0.06)"
    brd = "rgba(34,197,94,0.70)" if filled else "rgba(255,255,255,0.18)"
    ico = "&#128167;" if filled else ""
    glass_html += ("<div style='width:38px;height:50px;border-radius:4px 4px 10px 10px;"
                   "border:2px solid " + brd + ";background:" + bg + ";"
                   "display:flex;align-items:center;justify-content:center;font-size:1.1rem'>"
                   + ico + "</div>")

st.markdown("<div style='font-size:0.72rem;font-weight:700;letter-spacing:3px;text-transform:uppercase;"
            "color:rgba(229,9,20,0.75);margin:16px 0 8px;display:flex;align-items:center;gap:8px'>"
            "<span style='width:16px;height:1.5px;background:#E50914;display:block'></span>"
            "Water Intake Tracker</div>", unsafe_allow_html=True)

st.markdown(
    "<div class='water-card'>"
    "<div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:12px'>"
    "<div><div style='font-size:0.72rem;font-weight:700;letter-spacing:3px;text-transform:uppercase;"
    "color:rgba(96,165,250,0.85)'>Today&#39;s Water Intake</div>"
    "<div style='font-size:0.78rem;color:rgba(255,255,255,0.90);margin-top:2px'>"
    "Goal: 8 glasses &middot; " + today_str + "</div></div>"
    "<div style='font-family:Bebas Neue,sans-serif;font-size:2.4rem;color:" + fill_col + ";letter-spacing:2px'>"
    + str(glasses) + "<span style='font-size:1.1rem;color:rgba(255,255,255,0.90)'>/" + str(goal_w) + "</span></div>"
    "</div>"
    "<div style='display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap'>" + glass_html + "</div>"
    "<div style='height:5px;background:rgba(255,255,255,0.10);border-radius:3px;overflow:hidden'>"
    "<div style='height:100%;width:" + str(pct_w) + "%;background:linear-gradient(90deg,#60a5fa,#2563eb);border-radius:3px'></div>"
    "</div>"
    + ("<div style='margin-top:8px;font-size:0.78rem;font-weight:700;color:#22c55e'>&#127881; Daily goal reached! Well done!</div>" if glasses >= goal_w else "") +
    "</div>",
    unsafe_allow_html=True
)
wc1, wc2, _ = st.columns([2,2,6])
with wc1:
    if st.button("+ 1 Glass", key="water_add", use_container_width=True):
        st.session_state[water_key] = min(glasses+1, 20)
        try:
            from utils.db import save_water as save_water_intake
            save_water_intake(uname, today_str, st.session_state[water_key])
        except Exception: pass
        st.rerun()
with wc2:
    if glasses > 0 and st.button("Undo", key="water_undo", use_container_width=True):
        st.session_state[water_key] = max(glasses-1, 0)
        try:
            from utils.db import save_water as save_water_intake
            save_water_intake(uname, today_str, st.session_state[water_key])
        except Exception: pass
        st.rerun()

# FEATURE CARDS — collapsible expanders
import re as _re, json as _json
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
fe1, fe2, fe3 = st.columns(3)

with fe1:
    with st.expander("&#128722;  Grocery List — Next 7 Days", expanded=False):
        all_items = set()
        for sd in sdays[:7]:
            for meal_txt in sd.get("dietary", {}).values():
                if not meal_txt: continue
                words = _re.findall(r'\b[A-Z][a-zA-Z]{3,}\b', meal_txt)
                stopwords = {"With","Your","From","This","That","Have","Will","Each","Slices","Tbsp","Cups","Grams","Steamed","Grilled","Cooked","Mixed","Fresh"}
                for w in words:
                    if w not in stopwords: all_items.add(w)
        if all_items:
            sorted_items = sorted(all_items)[:20]
            # Feature #4: interactive checkable grocery list
            st.markdown("<div style='font-size:0.65rem;color:rgba(255,255,255,0.90);margin-bottom:8px'>&#10003; Tap to cross off while shopping</div>", unsafe_allow_html=True)
            for item in sorted_items:
                g_key = f"grocery_{uname}_{item}"
                checked = st.session_state.get(g_key, False)
                strike  = "text-decoration:line-through;opacity:0.40;" if checked else ""
                col_item, col_check = st.columns([5,1])
                with col_item:
                    st.markdown(
                        "<div style='display:flex;align-items:center;gap:10px;padding:5px 4px;"
                        "border-bottom:1px solid rgba(255,255,255,0.08);font-size:0.85rem;"
                        "color:#fff;font-weight:500;" + strike + "'>&#128722; " + item + "</div>",
                        unsafe_allow_html=True
                    )
                with col_check:
                    if st.checkbox("", value=checked, key=g_key+"_cb", label_visibility="collapsed"):
                        st.session_state[g_key] = True
                    else:
                        st.session_state[g_key] = False
            # Clear all button
            if any(st.session_state.get(f"grocery_{uname}_{i}", False) for i in sorted_items):
                if st.button("Clear all ✓", key="grocery_clear", use_container_width=True):
                    for i in sorted_items:
                        st.session_state[f"grocery_{uname}_{i}"] = False
                    st.rerun()
        else:
            st.markdown("<div style='color:rgba(255,255,255,0.90);font-size:0.82rem;padding:8px 0'>"
                        "Generate a plan first to see your grocery list.</div>", unsafe_allow_html=True)

with fe2:
    with st.expander("&#128138;  Supplement Guide", expanded=False):
        # Fix #12: load from DB first
        supp_key = "supp_" + uname
        if not st.session_state.get(supp_key):
            try:
                from utils.db import get_user_setting
                _db_supp = get_user_setting(uname, "supplement_guide")
                if _db_supp: st.session_state[supp_key] = _db_supp
            except Exception: pass
        if not st.session_state.get(supp_key):
            if st.button("Get AI Guide", key="supp_btn", use_container_width=True):
                with st.spinner("Generating..."):
                    try:
                        from model_api import query_model
                        prompt = ("List 5 supplements for a " + data.get("level","Beginner")
                                  + " person, goal: " + data.get("goal","Fitness")
                                  + ". Format each as: NAME: dosage — benefit. Plain text, no JSON, no brackets.")
                        raw = query_model(prompt, max_tokens=250).strip()
                        st.session_state[supp_key] = raw
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
        else:
            raw_supp = st.session_state[supp_key]
            lines = []
            try:
                parsed = _json.loads(raw_supp) if raw_supp.strip().startswith("[") else None
                if parsed:
                    for item in parsed:
                        if isinstance(item, dict):
                            for k, v in item.items():
                                lines.append((k.strip(), v.strip()))
            except Exception:
                parsed = None
            if not parsed:
                for line in raw_supp.splitlines():
                    line = line.strip().lstrip("-*1234567890. ")
                    if not line: continue
                    if ":" in line:
                        parts = line.split(":", 1)
                        lines.append((parts[0].strip(), parts[1].strip()))
                    else:
                        lines.append(("", line))
            for name, desc in lines[:5]:
                st.markdown(
                    "<div style='padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.10)'>"
                    + ("<b style='color:#E50914;font-size:0.85rem'>" + name + "</b><br>" if name else "")
                    + "<span style='font-size:0.82rem;color:#fff;line-height:1.5'>" + desc + "</span></div>",
                    unsafe_allow_html=True
                )
            if st.button("Refresh", key="supp_refresh"):
                st.session_state.pop(supp_key, None)
                st.rerun()

with fe3:
    with st.expander("&#128200;  Weekly Adherence", expanded=False):
        done_m = 0; total_m = 0
        for i, sd in enumerate(sdays[:7]):
            dn = sd.get("day", i+1)
            for meal in sd.get("dietary", {}):
                total_m += 1
                if st.session_state.get("meal_d" + str(dn) + "_" + meal, False):
                    done_m += 1
        adh   = int(done_m / max(total_m, 1) * 100)
        col_a = "#22c55e" if adh >= 70 else ("#fbbf24" if adh >= 40 else "#ef4444")
        st.markdown(
            "<div style='text-align:center;padding:8px 0'>"
            "<div style='font-family:Bebas Neue,sans-serif;font-size:3.5rem;color:" + col_a + ";line-height:1'>"
            + str(adh) + "%</div>"
            "<div style='font-size:0.78rem;color:#fff;margin-top:6px;font-weight:600'>Weekly Diet Adherence</div>"
            "<div style='font-size:0.72rem;color:rgba(255,255,255,0.70);margin-top:4px'>"
            + str(done_m) + " of " + str(total_m) + " meals tracked</div>"
            "<div class='prog-bar-bg' style='margin-top:10px'>"
            "<div style='height:100%;width:" + str(adh) + "%;background:" + col_a + ";border-radius:3px'></div>"
            "</div></div>",
            unsafe_allow_html=True
        )

# DAY TABS
st.markdown("<div style='font-size:0.72rem;font-weight:700;letter-spacing:3px;text-transform:uppercase;"
            "color:rgba(229,9,20,0.75);margin:20px 0 10px;display:flex;align-items:center;gap:8px'>"
            "<span style='width:16px;height:1.5px;background:#E50914;display:block'></span>"
            "Your Meal Plan by Day</div>", unsafe_allow_html=True)

MEAL_ICONS = {"breakfast":"&#127773;","lunch":"&#9728;&#65039;","dinner":"&#127769;","snacks":"&#127822;"}

tab_labels = ["Day " + str(d.get("day",i+1)) + (" &#128564;" if d.get("is_rest_day") else "")
              for i,d in enumerate(sdays)]
tabs = st.tabs(tab_labels)

for tab, day_data in zip(tabs, sdays):
    with tab:
        dn      = day_data.get("day", 1)
        dietary = day_data.get("dietary", {})
        is_rest = day_data.get("is_rest_day", False)
        mg      = day_data.get("muscle_group", "Full Body")
        total_meals = len([m for m,v in dietary.items() if v])
        done_meals  = sum(1 for m in dietary if st.session_state.get("meal_d"+str(dn)+"_"+m, False))
        pct_m       = int(done_meals / max(total_meals,1) * 100)

        hdr, pct_col = st.columns([4,1])
        with hdr:
            tag = "REST DAY" if is_rest else ("DAILY NUTRITION &mdash; " + mg.upper())
            st.markdown("<div style='font-size:0.72rem;font-weight:700;letter-spacing:3px;text-transform:uppercase;"
                        "color:" + accent + ";margin-bottom:8px'>" + tag + "</div>", unsafe_allow_html=True)
        with pct_col:
            st.markdown("<div style='text-align:right;font-size:0.78rem;font-weight:700;color:" + accent + ";padding-top:2px'>"
                        + str(done_meals) + "/" + str(total_meals) + " &middot; " + str(pct_m) + "%</div>",
                        unsafe_allow_html=True)

        left_col, right_col = st.columns([3,2])

        with left_col:
            if not dietary:
                st.markdown("<div style='color:rgba(255,255,255,0.90);font-size:0.82rem;padding:20px;text-align:center'>No meals for this day.</div>", unsafe_allow_html=True)
            else:
                for meal, desc in dietary.items():
                    if not desc: continue
                    icon  = MEAL_ICONS.get(meal, "&#127869;&#65039;")
                    ck    = "meal_d" + str(dn) + "_" + meal
                    done  = st.session_state.get(ck, False)
                    strike = "text-decoration:line-through;opacity:0.40;" if done else ""

                    # Each meal card with its own swap button
                    mc_top, mc_btn = st.columns([4,1])
                    with mc_top:
                        st.markdown(
                            "<div class='meal-card'>"
                            "<div class='meal-label'>"
                            "<span style='color:" + accent + "'>" + icon + " " + meal.upper() + "</span>"
                            + (" <span style='color:" + accent + ";font-size:0.75rem'>&#10003; Done</span>" if done else "") +
                            "</div>"
                            "<div class='meal-text' style='" + strike + "'>" + str(desc) + "</div>"
                            "</div>",
                            unsafe_allow_html=True
                        )
                    with mc_btn:
                        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
                        st.markdown("<div class='swap-mini'>", unsafe_allow_html=True)
                        if st.button("&#129302; Swap", key="swap_" + str(dn) + "_" + meal, use_container_width=True):
                            with st.spinner("Getting swap..."):
                                try:
                                    from model_api import query_model
                                    d_label = {"veg":"Vegetarian","nonveg":"Non-Vegetarian","both":"Flexible"}.get(dietary_type,"")
                                    prompt = ("Suggest 1 alternative " + meal + " meal for a " + d_label
                                              + " person (goal: " + data.get("goal","Fitness")
                                              + "). Current meal: " + str(desc)
                                              + ". Give only the meal name and ingredients in 1-2 lines. No JSON.")
                                    result = query_model(prompt, max_tokens=80)
                                    st.session_state["swap_result_" + str(dn) + "_" + meal] = result.strip()
                                    st.rerun()
                                except Exception as e:
                                    st.error(str(e))
                        st.markdown("</div>", unsafe_allow_html=True)

                    # Show swap options: original vs AI alternative
                    swap_res = st.session_state.get("swap_result_" + str(dn) + "_" + meal)
                    chosen_key = "meal_choice_" + str(dn) + "_" + meal
                    if swap_res:
                        chosen = st.session_state.get(chosen_key, "original")
                        st.markdown(
                            "<div style='background:rgba(0,0,0,0.70);border:1px solid rgba(255,255,255,0.18);"
                            "border-radius:12px;padding:12px 14px;margin-bottom:8px;backdrop-filter:blur(10px)'>"
                            "<div style='font-size:0.72rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;"
                            "color:rgba(229,9,20,0.85);margin-bottom:8px'>&#129302; Choose Your " + meal.title() + "</div>"
                            "<div style='display:flex;gap:8px;flex-wrap:wrap'>"
                            # Original option
                            "<div style='flex:1;min-width:140px;background:" + ("rgba(229,9,20,0.25);border:2px solid #E50914" if chosen=="original" else "rgba(255,255,255,0.07);border:1.5px solid rgba(255,255,255,0.15)") + ";"
                            "border-radius:10px;padding:10px 12px;cursor:pointer'>"
                            "<div style='font-size:0.72rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;"
                            "color:" + ("rgba(229,9,20,0.90)" if chosen=="original" else "rgba(255,255,255,0.45)") + ";margin-bottom:4px'>&#127775; Original</div>"
                            "<div style='font-size:0.80rem;color:#fff;line-height:1.5'>" + str(desc) + "</div>"
                            "</div>"
                            # AI swap option
                            "<div style='flex:1;min-width:140px;background:" + ("rgba(34,197,94,0.20);border:2px solid #22c55e" if chosen=="swap" else "rgba(255,255,255,0.07);border:1.5px solid rgba(255,255,255,0.15)") + ";"
                            "border-radius:10px;padding:10px 12px;cursor:pointer'>"
                            "<div style='font-size:0.72rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;"
                            "color:" + ("rgba(34,197,94,0.90)" if chosen=="swap" else "rgba(255,255,255,0.45)") + ";margin-bottom:4px'>&#129302; AI Alternative</div>"
                            "<div style='font-size:0.80rem;color:#fff;line-height:1.5'>" + swap_res + "</div>"
                            "</div>"
                            "</div></div>",
                            unsafe_allow_html=True
                        )
                        # Buttons to pick one
                        pick1, pick2, pick3 = st.columns([2,2,1])
                        with pick1:
                            btn_style1 = "background:rgba(229,9,20,0.85)" if chosen=="original" else ""
                            if st.button(
                                ("&#10003; Original" if chosen=="original" else "Keep Original"),
                                key="pick_orig_" + str(dn) + "_" + meal,
                                use_container_width=True
                            ):
                                st.session_state[chosen_key] = "original"
                                st.rerun()
                        with pick2:
                            if st.button(
                                ("&#10003; AI Swap" if chosen=="swap" else "Use AI Swap"),
                                key="pick_swap_" + str(dn) + "_" + meal,
                                use_container_width=True
                            ):
                                st.session_state[chosen_key] = "swap"
                                st.rerun()
                        with pick3:
                            if st.button("&#10005;", key="dismiss_swap_" + str(dn) + "_" + meal, use_container_width=True):
                                st.session_state.pop("swap_result_" + str(dn) + "_" + meal, None)
                                st.session_state.pop(chosen_key, None)
                                st.rerun()
                        # Show which is active
                        if chosen == "swap":
                            st.markdown(
                                "<div style='font-size:0.72rem;color:rgba(34,197,94,0.85);font-weight:600;"
                                "padding:4px 0'>&#129302; AI Alternative selected for today</div>",
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                "<div style='font-size:0.72rem;color:rgba(229,9,20,0.75);padding:4px 0'>"
                                "&#127775; Original meal selected</div>",
                                unsafe_allow_html=True
                            )

                    # Checkbox
                    if st.checkbox("Mark as done", value=done, key=ck+"_cb"):
                        if not done:
                            st.session_state[ck] = True
                            if plan_id:
                                try:
                                    from utils.db import save_progress
                                    dc_ = {m2: st.session_state.get("meal_d"+str(dn)+"_"+m2,False)
                                           for m2 in ["breakfast","lunch","dinner","snacks"]}
                                    save_progress(uname, plan_id, dn, {}, dc_)
                                except Exception: pass
                            st.rerun()

        with right_col:
            # Nutrition summary
            cal_map  = {"breakfast":420,"lunch":620,"dinner":560,"snacks":190}
            prot_map = {"breakfast":28,"lunch":42,"dinner":38,"snacks":10}
            total_cal  = sum(cal_map.get(m,0) for m in dietary if dietary.get(m))
            total_prot = sum(prot_map.get(m,0) for m in dietary if dietary.get(m))

            st.markdown(
                "<div style='background:rgba(0,0,0,0.45);border:1.5px solid rgba(255,255,255,0.12);"
                "border-radius:14px;padding:16px 18px;margin-bottom:12px;backdrop-filter:blur(10px)'>"
                "<div class='feature-card-title'>Nutrition Summary</div>"
                "<div style='display:grid;grid-template-columns:1fr 1fr;gap:8px'>"
                "<div style='background:rgba(229,9,20,0.12);border-radius:10px;padding:12px;text-align:center'>"
                "<div style='font-family:Bebas Neue,sans-serif;font-size:2rem;color:#E50914'>" + str(total_cal) + "</div>"
                "<div style='font-size:0.72rem;color:rgba(255,255,255,0.80);letter-spacing:2px;text-transform:uppercase;font-weight:600'>Calories</div></div>"
                "<div style='background:rgba(96,165,250,0.12);border-radius:10px;padding:12px;text-align:center'>"
                "<div style='font-family:Bebas Neue,sans-serif;font-size:2rem;color:#60a5fa'>" + str(total_prot) + "g</div>"
                "<div style='font-size:0.72rem;color:rgba(255,255,255,0.80);letter-spacing:2px;text-transform:uppercase;font-weight:600'>Protein</div></div>"
                "</div>"
                "<div class='prog-bar-bg' style='margin-top:12px'>"
                "<div style='height:100%;width:" + str(pct_m) + "%;background:" + accent + ";border-radius:3px'></div></div>"
                "<div style='font-size:0.68rem;color:rgba(255,255,255,0.90);margin-top:4px;text-align:right'>"
                + str(done_meals) + "/" + str(total_meals) + " meals done</div>"
                "</div>",
                unsafe_allow_html=True
            )