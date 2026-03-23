"""
nav_component.py — Single shared navigation bar for FitPlan Pro.
Import and call render_nav(current_page) from every page.
current_page: 'dashboard' | 'workout' | 'diet' | 'ai_coach' | 'records' | 'photos' | 'history' | 'profile'
"""
import streamlit as st
from auth_token import logout

NAV_PAGES = [
    ("dashboard",  "🏠 Home",     "pages/2_Dashboard.py"),
    ("workout",    "⚡ Workout",   "pages/3_Workout_Plan.py"),
    ("diet",       "🥗 Diet",      "pages/4_Diet_Plan.py"),
    ("ai_coach",   "🤖 AI Coach",  "pages/5_ai_coach.py"),
    ("records",    "🏆 Records",   "pages/6_records.py"),
    ("photos",     "📸 Photos",    "pages/7_progress_photos.py"),
    ("history",    "📅 History",   "pages/9_history.py"),
]

NAV_CSS = """
<style>
.nav-wrap{
  background:rgba(5,2,1,0.97);backdrop-filter:blur(20px);
  border-bottom:1.5px solid rgba(229,9,20,0.22);
  box-shadow:0 2px 24px rgba(0,0,0,0.65);
  padding:5px 0;margin-bottom:4px;}
.nav-logo{
  font-family:'Bebas Neue',sans-serif;font-size:1.4rem;letter-spacing:5px;
  color:#E50914;text-shadow:0 0 18px rgba(229,9,20,0.45);line-height:1;}
div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stButton"] > button{
  background:rgba(18,4,4,0.82)!important;border:1.5px solid rgba(229,9,20,0.30)!important;
  color:rgba(255,255,255,0.75)!important;border-radius:9px!important;
  font-family:'DM Sans',sans-serif!important;font-size:0.68rem!important;font-weight:700!important;
  padding:5px 8px!important;height:32px!important;min-height:32px!important;
  white-space:nowrap!important;box-shadow:none!important;
  transition:all 0.15s ease!important;text-transform:none!important;
  animation:none!important;}
div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stButton"] > button:hover{
  background:rgba(229,9,20,0.22)!important;border-color:rgba(229,9,20,0.70)!important;
  color:#fff!important;transform:translateY(-1px)!important;}
.nav-active > div > div > div[data-testid="stButton"] > button{
  background:rgba(229,9,20,0.28)!important;
  border:1.5px solid rgba(229,9,20,0.85)!important;
  color:#fff!important;
  box-shadow:0 0 10px rgba(229,9,20,0.35)!important;}
/* Sign Out - subdued, no pulse */
div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stButton"]:last-child > button{
  background:rgba(60,5,5,0.55)!important;
  border:1.5px solid rgba(229,9,20,0.30)!important;
  color:rgba(255,255,255,0.55)!important;
  box-shadow:none!important;animation:none!important;}
div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stButton"]:last-child > button:hover{
  background:rgba(140,0,8,0.65)!important;border-color:rgba(229,9,20,0.70)!important;
  color:#fff!important;}
</style>
"""

_CLEAR_KEYS = [
    "logged_in","username","auth_token","user_data","workout_plan",
    "structured_days","dietary_type","full_plan_data","plan_id","plan_start",
    "plan_duration","plan_for","force_regen","tracking","_plan_checked",
    "_db_loaded_dash","_auto_redirect","_diet_chosen","_needs_rerun",
    "_db_streak","edit_profile_mode","_login_db_err","_notes_loaded",
    "_streak_synced","last_badge_count","_regen_confirm",
]

def render_nav(current_page: str, username: str = None):
    """Render the shared nav bar. current_page is the key string, e.g. 'dashboard'."""
    if username is None:
        username = st.session_state.get("username", "Athlete")

    st.markdown(NAV_CSS, unsafe_allow_html=True)
    st.markdown("<div class='nav-wrap'>", unsafe_allow_html=True)

    cols = st.columns([1.6, 1, 1, 1, 1, 1, 1, 1, 1.1])

    with cols[0]:
        st.markdown("<div class='nav-logo'>&#9889; FITPLAN PRO</div>", unsafe_allow_html=True)

    for i, (page_key, label, path) in enumerate(NAV_PAGES):
        with cols[i + 1]:
            is_active = (page_key == current_page)
            if is_active:
                st.markdown("<div class='nav-active'>", unsafe_allow_html=True)
            if st.button(label, key=f"nav_{page_key}", use_container_width=True):
                try:
                    st.switch_page(path)
                except Exception:
                    pass
            if is_active:
                st.markdown("</div>", unsafe_allow_html=True)

    with cols[8]:
        if st.button("🚪 Sign Out", key="nav_signout", use_container_width=True):
            logout(username)
            for k in _CLEAR_KEYS:
                st.session_state.pop(k, None)
            st.switch_page("app.py")

    st.markdown("</div>", unsafe_allow_html=True)