import streamlit as st
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from prompt_builder import build_prompt
from model_api import query_model
from auth_token import logout

st.set_page_config(page_title="FitPlan Pro – My Plan", page_icon="⚡", layout="wide")

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")
if "user_data" not in st.session_state:
    st.switch_page("pages/1_Profile.py")

uname = st.session_state.get("username", "Athlete")
data  = st.session_state.user_data

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&display=swap');

#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stSidebarNav"],section[data-testid="stSidebar"]{display:none!important;}

html,body,.stApp,[data-testid="stAppViewContainer"]{
  background:#141414!important;color:#fff!important;
  font-family:'DM Sans',sans-serif!important;
}
[data-testid="stAppViewContainer"]>section>div.block-container{
  max-width:960px!important;margin:0 auto!important;
  padding:0 24px 80px!important;
}

/* ━━━ TOPNAV ━━━ */
.topnav{
  position:sticky;top:0;z-index:100;
  display:flex;align-items:center;justify-content:space-between;
  padding:18px 0 14px;
  background:linear-gradient(180deg,#141414 80%,transparent);
  margin-bottom:4px;
}
.nav-logo{font-family:'Bebas Neue',sans-serif;font-size:1.8rem;letter-spacing:4px;color:#E50914;text-shadow:0 0 20px rgba(229,9,20,0.35);}

/* ━━━ HERO BANNER ━━━ */
.plan-hero{
  background:linear-gradient(135deg,#1a0000 0%,#1f1f1f 60%,#0a0a0a 100%);
  border:1px solid rgba(229,9,20,0.2);
  border-radius:8px;padding:36px 40px;
  margin:24px 0 32px;
  position:relative;overflow:hidden;
}
.plan-hero::before{
  content:'';position:absolute;
  top:-40px;right:-40px;width:200px;height:200px;border-radius:50%;
  background:radial-gradient(circle,rgba(229,9,20,0.2),transparent 70%);
  pointer-events:none;
}
.plan-hero-title{
  font-family:'Bebas Neue',sans-serif;
  font-size:clamp(1.8rem,4vw,2.8rem);
  letter-spacing:2px;color:#fff;line-height:1;margin-bottom:6px;
}
.plan-hero-title em{color:#E50914;font-style:normal;}
.plan-hero-sub{font-size:0.85rem;color:rgba(255,255,255,0.45);font-weight:300;}

/* ━━━ STATS ROW ━━━ */
.stats-row{
  display:grid;grid-template-columns:repeat(5,1fr);
  gap:12px;margin-bottom:32px;
}
.stat-card{
  background:#1f1f1f;
  border:1px solid rgba(255,255,255,0.07);
  border-radius:6px;padding:16px 12px 14px;
  text-align:center;
  transition:border-color 0.2s;
}
.stat-card:hover{border-color:rgba(229,9,20,0.35);}
.stat-card-label{
  font-size:0.6rem;font-weight:600;letter-spacing:2.5px;
  text-transform:uppercase;color:rgba(255,255,255,0.35);
  margin-bottom:8px;
}
.stat-card-value{
  font-family:'Bebas Neue',sans-serif;
  font-size:1.7rem;letter-spacing:1px;
  color:#fff;line-height:1;
}
.stat-card-unit{
  font-size:0.62rem;color:rgba(255,255,255,0.3);margin-top:4px;
}
.stat-card.highlight .stat-card-value{color:#E50914;}
.stat-card.highlight{border-color:rgba(229,9,20,0.25);}

/* ━━━ SECTION HEADER ━━━ */
.section-hdr{
  display:flex;align-items:center;gap:10px;
  font-size:0.65rem;font-weight:600;letter-spacing:3px;
  text-transform:uppercase;color:rgba(255,255,255,0.35);
  margin-bottom:16px;
}
.section-hdr::before{content:'';width:20px;height:1px;background:#E50914;flex-shrink:0;}

/* ━━━ TABS (Days) ━━━ */
.stTabs [data-baseweb="tab-list"]{
  background:#1a1a1a!important;
  border-radius:6px!important;
  padding:4px!important;
  gap:4px!important;
  border:1px solid rgba(255,255,255,0.06)!important;
}
.stTabs [data-baseweb="tab"]{
  background:transparent!important;
  color:rgba(255,255,255,0.45)!important;
  border-radius:4px!important;
  font-family:'DM Sans',sans-serif!important;
  font-size:0.82rem!important;font-weight:600!important;
  letter-spacing:0.5px!important;
  border:none!important;
  padding:10px 16px!important;
  transition:all 0.2s!important;
}
.stTabs [data-baseweb="tab"]:hover{
  background:rgba(255,255,255,0.06)!important;
  color:rgba(255,255,255,0.8)!important;
}
.stTabs [aria-selected="true"]{
  background:#E50914!important;
  color:#fff!important;
}
.stTabs [data-baseweb="tab-highlight"]{display:none!important;}
.stTabs [data-baseweb="tab-border"]{display:none!important;}

/* ━━━ PLAN CONTENT CARD ━━━ */
.plan-card{
  background:#1a1a1a;
  border:1px solid rgba(255,255,255,0.07);
  border-radius:8px;padding:32px 36px;
  color:rgba(255,255,255,0.85);
  line-height:1.9;font-size:0.92rem;font-weight:300;
  min-height:300px;
}
.plan-card h2,.plan-card h3{
  font-family:'Bebas Neue',sans-serif;
  color:#fff;letter-spacing:1.5px;margin:20px 0 10px 0;
  font-size:1.3rem;font-weight:400;
}
.plan-card strong{color:#fff;font-weight:600;}
.plan-card ul{margin:8px 0 8px 18px;}
.plan-card li{margin-bottom:4px;color:rgba(255,255,255,0.75);}
/* Highlight sets/reps inline */
.plan-card .badge{
  display:inline-block;background:rgba(229,9,20,0.18);
  border:1px solid rgba(229,9,20,0.3);
  border-radius:3px;padding:1px 7px;
  font-size:0.75rem;font-weight:600;color:#E50914;
  margin:0 3px;
}

/* ━━━ ACTION BUTTONS ━━━ */
.stButton>button{
  background:transparent!important;
  border:1.5px solid rgba(255,255,255,0.25)!important;
  color:rgba(255,255,255,0.7)!important;
  border-radius:4px!important;
  font-family:'DM Sans',sans-serif!important;
  font-size:0.85rem!important;font-weight:600!important;
  padding:12px 24px!important;
  transition:all 0.2s!important;
  letter-spacing:0.5px!important;
}
.stButton>button:hover{
  background:rgba(255,255,255,0.06)!important;
  border-color:rgba(255,255,255,0.6)!important;
  color:#fff!important;
  transform:translateY(-1px)!important;
}

/* Primary regen button */
.regen-btn .stButton>button{
  background:#E50914!important;border-color:#E50914!important;
  color:#fff!important;
  box-shadow:0 4px 20px rgba(229,9,20,0.3)!important;
}
.regen-btn .stButton>button:hover{
  background:#f6121d!important;border-color:#f6121d!important;
  box-shadow:0 6px 28px rgba(229,9,20,0.5)!important;
}

/* Logout */
.logout-btn .stButton>button{
  background:transparent!important;
  border:1.5px solid rgba(255,255,255,0.2)!important;
  color:rgba(255,255,255,0.5)!important;
  padding:8px 18px!important;
  font-size:0.78rem!important;
  box-shadow:none!important;
}
.logout-btn .stButton>button:hover{
  border-color:rgba(255,255,255,0.5)!important;
  color:#fff!important;transform:none!important;box-shadow:none!important;
}

/* ━━━ SPINNER ━━━ */
.stSpinner>div{border-top-color:#E50914!important;}
[data-testid="stSpinner"] p{color:rgba(255,255,255,0.5)!important;font-size:0.85rem!important;}

/* ━━━ MOTIVATIONAL FOOTER ━━━ */
.motive-card{
  background:linear-gradient(135deg,#1a0000,#111);
  border:1px solid rgba(229,9,20,0.2);
  border-radius:8px;padding:28px 32px;
  margin-top:28px;
  display:flex;align-items:center;gap:20px;
}
.motive-icon{font-size:2.2rem;flex-shrink:0;}
.motive-text{font-size:0.95rem;color:rgba(255,255,255,0.65);line-height:1.7;font-weight:300;}
.motive-text strong{color:#fff;font-size:1rem;}

hr{border:none!important;border-top:1px solid rgba(255,255,255,0.06)!important;margin:28px 0!important;}
</style>
""", unsafe_allow_html=True)

# ── BUILD PROMPT + BMI ──
from prompt_builder import build_prompt
prompt, bmi, category = build_prompt(
    name=data["name"], gender=data["gender"],
    height=data["height"], weight=data["weight"],
    goal=data["goal"], fitness_level=data["level"],
    equipment=data["equipment"]
)

# ── TOPNAV ──
c1, c2, c3 = st.columns([3,4,2])
with c1:
    st.markdown("<div class='nav-logo'>⚡ FitPlan Pro</div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div style='padding-top:8px;text-align:center;font-size:0.82rem;color:rgba(255,255,255,0.4)'>Logged in as <strong style='color:#fff'>{uname}</strong></div>", unsafe_allow_html=True)
with c3:
    st.markdown("<div class='logout-btn'>", unsafe_allow_html=True)
    if st.button("Sign Out", key="nav_logout"):
        logout(st.session_state.get("username",""))
        for k in ["logged_in","username","auth_token","user_data","workout_plan","plan_for"]:
            st.session_state.pop(k, None)
        st.switch_page("app.py")
    st.markdown("</div>", unsafe_allow_html=True)

# ── HERO BANNER ──
bmi_label = f"{bmi:.1f} · {category}"
st.markdown(f"""
<div class='plan-hero'>
  <div class='plan-hero-title'>{data['name'].upper()}'S <em>5-DAY PLAN</em></div>
  <div class='plan-hero-sub'>Goal: {data['goal']} &nbsp;·&nbsp; Level: {data['level']} &nbsp;·&nbsp; BMI: {bmi_label}</div>
</div>
""", unsafe_allow_html=True)

# ── STATS ──
bmi_cls = "highlight" if category != "Normal Weight" else ""
stats_html = f"""<div class='stats-row'>
  <div class='stat-card'>
    <div class='stat-card-label'>Age</div>
    <div class='stat-card-value'>{data['age']}</div>
    <div class='stat-card-unit'>years</div>
  </div>
  <div class='stat-card'>
    <div class='stat-card-label'>Height</div>
    <div class='stat-card-value'>{data['height']}</div>
    <div class='stat-card-unit'>cm</div>
  </div>
  <div class='stat-card'>
    <div class='stat-card-label'>Weight</div>
    <div class='stat-card-value'>{data['weight']}</div>
    <div class='stat-card-unit'>kg</div>
  </div>
  <div class='stat-card {bmi_cls}'>
    <div class='stat-card-label'>BMI</div>
    <div class='stat-card-value'>{bmi:.1f}</div>
    <div class='stat-card-unit'>{category}</div>
  </div>
  <div class='stat-card'>
    <div class='stat-card-label'>Goal</div>
    <div class='stat-card-value' style='font-size:1rem;margin-top:4px;'>{data['goal'][:12]}</div>
    <div class='stat-card-unit'>{data['level']}</div>
  </div>
</div>"""
st.markdown(stats_html, unsafe_allow_html=True)

# ── GENERATE PLAN ──
if "workout_plan" not in st.session_state or st.session_state.get("plan_for") != data["name"]:
    with st.spinner("⚡ Generating your personalised 5-day plan…"):
        try:
            workout_plan = query_model(prompt)
            st.session_state.workout_plan = workout_plan
            st.session_state.plan_for = data["name"]
        except Exception as e:
            st.error(f"Model error: {e}")
            st.stop()
else:
    workout_plan = st.session_state.workout_plan

# ── PARSE INTO DAY BLOCKS ──
lines = workout_plan.split("\n")
day_blocks, current = [], []
for line in lines:
    stripped = line.strip()
    is_day_header = (
        re.match(r"^#{1,3}\s*day\s*\d", stripped, re.I) or
        re.match(r"^day\s*\d", stripped, re.I)
    )
    if is_day_header and current:
        day_blocks.append("\n".join(current))
        current = [line]
    else:
        current.append(line)
if current:
    day_blocks.append("\n".join(current))

# ── RENDER TABS ──
st.markdown("<div class='section-hdr'>Your Workout Schedule</div>", unsafe_allow_html=True)

def fmt_block(text):
    """Format raw plan text into readable HTML"""
    html = ""
    for line in text.split("\n"):
        s = line.strip()
        if not s:
            html += "<br>"
            continue
        # Day headers
        if re.match(r"^#{1,3}\s*day", s, re.I) or re.match(r"^day\s*\d", s, re.I):
            clean = re.sub(r"^#+\s*","",s)
            html += f"<h2>{clean.upper()}</h2>"
        # Sub-section headers
        elif s.startswith("###") or s.startswith("**") and s.endswith("**"):
            clean = re.sub(r"[*#]","",s).strip()
            html += f"<h3>{clean}</h3>"
        # Bullet or numbered list
        elif re.match(r"^[-•*]\s+",s) or re.match(r"^\d+\.\s+",s):
            content = re.sub(r"^[-•*\d\.]+\s+","",s)
            # Highlight sets x reps pattern
            content = re.sub(
                r"(\d+\s*[xX×]\s*\d+(?:\s*reps?)?)",
                r'<span class="badge">\1</span>', content
            )
            content = re.sub(r"\*\*(.+?)\*\*",r"<strong>\1</strong>",content)
            html += f"<li>{content}</li>"
        else:
            clean = re.sub(r"\*\*(.+?)\*\*",r"<strong>\1</strong>",s)
            html += f"<p>{clean}</p>"
    return html

if len(day_blocks) >= 2:
    labels = []
    for i, blk in enumerate(day_blocks):
        first_line = blk.strip().split("\n")[0]
        first_line = re.sub(r"^#+\s*","",first_line).strip()
        short = first_line[:22] if first_line else f"Day {i+1}"
        labels.append(short)

    tabs = st.tabs(labels)
    for tab, block in zip(tabs, day_blocks):
        with tab:
            st.markdown(
                f"<div class='plan-card'>{fmt_block(block)}</div>",
                unsafe_allow_html=True
            )
else:
    st.markdown(
        f"<div class='plan-card'>{fmt_block(workout_plan)}</div>",
        unsafe_allow_html=True
    )

# ── MOTIVATIONAL FOOTER ──
motive_lines = [l.strip() for l in workout_plan.split("\n") if l.strip() and len(l.strip()) > 60]
motive_text  = motive_lines[-1] if motive_lines else f"Keep pushing, {data['name']}. Every rep counts."
st.markdown(f"""
<div class='motive-card'>
  <div class='motive-icon'>🔥</div>
  <div class='motive-text'><strong>Your Coach Says:</strong><br>{motive_text}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── ACTION BUTTONS ──
ca, cb, cc = st.columns(3)
with ca:
    st.markdown("<div class='regen-btn'>", unsafe_allow_html=True)
    if st.button("⚡  Regenerate Plan", use_container_width=True):
        st.session_state.pop("workout_plan", None)
        st.session_state.pop("plan_for", None)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
with cb:
    if st.button("✏️  Edit Profile", use_container_width=True):
        st.switch_page("pages/1_Profile.py")
with cc:
    st.markdown("<div class='logout-btn'>", unsafe_allow_html=True)
    if st.button("🚪  Sign Out", use_container_width=True):
        logout(st.session_state.get("username",""))
        for k in ["logged_in","username","auth_token","user_data","workout_plan","plan_for"]:
            st.session_state.pop(k, None)
        st.switch_page("app.py")
    st.markdown("</div>", unsafe_allow_html=True)
