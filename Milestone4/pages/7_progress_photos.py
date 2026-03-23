# -*- coding: utf-8 -*-
import streamlit as st
import os, sys, base64
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_token import logout
from bg_utils import apply_bg

st.set_page_config(page_title="Progress Photos | FitPlan Pro", page_icon="📸",
                   layout="wide", initial_sidebar_state="collapsed")

if not st.session_state.get("logged_in"): st.switch_page("app.py")
if "user_data" not in st.session_state:   st.switch_page("pages/1_Profile.py")

uname = st.session_state.get("username", "Athlete")
data  = st.session_state.user_data

st.markdown("""
<style>
/* ── Background blur via pseudo-element ── */
[data-testid="stAppViewContainer"]::before{
  content:'';position:fixed;inset:0;z-index:0;
  background:url('https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?fm=jpg&w=1600&q=80&fit=crop') center center/cover no-repeat;
  filter:blur(8px) brightness(0.25) saturate(0.55);
  transform:scale(1.06);
}
[data-testid="stAppViewContainer"]{
  background:linear-gradient(160deg,rgba(2,4,8,0.90) 0%,rgba(3,5,10,0.82) 50%,rgba(2,4,8,0.94) 100%)!important;
  position:relative;
}
[data-testid="stAppViewContainer"]>section>div.block-container{
  position:relative;z-index:2;
}
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:opsz,wght@9..40,400;9..40,600;9..40,700&display=swap');

#MainMenu, footer, header,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stSidebarNav"], [data-testid="collapsedControl"],
section[data-testid="stSidebar"], button[kind="header"] { display:none!important; }

html,body,.stApp { background:#020408!important; color:#fff!important; font-family:'DM Sans',sans-serif!important; }
[data-testid="stAppViewContainer"]>section>div.block-container {
  max-width:1100px!important; margin:0 auto!important; padding:0 24px 80px!important;
  background:rgba(0,0,0,0.38)!important; border-radius:0!important; }
[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] p {
  color:rgba(255,255,255,0.75)!important; font-size:1.05rem!important; font-weight:600!important; }

[data-testid="stFormSubmitButton"] button { background:linear-gradient(135deg,#E50914,#c0000c)!important;
  border:none!important; color:#fff!important; border-radius:10px!important; font-weight:700!important;
  box-shadow:0 4px 20px rgba(229,9,20,0.45)!important; }
.stButton>button { background:linear-gradient(135deg,rgba(229,9,20,0.85),rgba(160,0,10,0.90))!important;
  border:2px solid rgba(229,9,20,0.65)!important; color:#fff!important; border-radius:10px!important;
  font-family:'DM Sans',sans-serif!important; font-size:1.0rem!important; font-weight:700!important;
  box-shadow:0 0 12px rgba(229,9,20,0.30)!important; transition:all 0.20s!important; }
.stButton>button:hover { transform:translateY(-2px)!important; box-shadow:0 0 24px rgba(229,9,20,0.60)!important; }

div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stButton"]>button {
  background:rgba(18,4,4,0.82)!important; border:2px solid rgba(229,9,20,0.65)!important;
  color:rgba(255,255,255,0.92)!important; border-radius:9px!important;
  font-size:0.85rem!important; font-weight:700!important; padding:5px 8px!important;
  height:32px!important; min-height:32px!important; white-space:nowrap!important;
  box-shadow:0 0 8px rgba(229,9,20,0.22)!important; transition:all 0.15s ease!important; }
div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stButton"]>button:hover {
  background:rgba(229,9,20,0.28)!important; border-color:rgba(229,9,20,0.85)!important;
  color:#fff!important; transform:translateY(-1px)!important; }
div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stButton"]:last-child>button {
  background:linear-gradient(135deg,#c0000c,#8b0000)!important; border-color:rgba(229,9,20,0.80)!important; }

.nav-logo { font-family:'Bebas Neue',sans-serif; font-size:1.4rem; letter-spacing:5px;
  color:#E50914; text-shadow:0 0 18px rgba(229,9,20,0.45); line-height:1; }

[data-testid="stFileUploader"]>div, [data-testid="stFileUploadDropzone"] {
  background:rgba(255,255,255,0.06)!important; border:2px dashed rgba(229,9,20,0.45)!important;
  border-radius:20px!important; backdrop-filter:blur(38px) saturate(1.7)!important;-webkit-backdrop-filter:blur(38px) saturate(1.7)!important; transition:all 0.22s!important;
  box-shadow:0 4px 24px rgba(0,0,0,0.30)!important; }
[data-testid="stFileUploader"]>div:hover, [data-testid="stFileUploadDropzone"]:hover {
  border-color:rgba(229,9,20,0.80)!important; background:rgba(229,9,20,0.08)!important; }
[data-testid="stFileUploader"] span, [data-testid="stFileUploader"] p,
[data-testid="stFileUploader"] small, [data-testid="stFileUploader"] button { color:rgba(255,255,255,0.80)!important; }

[data-baseweb="select"]>div { background:rgba(255,255,255,0.08)!important;
  border:1.5px solid rgba(255,255,255,0.22)!important; border-radius:14px!important;
  backdrop-filter:blur(28px)!important; color:#fff!important; }
[data-baseweb="select"] span,[data-baseweb="select"] div { color:#fff!important; }
[data-baseweb="popover"] [role="option"] { background:rgba(15,6,4,0.96)!important; color:#fff!important; }
[data-baseweb="popover"] [role="option"]:hover { background:rgba(229,9,20,0.22)!important; }

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

apply_bg(
    "https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?fm=jpg&w=1600&q=80&fit=crop",
    overlay="rgba(8,5,3,0.72)"
)

# NAV
st.markdown("<div style='background:rgba(5,2,1,0.97);backdrop-filter:blur(20px);"
            "border-bottom:1.5px solid rgba(229,9,20,0.22);padding:5px 0;margin-bottom:16px'>",
            unsafe_allow_html=True)
_n = st.columns([1.8,1,1,1,1,1,1,1.3])
with _n[0]: st.markdown("<div class='nav-logo'>FitPlan Pro</div>", unsafe_allow_html=True)
with _n[1]:
    if st.button("Home",     key="pp_db", use_container_width=True): st.switch_page("pages/2_Dashboard.py")
with _n[2]:
    if st.button("Workout",  key="pp_wp", use_container_width=True): st.switch_page("pages/3_Workout_Plan.py")
with _n[3]:
    if st.button("Diet",     key="pp_dp", use_container_width=True): st.switch_page("pages/4_Diet_Plan.py")
with _n[4]:
    if st.button("AI Coach", key="pp_ai", use_container_width=True):
        try: st.switch_page("pages/5_ai_coach.py")
        except Exception as e: st.warning(str(e))
with _n[5]:
    if st.button("Records",  key="pp_rc", use_container_width=True):
        try: st.switch_page("pages/6_records.py")
        except Exception as e: st.warning(str(e))
with _n[6]:
    if st.button("Photos",   key="pp_ph", use_container_width=True): st.switch_page("pages/7_progress_photos.py")
with _n[7]:
    if st.button("Sign Out", key="pp_so", use_container_width=True):
        logout(uname)
        for _k in ["logged_in","username","auth_token","user_data","workout_plan",
                   "structured_days","dietary_type","full_plan_data","plan_id","plan_start",
                   "plan_duration","plan_for","force_regen","tracking","_plan_checked",
                   "_db_loaded_dash","_auto_redirect","_diet_chosen","_needs_rerun",
                   "_db_streak","edit_profile_mode","_login_db_err","_notes_loaded"]:
            st.session_state.pop(_k, None)
        st.switch_page("app.py")
st.markdown("</div>", unsafe_allow_html=True)

# HERO
st.markdown(
    "<div style='background:linear-gradient(135deg,rgba(99,102,241,0.15),rgba(67,56,202,0.08) 50%,rgba(6,2,1,0.60));"
    "border:1px solid rgba(99,102,241,0.28);border-radius:18px;padding:28px 36px;margin-bottom:24px;"
    "position:relative;overflow:hidden'>"
    "<div style='position:absolute;top:0;left:0;right:0;height:2px;"
    "background:linear-gradient(90deg,transparent,#818cf8,transparent)'></div>"
    "<div style='font-family:Bebas Neue,sans-serif;font-size:2.4rem;font-weight:900;"
    "text-transform:uppercase;color:#fff;line-height:1;margin-bottom:6px'>"
    "Progress <span style='color:#818cf8'>Photos</span></div>"
    "<div style='font-size:1.00rem;color:rgba(255,255,255,0.90)'>"
    "Document your transformation journey with before and after photos</div></div>",
    unsafe_allow_html=True)

# Load photos
if "progress_photos" not in st.session_state:
    try:
        from utils.db import get_progress_photos as _gpp
        _db_photos = _gpp(uname)
        st.session_state.progress_photos = _db_photos if _db_photos else []
    except Exception:
        st.session_state.progress_photos = []
photos = st.session_state.progress_photos

# Upload
st.markdown("<div style='font-size:0.85rem;font-weight:700;letter-spacing:3px;text-transform:uppercase;"
            "color:rgba(229,9,20,0.75);margin-bottom:10px'>Upload Progress Photo</div>", unsafe_allow_html=True)
uc1, uc2 = st.columns([3,1])
with uc1:
    uploaded = st.file_uploader("photo", type=["jpg","jpeg","png","webp"],
                                 key="photo_upload", label_visibility="collapsed")
with uc2:
    photo_label = st.selectbox("Label",
                                ["Current","Before","After","Week 1","Week 4","Week 8","Week 12","Custom"],
                                key="photo_label", label_visibility="collapsed")

if uploaded:
    img_bytes = uploaded.read()
    img_b64   = base64.b64encode(img_bytes).decode()
    ext       = uploaded.name.split(".")[-1].lower()
    mime      = "image/jpeg" if ext in ["jpg","jpeg"] else ("image/" + ext)
    src       = "data:" + mime + ";base64," + img_b64

    pc1, pc2 = st.columns([1,2])
    with pc1:
        st.markdown("<img src='" + src + "' style='width:100%;border-radius:12px;"
                    "border:1px solid rgba(99,102,241,0.30)'>", unsafe_allow_html=True)
    with pc2:
        st.markdown("<div style='font-size:1.05rem;color:rgba(255,255,255,0.90);margin-bottom:8px'>"
                    "File: " + uploaded.name + "<br>Size: " + str(len(img_bytes)//1024) + " KB<br>"
                    "Label: " + photo_label + "</div>", unsafe_allow_html=True)
        if st.button("Save Photo", key="save_photo", use_container_width=True):
            new_photo = {"date":date.today().isoformat(),"label":photo_label,"b64":img_b64,"mime":mime}
            photos.append(new_photo)
            st.session_state.progress_photos = photos
            try:
                from utils.db import save_progress_photo
                save_progress_photo(uname, new_photo)
            except Exception: pass
            st.toast("Photo saved!", icon="📸")
            st.rerun()

st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.08);margin:20px 0'>",
            unsafe_allow_html=True)

# Gallery
if not photos:
    st.markdown(
        "<div style='text-align:center;padding:60px 20px'>"
        "<div style='font-size:3.5rem;margin-bottom:12px'>&#128247;</div>"
        "<div style='font-family:Bebas Neue,sans-serif;font-size:1.8rem;letter-spacing:2px;"
        "color:#818cf8;margin-bottom:8px'>No Photos Yet</div>"
        "<div style='font-size:1.05rem;color:rgba(255,255,255,0.90)'>"
        "Upload your first progress photo above to start tracking your transformation.</div></div>",
        unsafe_allow_html=True)
else:
    if len(photos) >= 2:
        st.markdown("<div style='font-size:0.85rem;font-weight:700;letter-spacing:3px;text-transform:uppercase;"
                    "color:rgba(229,9,20,0.75);margin-bottom:10px'>Before / After Comparison</div>",
                    unsafe_allow_html=True)
        ba1, ba2 = st.columns(2)
        pf = photos[0]
        src_f = "data:" + pf["mime"] + ";base64," + pf["b64"]
        with ba1:
            st.markdown(
                "<div style='text-align:center'>"
                "<div style='font-size:1.00rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;"
                "color:rgba(255,255,255,0.90);margin-bottom:6px'>" + pf["label"] + " — " + pf["date"] + "</div>"
                "<img src='" + src_f + "' style='width:100%;border-radius:12px;"
                "border:1.5px solid rgba(229,9,20,0.30)'></div>",
                unsafe_allow_html=True)
        pl = photos[-1]
        src_l = "data:" + pl["mime"] + ";base64," + pl["b64"]
        with ba2:
            st.markdown(
                "<div style='text-align:center'>"
                "<div style='font-size:1.00rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;"
                "color:rgba(255,255,255,0.90);margin-bottom:6px'>" + pl["label"] + " — " + pl["date"] + "</div>"
                "<img src='" + src_l + "' style='width:100%;border-radius:12px;"
                "border:1.5px solid rgba(99,102,241,0.40)'></div>",
                unsafe_allow_html=True)
        d0   = date.fromisoformat(photos[0]["date"])
        d1   = date.fromisoformat(photos[-1]["date"])
        st.markdown("<div style='text-align:center;margin:12px 0;font-size:1.00rem;color:rgba(255,255,255,0.90)'>"
                    + str((d1-d0).days) + " days tracked across " + str(len(photos)) + " photos</div>",
                    unsafe_allow_html=True)
        st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.08);margin:16px 0'>",
                    unsafe_allow_html=True)

    st.markdown("<div style='font-size:0.85rem;font-weight:700;letter-spacing:3px;text-transform:uppercase;"
                "color:rgba(229,9,20,0.75);margin-bottom:10px'>All Photos</div>", unsafe_allow_html=True)
    gcols = st.columns(3)
    for i, p in enumerate(reversed(photos)):
        p_mime  = p["mime"]
        p_b64   = p["b64"]
        p_label = p["label"]
        p_date  = p["date"]
        src_p   = "data:" + p_mime + ";base64," + p_b64
        with gcols[i % 3]:
            st.markdown(
                "<div style='margin-bottom:14px'>"
                "<img src='" + src_p + "' style='width:100%;border-radius:10px;"
                "border:1px solid rgba(99,102,241,0.25)'>"
                "<div style='display:flex;justify-content:space-between;margin-top:5px;"
                "font-size:0.85rem;color:rgba(255,255,255,0.90)'>"
                "<span>" + p_label + "</span><span>" + p_date + "</span></div></div>",
                unsafe_allow_html=True)

    if st.button("Clear All Photos", key="clear_photos"):
        st.session_state.progress_photos = []
        st.rerun()