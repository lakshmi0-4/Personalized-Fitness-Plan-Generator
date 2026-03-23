# -*- coding: utf-8 -*-
import streamlit as st
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_token import logout
from bg_utils import apply_bg

st.set_page_config(page_title="AI Coach | FitPlan Pro", page_icon="🤖",
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
  background:url('https://images.unsplash.com/photo-1534438327276-14e5300c3a48?fm=jpg&w=1600&q=80&fit=crop') center center/cover no-repeat;
  filter:blur(8px) brightness(0.25) saturate(0.55);
  transform:scale(1.06);
}
[data-testid="stAppViewContainer"]{
  background:linear-gradient(160deg,rgba(2,4,7,0.90) 0%,rgba(3,5,9,0.82) 50%,rgba(2,4,7,0.94) 100%)!important;
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

html,body,.stApp { background:#020407!important; color:#fff!important; font-family:'DM Sans',sans-serif!important; }
[data-testid="stAppViewContainer"]>section>div.block-container {
  max-width:900px!important; margin:0 auto!important; padding:0 24px 80px!important;
  background:rgba(0,0,0,0.35)!important; border-radius:0!important; }
[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] p { color:#fff!important; }

.stButton>button { background:linear-gradient(135deg,rgba(229,9,20,0.85),rgba(160,0,10,0.90))!important;
  border:none!important; color:#fff!important; border-radius:10px!important;
  font-family:'DM Sans',sans-serif!important; font-size:1.0rem!important; font-weight:700!important;
  box-shadow:0 4px 18px rgba(229,9,20,0.35)!important; transition:all 0.20s!important; }
.stButton>button:hover { transform:translateY(-2px)!important; box-shadow:0 6px 26px rgba(229,9,20,0.60)!important; }

.stNumberInput>div>div>input, .stTextInput>div>div>input,
.stTextArea>div>div>textarea, .stSelectbox>div>div>div, .stSelectbox>div>div {
  background:rgba(255,255,255,0.08)!important; border:1.5px solid rgba(255,255,255,0.22)!important;
  color:#fff!important; border-radius:14px!important; backdrop-filter:blur(28px)!important;
  box-shadow:0 2px 10px rgba(0,0,0,0.30)!important; font-family:'DM Sans',sans-serif!important; font-size:1.05rem!important; }
.stNumberInput>div>div>input:focus, .stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus {
  border-color:rgba(229,9,20,0.65)!important; background:rgba(255,255,255,0.12)!important;
  box-shadow:0 0 0 2px rgba(229,9,20,0.20)!important; }
[data-testid="baseButton-secondaryFormSubmit"] button, .stFormSubmitButton>button {
  background:linear-gradient(135deg,#E50914,#c0000c)!important; border:none!important;
  color:#fff!important; border-radius:12px!important; font-weight:700!important;
  box-shadow:0 4px 20px rgba(229,9,20,0.45)!important; letter-spacing:0.5px!important; text-transform:uppercase!important; }
[data-baseweb="select"]>div { background:rgba(255,255,255,0.08)!important;
  border:1.5px solid rgba(255,255,255,0.22)!important; border-radius:14px!important;
  backdrop-filter:blur(28px)!important; color:#fff!important; }
[data-baseweb="select"] span { color:#fff!important; }
[data-baseweb="popover"] [role="option"] { background:rgba(10,6,4,0.92)!important; color:#fff!important; }
[data-baseweb="popover"] [role="option"]:hover { background:rgba(229,9,20,0.25)!important; }

div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stButton"]>button {
  background:rgba(255,255,255,0.08)!important; border:2px solid rgba(229,9,20,0.60)!important;
  color:rgba(255,255,255,0.90)!important; border-radius:9px!important;
  font-size:0.85rem!important; font-weight:700!important; padding:6px 8px!important;
  height:36px!important; min-height:36px!important; backdrop-filter:blur(28px)!important;
  box-shadow:none!important; transition:all 0.15s ease!important; }
div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stButton"]>button:hover {
  background:rgba(229,9,20,0.30)!important; border-color:rgba(229,9,20,0.80)!important;
  color:#fff!important; transform:translateY(-1px)!important; }
div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stButton"]:last-child>button {
  background:rgba(229,9,20,0.35)!important; border:1.5px solid #E50914!important; }

.nav-logo-txt { font-family:'Bebas Neue',sans-serif; font-size:1.4rem; letter-spacing:5px;
  color:#E50914; text-shadow:0 0 18px rgba(229,9,20,0.50); line-height:1; }
.chat-user { background:rgba(229,9,20,0.18); border:2px solid rgba(229,9,20,0.50);
  border-radius:18px 18px 4px 18px; padding:12px 18px; margin:8px 0 8px 60px;
  font-size:1.05rem; color:#fff; line-height:1.65; }
.chat-ai { background:rgba(10,6,4,0.72); border:2px solid rgba(255,255,255,0.16);
  border-radius:18px 18px 18px 4px; padding:14px 18px; margin:8px 60px 8px 0;
  font-size:1.05rem; color:rgba(255,255,255,0.90); line-height:1.65; backdrop-filter:blur(28px); }
.quick-btn .stButton>button {
  background:rgba(255,255,255,0.06)!important; border:1px solid rgba(255,255,255,0.16)!important;
  color:rgba(255,255,255,0.80)!important; font-size:1.05rem!important; font-weight:500!important;
  text-transform:none!important; border-radius:22px!important; padding:6px 16px!important;
  height:auto!important; min-height:auto!important; box-shadow:none!important;
  backdrop-filter:blur(28px)!important; letter-spacing:0!important;
  transition:all 0.14s ease!important; font-style:italic!important; }
.quick-btn .stButton>button:hover { background:rgba(255,255,255,0.14)!important;
  border-color:rgba(255,255,255,0.80)!important; color:#fff!important; transform:none!important; }

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
    "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?fm=jpg&w=1600&q=80&fit=crop",
    overlay="rgba(4,8,14,0.78)"
)

# NAV
st.markdown("<div style='padding:8px 0;margin-bottom:16px'>", unsafe_allow_html=True)
_n = st.columns([1.6,1,1,1,1,1,1,1.2])
with _n[0]: st.markdown("<div class='nav-logo-txt'>&#9889; FITPLAN PRO</div>", unsafe_allow_html=True)
with _n[1]:
    if st.button("Home",      key="ac_db", use_container_width=True): st.switch_page("pages/2_Dashboard.py")
with _n[2]:
    if st.button("Workout",   key="ac_wp", use_container_width=True): st.switch_page("pages/3_Workout_Plan.py")
with _n[3]:
    if st.button("Diet",      key="ac_dp", use_container_width=True): st.switch_page("pages/4_Diet_Plan.py")
with _n[4]:
    if st.button("AI Coach",  key="ac_ai", use_container_width=True): st.switch_page("pages/5_ai_coach.py")
with _n[5]:
    if st.button("Records",   key="ac_rc", use_container_width=True):
        try: st.switch_page("pages/6_records.py")
        except Exception as e: st.warning(str(e))
with _n[6]:
    if st.button("Photos",    key="ac_ph", use_container_width=True):
        try: st.switch_page("pages/7_progress_photos.py")
        except Exception as e: st.warning(str(e))
with _n[7]:
    if st.button("Sign Out",  key="ac_so", use_container_width=True):
        logout(uname)
        for _k in ["logged_in","username","auth_token","user_data","workout_plan","structured_days",
                   "dietary_type","full_plan_data","plan_id","plan_start","plan_duration","plan_for",
                   "force_regen","tracking","_plan_checked","_db_loaded_dash","_auto_redirect",
                   "_diet_chosen","_needs_rerun","_db_streak","edit_profile_mode"]:
            st.session_state.pop(_k, None)
        st.switch_page("app.py")
st.markdown("</div>", unsafe_allow_html=True)

# HERO
st.markdown(
    "<div style='background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.12);"
    "border-radius:20px;padding:32px 40px;margin-bottom:24px;text-align:center;"
    "backdrop-filter:blur(16px);position:relative;overflow:hidden'>"
    "<div style='position:absolute;top:0;left:0;right:0;height:2px;"
    "background:linear-gradient(90deg,transparent,#E50914,transparent)'></div>"
    "<div style='font-size:3rem;margin-bottom:10px'>&#129302;</div>"
    "<div style='font-family:Bebas Neue,sans-serif;font-size:2.2rem;letter-spacing:3px;color:#fff;margin-bottom:6px'>"
    "YOUR AI FITNESS COACH</div>"
    "<div style='font-size:1.00rem;color:rgba(255,255,255,0.85)'>"
    "Knows your profile, workout plan &amp; "
    + str(len(st.session_state.get("structured_days",[]))) +
    "-day plan. Ask anything about your fitness journey.</div></div>",
    unsafe_allow_html=True
)

# Init chat history
if "chat_messages" not in st.session_state:
    try:
        from utils.db import get_chat_history
        _hist = get_chat_history(uname, limit=20)
        st.session_state.chat_messages = _hist if _hist else []
    except Exception:
        st.session_state.chat_messages = []

sdays = st.session_state.get("structured_days", [])
plan_ctx = ""
if sdays:
    plan_ctx = (str(len(sdays)) + "-day plan. Diet: "
                + ("Vegetarian" if st.session_state.get("dietary_type")=="veg" else "Non-Vegetarian") + ". ")

system_prompt = (
    "You are a professional AI fitness coach inside FitPlan Pro. "
    "User: " + uname + ", Age: " + str(data.get("age","?")) +
    ", Weight: " + str(data.get("weight","?")) + "kg"
    ", Height: " + str(data.get("height","?")) + "cm"
    ", Goal: " + data.get("goal","Fitness") +
    ", Level: " + data.get("level","Beginner") +
    ", Equipment: " + (", ".join(data.get("equipment",[])) or "None") + ". " +
    plan_ctx +
    "RULES: 1. Reply in plain English only — NO JSON, NO curly braces, NO code blocks. "
    "2. Be warm, direct, motivating. 3. Keep replies under 120 words. "
    "4. For lists use a dash (-) on a new line. 5. Never start with 'Assistant:'."
)

# Quick questions
st.markdown("<div style='font-size:0.58rem;font-weight:700;letter-spacing:3px;text-transform:uppercase;"
            "color:rgba(229,9,20,0.75);margin-bottom:10px'>Quick Questions</div>", unsafe_allow_html=True)
quick_qs = [
    "What should I eat after today's workout?",
    "How do I improve my form on push-ups?",
    "What's the best time to work out?",
    "How much protein do I need daily?",
    "Should I take rest days seriously?",
    "How do I reduce muscle soreness?",
]
qc = st.columns(3)
for i, q in enumerate(quick_qs):
    with qc[i % 3]:
        st.markdown("<div class='quick-btn'>", unsafe_allow_html=True)
        if st.button(q, key="qq_"+str(i), use_container_width=True):
            st.session_state.chat_messages.append({"role":"user","content":q})
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.10);margin:16px 0'>", unsafe_allow_html=True)

# Chat display
if not st.session_state.chat_messages:
    st.markdown("<div style='text-align:center;padding:30px 20px;color:rgba(255,255,255,0.80);font-size:1.05rem'>"
                "Ask me anything about your workout plan, nutrition, recovery, or fitness goals.</div>",
                unsafe_allow_html=True)
else:
    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.markdown(
                "<div class='chat-user'><b style='color:rgba(229,9,20,0.85);font-size:0.85rem;"
                "letter-spacing:1px;text-transform:uppercase'>You</b><br>" + msg["content"] + "</div>",
                unsafe_allow_html=True)
        else:
            _formatted_lines = []
            for _ln in msg["content"].splitlines():
                _s = _ln.strip()
                if _s.startswith("- ") or _s.startswith("• "):
                    _formatted_lines.append(
                        "<div style='display:flex;gap:8px;margin:3px 0'>"
                        "<span style='color:#E50914;flex-shrink:0'>&#9658;</span>"
                        "<span>" + _s[2:] + "</span></div>")
                elif _s:
                    _formatted_lines.append("<div style='margin-bottom:4px'>" + _s + "</div>")
                else:
                    _formatted_lines.append("<div style='height:6px'></div>")
            st.markdown(
                "<div class='chat-ai'>"
                "<div style='display:flex;align-items:center;gap:6px;margin-bottom:8px'>"
                "<span style='font-size:1rem'>&#129302;</span>"
                "<b style='color:rgba(229,9,20,0.80);font-size:0.85rem;letter-spacing:1px;"
                "text-transform:uppercase'>AI Coach</b></div>"
                + "".join(_formatted_lines) + "</div>",
                unsafe_allow_html=True)

# Process pending AI reply
if st.session_state.chat_messages and st.session_state.chat_messages[-1]["role"] == "user":
    with st.spinner("AI Coach is thinking..."):
        try:
            from model_api import query_model
            history = st.session_state.chat_messages[-8:]
            conv = ""
            for m in history[:-1]:
                conv += ("User" if m["role"]=="user" else "Assistant") + ": " + m["content"] + "\n"
            full_prompt = system_prompt + "\n\nConversation:\n" + conv + "\nUser: " + history[-1]["content"] + "\nAssistant:"
            reply = query_model(full_prompt, max_tokens=300).strip()
            if reply.startswith("Assistant:"): reply = reply[10:].strip()
            if reply.startswith("AI Coach:"):  reply = reply[9:].strip()
            import re as _re
            _clean = [ln for ln in reply.splitlines()
                      if not (ln.strip().startswith("{") or ln.strip().startswith("[")
                              or (ln.strip().startswith('"') and ln.strip().endswith('"},')))]
            reply = _re.sub(r"\{[^}]*\}", "", "\n".join(_clean))
            reply = _re.sub(r"\[[^\]]*\]", "", reply)
            reply = _re.sub(r"\n{3,}", "\n\n", reply).strip()
            if not reply: reply = "Great question! Please try asking again."
            st.session_state.chat_messages.append({"role":"assistant","content":reply})
            try:
                from utils.db import save_chat_history
                save_chat_history(uname, st.session_state.chat_messages[-20:])
            except Exception: pass
            st.rerun()
        except Exception as e:
            st.error("AI error: " + str(e))

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
with st.form("chat_form", clear_on_submit=True):
    inp_col, btn_col = st.columns([5,1])
    with inp_col:
        user_input = st.text_input("", placeholder="Type your question and press Enter or Send →",
                                    key="chat_input_field", label_visibility="collapsed")
    with btn_col:
        send = st.form_submit_button("Send →", use_container_width=True)
    if send and user_input.strip():
        st.session_state.chat_messages.append({"role":"user","content":user_input.strip()})
        st.rerun()

if st.session_state.chat_messages:
    if st.button("Clear Chat", key="clear_chat"):
        st.session_state.chat_messages = []
        st.rerun()