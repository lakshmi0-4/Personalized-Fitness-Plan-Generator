"""
utils/workout_components.py — Reusable UI components for workout pages.
Includes: countdown timer, safety cautions, pre/post stretch video embeds.
"""

import streamlit as st
import json, os

# ══════════════════════════════════════════════════════════════════════════════
# SAFETY CAUTIONS
# ══════════════════════════════════════════════════════════════════════════════

PRE_WORKOUT_CAUTIONS = [
    ("🔥", "Always warm up for at least 5 minutes before starting"),
    ("💧", "Drink water before you begin — stay hydrated throughout"),
    ("🩺", "If you have any injury or pain, consult a doctor first"),
    ("👟", "Wear proper footwear and workout on a non-slip surface"),
    ("😴", "Never train on no sleep — rest is part of the programme"),
    ("🧘", "Take deep breaths — controlled breathing improves performance"),
]

DURING_WORKOUT_CAUTIONS = [
    ("✅", "Maintain proper form — quality over quantity always"),
    ("🛑", "Stop immediately if you feel sharp pain or dizziness"),
    ("💧", "Sip water between sets — do not chug large amounts"),
    ("⏱️", "Respect your rest periods — they are part of the programme"),
    ("🔄", "Control the movement in both directions (concentric + eccentric)"),
    ("📏", "Use full range of motion unless instructed otherwise"),
]

POST_WORKOUT_CAUTIONS = [
    ("🧊", "Cool down for 5–10 minutes — never stop suddenly"),
    ("🥗", "Eat a protein + carb meal within 45 minutes of finishing"),
    ("💧", "Rehydrate — drink at least 500ml water post workout"),
    ("😴", "Get 7–9 hours of sleep for muscle recovery"),
    ("📅", "Log your workout — tracking drives progress"),
    ("🚿", "Shower after workout to prevent skin irritation"),
]


def render_safety_cautions(phase="pre"):
    """
    Render safety caution cards.
    phase: 'pre' | 'during' | 'post'
    """
    cautions_map = {
        "pre":    (PRE_WORKOUT_CAUTIONS,    "⚠️ PRE-WORKOUT SAFETY CAUTIONS",    "rgba(251,191,36,0.12)",  "rgba(251,191,36,0.30)"),
        "during": (DURING_WORKOUT_CAUTIONS, "🛡️ DURING WORKOUT — STAY SAFE",      "rgba(239,68,68,0.10)",   "rgba(239,68,68,0.28)"),
        "post":   (POST_WORKOUT_CAUTIONS,   "✅ POST-WORKOUT RECOVERY TIPS",       "rgba(34,197,94,0.10)",   "rgba(34,197,94,0.28)"),
    }

    cautions, title, bg, border = cautions_map.get(phase, cautions_map["pre"])

    items_html = "".join(
        f"""<div style='display:flex;align-items:flex-start;gap:12px;
                        padding:9px 0;border-bottom:1px solid rgba(255,255,255,0.04)'>
              <span style='font-size:1.1rem;flex-shrink:0'>{icon}</span>
              <span style='font-size:0.83rem;color:rgba(255,255,255,0.75);
                           line-height:1.5'>{text}</span>
            </div>"""
        for icon, text in cautions
    )

    st.markdown(f"""
    <div style='background:{bg};border:1px solid {border};
                border-radius:14px;padding:20px 24px;margin:16px 0'>
      <div style='font-size:0.60rem;font-weight:700;letter-spacing:3px;
                  text-transform:uppercase;color:rgba(255,255,255,0.60);
                  margin-bottom:14px'>{title}</div>
      {items_html}
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# COUNTDOWN TIMER
# ══════════════════════════════════════════════════════════════════════════════

def render_exercise_timer(exercise_name, seconds, timer_key):
    """
    Render a JavaScript countdown timer for an exercise.

    exercise_name : display name of the exercise
    seconds       : timer duration in seconds
    timer_key     : unique key to avoid conflicts between multiple timers
    """
    mins = seconds // 60
    secs = seconds % 60
    display_time = f"{mins:02d}:{secs:02d}" if mins > 0 else f"{seconds}s"

    st.markdown(f"""
    <div id="timer-container-{timer_key}" style='
        background:rgba(10,6,4,0.70);
        border:1.5px solid rgba(229,9,20,0.35);
        border-radius:16px;padding:24px 20px;
        text-align:center;margin:12px 0;
        backdrop-filter:blur(12px);
        box-shadow:0 0 20px rgba(229,9,20,0.15);
        position:relative;overflow:hidden;'>

      <!-- red top line -->
      <div style='position:absolute;top:0;left:0;right:0;height:2px;
                  background:linear-gradient(90deg,transparent,
                  rgba(229,9,20,0.60),transparent)'></div>

      <!-- Exercise label -->
      <div style='font-size:0.60rem;font-weight:700;letter-spacing:3px;
                  text-transform:uppercase;color:rgba(229,9,20,0.70);
                  margin-bottom:8px'>⏱ TIMER</div>
      <div style='font-size:0.92rem;color:rgba(255,255,255,0.65);
                  margin-bottom:12px;font-weight:500'>{exercise_name}</div>

      <!-- Timer display -->
      <div id="timer-display-{timer_key}" style='
          font-family:Bebas Neue,sans-serif;
          font-size:3.8rem;color:#E50914;
          letter-spacing:4px;line-height:1;
          text-shadow:0 0 30px rgba(229,9,20,0.55);
          margin-bottom:16px;
          transition:color 0.3s;'>{display_time}</div>

      <!-- Progress ring (CSS circle) -->
      <div style='margin:0 auto 16px;width:80px;height:6px;
                  background:rgba(255,255,255,0.08);border-radius:3px;overflow:hidden'>
        <div id="timer-bar-{timer_key}" style='width:100%;height:100%;
             background:linear-gradient(90deg,#E50914,#ff4444);
             border-radius:3px;transition:width 0.9s linear'></div>
      </div>

      <!-- Buttons -->
      <div style='display:flex;gap:10px;justify-content:center;flex-wrap:wrap'>
        <button onclick="startTimer_{timer_key}()" id="btn-start-{timer_key}"
          style='background:linear-gradient(135deg,#E50914,#c0000c);
                 border:none;color:white;padding:10px 24px;border-radius:8px;
                 cursor:pointer;font-size:0.85rem;font-weight:700;
                 letter-spacing:1px;text-transform:uppercase;
                 box-shadow:0 0 16px rgba(229,9,20,0.45);
                 transition:all 0.2s'>▶ START</button>
        <button onclick="pauseTimer_{timer_key}()" id="btn-pause-{timer_key}"
          style='background:rgba(255,255,255,0.08);
                 border:1px solid rgba(255,255,255,0.20);
                 color:rgba(255,255,255,0.70);padding:10px 20px;
                 border-radius:8px;cursor:pointer;font-size:0.85rem;
                 font-weight:700;letter-spacing:1px;text-transform:uppercase;
                 transition:all 0.2s'>⏸ PAUSE</button>
        <button onclick="resetTimer_{timer_key}()" id="btn-reset-{timer_key}"
          style='background:rgba(255,255,255,0.05);
                 border:1px solid rgba(255,255,255,0.12);
                 color:rgba(255,255,255,0.50);padding:10px 18px;
                 border-radius:8px;cursor:pointer;font-size:0.85rem;
                 font-weight:700;letter-spacing:1px;text-transform:uppercase'>↺ RESET</button>
      </div>

      <!-- Done message (hidden) -->
      <div id="timer-done-{timer_key}" style='display:none;margin-top:14px;
           font-family:Bebas Neue,sans-serif;font-size:1.6rem;
           letter-spacing:3px;color:#22c55e;
           text-shadow:0 0 20px rgba(34,197,94,0.55)'>
        ✓ TIME'S UP! WELL DONE!
      </div>
    </div>

    <script>
    (function() {{
      const TOTAL_{timer_key} = {seconds};
      let timeLeft_{timer_key} = TOTAL_{timer_key};
      let running_{timer_key} = false;
      let interval_{timer_key} = null;

      function formatTime(s) {{
        const m = Math.floor(s / 60);
        const sec = s % 60;
        if (m > 0) return String(m).padStart(2,'0') + ':' + String(sec).padStart(2,'0');
        return s + 's';
      }}

      function updateDisplay() {{
        const disp = document.getElementById('timer-display-{timer_key}');
        const bar  = document.getElementById('timer-bar-{timer_key}');
        const done = document.getElementById('timer-done-{timer_key}');
        if (!disp) return;

        const pct = (timeLeft_{timer_key} / TOTAL_{timer_key}) * 100;
        disp.textContent = formatTime(timeLeft_{timer_key});
        if (bar) bar.style.width = pct + '%';

        // Change color when low
        if (timeLeft_{timer_key} <= 5) {{
          disp.style.color = '#ef4444';
          disp.style.textShadow = '0 0 40px rgba(239,68,68,0.80)';
        }} else if (timeLeft_{timer_key} <= 10) {{
          disp.style.color = '#fbbf24';
          disp.style.textShadow = '0 0 30px rgba(251,191,36,0.60)';
        }}

        if (timeLeft_{timer_key} <= 0) {{
          clearInterval(interval_{timer_key});
          running_{timer_key} = false;
          disp.textContent = '✓';
          disp.style.color = '#22c55e';
          disp.style.textShadow = '0 0 30px rgba(34,197,94,0.70)';
          if (bar) bar.style.width = '0%';
          if (done) done.style.display = 'block';
          // Play beep if available
          try {{
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            [880, 1100, 1320].forEach((freq, i) => {{
              const osc = ctx.createOscillator();
              const gain = ctx.createGain();
              osc.connect(gain); gain.connect(ctx.destination);
              osc.frequency.value = freq;
              gain.gain.setValueAtTime(0.3, ctx.currentTime + i*0.18);
              gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i*0.18 + 0.3);
              osc.start(ctx.currentTime + i*0.18);
              osc.stop(ctx.currentTime + i*0.18 + 0.3);
            }});
          }} catch(e) {{}}
        }}
      }}

      window['startTimer_{timer_key}'] = function() {{
        if (running_{timer_key} || timeLeft_{timer_key} <= 0) return;
        running_{timer_key} = true;
        const done = document.getElementById('timer-done-{timer_key}');
        if (done) done.style.display = 'none';
        interval_{timer_key} = setInterval(() => {{
          timeLeft_{timer_key}--;
          updateDisplay();
        }}, 1000);
      }};

      window['pauseTimer_{timer_key}'] = function() {{
        if (!running_{timer_key}) return;
        clearInterval(interval_{timer_key});
        running_{timer_key} = false;
      }};

      window['resetTimer_{timer_key}'] = function() {{
        clearInterval(interval_{timer_key});
        running_{timer_key} = false;
        timeLeft_{timer_key} = TOTAL_{timer_key};
        const disp = document.getElementById('timer-display-{timer_key}');
        const bar  = document.getElementById('timer-bar-{timer_key}');
        const done = document.getElementById('timer-done-{timer_key}');
        if (disp) {{ disp.textContent = formatTime(TOTAL_{timer_key}); disp.style.color = '#E50914'; disp.style.textShadow = '0 0 30px rgba(229,9,20,0.55)'; }}
        if (bar)  bar.style.width = '100%';
        if (done) done.style.display = 'none';
      }};
    }})();
    </script>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STRETCH VIDEO EMBEDS
# ══════════════════════════════════════════════════════════════════════════════

def _load_stretch_videos():
    """Load stretch video data from JSON file."""
    paths = [
        "data/stretch_videos.json",
        os.path.join(os.path.dirname(__file__), "..", "data", "stretch_videos.json"),
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return json.load(open(p))
            except Exception:
                pass
    # Fallback defaults
    return {
        "pre_workout": [
            {"name": "Full Body Warm-Up", "duration": "5 min",
             "url": "https://www.youtube.com/embed/HDiHMHBpHBQ"},
        ],
        "post_workout": [
            {"name": "Full Body Cool Down", "duration": "5 min",
             "url": "https://www.youtube.com/embed/qULTwquOuT4"},
        ]
    }


def render_stretch_videos(phase="pre"):
    """
    Render embedded YouTube stretch/warm-up videos.
    phase: 'pre' | 'post'
    """
    data = _load_stretch_videos()
    key  = "pre_workout" if phase == "pre" else "post_workout"
    videos = data.get(key, [])

    if not videos:
        return

    title = "🔥 PRE-WORKOUT WARM-UP VIDEOS" if phase == "pre" else "🧊 POST-WORKOUT COOL-DOWN VIDEOS"
    border_color = "rgba(251,191,36,0.30)" if phase == "pre" else "rgba(34,197,94,0.28)"
    header_color = "#fbbf24" if phase == "pre" else "#22c55e"

    st.markdown(f"""
    <div style='border-top:1px solid {border_color};padding-top:20px;margin-top:20px'>
      <div style='font-size:0.60rem;font-weight:700;letter-spacing:3px;
                  text-transform:uppercase;color:{header_color};
                  margin-bottom:16px;display:flex;align-items:center;gap:8px'>
        <span style='display:block;width:18px;height:1.5px;
                     background:{header_color};border-radius:1px'></span>
        {title}
      </div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(min(len(videos), 3))
    for col, video in zip(cols, videos):
        with col:
            st.markdown(f"""
            <div style='background:rgba(10,6,4,0.60);
                        border:1px solid rgba(255,255,255,0.08);
                        border-radius:12px;overflow:hidden;margin-bottom:12px'>
              <div style='position:relative;padding-bottom:56.25%;height:0;overflow:hidden'>
                <iframe src="{video['url']}"
                  style='position:absolute;top:0;left:0;width:100%;height:100%;border:none'
                  allow="accelerometer;autoplay;clipboard-write;encrypted-media;
                         gyroscope;picture-in-picture"
                  allowfullscreen></iframe>
              </div>
              <div style='padding:10px 14px'>
                <div style='font-size:0.82rem;font-weight:600;color:#fff;
                             margin-bottom:4px'>{video['name']}</div>
                <div style='font-size:0.70rem;color:rgba(255,255,255,0.40)'>
                  ⏱ {video['duration']}
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# COMBINED WORKOUT DAY SECTION (pre-caution + timer per exercise + post-caution)
# ══════════════════════════════════════════════════════════════════════════════

def render_full_workout_day(day_data, day_num):
    """
    Render a complete workout day with:
    1. Pre-workout cautions
    2. Pre-workout stretch videos
    3. Exercise cards with individual timers
    4. During-workout cautions
    5. Post-workout stretch videos
    6. Post-workout cautions
    """
    exercises   = day_data.get("workout", [])
    pre_stretch = day_data.get("pre_stretch", [])
    post_stretch= day_data.get("post_stretch", [])
    muscle_grp  = day_data.get("muscle_group", "Full Body")

    # ── Day header ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:12px;margin-bottom:20px'>
      <div style='font-family:Barlow Condensed,sans-serif;font-size:2.2rem;
                  font-weight:900;text-transform:uppercase;color:#fff'>
        Day {day_num}
        <span style='color:#E50914'>— {muscle_grp}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 1. PRE-WORKOUT CAUTIONS ───────────────────────────────────────────
    with st.expander("⚠️ Pre-Workout Safety Cautions — Read Before Starting", expanded=False):
        render_safety_cautions("pre")

    # ── 2. PRE-WORKOUT STRETCH VIDEOS ────────────────────────────────────
    with st.expander("🔥 Warm-Up Videos — Watch Before Starting", expanded=False):
        if pre_stretch:
            # Use day-specific stretch videos if model provided them
            for stretch in pre_stretch:
                st.markdown(f"""
                <div style='display:flex;align-items:center;gap:12px;
                            padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.05)'>
                  <span style='color:#fbbf24;font-size:1.1rem'>🔥</span>
                  <div>
                    <div style='font-size:0.88rem;color:#fff;font-weight:600'>
                      {stretch.get('name','Stretch')}</div>
                    <div style='font-size:0.72rem;color:rgba(255,255,255,0.42)'>
                      ⏱ {stretch.get('duration','30s')}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
        render_stretch_videos("pre")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── 3. EXERCISES WITH TIMERS ──────────────────────────────────────────
    st.markdown("""
    <div style='font-size:0.62rem;font-weight:700;letter-spacing:3px;
                text-transform:uppercase;color:rgba(229,9,20,0.75);
                margin-bottom:16px;display:flex;align-items:center;gap:8px'>
      <span style='display:block;width:18px;height:1.5px;
                   background:#E50914;border-radius:1px'></span>
      💪 MAIN WORKOUT
    </div>
    """, unsafe_allow_html=True)

    EX_ICONS = ["🏋️","💪","🔄","⬆️","🦵","🤸","🏃","🚴","🧗","🥊","🏊","🤼"]

    for idx, ex in enumerate(exercises):
        name  = ex.get("name",  f"Exercise {idx+1}")
        sets  = ex.get("sets",  3)
        reps  = ex.get("reps",  "12")
        rest  = ex.get("rest",  "60s")
        timer = ex.get("timer", 60)
        notes = ex.get("notes", "Maintain proper form throughout")
        icon  = EX_ICONS[idx % len(EX_ICONS)]

        with st.expander(f"{icon} {name} — {sets} sets × {reps} reps", expanded=False):
            col_info, col_timer = st.columns([1.4, 1])

            with col_info:
                st.markdown(f"""
                <div style='background:rgba(10,6,4,0.55);
                            border:1px solid rgba(229,9,20,0.18);
                            border-radius:12px;padding:18px 20px;height:100%'>
                  <div style='font-size:0.60rem;font-weight:700;letter-spacing:2.5px;
                               text-transform:uppercase;
                               color:rgba(229,9,20,0.70);margin-bottom:12px'>
                    EXERCISE DETAILS
                  </div>
                  <div style='display:flex;gap:10px;margin-bottom:14px;flex-wrap:wrap'>
                    <div style='background:rgba(100,160,255,0.13);
                                border:1px solid rgba(100,160,255,0.24);
                                border-radius:8px;padding:8px 14px;text-align:center'>
                      <div style='font-size:1.3rem;font-weight:800;color:#93c5fd'>{sets}</div>
                      <div style='font-size:0.50rem;letter-spacing:1.5px;
                                  color:rgba(255,255,255,0.45)'>SETS</div>
                    </div>
                    <div style='background:rgba(100,230,180,0.11);
                                border:1px solid rgba(100,230,180,0.21);
                                border-radius:8px;padding:8px 14px;text-align:center'>
                      <div style='font-size:1.3rem;font-weight:800;color:#6ee7b7'>{reps}</div>
                      <div style='font-size:0.50rem;letter-spacing:1.5px;
                                  color:rgba(255,255,255,0.45)'>REPS</div>
                    </div>
                    <div style='background:rgba(255,180,80,0.11);
                                border:1px solid rgba(255,180,80,0.21);
                                border-radius:8px;padding:8px 14px;text-align:center'>
                      <div style='font-size:1.3rem;font-weight:800;color:#fdba74'>{rest}</div>
                      <div style='font-size:0.50rem;letter-spacing:1.5px;
                                  color:rgba(255,255,255,0.45)'>REST</div>
                    </div>
                  </div>
                  <div style='font-size:0.75rem;color:rgba(255,255,255,0.60);
                               line-height:1.6;border-top:1px solid rgba(255,255,255,0.07);
                               padding-top:10px'>
                    <span style='color:rgba(229,9,20,0.70);font-weight:700'>Form tip: </span>
                    {notes}
                  </div>
                </div>
                """, unsafe_allow_html=True)

            with col_timer:
                render_exercise_timer(name, timer, f"d{day_num}_ex{idx}")

    # ── 4. DURING-WORKOUT CAUTIONS ────────────────────────────────────────
    with st.expander("🛡️ During Workout — Safety Reminders", expanded=False):
        render_safety_cautions("during")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── 5. POST-WORKOUT STRETCH VIDEOS ───────────────────────────────────
    with st.expander("🧊 Cool-Down Videos — Do These After Workout", expanded=False):
        if post_stretch:
            for stretch in post_stretch:
                st.markdown(f"""
                <div style='display:flex;align-items:center;gap:12px;
                            padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.05)'>
                  <span style='color:#22c55e;font-size:1.1rem'>🧊</span>
                  <div>
                    <div style='font-size:0.88rem;color:#fff;font-weight:600'>
                      {stretch.get('name','Cool-down')}</div>
                    <div style='font-size:0.72rem;color:rgba(255,255,255,0.42)'>
                      ⏱ {stretch.get('duration','30s')}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
        render_stretch_videos("post")

    # ── 6. POST-WORKOUT CAUTIONS ──────────────────────────────────────────
    with st.expander("✅ Post-Workout Recovery Tips", expanded=False):
        render_safety_cautions("post")