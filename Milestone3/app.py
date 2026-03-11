import streamlit as st
from auth_token import login, initiate_signup, complete_signup
import streamlit.components.v1 as components
import os

st.set_page_config(page_title="FitPlan Pro", page_icon="⚡", layout="wide")

# ── Already logged in → go to profile ────────────────────────────────────────
if st.session_state.get("logged_in"):
    st.switch_page("pages/1_Profile.py")

# ── State init ────────────────────────────────────────────────────────────────
for k, v in [("page_mode","login"),("signup_step","form"),("pending_signup",{})]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Hide Streamlit chrome, make iframe full screen ───────────────────────────
st.markdown("""
<style>
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stSidebarNav"],section[data-testid="stSidebar"]{display:none!important;}
html,body,.stApp,[data-testid="stAppViewContainer"]{
    background:#0d0d1a!important;margin:0!important;padding:0!important;
    height:100%!important;overflow:hidden!important;}
[data-testid="stAppViewContainer"]>section{padding:0!important;margin:0!important;}
[data-testid="stAppViewContainer"]>section>div.block-container{
    padding:0!important;max-width:100%!important;margin:0!important;height:100vh!important;}
iframe{border:none!important;display:block!important;width:100vw!important;
    height:100vh!important;position:fixed!important;top:0!important;left:0!important;z-index:9999!important;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ACTION HANDLERS  (query params set by JS window.location.href inside iframe)
# ══════════════════════════════════════════════════════════════════════════════
params = st.query_params
action = params.get("action", "")

# ── STEP 5: LOGIN ─────────────────────────────────────────────────────────────
if action == "login":
    u = params.get("u", ""); p = params.get("p", "")
    if u and p:
        ok, token, msg = login(u, p)
        if ok:
            st.session_state.logged_in  = True
            st.session_state.username   = u.strip()
            st.session_state.auth_token = token
            st.query_params.clear()
            st.switch_page("pages/1_Profile.py")   # → STEP 6: Profile
        else:
            st.session_state.login_error = msg
            st.query_params.clear(); st.rerun()

# ── STEP 2a: SEND OTP ─────────────────────────────────────────────────────────
if action == "send_otp":
    su = params.get("u",""); se = params.get("e","")
    sp = params.get("p",""); sp2 = params.get("p2","")
    if sp != sp2:
        st.session_state.signup_error = "Passwords don't match."
    elif "@" not in se or "." not in se:
        st.session_state.signup_error = "Enter a valid email address."
    elif len(sp) < 6:
        st.session_state.signup_error = "Password must be at least 6 characters."
    elif not su.strip():
        st.session_state.signup_error = "Username is required."
    else:
        with st.spinner(""):
            ok, msg = initiate_signup(su.strip(), se.strip().lower(), sp)
        if ok:
            if msg == "__NO_OTP__":
                # Brevo not configured — user saved directly, redirect to login
                st.session_state.signup_success = "✓ Account created! Please sign in."
                st.session_state.page_mode  = "login"
                st.session_state.signup_step = "form"
                st.session_state.pending_signup = {}
            else:
                # OTP sent — go to verification step
                st.session_state.pending_signup = {"username": su.strip(), "email": se.strip().lower(), "password": sp}
                st.session_state.signup_step  = "otp"
                st.session_state.signup_error = ""
                st.session_state.page_mode    = "signup"
        else:
            st.session_state.signup_error = msg
            st.session_state.page_mode = "signup"
    st.query_params.clear(); st.rerun()

# ── STEP 2b: VERIFY OTP → STEP 3: CREATE ACCOUNT ────────────────────────────
if action == "verify_otp":
    otp_val = params.get("otp", "")
    # Data travels in URL — never relies on session_state (iframe boundary safe)
    su = params.get("u", "").strip()
    se = params.get("e", "").strip()
    sp = params.get("p", "").strip()
    if not su:   # fallback (same-origin reload)
        pd = st.session_state.get("pending_signup", {})
        su = pd.get("username",""); se = pd.get("email",""); sp = pd.get("password","")
    ok, token, msg = complete_signup(su, se, sp, otp_val)
    if ok:
        # STEP 4: redirect to login after account created
        st.session_state.signup_success = "✓ Account created! Please sign in."
        st.session_state.signup_step    = "form"
        st.session_state.page_mode      = "login"
        st.session_state.pending_signup = {}
    else:
        st.session_state.otp_error   = msg
        st.session_state.signup_step = "otp"
        st.session_state.page_mode   = "signup"
    st.query_params.clear(); st.rerun()

# ── NAV ───────────────────────────────────────────────────────────────────────
if action == "go_signup":
    st.session_state.page_mode = "signup"; st.session_state.signup_step = "form"
    st.query_params.clear(); st.rerun()
if action == "go_login":
    st.session_state.page_mode = "login"
    st.query_params.clear(); st.rerun()
if action == "go_back":
    st.session_state.signup_step    = "form"
    st.session_state.pending_signup = {}
    st.session_state.page_mode      = "signup"
    st.query_params.clear(); st.rerun()

# ── Pop flash messages ────────────────────────────────────────────────────────
login_error    = st.session_state.pop("login_error",    "")
signup_error   = st.session_state.pop("signup_error",   "")
otp_error      = st.session_state.pop("otp_error",      "")
signup_success = st.session_state.pop("signup_success", "")
mode           = st.session_state.page_mode
signup_step    = st.session_state.signup_step
pending        = st.session_state.pending_signup
pending_email  = pending.get("email",    "")
pending_u      = pending.get("username", "")
pending_e      = pending.get("email",    "")
pending_p      = pending.get("password", "")
is_signup      = mode == "signup"

def err(msg):  return f"<div class='msg err'><span>⚠</span>{msg}</div>"  if msg else ""
def good(msg): return f"<div class='msg ok'><span>✓</span>{msg}</div>"   if msg else ""

# ── Config status (shown on signup page) ─────────────────────────────────────
_brevo_ok    = bool(os.environ.get("BREVO_API_KEY","")) and bool(os.environ.get("EMAIL_SENDER",""))
_supabase_ok = bool(os.environ.get("SUPABASE_URL","")) and bool(os.environ.get("SUPABASE_KEY",""))

def cfg_banner():
    lines = []
    if not _supabase_ok:
        lines.append("⚠ SUPABASE_URL/SUPABASE_KEY not set — accounts reset on restart")
    if not _brevo_ok:
        lines.append("⚠ BREVO_API_KEY/EMAIL_SENDER not set — OTP email disabled, direct signup used")
    if not lines: return ""
    return ("<div style='background:rgba(232,124,3,.13);border-left:3px solid #e87c03;"
            "color:#e87c03;font-size:.7rem;padding:8px 12px;border-radius:4px;"
            "margin-bottom:14px;line-height:1.9'>" + "<br>".join(lines) + "</div>")

# ══════════════════════════════════════════════════════════════════════════════
# SVG TILE ICONS
# ══════════════════════════════════════════════════════════════════════════════
SVG_ICONS = {
"barbell":    '<rect x="4" y="28" width="56" height="8" rx="4" fill="currentColor"/><rect x="2" y="21" width="9" height="22" rx="3" fill="currentColor"/><rect x="53" y="21" width="9" height="22" rx="3" fill="currentColor"/><rect x="0" y="25" width="5" height="14" rx="2" fill="currentColor" opacity=".55"/><rect x="59" y="25" width="5" height="14" rx="2" fill="currentColor" opacity=".55"/>',
"dumbbell":   '<rect x="16" y="28" width="32" height="8" rx="4" fill="currentColor"/><rect x="7" y="20" width="11" height="24" rx="3" fill="currentColor"/><rect x="46" y="20" width="11" height="24" rx="3" fill="currentColor"/><rect x="3" y="25" width="7" height="14" rx="2" fill="currentColor" opacity=".55"/><rect x="54" y="25" width="7" height="14" rx="2" fill="currentColor" opacity=".55"/>',
"runner":     '<circle cx="40" cy="9" r="6" fill="currentColor"/><path d="M38 16 L28 30 L16 43" stroke="currentColor" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M28 30 L40 41 L46 56" stroke="currentColor" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M20 19 L42 24 L54 15" stroke="currentColor" stroke-width="4" stroke-linecap="round" fill="none"/>',
"pullup":     '<rect x="4" y="4" width="56" height="7" rx="3.5" fill="currentColor"/><line x1="20" y1="11" x2="20" y2="26" stroke="currentColor" stroke-width="4" stroke-linecap="round"/><line x1="44" y1="11" x2="44" y2="26" stroke="currentColor" stroke-width="4" stroke-linecap="round"/><circle cx="32" cy="33" r="7" fill="currentColor"/><path d="M19 27 Q32 20 45 27" stroke="currentColor" stroke-width="4" fill="none" stroke-linecap="round"/><path d="M25 40 L21 56 M39 40 L43 56" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>',
"bicycle":    '<circle cx="15" cy="45" r="13" stroke="currentColor" stroke-width="3.5" fill="none"/><circle cx="49" cy="45" r="13" stroke="currentColor" stroke-width="3.5" fill="none"/><path d="M15 45 L32 20 L49 45" stroke="currentColor" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/><circle cx="15" cy="45" r="3.5" fill="currentColor"/><circle cx="49" cy="45" r="3.5" fill="currentColor"/>',
"yoga":       '<circle cx="32" cy="8" r="6.5" fill="currentColor"/><line x1="32" y1="15" x2="32" y2="34" stroke="currentColor" stroke-width="4" stroke-linecap="round"/><path d="M8 22 Q20 32 32 28 Q44 32 56 22" stroke="currentColor" stroke-width="4" stroke-linecap="round" fill="none"/><path d="M32 34 L17 52 M32 34 L47 52" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>',
"kettlebell": '<path d="M23 24 Q18 14 24 8 Q32 1 40 8 Q46 14 41 24" stroke="currentColor" stroke-width="4" fill="none" stroke-linecap="round"/><path d="M23 24 Q14 26 13 37 Q11 50 24 56 Q32 60 40 56 Q53 50 51 37 Q49 26 41 24Z" stroke="currentColor" stroke-width="3" fill="currentColor" opacity=".18"/><path d="M23 24 Q14 26 13 37 Q11 50 24 56 Q32 60 40 56 Q53 50 51 37 Q49 26 41 24Z" stroke="currentColor" stroke-width="3" fill="none"/>',
"pushup":     '<circle cx="47" cy="10" r="6" fill="currentColor"/><path d="M47 17 L47 31 L8 31" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M8 31 L4 46" stroke="currentColor" stroke-width="4" stroke-linecap="round"/><line x1="0" y1="46" x2="10" y2="46" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>',
"stopwatch":  '<circle cx="32" cy="37" r="22" stroke="currentColor" stroke-width="3.5" fill="none"/><line x1="32" y1="37" x2="32" y2="21" stroke="currentColor" stroke-width="4" stroke-linecap="round"/><line x1="32" y1="37" x2="45" y2="29" stroke="currentColor" stroke-width="3" stroke-linecap="round"/><line x1="26" y1="6" x2="38" y2="6" stroke="currentColor" stroke-width="3.5" stroke-linecap="round"/><line x1="32" y1="6" x2="32" y2="15" stroke="currentColor" stroke-width="3.5" stroke-linecap="round"/>',
"medal":      '<path d="M22 4 L42 4 L50 20 L32 29 L14 20Z" fill="currentColor" opacity=".22" stroke="currentColor" stroke-width="2.5"/><circle cx="32" cy="45" r="17" stroke="currentColor" stroke-width="3.5" fill="none"/><path d="M32 37 L34.8 42.5 L41 43.4 L36.5 47.8 L37.6 54 L32 51 L26.4 54 L27.5 47.8 L23 43.4 L29.2 42.5Z" fill="currentColor"/>',
"heartrate":  '<path d="M32 54 Q9 39 9 24 Q9 12 20 11 Q28 9 32 19 Q36 9 44 11 Q55 12 55 24 Q55 39 32 54Z" stroke="currentColor" stroke-width="3" fill="currentColor" opacity=".15"/><path d="M32 54 Q9 39 9 24 Q9 12 20 11 Q28 9 32 19 Q36 9 44 11 Q55 12 55 24 Q55 39 32 54Z" stroke="currentColor" stroke-width="3" fill="none"/><path d="M5 33 L15 33 L21 22 L28 44 L34 27 L38 37 L44 33 L59 33" stroke="currentColor" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" fill="none"/>',
"squat":      '<circle cx="32" cy="8" r="6" fill="currentColor"/><line x1="32" y1="14" x2="32" y2="29" stroke="currentColor" stroke-width="4" stroke-linecap="round"/><line x1="13" y1="20" x2="51" y2="20" stroke="currentColor" stroke-width="4" stroke-linecap="round"/><path d="M32 29 L19 46 L15 60 M32 29 L45 46 L49 60" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>',
"plank":      '<circle cx="55" cy="12" r="6" fill="currentColor"/><path d="M55 19 L46 29 L8 29" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none"/><line x1="8" y1="29" x2="4" y2="42" stroke="currentColor" stroke-width="4" stroke-linecap="round"/><line x1="46" y1="29" x2="51" y2="42" stroke="currentColor" stroke-width="4" stroke-linecap="round"/><line x1="0" y1="42" x2="58" y2="42" stroke="currentColor" stroke-width="3.5" stroke-linecap="round"/>',
"boxing":     '<path d="M15 23 Q11 16 14 9 Q20 2 30 8 L48 21 Q56 29 52 39 Q48 45 38 42 L23 37 Q13 34 15 24Z" fill="currentColor" opacity=".18" stroke="currentColor" stroke-width="3"/><path d="M23 37 L19 52 M38 42 L43 56" stroke="currentColor" stroke-width="3.5" stroke-linecap="round"/>',
"flame":      '<path d="M32 60 Q12 50 12 33 Q12 17 26 9 Q22 21 32 24 Q24 12 36 3 Q33 16 43 20 Q54 26 54 40 Q54 53 32 60Z" fill="currentColor" opacity=".2" stroke="currentColor" stroke-width="3"/><path d="M32 60 Q12 50 12 33 Q12 17 26 9 Q22 21 32 24 Q24 12 36 3 Q33 16 43 20 Q54 26 54 40 Q54 53 32 60Z" fill="none" stroke="currentColor" stroke-width="3"/><path d="M32 52 Q20 44 22 35 Q24 28 32 31 Q40 28 42 35 Q44 44 32 52Z" fill="currentColor" opacity=".55"/>',
"target":     '<circle cx="32" cy="32" r="27" stroke="currentColor" stroke-width="3" fill="none"/><circle cx="32" cy="32" r="17" stroke="currentColor" stroke-width="3" fill="none"/><circle cx="32" cy="32" r="7" fill="currentColor"/><line x1="32" y1="3" x2="32" y2="10" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/><line x1="32" y1="54" x2="32" y2="61" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/><line x1="3" y1="32" x2="10" y2="32" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/><line x1="54" y1="32" x2="61" y2="32" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>',
}
TILE_DATA = [
    ("barbell","BARBELL","#2a1f3d","#c4b5fd"),("runner","RUNNING","#1e2d45","#93c5fd"),
    ("dumbbell","DUMBBELL","#2a1f3d","#e0aaff"),("heartrate","CARDIO","#3a1a2a","#fca5a5"),
    ("bicycle","CYCLING","#1a2e2a","#6ee7b7"),("yoga","YOGA","#2a1f3d","#d8b4fe"),
    ("pullup","PULL-UPS","#1a2e25","#86efac"),("kettlebell","KETTLEBELL","#1d2e36","#5eead4"),
    ("stopwatch","INTERVALS","#1e2d45","#7dd3fc"),("pushup","PUSH-UPS","#32210f","#fdba74"),
    ("squat","SQUATS","#1f2040","#a5b4fc"),("plank","PLANK","#2a1f3d","#f0abfc"),
    ("boxing","BOXING","#3a1a1e","#fda4af"),("medal","CHAMPION","#30280e","#fde68a"),
    ("flame","HIIT","#351808","#fed7aa"),("target","GOALS","#1e2d45","#7dd3fc"),
]
def make_tile(i):
    key, label, bg, accent = TILE_DATA[i % len(TILE_DATA)]
    d   = round((i * 0.4) % 4, 1)
    dur = round(3 + (i * 0.3) % 2, 1)
    border = "border-bottom:2px solid rgba(229,9,20,0.45);" if i % 7 == 0 else ""
    return (
        f'<div class="tile" style="background:{bg};animation-delay:{d}s;animation-duration:{dur}s;{border}">'
        f'<svg viewBox="0 0 64 64" fill="none" style="color:{accent};width:clamp(22px,3vw,38px);height:clamp(22px,3vw,38px)">'
        + SVG_ICONS[key] +
        f'</svg><div class="tile-label" style="color:{accent}bb">{label}</div></div>'
    )
tiles_html = "".join(make_tile(i) for i in range(60))

# ══════════════════════════════════════════════════════════════════════════════
# BUILD CARD HTML  (no nested f-strings — plain concatenation)
# ══════════════════════════════════════════════════════════════════════════════
if not is_signup:
    # STEP 4 / STEP 5 — Login page
    card_html = (
        "<div class='card-title'>Sign In</div>"
        + err(login_error) + good(signup_success)
        + """<form id="fLogin">
  <div class="f"><input type="text" id="li_u" placeholder="x" autocomplete="username"><label>Email or Username</label></div>
  <div class="f"><input type="password" id="li_p" placeholder="x" autocomplete="current-password"><label>Password</label></div>
  <button class="btn-main" type="submit">Sign In</button>
</form>
<div class="or-row"><span>OR</span></div>
<div class="switch-row">New here? <a onclick="goSignup()">Create an account.</a></div>
<div class="legal">Your data is encrypted and never shared with third parties.</div>"""
    )

elif signup_step == "otp":
    # STEP 2b — OTP verification
    card_html = (
        "<div class='card-title'>Verify Email</div>"
        + err(otp_error)
        + "<div class='otp-info'><p>We sent a 6-digit code to</p><strong>" + pending_email + "</strong><p style='margin-top:6px;font-size:.68rem'>Check your inbox and spam folder</p></div>"
        + '<form id="fOtp">'
        + '<input type="hidden" id="h_u" value="' + pending_u + '">'
        + '<input type="hidden" id="h_e" value="' + pending_e + '">'
        + '<input type="hidden" id="h_p" value="' + pending_p + '">'
        + """<div class="f"><input class="otp" type="text" id="otp_val" placeholder="000000" maxlength="6" autocomplete="one-time-code" inputmode="numeric"></div>
  <button class="btn-main" type="submit">Verify &amp; Create Account</button>
</form>
<div class="back-link"><button id="backBtn">&#8592; Wrong email? Start over</button></div>
<div class="switch-row">Already a member? <a onclick="goLogin()">Sign in.</a></div>"""
    )

else:
    # STEP 1 — Signup form
    card_html = (
        "<div class='card-title'>Create Account</div>"
        + cfg_banner()
        + err(signup_error)
        + """<form id="fSignup">
  <div class="f"><input type="text" id="su_u" placeholder="x" autocomplete="username"><label>Username</label></div>
  <div class="f"><input type="email" id="su_e" placeholder="x" autocomplete="email"><label>Email Address</label></div>
  <div class="f"><input type="password" id="su_p" placeholder="x" autocomplete="new-password"><label>Password (min 6 chars)</label></div>
  <div class="f"><input type="password" id="su_p2" placeholder="x" autocomplete="new-password"><label>Confirm Password</label></div>
  <button class="btn-main" type="submit">Send Verification Code</button>
</form>
<div class="switch-row">Already a member? <a onclick="goLogin()">Sign in.</a></div>"""
    )

# ══════════════════════════════════════════════════════════════════════════════
# FULL HTML
# ══════════════════════════════════════════════════════════════════════════════
HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap" rel="stylesheet">
<style>
:root{{
  --red:#E50914;--red-h:#f40612;
  --white:#fff;
  --ease:cubic-bezier(0.22,1,0.36,1);
  --spring:cubic-bezier(0.34,1.56,0.64,1);
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
html,body{{
  width:100%;height:100%;overflow:hidden;
  font-family:'DM Sans',sans-serif;
  background:radial-gradient(ellipse 140% 100% at 50% 0%,#1a1040 0%,#0d0d1a 55%,#080810 100%);
  color:#fff;-webkit-font-smoothing:antialiased;
}}

/* ━━ MOSAIC ━━ */
.mosaic{{
  position:fixed;inset:0;z-index:0;overflow:hidden;
  display:grid;grid-template-columns:repeat(10,1fr);grid-template-rows:repeat(6,1fr);
  gap:4px;
  transform:perspective(800px) rotateX(5deg) rotateZ(-6deg) scale(1.5);
  animation:mosaic-pan 40s linear infinite alternate;
}}
@keyframes mosaic-pan{{
  0%  {{transform:perspective(800px) rotateX(5deg) rotateZ(-6deg) scale(1.5) translate(0,0);}}
  100%{{transform:perspective(800px) rotateX(5deg) rotateZ(-6deg) scale(1.5) translate(-3%,4%);}}
}}
.tile{{
  position:relative;display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:6px;
  border-radius:6px;overflow:hidden;
  animation:tile-breathe ease-in-out infinite alternate;
  cursor:default;user-select:none;
  transition:transform 0.15s var(--spring),filter 0.15s,opacity 0.15s;
}}
@keyframes tile-breathe{{
  from{{opacity:0.52;filter:brightness(0.75) saturate(0.8);}}
  to  {{opacity:0.82;filter:brightness(1.2) saturate(1.3);}}
}}
.tile::after{{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,rgba(255,255,255,0) 0%,rgba(255,255,255,0.04) 50%,rgba(255,255,255,0) 100%);
  animation:tile-shimmer 6s ease-in-out infinite;animation-delay:inherit;
}}
@keyframes tile-shimmer{{0%,100%{{opacity:0;}}50%{{opacity:1;}}}}
.tile-label{{font-family:'Bebas Neue',sans-serif;font-size:clamp(0.34rem,0.65vw,0.55rem);letter-spacing:3px;}}

/* ━━ OVERLAY ━━ */
.overlay{{
  position:fixed;inset:0;z-index:1;pointer-events:none;
  background:
    radial-gradient(ellipse 80% 65% at 50% 50%,rgba(13,13,26,.05) 0%,rgba(13,13,26,.55) 60%,rgba(8,8,16,.92) 100%),
    linear-gradient(to bottom,rgba(8,8,16,.55) 0%,rgba(8,8,16,0) 18%,rgba(8,8,16,0) 80%,rgba(8,8,16,.72) 100%);
}}

/* ━━ LOGO ━━ */
.site-logo{{
  position:fixed;top:28px;left:36px;z-index:10;
  font-family:'Bebas Neue',sans-serif;
  font-size:clamp(1.6rem,3vw,2.4rem);letter-spacing:4px;
  color:var(--red);text-shadow:0 0 30px rgba(229,9,20,0.5);
  animation:logo-in 0.8s var(--ease) 0.2s both;
}}
@keyframes logo-in{{from{{opacity:0;transform:translateX(-20px)}}to{{opacity:1;transform:none}}}}

/* ━━ CARD ━━ */
.page{{position:fixed;inset:0;z-index:10;display:flex;align-items:center;justify-content:center;padding:16px;overflow-y:auto;}}
.card{{
  width:100%;max-width:450px;
  background:rgba(12,10,28,0.88);
  border-radius:8px;
  padding:clamp(32px,5vw,52px) clamp(28px,5vw,64px);
  box-shadow:0 8px 48px rgba(0,0,0,0.75),0 0 0 1px rgba(140,100,255,0.06);
  border:1px solid rgba(180,150,255,0.10);
  backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);
  animation:card-in 0.7s var(--ease) 0.1s both;
  flex-shrink:0;
}}
@keyframes card-in{{from{{opacity:0;transform:translateY(24px)}}to{{opacity:1;transform:none}}}}
.card-title{{
  font-family:'Bebas Neue',sans-serif;
  font-size:clamp(1.8rem,3.5vw,2.4rem);
  letter-spacing:1px;color:var(--white);margin-bottom:24px;
}}

/* ━━ FLOATING LABEL INPUTS ━━ */
.f{{margin-bottom:14px;position:relative;}}
.f input{{
  width:100%;height:52px;padding:22px 16px 8px;
  background:rgba(255,255,255,0.09);
  border:1.5px solid rgba(255,255,255,0.18);
  border-radius:4px;font-family:'DM Sans',sans-serif;
  font-size:1rem;color:#fff;outline:none;
  transition:background .2s,border-color .2s,box-shadow .2s;
  -webkit-appearance:none;caret-color:#fff;
}}
.f input::placeholder{{color:transparent;}}
.f label{{
  position:absolute;left:16px;top:50%;transform:translateY(-50%);
  font-size:0.88rem;font-weight:400;color:rgba(255,255,255,0.52);
  pointer-events:none;transition:all 0.2s var(--ease);
}}
.f input:focus+label,
.f input:not(:placeholder-shown)+label{{
  top:10px;transform:none;font-size:0.66rem;
  letter-spacing:0.8px;text-transform:uppercase;
  color:rgba(255,255,255,0.65);font-weight:600;
}}
.f input:focus{{
  background:rgba(255,255,255,0.13);
  border-color:rgba(255,255,255,0.7);
  box-shadow:0 0 0 2px rgba(255,255,255,0.06);
}}
/* OTP input */
.f input.otp{{
  height:68px;padding:0;
  font-family:'Bebas Neue',sans-serif;
  font-size:2.6rem;letter-spacing:20px;
  text-align:center;color:var(--red);
  border-color:rgba(229,9,20,0.35);
  background:rgba(229,9,20,0.05);
  caret-color:var(--red);
}}
.f input.otp:focus{{border-color:var(--red);background:rgba(229,9,20,0.09);box-shadow:0 0 0 2px rgba(229,9,20,0.15);}}

/* ━━ BUTTON ━━ */
.btn-main{{
  width:100%;height:52px;background:var(--red);border:none;border-radius:4px;
  font-family:'DM Sans',sans-serif;font-size:1rem;font-weight:700;
  letter-spacing:0.5px;color:#fff;cursor:pointer;
  position:relative;overflow:hidden;
  transition:background .2s,transform .15s,box-shadow .2s;
  margin-top:8px;box-shadow:0 2px 12px rgba(229,9,20,0.35);
}}
.btn-main::before{{
  content:'';position:absolute;top:0;bottom:0;left:-80%;width:50%;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,0.18),transparent);
  transform:skewX(-15deg);transition:left .5s var(--ease);
}}
.btn-main:hover{{background:var(--red-h);transform:translateY(-1px);box-shadow:0 4px 22px rgba(229,9,20,0.5);}}
.btn-main:hover::before{{left:130%;}}
.btn-main:active{{transform:translateY(0);}}
.btn-main:disabled{{opacity:0.55;cursor:not-allowed;transform:none;box-shadow:none;}}

/* ━━ OR / switch / forgot ━━ */
.or-row{{display:flex;align-items:center;gap:12px;margin:14px 0;}}
.or-row::before,.or-row::after{{content:'';flex:1;height:1px;background:rgba(255,255,255,0.15);}}
.or-row span{{font-size:0.78rem;color:rgba(255,255,255,0.4);letter-spacing:1px;}}
.switch-row{{margin-top:18px;font-size:0.88rem;color:rgba(255,255,255,0.5);text-align:center;}}
.switch-row a{{color:#fff;font-weight:600;cursor:pointer;text-decoration:none;}}
.switch-row a:hover{{text-decoration:underline;}}
.legal{{font-size:0.65rem;color:rgba(255,255,255,0.22);margin-top:14px;line-height:1.7;}}

/* ━━ MESSAGES ━━ */
.msg{{
  display:flex;align-items:flex-start;gap:7px;
  padding:10px 13px;border-radius:4px;
  font-size:0.8rem;font-weight:500;margin-bottom:14px;
  line-height:1.5;animation:msg-in 0.35s var(--spring) both;
}}
@keyframes msg-in{{from{{opacity:0;transform:translateY(-5px)}}to{{opacity:1;transform:none}}}}
.err{{background:rgba(229,9,20,0.12);border-left:3px solid var(--red);color:#ff8090;}}
.ok {{background:rgba(0,200,90,0.1);border-left:3px solid #00c85a;color:#3ddc84;}}

/* ━━ OTP INFO BADGE ━━ */
.otp-info{{
  background:rgba(229,9,20,0.07);border:1px solid rgba(229,9,20,0.2);
  border-radius:6px;padding:14px 16px;margin-bottom:18px;text-align:center;
}}
.otp-info p{{font-size:0.72rem;color:rgba(255,255,255,0.45);margin-bottom:2px;}}
.otp-info strong{{color:var(--red);font-size:0.9rem;display:block;margin:4px 0 2px;}}
.back-link{{text-align:center;margin-top:12px;}}
.back-link button{{font-size:0.72rem;color:rgba(255,255,255,0.35);background:none;border:none;cursor:pointer;font-family:'DM Sans',sans-serif;transition:color 0.2s;}}
.back-link button:hover{{color:rgba(255,255,255,0.75);}}

/* ━━ MOBILE ━━ */
@media(max-width:480px){{
  .site-logo{{top:18px;left:20px;font-size:1.6rem;}}
  .card{{padding:32px 22px;border-radius:6px;max-width:100%;}}
  .mosaic{{grid-template-columns:repeat(5,1fr);grid-template-rows:repeat(8,1fr);}}
}}
</style>
</head>
<body>

<div class="mosaic">{tiles_html}</div>
<div class="overlay"></div>
<div class="site-logo">⚡ FitPlan Pro</div>

<div class="page">
<div class="card">
  {card_html}
</div>
</div>

<script>
function goSignup(){{setTimeout(function(){{window.location.href='?action=go_signup';}},50);}}
function goLogin() {{setTimeout(function(){{window.location.href='?action=go_login';}},50);}}

function shake(el){{
  el.animate([
    {{transform:'translateX(0)'}},{{transform:'translateX(-7px)'}},
    {{transform:'translateX(7px)'}},{{transform:'translateX(-4px)'}},
    {{transform:'translateX(4px)'}},{{transform:'translateX(0)'}}
  ],{{duration:400,easing:'ease-in-out'}});
}}

/* ━━ MAGNETIC HOVER + CLICK BOUNCE ━━ */
(function(){{
  var tiles=[],centres=[],mx=innerWidth/2,my=innerHeight/2,raf=null,R=220,P=22;
  function init(){{
    tiles=Array.from(document.querySelectorAll('.tile'));
    if(!tiles.length){{setTimeout(init,300);return;}}
    cache();
    addEventListener('resize',cache,{{passive:true}});
    document.addEventListener('mousemove',function(e){{
      mx=e.clientX;my=e.clientY;
      if(!raf)raf=requestAnimationFrame(tick);
    }},{{passive:true}});
    tiles.forEach(function(t){{
      t.addEventListener('click',function(){{
        var el=this;el.style.animationPlayState='paused';
        el.animate([
          {{transform:'scale(1.22)',filter:'brightness(2.2) saturate(2)'}},
          {{transform:'scale(0.86)',filter:'brightness(0.9)'}},
          {{transform:'scale(1.06)',filter:'brightness(1.35)'}},
          {{transform:'scale(1)',  filter:'brightness(1)'}}
        ],{{duration:480,easing:'cubic-bezier(.34,1.56,.64,1)'}})
        .onfinish=function(){{el.style.animationPlayState='';}};
      }});
    }});
  }}
  function cache(){{
    centres=tiles.map(function(t){{
      var r=t.getBoundingClientRect();
      return{{x:r.left+r.width*.5,y:r.top+r.height*.5,el:t}};
    }});
  }}
  function tick(){{
    raf=null;
    centres.forEach(function(c){{
      var dx=mx-c.x,dy=my-c.y,d=Math.sqrt(dx*dx+dy*dy);
      if(d<R&&d>0){{
        var s=(1-d/R),mag=s*s*P;
        c.el.style.transform='translate('+(-(dx/d)*mag)+'px,'+(-(dy/d)*mag)+'px) scale('+(1+s*.13)+')';
        c.el.style.filter='brightness('+(1+s*.65)+') saturate('+(1+s*.55)+')';
        c.el.style.opacity=(0.5+s*.5)+'';
        c.el.style.animationPlayState='paused';
      }}else{{
        c.el.style.transform=c.el.style.filter=c.el.style.opacity='';
        c.el.style.animationPlayState='';
      }}
    }});
  }}
  setTimeout(init,300);
}})();

/* ━━ LOGIN FORM ━━ */
var fL=document.getElementById('fLogin');
if(fL) fL.addEventListener('submit',function(e){{
  e.preventDefault();
  var u=document.getElementById('li_u').value.trim();
  var p=document.getElementById('li_p').value;
  if(!u||!p){{shake(fL);return;}}
  var b=fL.querySelector('.btn-main');b.disabled=true;b.textContent='Signing in\u2026';
  window.location.href='?action=login&u='+encodeURIComponent(u)+'&p='+encodeURIComponent(p);
}});

/* ━━ SIGNUP FORM ━━ */
var fS=document.getElementById('fSignup');
if(fS) fS.addEventListener('submit',function(e){{
  e.preventDefault();
  var u=document.getElementById('su_u').value.trim();
  var em=document.getElementById('su_e').value.trim();
  var p=document.getElementById('su_p').value;
  var p2=document.getElementById('su_p2').value;
  if(!u||!em||!p||!p2){{shake(fS);return;}}
  if(p!==p2){{shake(fS);return;}}
  var b=fS.querySelector('.btn-main');b.disabled=true;b.textContent='Sending code\u2026';
  window.location.href='?action=send_otp&u='+encodeURIComponent(u)+'&e='+encodeURIComponent(em)+'&p='+encodeURIComponent(p)+'&p2='+encodeURIComponent(p2);
}});

/* ━━ OTP FORM ━━ */
var fO=document.getElementById('fOtp');
if(fO) fO.addEventListener('submit',function(e){{
  e.preventDefault();
  var otp=document.getElementById('otp_val').value.trim();
  if(!otp||otp.length<6){{shake(fO);return;}}
  var b=fO.querySelector('.btn-main');b.disabled=true;b.textContent='Verifying\u2026';
  var hu=document.getElementById('h_u').value;
  var he=document.getElementById('h_e').value;
  var hp=document.getElementById('h_p').value;
  window.location.href='?action=verify_otp&otp='+encodeURIComponent(otp)
    +'&u='+encodeURIComponent(hu)+'&e='+encodeURIComponent(he)+'&p='+encodeURIComponent(hp);
}});

/* OTP auto-submit at 6 digits */
var otpEl=document.getElementById('otp_val');
if(otpEl){{
  otpEl.addEventListener('input',function(){{
    this.value=this.value.replace(/[^0-9]/g,'');
    if(this.value.length===6){{
      setTimeout(function(){{
        var b=document.querySelector('#fOtp .btn-main');
        if(b&&!b.disabled)b.click();
      }},350);
    }}
  }});
}}

var bb=document.getElementById('backBtn');
if(bb) bb.addEventListener('click',function(){{window.location.href='?action=go_back';}});
</script>
</body>
</html>"""

components.html(HTML, height=900, scrolling=False)
