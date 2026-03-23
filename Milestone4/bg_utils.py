import streamlit as st

def apply_bg(url: str = None, overlay: str = "rgba(0,0,0,0.60)") -> None:
    """Apply full-page background image with overlay. Single authoritative selector."""
    if url:
        bg = (
            f"linear-gradient(180deg,rgba(0,0,0,0.62) 0%,rgba(0,0,0,0.48) 50%,rgba(0,0,0,0.62) 100%),"
            f"url(\'{url}\') center center / cover no-repeat fixed"
        )
    else:
        bg = "linear-gradient(135deg,#1a0f08 0%,#2d1810 50%,#1a0f08 100%)"

    st.markdown(f"""
<style>
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > div,
[data-testid="stAppViewContainer"] > section {{
    background: {bg} !important;
    background-size: cover !important;
    background-attachment: fixed !important;
}}
[data-testid="stAppViewContainer"] > section > div.block-container,
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {{
    background: transparent !important;
}}
/* GLOBAL VISIBILITY FIX */
html,body,.stApp,.stMarkdown,p,div,span,label{{text-shadow:0 1px 3px rgba(0,0,0,0.95)!important;}}
[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] p{{color:#fff!important;text-shadow:0 1px 4px rgba(0,0,0,0.95)!important;}}
.stCheckbox>label,.stCheckbox>label p{{color:#fff!important;font-weight:600!important;text-shadow:0 1px 4px rgba(0,0,0,0.95)!important;}}
.stTabs [data-baseweb="tab"]{{color:rgba(255,255,255,0.88)!important;text-shadow:0 1px 3px rgba(0,0,0,0.90)!important;}}
.stExpander details summary{{color:#fff!important;text-shadow:0 1px 3px rgba(0,0,0,0.90)!important;}}
.stMarkdown p,.stMarkdown li{{color:#fff!important;text-shadow:0 1px 4px rgba(0,0,0,0.95)!important;}}
.cal-cell{{background:rgba(0,0,0,0.82)!important;border:1px solid rgba(255,255,255,0.22)!important;}}
.cal-cell.today-cell{{background:rgba(229,9,20,0.35)!important;border:2px solid #E50914!important;}}
.cal-cell.done-cell{{background:rgba(34,197,94,0.30)!important;border:1.5px solid rgba(34,197,94,0.70)!important;}}
.cal-num{{color:#fff!important;font-weight:700!important;text-shadow:0 1px 4px rgba(0,0,0,0.95)!important;}}
.cal-dow{{color:rgba(255,255,255,0.92)!important;font-weight:700!important;}}
.act-day{{color:#fff!important;font-weight:700!important;text-shadow:0 1px 4px rgba(0,0,0,0.95)!important;}}
.g-panel{{background:rgba(0,0,0,0.82)!important;}}
.meal-card,.feature-card,.water-card{{background:rgba(0,0,0,0.82)!important;}}
</style>
""", unsafe_allow_html=True)