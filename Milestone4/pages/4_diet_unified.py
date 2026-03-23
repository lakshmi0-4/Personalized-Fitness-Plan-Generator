# -*- coding: utf-8 -*-
"""
pages/4_diet_unified.py
Replaces 4a_veg_diet.py, 4b_nonveg_diet.py, 4c_both_diet.py AND 4_Diet_Plan.py.
Contains EVERY feature from all four files:
  - Themed background, accent colour, logo per diet type (from 4a/4b/4c)
  - Water tracker (from 4_Diet_Plan)
  - Grocery list with cross-off (from 4_Diet_Plan)
  - AI supplement guide (from 4_Diet_Plan)
  - Weekly adherence (from 4_Diet_Plan)
  - AI meal swap with original vs AI choice (from 4_Diet_Plan)
  - Nutrition summary per day (from 4_Diet_Plan)
  - Nutrition tips sidebar (from 4a/4b/4c)
  - Two-way checkboxes (FIX)
  - AI swap persists to structured_days (FIX)
  - Shared nav (FIX)
  - Font sizes fixed (FIX)
  - Estimated calorie disclaimer (FIX)
  - Better grocery stopwords (FIX)
"""
import streamlit as st
import os, sys, json as _json, re as _re
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bg_utils import apply_bg

st.set_page_config(
    page_title="FitPlan Pro - Diet Plan", page_icon="🥗",
    layout="wide", initial_sidebar_state="collapsed"
)
if not st.session_state.get("logged_in"):     st.switch_page("app.py")
if "user_data" not in st.session_state:        st.switch_page("pages/1_Profile.py")

uname        = st.session_state.get("username", "Athlete")
data         = st.session_state.user_data
sdays        = st.session_state.get("structured_days", [])
plan_id      = st.session_state.get("plan_id", "")
today_str    = date.today().isoformat()
dietary_type = st.session_state.get("dietary_type", "veg")
if not dietary_type:
    dietary_type = "veg"
    st.session_state.dietary_type = "veg"

# ══════════════════════════════════════════════════════════════════════════════
# THEME CONFIG — all three diet types in one place
# ══════════════════════════════════════════════════════════════════════════════
THEME = {
    "veg": {
        "icon": "🥦", "label": "Vegetarian",
        "accent": "#22c55e", "rgb": "34,197,94",
        "logo_color": "#22c55e", "logo_glow": "rgba(34,197,94,0.60)",
        "bg_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=1800&q=80&auto=format&fit=crop",
        "overlay": "rgba(0,30,5,0.52)",
        "tab_bg": "rgba(6,30,15,0.80)",
        "tips": [
            "💧 Drink 2–3 litres of water daily",
            "⏰ Eat every 3–4 hours to maintain energy",
            "🥦 Include protein in every meal (dal, paneer, tofu)",
            "☀️ Eat your largest meal at lunch",
            "🌈 Add colour to your plate — eat the rainbow",
            "🚫 Avoid processed foods and refined sugar",
            "💪 Pair carbs with protein for better absorption",
        ],
    },
    "nonveg": {
        "icon": "🍗", "label": "Non-Vegetarian",
        "accent": "#f97316", "rgb": "249,115,22",
        "logo_color": "#f97316", "logo_glow": "rgba(249,115,22,0.60)",
        "bg_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1800&q=80&auto=format&fit=crop",
        "overlay": "rgba(40,15,4,0.52)",
        "tab_bg": "rgba(40,15,4,0.80)",
        "tips": [
            "💧 Drink 3 litres of water daily — protein needs hydration",
            "🥩 Eat lean protein within 30 mins post workout",
            "🍳 Grill or bake — avoid deep frying",
            "🥦 Include 2–3 servings of vegetables per meal",
            "⏰ Space meals 3–4 hours apart for metabolism",
            "🐟 Choose fish twice a week for omega-3",
            "🔴 Limit red meat to 2–3 times per week",
        ],
    },
    "both": {
        "icon": "🌿🍗", "label": "Flexible",
        "accent": "#facc15", "rgb": "250,204,21",
        "logo_color": "#facc15", "logo_glow": "rgba(250,204,21,0.55)",
        "bg_url": "https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=1800&q=80&auto=format&fit=crop",
        "overlay": "rgba(20,35,8,0.52)",
        "tab_bg": "rgba(20,35,8,0.80)",
        "tips": [
            "💧 Drink 2.5–3 litres of water daily",
            "🥦 Fill half your plate with vegetables",
            "🌿🍗 Alternate veg & non-veg days for variety",
            "⏰ Eat every 3–4 hours to keep metabolism active",
            "🚫 Limit processed foods and refined carbs",
            "🥩 Post-workout: lean protein within 30 mins",
            "🍎 Snack on fruits, nuts, and yoghurt",
        ],
    },
}

cfg    = THEME.get(dietary_type, THEME["veg"])
accent = cfg["accent"]
rgb    = cfg["rgb"]

# Inject background image directly — same method as 4_Diet_Plan.py (proven to work)
_bg_url = cfg["bg_url"]
st.markdown(
    "<style>"
    "html,body,.stApp{background:#050202!important;color:#fff!important;}"
    "[data-testid='stAppViewContainer']::before{"
    "content:'';position:fixed;inset:0;z-index:0;"
    "background:url('" + _bg_url + "') center center/cover no-repeat;"
    "filter:blur(8px) brightness(0.25) saturate(0.55);"
    "transform:scale(1.06);}"
    "[data-testid='stAppViewContainer']{"
    "background:linear-gradient(160deg,rgba(3,1,0,0.88) 0%,rgba(4,2,0,0.80) 50%,rgba(3,1,0,0.92) 100%)!important;"
    "position:relative;}"
    "[data-testid='stAppViewContainer']>section>div.block-container{"
    "position:relative;z-index:2;}"
    "</style>", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@700;800;900&family=DM+Sans:opsz,wght@9..40,400;9..40,600;9..40,700&display=swap');
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stSidebarNav"],[data-testid="collapsedControl"],
section[data-testid="stSidebar"],button[kind="header"]{{display:none!important;}}
html,body,.stApp{{background-color:transparent!important;color:#fff!important;font-family:'DM Sans',sans-serif!important;}}
[data-testid="stAppViewContainer"]>section>div.block-container{{
  max-width:1200px!important;margin:0 auto!important;padding:0 32px 80px!important;background:transparent!important;}}
[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] p{{color:rgba(255,255,255,0.80)!important;}}

/* Content buttons — themed accent colour */
.stButton>button{{
  background:linear-gradient(135deg,{accent},rgba({rgb},0.80))!important;
  border:none!important;color:#fff!important;border-radius:8px!important;
  font-family:'DM Sans',sans-serif!important;font-size:1.00rem!important;font-weight:700!important;
  box-shadow:0 4px 16px rgba({rgb},0.35)!important;transition:all 0.20s!important;}}
.stButton>button:hover{{transform:translateY(-2px)!important;box-shadow:0 6px 24px rgba({rgb},0.60)!important;}}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{{
  background:{cfg["tab_bg"]}!important;border-radius:10px!important;
  padding:4px!important;border:1px solid rgba({rgb},0.25)!important;}}
.stTabs [data-baseweb="tab"]{{
  background:transparent!important;color:rgba(255,255,255,0.90)!important;
  border-radius:7px!important;font-size:0.75rem!important;font-weight:600!important;padding:8px 14px!important;}}
.stTabs [aria-selected="true"]{{
  background:linear-gradient(135deg,{accent},rgba({rgb},0.75))!important;
  color:#fff!important;box-shadow:0 3px 12px rgba({rgb},0.50)!important;}}
.stCheckbox>label{{color:#fff!important;font-weight:500!important;}}

/* Expanders */
.stExpander{{
  background:rgba(0,0,0,0.65)!important;border:1.5px solid rgba(255,255,255,0.18)!important;
  border-radius:14px!important;backdrop-filter:blur(30px)!important;}}
.stExpander:hover{{border-color:rgba({rgb},0.45)!important;}}
.stExpander details summary{{color:#fff!important;font-weight:700!important;font-size:1.05rem!important;padding:14px 18px!important;}}
.stExpander details summary:hover,.stExpander details[open] summary{{color:{accent}!important;}}

/* Swap mini button */
.swap-mini .stButton>button{{
  background:rgba({rgb},0.15)!important;border:1px solid rgba({rgb},0.40)!important;
  color:rgba(255,255,255,0.85)!important;font-size:0.65rem!important;font-weight:700!important;
  padding:3px 10px!important;height:auto!important;border-radius:6px!important;
  box-shadow:none!important;text-transform:uppercase!important;letter-spacing:0.5px!important;}}
.swap-mini .stButton>button:hover{{background:rgba({rgb},0.35)!important;transform:none!important;}}

/* Water card */
.water-card{{
  background:rgba(0,0,0,0.78)!important;border:1.5px solid rgba(96,165,250,0.45)!important;
  border-radius:16px;padding:18px 22px;margin-bottom:16px;backdrop-filter:blur(28px);}}

/* Meal card */
.meal-card{{
  background:rgba(0,0,0,0.78)!important;border:1.5px solid rgba({rgb},0.28)!important;
  border-radius:14px;padding:16px 20px;margin-bottom:10px;
  position:relative;overflow:hidden;backdrop-filter:blur(28px);}}
.meal-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,rgba({rgb},0.60),transparent);}}
.meal-label{{
  font-size:0.85rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;
  color:rgba({rgb},0.90);margin-bottom:8px;display:flex;align-items:center;justify-content:space-between;}}
.meal-text{{color:#fff!important;font-size:0.92rem!important;line-height:1.65;
  text-shadow:0 1px 4px rgba(0,0,0,0.90)!important;}}

/* Tip card */
.tip-card{{
  background:rgba(0,0,0,0.60);border:1px solid rgba({rgb},0.22);
  border-radius:10px;padding:10px 14px;margin-bottom:8px;
  font-size:1.00rem;color:rgba(255,255,255,0.75);}}

/* Feature cards */
.feature-card{{
  background:rgba(0,0,0,0.78)!important;border:1.5px solid rgba(255,255,255,0.20)!important;
  border-radius:14px;padding:20px 18px;height:100%;backdrop-filter:blur(28px);transition:border-color 0.2s;}}
.feature-card:hover{{border-color:rgba({rgb},0.45);}}
.feature-card-title{{
  font-size:0.85rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;
  color:rgba({rgb},0.90)!important;margin-bottom:12px;}}

/* Progress bar */
.prog-bar-bg{{height:5px;background:rgba(255,255,255,0.10);border-radius:3px;overflow:hidden;margin-top:6px;}}
.prog-bar-fill{{height:100%;background:linear-gradient(90deg,{accent},rgba({rgb},0.70));border-radius:3px;}}

/* Glassy inputs */
.stNumberInput>div>div>input,.stTextInput>div>div>input,.stTextArea>div>div>textarea{{
  background:rgba(0,0,0,0.75)!important;border:1.5px solid rgba(255,255,255,0.22)!important;
  color:#fff!important;border-radius:14px!important;backdrop-filter:blur(28px)!important;
  box-shadow:0 2px 12px rgba(0,0,0,0.30)!important;}}
.stNumberInput>div>div>input:focus,.stTextInput>div>div>input:focus{{
  border-color:rgba({rgb},0.60)!important;background:rgba(255,255,255,0.12)!important;
  box-shadow:0 0 0 3px rgba({rgb},0.15)!important;}}
.stNumberInput [data-testid="stNumberInputStepUp"],
.stNumberInput [data-testid="stNumberInputStepDown"]{{
  background:rgba({rgb},0.22)!important;border:none!important;color:#fff!important;border-radius:8px!important;}}
[data-baseweb="select"]>div{{
  background:rgba(0,0,0,0.75)!important;border:1.5px solid rgba(255,255,255,0.22)!important;
  border-radius:14px!important;backdrop-filter:blur(28px)!important;color:#fff!important;}}
[data-baseweb="select"] span,[data-baseweb="select"] div{{color:#fff!important;}}
[data-baseweb="popover"] [role="option"]{{background:rgba(5,5,5,0.97)!important;color:#fff!important;}}
[data-baseweb="popover"] [role="option"]:hover{{background:rgba({rgb},0.18)!important;}}

/* Nav */
div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stButton"] > button{{
  background:rgba(18,4,4,0.82)!important;border:1.5px solid rgba(229,9,20,0.35)!important;
  color:rgba(255,255,255,0.80)!important;border-radius:9px!important;
  font-size:0.85rem!important;font-weight:700!important;height:32px!important;animation:none!important;
  box-shadow:none!important;}}
div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stButton"] > button:hover{{
  background:rgba(229,9,20,0.22)!important;border-color:rgba(229,9,20,0.70)!important;color:#fff!important;}}
/* Sign Out — subdued, NO pulse */
div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stButton"]:last-child > button{{
  background:rgba(60,5,5,0.70)!important;color:rgba(255,120,120,0.90)!important;animation:none!important;}}
/* ── GLOBAL TEXT VISIBILITY FIX ──────────────────────────────── */
html,body,.stApp,.stMarkdown,p,div,span{text-shadow:0 1px 4px rgba(0,0,0,0.88)!important;}
.stMarkdown p,.stMarkdown li{color:#fff!important;text-shadow:0 1px 6px rgba(0,0,0,0.95)!important;}
[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] p{
  color:rgba(255,255,255,0.95)!important;text-shadow:0 1px 6px rgba(0,0,0,0.95)!important;}
.stCheckbox>label{color:#fff!important;font-weight:600!important;
  text-shadow:0 1px 5px rgba(0,0,0,0.95)!important;}
.stTabs [data-baseweb="tab"]{text-shadow:0 1px 4px rgba(0,0,0,0.90)!important;}


/* ═══ UX OVERHAUL: VISIBILITY & READABILITY ════════════════════════════════ */
html,body,.stApp,.stMarkdown,p,div,span,label{text-shadow:0 2px 6px rgba(0,0,0,0.98)!important;}
[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] p{color:#fff!important;font-size:0.88rem!important;font-weight:700!important;text-shadow:0 2px 8px rgba(0,0,0,0.99)!important;}
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


# ══════════════════════════════════════════════════════════════════════════════
# NAV
# ══════════════════════════════════════════════════════════════════════════════
try:
    from nav_component import render_nav as _render_nav
    _render_nav("diet", uname)
except ImportError:
    from auth_token import logout
    _n = st.columns([1.6,1,1,1,1,1,1,1.2])
    with _n[0]:
        st.markdown(
            f"<div style='font-family:Bebas Neue,sans-serif;font-size:1.5rem;letter-spacing:5px;"
            f"color:{cfg['logo_color']};text-shadow:0 0 20px {cfg['logo_glow']};line-height:1;"
            f"padding-top:4px'>{cfg['icon']} FITPLAN PRO</div>",
            unsafe_allow_html=True
        )
    nav_items = [("Home","pages/2_Dashboard.py","fd_db"),("Workout","pages/3_Workout_Plan.py","fd_wp"),
                 ("● Diet","pages/4_Diet_Plan.py","fd_dp"),("AI Coach","pages/5_ai_coach.py","fd_ai"),
                 ("Records","pages/6_records.py","fd_rc"),("Photos","pages/7_progress_photos.py","fd_ph")]
    for i,(lbl,path,key) in enumerate(nav_items):
        with _n[i+1]:
            if st.button(lbl, key=key, use_container_width=True):
                try: st.switch_page(path)
                except Exception: pass
    with _n[7]:
        if st.button("Sign Out", key="fd_so", use_container_width=True):
            logout(uname)
            for k in ["logged_in","username","auth_token","user_data","workout_plan","structured_days",
                      "dietary_type","full_plan_data","plan_id","plan_start","plan_duration","plan_for",
                      "force_regen","tracking","_plan_checked","_db_loaded_dash"]:
                st.session_state.pop(k, None)
            st.switch_page("app.py")

# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
uname_up = uname.upper()
diet_icons = {"veg":"&#127807;","nonveg":"&#127829;","both":"&#127807;&#127829;"}
d_icon = diet_icons.get(dietary_type,"&#127807;")

st.markdown(
    f"<div style='background:rgba(0,0,0,0.58);border:1.5px solid rgba({rgb},0.40);"
    f"border-radius:20px;padding:28px 36px;margin-bottom:20px;backdrop-filter:blur(14px);"
    f"position:relative;overflow:hidden'>"
    f"<div style='position:absolute;top:0;left:0;right:0;height:2px;"
    f"background:linear-gradient(90deg,transparent,{accent},transparent)'></div>"
    f"<div style='position:absolute;top:16px;right:24px;font-size:0.85rem;font-weight:700;"
    f"letter-spacing:2px;color:rgba({rgb},0.80);background:rgba({rgb},0.12);"
    f"border:1px solid rgba({rgb},0.30);border-radius:20px;padding:4px 14px'>{d_icon} {cfg['label']}</div>"
    f"<div style='font-size:0.85rem;font-weight:700;letter-spacing:4px;text-transform:uppercase;"
    f"color:rgba({rgb},0.80);margin-bottom:10px'>Personalised Nutrition Plan</div>"
    f"<div style='font-family:Barlow Condensed,sans-serif;font-size:clamp(2rem,5vw,3.4rem);"
    f"font-weight:900;text-transform:uppercase;color:#fff;line-height:1;margin-bottom:12px'>"
    f"{uname_up}'s <span style='color:{accent}'>Diet Plan</span></div>"
    f"<div style='display:flex;gap:12px;flex-wrap:wrap'>"
    f"<span style='background:rgba({rgb},0.15);border:1px solid rgba({rgb},0.35);"
    f"border-radius:20px;padding:4px 14px;font-size:1.05rem;font-weight:600;color:{accent}'>"
    f"{d_icon} {cfg['label']}</span>"
    f"<span style='font-size:1.00rem;color:rgba(255,255,255,0.90);align-self:center'>"
    f"Goal: {data.get('goal','Fitness')} &middot; {len(sdays)} days</span>"
    f"</div></div>",
    unsafe_allow_html=True
)

if not sdays:
    st.markdown(
        "<div style='text-align:center;padding:60px 20px'>"
        "<div style='font-size:3rem;margin-bottom:14px'>🥗</div>"
        "<div style='font-family:Bebas Neue,sans-serif;font-size:1.8rem;color:#E50914;"
        "letter-spacing:2px;margin-bottom:8px'>No Plan Found</div>"
        "<div style='font-size:0.85rem;color:rgba(255,255,255,0.90);margin-bottom:24px'>"
        "Generate your personalised plan first from the Profile page.</div></div>",
        unsafe_allow_html=True
    )
    if st.button("👤 Go to Profile"): st.switch_page("pages/1_Profile.py")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# WATER TRACKER
# ══════════════════════════════════════════════════════════════════════════════
water_key = f"water_{uname}_{today_str}"
if water_key not in st.session_state:
    try:
        from utils.db import get_water as _gw
        st.session_state[water_key] = _gw(uname, today_str)
    except Exception:
        st.session_state[water_key] = 0

glasses  = st.session_state[water_key]
goal_w   = 8
pct_w    = min(int(glasses / goal_w * 100), 100)
fill_col = "#22c55e" if glasses >= goal_w else "#60a5fa"

glass_html = ""
for gi in range(goal_w):
    filled = gi < glasses
    bg  = "rgba(34,197,94,0.35)" if filled else "rgba(255,255,255,0.06)"
    brd = "rgba(34,197,94,0.70)" if filled else "rgba(255,255,255,0.18)"
    ico = "&#128167;" if filled else ""
    glass_html += (
        f"<div style='width:38px;height:50px;border-radius:4px 4px 10px 10px;"
        f"border:2px solid {brd};background:{bg};"
        f"display:flex;align-items:center;justify-content:center;font-size:1.1rem'>{ico}</div>"
    )

st.markdown(
    "<div style='font-size:0.85rem;font-weight:700;letter-spacing:3px;text-transform:uppercase;"
    "color:rgba(229,9,20,0.75);margin:16px 0 8px;display:flex;align-items:center;gap:8px'>"
    "<span style='width:16px;height:1.5px;background:#E50914;display:block'></span>"
    "Water Intake Tracker</div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div class='water-card'>"
    "<div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:12px'>"
    "<div><div style='font-size:0.85rem;font-weight:700;letter-spacing:3px;text-transform:uppercase;"
    "color:rgba(96,165,250,0.85)'>Today&#39;s Water Intake</div>"
    f"<div style='font-size:1.05rem;color:rgba(255,255,255,0.90);margin-top:2px'>Goal: 8 glasses &middot; {today_str}</div></div>"
    f"<div style='font-family:Bebas Neue,sans-serif;font-size:2.4rem;color:{fill_col};letter-spacing:2px'>"
    f"{glasses}<span style='font-size:1.1rem;color:rgba(255,255,255,0.90)'>/{goal_w}</span></div>"
    "</div>"
    f"<div style='display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap'>{glass_html}</div>"
    "<div style='height:5px;background:rgba(255,255,255,0.10);border-radius:3px;overflow:hidden'>"
    f"<div style='height:100%;width:{pct_w}%;background:linear-gradient(90deg,#60a5fa,#2563eb);border-radius:3px'></div>"
    "</div>"
    + ("<div style='margin-top:8px;font-size:1.05rem;font-weight:700;color:#22c55e'>&#127881; Daily goal reached! Well done!</div>" if glasses >= goal_w else "") +
    "</div>",
    unsafe_allow_html=True
)
wc1, wc2, _ = st.columns([2,2,6])
with wc1:
    if st.button("+ 1 Glass", key="water_add", use_container_width=True):
        st.session_state[water_key] = min(glasses+1, 20)
        try:
            from utils.db import save_water as _sw
            _sw(uname, today_str, st.session_state[water_key])
        except Exception: pass
        st.rerun()
with wc2:
    if glasses > 0 and st.button("Undo", key="water_undo", use_container_width=True):
        st.session_state[water_key] = max(glasses-1, 0)
        try:
            from utils.db import save_water as _sw2
            _sw2(uname, today_str, st.session_state[water_key])
        except Exception: pass
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# FEATURE CARDS — Grocery / Supplement / Weekly Adherence
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
fe1, fe2, fe3 = st.columns(3)

with fe1:
    with st.expander("🛒  Grocery List — Next 7 Days", expanded=False):
        all_items = set()
        # FIX: expanded stopwords list — filters units, adjectives, verbs
        _stop = {
            "With","Your","From","This","That","Have","Will","Each","Slice","Slices",
            "Tbsp","Cups","Grams","Gram","Steamed","Grilled","Cooked","Mixed","Fresh",
            "Chopped","Diced","Boiled","Baked","Roasted","Fried","Serve","Serving",
            "Medium","Large","Small","Half","Full","Side","Light","Dark","Lean","Whole",
            "Handful","Tablespoon","Teaspoon","Bowl","Plate","Glass","Piece","Pieces",
            "Optional","Include","Season","Seasoned","Drizzle","Garnish","Plus","Along",
            "Before","After","During","Based","Topped","Warm","Cool","Cold","Hot",
            "High","Low","Daily","Weekly","Rich","Good","Best","Well","Done","Made",
        }
        for sd in sdays[:7]:
            for meal_txt in sd.get("dietary", {}).values():
                if not meal_txt: continue
                words = _re.findall(r'\b[A-Z][a-zA-Z]{3,}\b', meal_txt)
                for w in words:
                    if w not in _stop and not w.endswith("ing") and not w.endswith("ed"):
                        all_items.add(w)
        if all_items:
            sorted_items = sorted(all_items)[:20]
            st.markdown(
                "<div style='font-size:0.85rem;color:rgba(255,255,255,0.90);margin-bottom:8px'>"
                "✓ Tap to cross off while shopping</div>",
                unsafe_allow_html=True
            )
            for item in sorted_items:
                g_key   = f"grocery_{uname}_{item}"
                checked = st.session_state.get(g_key, False)
                strike  = "text-decoration:line-through;opacity:0.40;" if checked else ""
                c_item, c_check = st.columns([5,1])
                with c_item:
                    st.markdown(
                        f"<div style='display:flex;align-items:center;gap:10px;padding:5px 4px;"
                        f"border-bottom:1px solid rgba(255,255,255,0.08);font-size:0.85rem;"
                        f"color:#fff;font-weight:500;{strike}'>🛒 {item}</div>",
                        unsafe_allow_html=True
                    )
                with c_check:
                    st.session_state[g_key] = st.checkbox("", value=checked, key=g_key+"_cb", label_visibility="collapsed")
            if any(st.session_state.get(f"grocery_{uname}_{i}", False) for i in sorted_items):
                if st.button("Clear all ✓", key="grocery_clear", use_container_width=True):
                    for i in sorted_items:
                        st.session_state[f"grocery_{uname}_{i}"] = False
                    st.rerun()
        else:
            st.markdown(
                "<div style='color:rgba(255,255,255,0.90);font-size:1.00rem;padding:8px 0'>"
                "Generate a plan first to see your grocery list.</div>",
                unsafe_allow_html=True
            )

with fe2:
    with st.expander("💊  Supplement Guide", expanded=False):
        supp_key = f"supp_{uname}"
        if not st.session_state.get(supp_key):
            try:
                from utils.db import get_user_setting
                _db_supp = get_user_setting(uname, "supplement_guide")
                if _db_supp: st.session_state[supp_key] = _db_supp
            except Exception: pass
        if not st.session_state.get(supp_key):
            if st.button("Get AI Guide", key="supp_btn", use_container_width=True):
                with st.spinner("Generating personalised guide..."):
                    try:
                        from model_api import query_model
                        prompt = (
                            f"List 5 supplements for a {data.get('level','Beginner')} person, "
                            f"goal: {data.get('goal','Fitness')}, diet: {cfg['label']}. "
                            "Format: NAME: dosage — benefit. Plain text only."
                        )
                        raw = query_model(prompt, max_tokens=250).strip()
                        st.session_state[supp_key] = raw
                        try:
                            from utils.db import save_user_setting
                            save_user_setting(uname, "supplement_guide", raw)
                        except Exception: pass
                        st.rerun()
                    except Exception as e:
                        st.error("Could not generate guide. Try again.")
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
                    + (f"<b style='color:{accent};font-size:0.85rem'>{name}</b><br>" if name else "")
                    + f"<span style='font-size:1.00rem;color:#fff;line-height:1.5'>{desc}</span></div>",
                    unsafe_allow_html=True
                )
            if st.button("↻ Refresh", key="supp_refresh"):
                st.session_state.pop(supp_key, None)
                st.rerun()

with fe3:
    with st.expander("📊  Weekly Adherence", expanded=False):
        done_m = 0; total_m = 0
        for i, sd in enumerate(sdays[:7]):
            dn2 = sd.get("day", i+1)
            for meal in sd.get("dietary", {}):
                total_m += 1
                if st.session_state.get(f"meal_d{dn2}_{meal}", False):
                    done_m += 1
        adh   = int(done_m / max(total_m, 1) * 100)
        col_a = "#22c55e" if adh >= 70 else ("#fbbf24" if adh >= 40 else "#ef4444")
        st.markdown(
            f"<div style='text-align:center;padding:8px 0'>"
            f"<div style='font-family:Bebas Neue,sans-serif;font-size:3.5rem;color:{col_a};line-height:1'>{adh}%</div>"
            f"<div style='font-size:1.05rem;color:#fff;margin-top:6px;font-weight:600'>Weekly Diet Adherence</div>"
            f"<div style='font-size:0.85rem;color:rgba(255,255,255,0.70);margin-top:4px'>{done_m} of {total_m} meals tracked</div>"
            f"<div class='prog-bar-bg' style='margin-top:10px'>"
            f"<div style='height:100%;width:{adh}%;background:{col_a};border-radius:3px'></div>"
            f"</div></div>",
            unsafe_allow_html=True
        )

# ══════════════════════════════════════════════════════════════════════════════
# DAY TABS — Meal cards + swap + nutrition summary + tips
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    f"<div style='font-size:0.85rem;font-weight:700;letter-spacing:3px;text-transform:uppercase;"
    f"color:rgba({rgb},0.80);margin:20px 0 10px;display:flex;align-items:center;gap:8px'>"
    f"<span style='width:16px;height:1.5px;background:{accent};display:block'></span>"
    f"Your Meal Plan by Day</div>",
    unsafe_allow_html=True
)

MEAL_ICONS = {"breakfast":"🌅","lunch":"☀️","dinner":"🌙","snacks":"🍎"}

tab_labels = [
    "Day " + str(d.get("day",i+1)) + (" 😴" if d.get("is_rest_day") else "")
    for i,d in enumerate(sdays)
]
tabs = st.tabs(tab_labels)

for tab, day_data in zip(tabs, sdays):
    with tab:
        dn          = day_data.get("day", 1)
        dietary     = day_data.get("dietary", {})
        is_rest     = day_data.get("is_rest_day", False)
        mg          = day_data.get("muscle_group", "Full Body")
        total_meals = len([m for m,v in dietary.items() if v])
        done_meals  = sum(1 for m in dietary if st.session_state.get(f"meal_d{dn}_{m}", False))
        pct_m       = int(done_meals / max(total_meals,1) * 100)

        hdr_col, pct_col = st.columns([4,1])
        with hdr_col:
            tag = "REST DAY" if is_rest else f"DAILY NUTRITION — {mg.upper()}"
            st.markdown(
                f"<div style='font-size:0.85rem;font-weight:700;letter-spacing:3px;"
                f"text-transform:uppercase;color:{accent};margin-bottom:8px'>{tag}</div>",
                unsafe_allow_html=True
            )
        with pct_col:
            st.markdown(
                f"<div style='text-align:right;font-size:1.05rem;font-weight:700;"
                f"color:{accent};padding-top:2px'>{done_meals}/{total_meals} &middot; {pct_m}%</div>",
                unsafe_allow_html=True
            )

        left_col, right_col = st.columns([3,2])

        # ── LEFT: Meal cards + swap ───────────────────────────────────────
        with left_col:
            if not dietary:
                st.markdown(
                    "<div style='color:rgba(255,255,255,0.90);font-size:1.00rem;"
                    "padding:20px;text-align:center'>No meals for this day.</div>",
                    unsafe_allow_html=True
                )
            else:
                for meal, desc in dietary.items():
                    if not desc: continue
                    icon  = MEAL_ICONS.get(meal, "🍽️")
                    ck    = f"meal_d{dn}_{meal}"
                    done  = st.session_state.get(ck, False)
                    strike = "text-decoration:line-through;opacity:0.40;" if done else ""

                    # Meal card + Swap button side by side
                    mc_top, mc_btn = st.columns([4,1])
                    with mc_top:
                        st.markdown(
                            f"<div class='meal-card'>"
                            f"<div class='meal-label'>"
                            f"<span style='color:{accent}'>{icon} {meal.upper()}</span>"
                            + (f" <span style='color:{accent};font-size:0.75rem'>✓ Done</span>" if done else "") +
                            f"</div>"
                            f"<div class='meal-text' style='{strike}'>{str(desc)}</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                    with mc_btn:
                        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
                        st.markdown("<div class='swap-mini'>", unsafe_allow_html=True)
                        if st.button("🤖 Swap", key=f"swap_{dn}_{meal}", use_container_width=True):
                            with st.spinner("Getting AI alternative..."):
                                try:
                                    from model_api import query_model
                                    d_label = {"veg":"Vegetarian","nonveg":"Non-Vegetarian","both":"Flexible"}.get(dietary_type,"")
                                    prompt = (
                                        f"Suggest 1 alternative {meal} meal for a {d_label} person "
                                        f"(goal: {data.get('goal','Fitness')}). "
                                        f"Current meal: {str(desc)}. "
                                        "Give only the meal name and key ingredients in 1-2 lines. No JSON."
                                    )
                                    result = query_model(prompt, max_tokens=80)
                                    st.session_state[f"swap_result_{dn}_{meal}"] = result.strip()
                                    st.rerun()
                                except Exception:
                                    st.error("Could not get swap. Try again.")
                        st.markdown("</div>", unsafe_allow_html=True)

                    # Swap picker UI
                    swap_res   = st.session_state.get(f"swap_result_{dn}_{meal}")
                    chosen_key = f"meal_choice_{dn}_{meal}"
                    if swap_res:
                        chosen = st.session_state.get(chosen_key, "original")
                        orig_style = f"background:rgba(229,9,20,0.25);border:2px solid #E50914" if chosen=="original" else "background:rgba(0,0,0,0.75);border:1.5px solid rgba(255,255,255,0.15)"
                        swap_style = f"background:rgba({rgb},0.20);border:2px solid {accent}" if chosen=="swap" else "background:rgba(0,0,0,0.75);border:1.5px solid rgba(255,255,255,0.15)"
                        orig_lbl_c = "rgba(229,9,20,0.90)" if chosen=="original" else "rgba(255,255,255,0.45)"
                        swap_lbl_c = f"rgba({rgb},0.90)" if chosen=="swap" else "rgba(255,255,255,0.45)"
                        st.markdown(
                            "<div style='background:rgba(0,0,0,0.70);border:1px solid rgba(255,255,255,0.18);"
                            "border-radius:12px;padding:12px 14px;margin-bottom:8px;backdrop-filter:blur(10px)'>"
                            f"<div style='font-size:0.85rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;"
                            f"color:{accent};margin-bottom:8px'>🤖 Choose Your {meal.title()}</div>"
                            "<div style='display:flex;gap:8px;flex-wrap:wrap'>"
                            f"<div style='flex:1;min-width:140px;{orig_style};border-radius:10px;padding:10px 12px'>"
                            f"<div style='font-size:0.85rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:{orig_lbl_c};margin-bottom:4px'>⭐ Original</div>"
                            f"<div style='font-size:0.80rem;color:#fff;line-height:1.5'>{str(desc)}</div></div>"
                            f"<div style='flex:1;min-width:140px;{swap_style};border-radius:10px;padding:10px 12px'>"
                            f"<div style='font-size:0.85rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:{swap_lbl_c};margin-bottom:4px'>🤖 AI Alternative</div>"
                            f"<div style='font-size:0.80rem;color:#fff;line-height:1.5'>{swap_res}</div></div>"
                            "</div></div>",
                            unsafe_allow_html=True
                        )
                        pick1, pick2, pick3 = st.columns([2,2,1])
                        with pick1:
                            if st.button("✓ Original" if chosen=="original" else "Keep Original",
                                         key=f"pick_orig_{dn}_{meal}", use_container_width=True):
                                st.session_state[chosen_key] = "original"
                                st.rerun()
                        with pick2:
                            if st.button("✓ AI Swap" if chosen=="swap" else "Use AI Swap",
                                         key=f"pick_swap_{dn}_{meal}", use_container_width=True):
                                st.session_state[chosen_key] = "swap"
                                # FIX: persist swap to structured_days so it survives rerun
                                _sdays_ref = st.session_state.get("structured_days", [])
                                for _sd_item in _sdays_ref:
                                    if _sd_item.get("day") == dn:
                                        _sd_item.setdefault("dietary", {})[meal] = swap_res
                                        break
                                st.session_state.structured_days = _sdays_ref
                                st.rerun()
                        with pick3:
                            if st.button("✕", key=f"dismiss_swap_{dn}_{meal}", use_container_width=True):
                                st.session_state.pop(f"swap_result_{dn}_{meal}", None)
                                st.session_state.pop(chosen_key, None)
                                st.rerun()
                        if chosen == "swap":
                            st.markdown(f"<div style='font-size:0.85rem;color:{accent};font-weight:600;padding:4px 0'>🤖 AI Alternative selected for today</div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div style='font-size:0.85rem;color:rgba(229,9,20,0.75);padding:4px 0'>⭐ Original meal selected</div>", unsafe_allow_html=True)

                    # FIX: two-way checkbox — can be unchecked
                    _new_done = st.checkbox("Mark as done", value=done, key=ck+"_cb")
                    if _new_done != done:
                        st.session_state[ck] = _new_done
                        if plan_id:
                            try:
                                from utils.db import save_progress
                                dc_ = {m2: st.session_state.get(f"meal_d{dn}_{m2}", False)
                                       for m2 in ["breakfast","lunch","dinner","snacks"]}
                                save_progress(uname, plan_id, dn, {}, dc_)
                            except Exception: pass
                        st.rerun()

        # ── RIGHT: Nutrition summary + Tips ─────────────────────────────
        with right_col:
            # FIX: estimated calorie values (not fake precision)
            # Using typical meal-type averages with clear "est." label
            _cal_base  = {"breakfast":380,"lunch":560,"dinner":480,"snacks":170}
            _prot_base = {"breakfast":20,"lunch":38,"dinner":32,"snacks":8}
            _cal_mult  = 1.1 if dietary_type=="nonveg" else 1.0
            total_cal  = int(sum(_cal_base.get(m,0)*_cal_mult for m in dietary if dietary.get(m)))
            total_prot = int(sum(_prot_base.get(m,0)*_cal_mult for m in dietary if dietary.get(m)))

            st.markdown(
                "<div style='background:rgba(0,0,0,0.75);border:1.5px solid rgba(255,255,255,0.15);"
                "border-radius:14px;padding:16px 18px;margin-bottom:12px;backdrop-filter:blur(10px)'>"
                f"<div class='feature-card-title'>Nutrition Summary</div>"
                "<div style='display:grid;grid-template-columns:1fr 1fr;gap:8px'>"
                "<div style='background:rgba(229,9,20,0.12);border-radius:10px;padding:12px;text-align:center'>"
                f"<div style='font-family:Bebas Neue,sans-serif;font-size:2rem;color:#E50914'>{total_cal}"
                "<span style='font-size:0.85rem;opacity:0.60;vertical-align:super'>est.</span></div>"
                "<div style='font-size:0.85rem;color:rgba(255,255,255,0.80);letter-spacing:2px;text-transform:uppercase;font-weight:600'>Calories</div></div>"
                "<div style='background:rgba(96,165,250,0.12);border-radius:10px;padding:12px;text-align:center'>"
                f"<div style='font-family:Bebas Neue,sans-serif;font-size:2rem;color:#60a5fa'>{total_prot}g"
                "<span style='font-size:0.85rem;opacity:0.60;vertical-align:super'>est.</span></div>"
                "<div style='font-size:0.85rem;color:rgba(255,255,255,0.80);letter-spacing:2px;text-transform:uppercase;font-weight:600'>Protein</div></div>"
                "</div>"
                "<div class='prog-bar-bg' style='margin-top:12px'>"
                f"<div class='prog-bar-fill' style='width:{pct_m}%'></div></div>"
                f"<div style='font-size:0.85rem;color:rgba(255,255,255,0.90);margin-top:4px;text-align:right'>"
                f"{done_meals}/{total_meals} meals done</div>"
                "</div>",
                unsafe_allow_html=True
            )

            # Nutrition tips (themed per diet type)
            st.markdown(
                f"<div style='background:rgba(0,0,0,0.70);border:1px solid rgba({rgb},0.22);"
                f"border-radius:12px;padding:16px 18px'>"
                f"<div style='font-size:0.85rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;"
                f"color:rgba({rgb},0.75);margin-bottom:10px'>💡 Nutrition Tips</div>",
                unsafe_allow_html=True
            )
            for tip in cfg["tips"][:5]:
                st.markdown(f"<div class='tip-card'>{tip}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)