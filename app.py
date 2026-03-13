import streamlit as st
import json
from datetime import date
from database import (
    init_db, save_plan, get_plan, update_topic_status, get_progress,
    get_forest_stats, add_xp, get_level_data, get_badges, get_missions,
    init_daily_missions, update_mission, award_badge, XP_LEVELS,
    get_difficulty, update_quiz_performance, BADGE_DEFINITIONS, MISSION_DEFINITIONS
)
from auth import login_user, register_user
from planner import generate_study_plan
from rag_bot import init_rag, ask_question, load_pdf
from adaptive import generate_adaptive_questions, evaluate_performance, get_ai_explanation
from visualizer import visualizer_page
from forest import forest_page
from music import music_player_page
from notebook import notebook_page
from news import news_page
from leaderboard import get_leaderboard, get_user_rank
from quotes import get_quote, BLOCKED_APPS

st.set_page_config(
    page_title="EduQuest",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Remove default Streamlit padding — works across all Streamlit versions
st.markdown("""
<style>
    /* Hide header */
    header[data-testid="stHeader"] { display: none !important; }
    /* Remove ALL padding from the main section */
    .main .block-container,
    div[data-testid="stMainBlockContainer"],
    div[data-testid="block-container"] {
        padding: 0 !important;
        max-width: 100% !important;
    }
    /* This is the key one — targets the actual wrapper div */
    [data-testid="stAppViewContainer"] > section > div {
        padding: 0 !important;
    }
    /* Prevent sidebar collapse from shifting content */
    [data-testid="stAppViewContainer"] {
        overflow: hidden !important;
    }
    [data-testid="stAppViewContainer"] > .main {
        padding-left: 0 !important;
        padding-right: 0 !important;
        overflow-x: hidden !important;
    }
</style>
""", unsafe_allow_html=True)

GOALS      = ["Doctor", "Engineer", "Architect", "Scientist", "Lawyer", "Teacher", "Other"]
GOAL_EMOJI = {"Doctor":"🩺","Engineer":"⚙️","Architect":"🏛️","Scientist":"🔬","Lawyer":"⚖️","Teacher":"📚","Other":"🎯"}

# ─────────────────────────────────────────
# GLOBAL CSS — Coursue-inspired
# ─────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Syne:wght@700;800&display=swap');

    /* ── Base ── */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 14px;
    }
    .main .block-container {
        padding: 0 !important;
        padding-top: 0 !important;
        max-width: 100% !important;
    }
    .main > div:first-child { padding-top: 0 !important; }
    section[data-testid="stMain"] > div { padding-top: 0 !important; }
    section[data-testid="stMain"] { padding-top: 0 !important; }
    div[data-testid="stVerticalBlock"] > div:first-child { padding-top: 0 !important; }

    /* ── Hide Streamlit chrome ── */
    #MainMenu, footer, header, [data-testid="stToolbar"],
    .stDeployButton { display: none !important; }

    /* Hide radio label text (the "nav" string) */
    [data-testid="stSidebar"] .stRadio > label:first-child {
        display: none !important;
    }
    /* Remove top gap in sidebar */
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0 !important;
    }
    /* Fix sidebar content padding */
    [data-testid="stSidebarContent"] {
        padding: 0 !important;
    }
    /* Always show the sidebar expand/collapse toggle */
    [data-testid="stSidebarCollapseButton"] button {
        background: #7c3aed !important;
        border-radius: 0 10px 10px 0 !important;
        border: none !important;
        color: white !important;
        box-shadow: 2px 0 12px rgba(124,58,237,0.4) !important;
    }
    [data-testid="stSidebarCollapseButton"] button:hover {
        background: #6d28d9 !important;
    }
    [data-testid="stSidebarCollapseButton"] svg { color: white !important; fill: white !important; }
    /* The re-open button when sidebar is collapsed */
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        position: fixed !important;
        left: 0 !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        z-index: 9999 !important;
        background: #7c3aed !important;
        border-radius: 0 14px 14px 0 !important;
        box-shadow: 3px 0 20px rgba(124,58,237,0.6) !important;
        width: 32px !important;
        height: 56px !important;
        align-items: center !important;
        justify-content: center !important;
    }
    [data-testid="collapsedControl"] button {
        background: transparent !important;
        border: none !important;
        color: white !important;
        padding: 0 !important;
        width: 100% !important;
        height: 100% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    [data-testid="collapsedControl"] svg { fill: white !important; color: white !important; width:16px !important; height:16px !important; }

    /* ── Sidebar — deep purple like Coursue ── */
    [data-testid="stSidebar"] {
        background: #1a0533 !important;
        min-width: 220px !important;
        max-width: 220px !important;
        border-right: none !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding: 0 !important;
    }
    [data-testid="stSidebar"] * { color: #c4b5d4 !important; }
    [data-testid="stSidebar"] .stRadio > div {
        gap: 2px !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        padding: 10px 16px !important;
        border-radius: 10px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255,255,255,0.08) !important;
        color: #fff !important;
    }
    [data-testid="stSidebar"] .stRadio [aria-checked="true"] + label,
    [data-testid="stSidebar"] .stRadio label[data-selected="true"] {
        background: rgba(139,92,246,0.25) !important;
        color: #a78bfa !important;
    }

    /* ── Main content area ── */
    .eq-content {
        padding: 24px 28px;
        background: #f7f5ff;
        min-height: 100vh;
    }
    /* Make the stMain background match so no white flash */
    section[data-testid="stMain"],
    .main, .stApp {
        background: #f7f5ff !important;
    }

    /* ── Sidebar collapse/expand fix ── */
    /* When sidebar is open: content starts after sidebar */
    [data-testid="stAppViewContainer"] > section.main {
        padding-left: 0 !important;
        margin-left: 0 !important;
    }
    /* When sidebar collapsed: full width */
    [data-testid="stAppViewContainer"][data-sidebar-state="collapsed"] > section.main,
    [data-testid="stAppViewContainer"]:not(:has([data-testid="stSidebar"])) > section.main {
        padding-left: 0 !important;
        margin-left: 0 !important;
        width: 100% !important;
    }
    /* Remove Streamlit's own left padding on main */
    section[data-testid="stMain"] {
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    /* eq-content handles its own padding */
    .eq-content {
        width: 100% !important;
        box-sizing: border-box !important;
    }
    /* Ensure columns dont overflow viewport */
    [data-testid="stHorizontalBlock"] {
        width: 100% !important;
        max-width: 100% !important;
        overflow: hidden !important;
    }
    /* Ensure columns don't overflow */
    [data-testid="stHorizontalBlock"] {
        gap: 20px !important;
        align-items: flex-start !important;
    }

    /* ── Hero Banner ── */
    .hero-banner {
        background: linear-gradient(135deg, #6d28d9 0%, #7c3aed 40%, #8b5cf6 100%);
        border-radius: 20px;
        padding: 32px 36px;
        color: white;
        position: relative;
        overflow: hidden;
        margin-bottom: 24px;
    }
    .hero-banner::before {
        content: '';
        position: absolute;
        top: -30px; right: -30px;
        width: 200px; height: 200px;
        background: rgba(255,255,255,0.06);
        border-radius: 50%;
    }
    .hero-banner::after {
        content: '';
        position: absolute;
        bottom: -50px; right: 80px;
        width: 150px; height: 150px;
        background: rgba(255,255,255,0.04);
        border-radius: 50%;
    }
    .hero-tag {
        background: rgba(255,255,255,0.2);
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: .05em;
        text-transform: uppercase;
        margin-bottom: 12px;
    }
    .hero-title {
        font-family: 'Syne', sans-serif;
        font-size: 28px;
        font-weight: 800;
        line-height: 1.2;
        margin: 0 0 16px;
        max-width: 380px;
    }
    .hero-btn {
        background: white;
        color: #6d28d9 !important;
        border: none;
        padding: 10px 24px;
        border-radius: 25px;
        font-weight: 700;
        font-size: 13px;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }

    /* ── Stat Cards ── */
    .stat-row { display: flex; gap: 16px; margin-bottom: 24px; }
    .stat-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        flex: 1;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        border: 1px solid rgba(0,0,0,0.05);
    }
    .stat-icon {
        width: 40px; height: 40px;
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 18px;
        margin-bottom: 12px;
    }
    .stat-value {
        font-size: 26px;
        font-weight: 800;
        color: #1a0533;
        line-height: 1;
        margin-bottom: 4px;
    }
    .stat-label {
        font-size: 12px;
        color: #888;
        font-weight: 500;
    }

    /* ── Section Headers ── */
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }
    .section-title {
        font-size: 16px;
        font-weight: 700;
        color: #1a0533;
    }
    .see-all {
        font-size: 12px;
        color: #7c3aed;
        font-weight: 600;
        cursor: pointer;
    }

    /* ── Feature Cards (Continue Watching style) ── */
    .feat-card {
        background: white;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        border: 1px solid rgba(0,0,0,0.05);
        transition: all 0.2s;
        height: 100%;
    }
    .feat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(109,40,217,0.12);
    }
    .feat-card-thumb {
        height: 120px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 48px;
    }
    .feat-card-body { padding: 14px; }
    .feat-tag {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 6px;
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .05em;
        margin-bottom: 8px;
    }
    .feat-title {
        font-weight: 700;
        font-size: 13px;
        color: #1a0533;
        line-height: 1.4;
        margin-bottom: 10px;
    }
    .feat-author {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 11px;
        color: #888;
    }
    .feat-avatar {
        width: 22px; height: 22px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 12px;
    }

    /* ── XP Progress Bar ── */
    .xp-bar-wrap {
        background: #f0ebff;
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
        margin: 6px 0;
    }
    .xp-bar-fill {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #7c3aed, #a78bfa);
        transition: width 0.5s ease;
    }

    /* ── Mission Cards ── */
    .mission-card {
        background: white;
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 14px;
        border: 1px solid rgba(0,0,0,0.05);
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .mission-icon {
        width: 36px; height: 36px;
        border-radius: 10px;
        background: #f0ebff;
        display: flex; align-items: center; justify-content: center;
        font-size: 16px;
        flex-shrink: 0;
    }
    .mission-label { font-weight: 600; font-size: 13px; color: #1a0533; }
    .mission-sub   { font-size: 11px; color: #888; margin-top: 2px; }
    .mission-done  { background: #dcfce7; color: #16a34a; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; }
    .mission-pct   { font-size: 12px; color: #7c3aed; font-weight: 600; }

    /* ── Badge Pills ── */
    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #f0ebff;
        border: 1px solid #e0d4ff;
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 12px;
        font-weight: 600;
        color: #6d28d9;
        margin: 4px;
    }

    /* ── Quiz Cards ── */
    .q-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 14px;
        border: 1px solid rgba(0,0,0,0.06);
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .q-num {
        font-size: 11px;
        font-weight: 700;
        color: #7c3aed;
        text-transform: uppercase;
        letter-spacing: .05em;
        margin-bottom: 6px;
    }
    .q-text {
        font-size: 15px;
        font-weight: 600;
        color: #1a0533;
        margin-bottom: 14px;
        line-height: 1.5;
    }
    .diff-badge {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
    }

    /* ── Profile Panel ── */
    .profile-panel {
        background: white;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        border: 1px solid rgba(0,0,0,0.05);
        margin-bottom: 16px;
    }
    .profile-avatar {
        width: 64px; height: 64px;
        border-radius: 50%;
        background: linear-gradient(135deg, #7c3aed, #a78bfa);
        display: flex; align-items: center; justify-content: center;
        font-size: 28px;
        margin: 0 auto 12px;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: #7c3aed !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background: #6d28d9 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 15px rgba(124,58,237,0.3) !important;
    }
    .stButton > button[kind="secondary"] {
        background: #f0ebff !important;
        color: #7c3aed !important;
    }

    /* ── Inputs (main app — dark text on white) ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        border-radius: 12px !important;
        border: 1.5px solid #e5e7eb !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background: white !important;
        color: #1a0533 !important;
        caret-color: #1a0533 !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #7c3aed !important;
        box-shadow: 0 0 0 3px rgba(124,58,237,0.1) !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: #f0ebff;
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 9px;
        font-weight: 600;
        font-size: 13px;
        color: #6b7280 !important;
    }
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #7c3aed !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1);
    }

    /* ── Expanders ── */
    .streamlit-expanderHeader {
        background: white !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        border: 1px solid rgba(0,0,0,0.06) !important;
    }

    /* ── Metrics ── */
    [data-testid="metric-container"] {
        background: white;
        border-radius: 14px;
        padding: 16px;
        border: 1px solid rgba(0,0,0,0.05);
    }

    /* ── Success/Error ── */
    .stSuccess, .stError, .stInfo, .stWarning {
        border-radius: 12px !important;
        font-size: 13px !important;
    }

    /* ── Leaderboard Row ── */
    .lb-row {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        background: white;
        border-radius: 12px;
        margin-bottom: 8px;
        border: 1px solid rgba(0,0,0,0.05);
    }
    .lb-avatar {
        width: 36px; height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, #7c3aed, #a78bfa);
        display: flex; align-items: center; justify-content: center;
        font-size: 14px;
        color: white;
        font-weight: 700;
        flex-shrink: 0;
    }
    .lb-name { font-weight: 600; font-size: 13px; color: #1a0533; }
    .lb-sub  { font-size: 11px; color: #888; }
    .lb-pts  { margin-left: auto; font-weight: 700; font-size: 14px; color: #7c3aed; }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def xp_bar(pct, label=""):
    st.markdown(f"""
    <div>
        <div class="xp-bar-wrap">
            <div class="xp-bar-fill" style="width:{pct}%"></div>
        </div>
        {f'<div style="font-size:11px;color:#888;margin-top:3px;">{label}</div>' if label else ''}
    </div>
    """, unsafe_allow_html=True)


def feat_card(emoji, tag, tag_color, title, subtitle, bg_color="#f0ebff"):
    return f"""
    <div class="feat-card">
        <div class="feat-card-thumb" style="background:{bg_color};">{emoji}</div>
        <div class="feat-card-body">
            <div class="feat-tag" style="background:{tag_color}20;color:{tag_color};">{tag}</div>
            <div class="feat-title">{title}</div>
            <div class="feat-author">
                <div class="feat-avatar" style="background:{tag_color}20;">{emoji[0]}</div>
                <span>{subtitle}</span>
            </div>
        </div>
    </div>"""


def stat_card(emoji, value, label, color):
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon" style="background:{color}20;">{emoji}</div>
        <div class="stat-value">{value}</div>
        <div class="stat-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def right_profile_panel():
    username  = st.session_state.get("username","")
    full_name = st.session_state.get("full_name", username)
    goal      = st.session_state.get("user_goal","Other")
    emoji     = GOAL_EMOJI.get(goal,"🎯")
    ld        = get_level_data(username)
    badges    = get_badges(username)
    rank      = get_user_rank(username) or {}

    st.markdown(f"""
    <div class="profile-panel">
        <div class="profile-avatar">{emoji}</div>
        <div style="text-align:center;">
            <div style="font-family:'Syne',sans-serif;font-size:16px;font-weight:800;color:#1a0533;">
                Good day, {full_name.split()[0]}
            </div>
            <div style="font-size:12px;color:#888;margin-top:2px;">Future {goal}</div>
        </div>
        <div style="display:flex;justify-content:center;gap:10px;margin:16px 0;">
            <div style="background:#f0ebff;border-radius:10px;padding:8px 14px;text-align:center;">
                <div style="font-size:16px;font-weight:800;color:#7c3aed;">Lv.{ld['level']}</div>
                <div style="font-size:10px;color:#888;">Level</div>
            </div>
            <div style="background:#f0ebff;border-radius:10px;padding:8px 14px;text-align:center;">
                <div style="font-size:16px;font-weight:800;color:#7c3aed;">{ld['total_xp']}</div>
                <div style="font-size:10px;color:#888;">XP</div>
            </div>
            <div style="background:#f0ebff;border-radius:10px;padding:8px 14px;text-align:center;">
                <div style="font-size:16px;font-weight:800;color:#7c3aed;">#{rank.get('rank','—')}</div>
                <div style="font-size:10px;color:#888;">Rank</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # XP Progress
    st.markdown(f"""
    <div class="profile-panel" style="padding:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span style="font-weight:700;font-size:13px;color:#1a0533;">XP Progress</span>
            <span style="font-size:12px;color:#7c3aed;font-weight:600;">{ld['xp_in_level']}/{ld['xp_needed']}</span>
        </div>
        <div class="xp-bar-wrap" style="height:10px;">
            <div class="xp-bar-fill" style="width:{ld['progress_pct']}%;"></div>
        </div>
        <div style="font-size:11px;color:#888;margin-top:6px;">
            {ld['progress_pct']}% to Level {min(ld['level']+1,10)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Badges
    if badges:
        st.markdown("""<div class="profile-panel" style="padding:16px;">
            <div style="font-weight:700;font-size:13px;color:#1a0533;margin-bottom:10px;">🏅 My Badges</div>""",
            unsafe_allow_html=True)
        badge_html = "".join(f'<span class="badge-pill">{b.get("icon","🏅")} {b["name"]}</span>' for b in badges[:4])
        st.markdown(badge_html + "</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────────
def show_login_page():
    # Style entire page as full-screen purple — no sidebar, no padding
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    .main .block-container { padding: 0 !important; max-width: 100% !important; }
    div.block-container { padding-top: 0 !important; }
    section[data-testid="stMain"] > div { padding-top: 0 !important; }
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f0224 0%, #2d0a5e 45%, #1a0533 100%) !important;
    }
    /* Login page — dark inputs with white text */
    .stTextInput input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 10px !important;
        color: white !important;
        caret-color: white !important;
    }
    .stTextInput input::placeholder { color: rgba(255,255,255,0.35) !important; }
    .stTextInput input:focus {
        background: rgba(255,255,255,0.12) !important;
        border-color: #a78bfa !important;
        box-shadow: 0 0 0 3px rgba(167,139,250,0.25) !important;
    }
    /* Password eye-icon color */
    .stTextInput button { color: rgba(255,255,255,0.6) !important; }
    .stTextInput label { color: rgba(255,255,255,0.75) !important; font-size:13px !important; font-weight:500 !important; }
    .stSelectbox label { color: rgba(255,255,255,0.75) !important; font-size:13px !important; }
    .stSelectbox [data-baseweb="select"] > div {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 10px !important;
        color: white !important;
    }
    /* Style the form card area */
    [data-testid="stForm"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    /* Input fields — login page only, scoped via body class */
    body[data-login="true"] .stTextInput input,
    .login-page .stTextInput input {
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 10px !important;
        color: white !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
    }
    /* Submit button */
    .stFormSubmitButton button {
        background: linear-gradient(135deg, #7c3aed, #6d28d9) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        padding: 12px !important;
        width: 100% !important;
        margin-top: 8px !important;
    }
    .stFormSubmitButton button:hover {
        background: linear-gradient(135deg, #6d28d9, #5b21b6) !important;
        transform: translateY(-1px) !important;
    }
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.08) !important;
        border-radius: 10px !important;
        padding: 4px !important;
        margin-bottom: 20px !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: rgba(255,255,255,0.5) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #6d28d9 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Centered layout: left decorative panel + right form
    left, mid, right = st.columns([1, 1.1, 1])

    with mid:
        # Vertical spacer to push card to center
        st.markdown("<div style='height:8vh'></div>", unsafe_allow_html=True)

        # Logo + branding
        st.markdown("""
        <div style="text-align:center; margin-bottom:28px;">
            <div style="font-size:52px; margin-bottom:12px; line-height:1;">🎯</div>
            <div style="font-family:'Syne',sans-serif; font-size:36px; font-weight:800;
                 color:white; letter-spacing:-0.5px; margin-bottom:6px;">EduQuest</div>
            <div style="color:rgba(196,181,212,0.85); font-size:13px; font-weight:500;">
                AI-Driven Personalized Learning Platform
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Glass card wrapper
        st.markdown("""
        <div style="background:rgba(255,255,255,0.06); backdrop-filter:blur(20px);
             border:1px solid rgba(255,255,255,0.12); border-radius:20px;
             padding:28px 28px 24px; box-shadow:0 24px 64px rgba(0,0,0,0.4);">
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["  Sign In  ", "  Create Account  "])

        with tab1:
            with st.form("lf"):
                st.text_input("Username or Email", key="li_id", placeholder="your username or email")
                st.text_input("Password", type="password", key="li_pw", placeholder="••••••••")
                if st.form_submit_button("Sign In →", use_container_width=True):
                    ok, res = login_user(st.session_state.li_id, st.session_state.li_pw)
                    if ok:
                        st.session_state.update({
                            "logged_in": True,
                            "username":  res["username"],
                            "full_name": res["full_name"],
                            "user_goal": res.get("goal","Other"),
                            "student_name": res["username"],
                        })
                        st.rerun()
                    else:
                        st.error(res)

        with tab2:
            with st.form("rf"):
                c1,c2 = st.columns(2)
                with c1: st.text_input("Full Name", key="rn", placeholder="Raghul D")
                with c2: st.text_input("Username",  key="ru", placeholder="raghuldpr")
                st.text_input("Email", key="re", placeholder="raghul@gmail.com")
                st.selectbox("I want to become a", GOALS, key="rg")
                c3,c4 = st.columns(2)
                with c3: st.text_input("Password",         type="password", key="rp")
                with c4: st.text_input("Confirm Password", type="password", key="rc")
                if st.form_submit_button("Create Account →", use_container_width=True):
                    if st.session_state.rp != st.session_state.rc:
                        st.error("Passwords don't match")
                    elif len(st.session_state.rp) < 6:
                        st.error("Password too short")
                    else:
                        ok, msg = register_user(st.session_state.ru, st.session_state.re,
                                                st.session_state.rp, st.session_state.rn,
                                                st.session_state.rg)
                        st.success(msg) if ok else st.error(msg)

        st.markdown("<div style='height:8vh'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
def render_sidebar():
    username  = st.session_state.get("username","")
    full_name = st.session_state.get("full_name", username)
    goal      = st.session_state.get("user_goal","Other")
    ld        = get_level_data(username)

    with st.sidebar:
        # Logo
        st.markdown(f"""
        <div style="padding:20px 16px 14px; border-bottom:1px solid rgba(255,255,255,0.08); margin-bottom:8px;">
            <div style="font-family:'Syne',sans-serif; font-size:20px; font-weight:800; color:white; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                🎯 EduQuest
            </div>
            <div style="font-size:11px; color:#9f75c4; margin-top:2px; white-space:nowrap;">Personalized AI Learning</div>
        </div>
        """, unsafe_allow_html=True)

        # Nav sections
        st.markdown('<div style="padding:8px 12px 4px; margin-top:4px; font-size:10px;font-weight:700;color:#6b4d8a;letter-spacing:.1em;text-transform:uppercase;">OVERVIEW</div>', unsafe_allow_html=True)

        NAV = [
            ("🏠","Dashboard"),
            ("🗺️","Learning Path"),
            ("⚔️","Challenge"),
            ("🔬","Visualizer"),
            ("🤖","AI Tutor"),
        ]
        NAV2 = [
            ("📓","Notebook"),
            ("🌳","Focus Timer"),
            ("🎵","Music"),
            ("📰","Daily News"),
        ]
        NAV3 = [
            ("🏆","Leaderboard"),
            ("📊","Analytics"),
            ("🎯","Missions"),
            ("🏅","Badges"),
        ]

        all_labels = [f"{ic}  {lb}" for ic,lb in NAV+NAV2+NAV3]
        page_label = st.radio("nav", all_labels, label_visibility="collapsed", key="nav_radio")
        page = page_label.split("  ",1)[1]

        st.markdown('<div style="padding:8px 12px 4px;margin-top:8px;font-size:10px;font-weight:700;color:#6b4d8a;letter-spacing:.1em;text-transform:uppercase;">TOOLS</div>', unsafe_allow_html=True)

        # XP bar in sidebar
        st.markdown(f"""
        <div style="padding:12px 16px; margin:8px 12px; background:rgba(255,255,255,0.06);
             border-radius:12px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="font-size:12px;color:#c4b5d4;font-weight:600;">Level {ld['level']}</span>
                <span style="font-size:12px;color:#a78bfa;">{ld['total_xp']} XP</span>
            </div>
            <div style="background:rgba(255,255,255,0.1);border-radius:6px;height:6px;">
                <div style="background:linear-gradient(90deg,#7c3aed,#a78bfa);height:100%;border-radius:6px;width:{ld['progress_pct']}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("Sign Out", use_container_width=True, key="signout"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    return page


# ─────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────
def page_dashboard():
    username  = st.session_state.get("username","")
    full_name = st.session_state.get("full_name", username)
    goal      = st.session_state.get("user_goal","Other")
    progress  = get_progress(username) or {}
    forest    = get_forest_stats(username)
    ld        = get_level_data(username)
    missions  = get_missions(username)

    main, right = st.columns([2.4, 1])

    with main:
        # Hero Banner
        quote = get_quote(goal, full_name)
        st.markdown(f"""
        <div class="hero-banner">
            <div class="hero-tag">🎯 AI-Powered Learning</div>
            <div class="hero-title">Level up your knowledge.<br/>One quest at a time.</div>
            <div style="font-size:13px; color:rgba(255,255,255,0.8); margin-bottom:20px; max-width:340px;">
                💬 "{quote}"
            </div>
            <div class="hero-btn">▶ Continue Learning &nbsp;→</div>
        </div>
        """, unsafe_allow_html=True)

        # Stats Row
        s1,s2,s3,s4 = st.columns(4)
        with s1: stat_card("✅", progress.get("done",0),       "Topics Done",    "#7c3aed")
        with s2: stat_card("🌳", forest.get("trees",0),         "Trees Grown",    "#059669")
        with s3: stat_card("⏱", f"{forest.get('today_mins',0)}m","Focus Today",  "#d97706")
        with s4: stat_card("⚡", ld["total_xp"],                 "Total XP",       "#dc2626")

        # Feature Cards
        st.markdown("""
        <div class="section-header" style="margin-top:8px;">
            <div class="section-title">Continue Learning</div>
        </div>
        """, unsafe_allow_html=True)

        c1,c2,c3 = st.columns(3)
        cards = [
            ("⚔️","CHALLENGE","#7c3aed","Adaptive Quiz Engine","Dynamic difficulty based on your performance","#f0ebff"),
            ("🔬","VISUALIZE","#059669","Concept Visualizer","PhET, GeoGebra & VisuAlgo simulations","#ecfdf5"),
            ("📓","NOTEBOOK","#d97706","AI Notebook","Summarize notes & generate podcasts","#fffbeb"),
        ]
        for col, (em,tag,color,title,sub,bg) in zip([c1,c2,c3], cards):
            with col:
                st.markdown(feat_card(em,tag,color,title,sub,bg), unsafe_allow_html=True)

        # Missions Preview
        st.markdown("""
        <div class="section-header" style="margin-top:20px;">
            <div class="section-title">Today's Missions</div>
        </div>
        """, unsafe_allow_html=True)

        for m in missions[:3]:
            pct  = min(int(m["current"]/max(m["target"],1)*100), 100)
            done = m["status"] == "completed"
            st.markdown(f"""
            <div class="mission-card">
                <div class="mission-icon">{m['emoji']}</div>
                <div style="flex:1;">
                    <div class="mission-label">{m['label']}</div>
                    <div class="mission-sub">{m['current']}/{m['target']} · +{m['xp']} XP</div>
                    <div class="xp-bar-wrap" style="margin-top:6px;">
                        <div class="xp-bar-fill" style="width:{pct}%;background:{'#16a34a' if done else 'linear-gradient(90deg,#7c3aed,#a78bfa)'};"></div>
                    </div>
                </div>
                {"<div class='mission-done'>✓ Done</div>" if done else f"<div class='mission-pct'>{pct}%</div>"}
            </div>
            """, unsafe_allow_html=True)

    with right:
        right_profile_panel()

        # Mini leaderboard
        st.markdown("""
        <div class="profile-panel" style="padding:16px;">
            <div style="font-weight:700;font-size:13px;color:#1a0533;margin-bottom:12px;">🏆 Top Learners</div>
        """, unsafe_allow_html=True)
        lb = get_leaderboard("week")[:3]
        me = st.session_state.get("username","")
        for entry in lb:
            you = " ✦" if entry["username"] == me else ""
            st.markdown(f"""
            <div class="lb-row">
                <div class="lb-avatar">{entry['medal']}</div>
                <div>
                    <div class="lb-name">{entry['full_name']}{you}</div>
                    <div class="lb-sub">@{entry['username']}</div>
                </div>
                <div class="lb-pts">{entry['score']} pts</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def page_challenge():
    username = st.session_state.get("username","")
    goal     = st.session_state.get("user_goal","Other")
    full_name= st.session_state.get("full_name","Student")

    st.markdown("""
    <div style="margin-bottom:20px;">
        <div style="font-family:'Syne',sans-serif;font-size:24px;font-weight:800;color:#1a0533;">⚔️ Adaptive Challenge</div>
        <div style="color:#888;font-size:13px;">Questions get harder as you improve — automatically</div>
    </div>
    """, unsafe_allow_html=True)

    main, right = st.columns([2.4, 1])

    with main:
        c1,c2,c3 = st.columns(3)
        with c1: subject = st.selectbox("Subject", ["Mathematics","Physics","Chemistry","Computer Science","Biology","Other"])
        with c2: topic   = st.text_input("Topic", placeholder="e.g. Binary Trees")
        with c3:
            current_diff = get_difficulty(username, subject, topic or "general")
            diff_labels  = {1:"🟢 Easy", 2:"🟡 Medium", 3:"🔴 Hard"}
            st.markdown(f"""
            <div style="background:#f0ebff;border-radius:12px;padding:12px;text-align:center;margin-top:4px;">
                <div style="font-size:11px;color:#888;">Your Level</div>
                <div style="font-size:18px;font-weight:800;color:#7c3aed;">{diff_labels[current_diff]}</div>
            </div>
            """, unsafe_allow_html=True)

        if st.button("⚔️ Start Challenge", use_container_width=True, type="primary"):
            if not topic:
                st.warning("Enter a topic first!")
            else:
                with st.spinner("Generating your personalized challenge..."):
                    qs = generate_adaptive_questions(subject, topic, current_diff, 5)
                    st.session_state["aq"]       = qs
                    st.session_state["aq_ans"]   = {}
                    st.session_state["aq_sub"]   = subject
                    st.session_state["aq_topic"] = topic
                    st.session_state["aq_diff"]  = current_diff

        if "aq" in st.session_state and st.session_state["aq"]:
            diff_label = diff_labels[st.session_state["aq_diff"]]
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;margin:16px 0 12px;">
                <div style="font-weight:700;color:#1a0533;">5 Questions</div>
                <div class="diff-badge" style="background:#f0ebff;color:#7c3aed;">{diff_label}</div>
            </div>
            """, unsafe_allow_html=True)

            for i, q in enumerate(st.session_state["aq"]):
                st.markdown(f"""
                <div class="q-card">
                    <div class="q-num">Question {i+1} of 5</div>
                    <div class="q-text">{q['question']}</div>
                </div>
                """, unsafe_allow_html=True)
                ans = st.radio("", q["options"], key=f"aq_{i}", index=None, label_visibility="collapsed")
                st.session_state["aq_ans"][i] = ans
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

            if st.button("Submit Challenge", use_container_width=True):
                qs      = st.session_state["aq"]
                correct = 0
                results = []
                for i, q in enumerate(qs):
                    user_ans = st.session_state["aq_ans"].get(i,"")
                    is_right = user_ans == q["answer"]
                    if is_right: correct += 1
                    results.append((q, user_ans, is_right))

                # Show results
                for i, (q, ua, ok) in enumerate(results):
                    if ok:
                        st.success(f"Q{i+1} ✓ — {q['answer']}")
                    else:
                        st.error(f"Q{i+1} ✗ — Correct: {q['answer']}")
                        with st.spinner("Getting AI explanation..."):
                            exp = get_ai_explanation(st.session_state["aq_sub"],
                                                     st.session_state["aq_topic"],
                                                     q["question"], q["answer"])
                        st.markdown(f"""
                        <div style="background:#f0ebff;border-radius:12px;padding:14px;
                             border-left:3px solid #7c3aed;margin:6px 0;">
                            💡 {exp}
                        </div>
                        """, unsafe_allow_html=True)

                # Evaluate + update
                total  = len(qs)
                diff   = st.session_state["aq_diff"]
                next_d, feedback, status, score = evaluate_performance(correct, total, diff)
                pct    = int(score * 100)

                update_quiz_performance(username, st.session_state["aq_sub"],
                                        st.session_state["aq_topic"], correct, total)

                # Award XP
                from adaptive import XP_MAP
                xp_earned = correct * XP_MAP.get(diff, 20)
                if xp_earned > 0:
                    leveled, new_lv = add_xp(username, "quiz_correct", xp_earned)
                    if leveled:
                        st.balloons()
                        st.success(f"🎉 Level Up! You're now Level {new_lv}!")

                update_mission(username, "pass_quizzes", 1 if pct >= 60 else 0)

                # Score card
                color = "#16a34a" if pct >= 80 else "#d97706" if pct >= 50 else "#dc2626"
                st.markdown(f"""
                <div style="background:white;border-radius:20px;padding:24px;text-align:center;
                     margin-top:16px;border:2px solid {color}20;box-shadow:0 4px 20px {color}15;">
                    <div style="font-size:48px;font-weight:800;color:{color};">{correct}/{total}</div>
                    <div style="font-size:14px;color:#888;margin:4px 0 12px;">{pct}% score</div>
                    <div style="font-size:15px;font-weight:600;color:#1a0533;">{feedback}</div>
                    <div style="margin-top:12px;">
                        <span style="background:#f0ebff;color:#7c3aed;padding:6px 16px;border-radius:20px;font-size:13px;font-weight:700;">
                            +{xp_earned} XP earned
                        </span>
                    </div>
                    <div style="margin-top:10px;font-size:13px;color:#888;">
                        Next difficulty: {["","🟢 Easy","🟡 Medium","🔴 Hard"][next_d]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.session_state.pop("aq", None)

    with right:
        right_profile_panel()


def page_learning_path():
    username = st.session_state.get("username","")
    st.markdown("""
    <div style="margin-bottom:20px;">
        <div style="font-family:'Syne',sans-serif;font-size:24px;font-weight:800;color:#1a0533;">🗺️ Learning Path</div>
        <div style="color:#888;font-size:13px;">Your personalized AI study plan</div>
    </div>
    """, unsafe_allow_html=True)

    main, right = st.columns([2.4, 1])
    with main:
        plan_data = st.session_state.get("plan") or get_plan(username)
        if not plan_data:
            st.markdown("""
            <div style="background:white;border-radius:20px;padding:32px;text-align:center;border:2px dashed #e5e7eb;">
                <div style="font-size:48px;margin-bottom:12px;">🗺️</div>
                <div style="font-weight:700;font-size:16px;color:#1a0533;margin-bottom:8px;">No Plan Yet</div>
                <div style="color:#888;font-size:13px;">Create your personalized study plan below</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            with st.form("pf"):
                c1,c2 = st.columns(2)
                with c1:
                    subjects  = st.text_area("Subjects", placeholder="Mathematics\nPhysics\nChemistry", height=100)
                    exam_date = st.date_input("Exam Date", min_value=date.today())
                with c2:
                    daily_hrs = st.slider("Daily Hours", 1, 12, 4)
                    weak      = st.text_area("Weak Topics", placeholder="Calculus\nThermodynamics", height=70)
                    s_goal    = st.selectbox("Goal", ["Pass with good marks","Top the exam","Deep understanding"])
                pdf = st.file_uploader("Upload Syllabus PDF", type=["pdf"])
                if st.form_submit_button("Generate My Plan →", use_container_width=True):
                    if not subjects:
                        st.error("Enter subjects!")
                    else:
                        with st.spinner("AI is building your plan..."):
                            sl = [s.strip() for s in subjects.split("\n") if s.strip()]
                            wl = [w.strip() for w in weak.split("\n") if w.strip()]
                            if pdf: init_rag(load_pdf(pdf))
                            plan = generate_study_plan(username, sl, str(exam_date), daily_hrs, wl, s_goal)
                            save_plan(username, plan, str(exam_date), sl)
                            st.session_state["plan"] = plan
                        st.rerun()
        else:
            if isinstance(plan_data, str):
                plan_data = json.loads(plan_data)
            col_h, col_b = st.columns([4,1])
            with col_b:
                if st.button("New Plan", key="np"):
                    st.session_state.pop("plan", None)
                    st.rerun()
            for day in plan_data.get("days",[]):
                day_num = day.get("day","?")
                topics  = day.get("topics",[])
                with st.expander(f"Day {day_num}  ·  {day.get('date','')}  ·  {len(topics)} topics", expanded=(day_num==1)):
                    for i, t in enumerate(topics):
                        c1,c2,c3 = st.columns([4,1,1])
                        with c1:
                            tag_bg = "#f0ebff" if t.get("type")=="New Topic" else "#ecfdf5"
                            tag_cl = "#7c3aed" if t.get("type")=="New Topic" else "#059669"
                            st.markdown(f"""
                            <div style="padding:4px 0;">
                                <span style="font-weight:600;color:#1a0533;">{t['subject']}</span>
                                <span style="color:#666;"> — {t['topic']}</span>
                                <span style="background:{tag_bg};color:{tag_cl};padding:2px 8px;border-radius:6px;font-size:11px;font-weight:600;margin-left:8px;">{t.get('type','Study')}</span>
                                <span style="color:#aaa;font-size:12px;margin-left:8px;">⏱ {t.get('duration',1)}h</span>
                            </div>
                            """, unsafe_allow_html=True)
                        with c2:
                            if st.button("Done", key=f"d_{day_num}_{i}", use_container_width=True):
                                update_topic_status(username, day_num, i, "done")
                                add_xp(username, 20, "topic_done")
                                update_mission(username, "complete_topics", 1)
                                award_badge(username, "first_topic")
                                st.rerun()
                        with c3:
                            if st.button("Skip", key=f"s_{day_num}_{i}", use_container_width=True):
                                update_topic_status(username, day_num, i, "skipped")
                                st.rerun()
    with right:
        right_profile_panel()


def page_ai_tutor():
    username = st.session_state.get("username","")
    st.markdown("""
    <div style="margin-bottom:20px;">
        <div style="font-family:'Syne',sans-serif;font-size:24px;font-weight:800;color:#1a0533;">🤖 AI Tutor</div>
        <div style="color:#888;font-size:13px;">Ask anything — get expert explanations instantly</div>
    </div>
    """, unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    user_input = st.chat_input("Ask any topic...")
    if user_input:
        st.session_state.chat_history.append({"role":"user","content":user_input})
        with st.chat_message("user"):
            st.write(user_input)
        with st.chat_message("assistant"):
            with st.spinner(""):
                resp = ask_question(user_input)
                st.write(resp)
                st.session_state.chat_history.append({"role":"assistant","content":resp})
        add_xp(username, "ask_ai", 5)
        update_mission(username, "ask_ai", 1)


def page_missions():
    username = st.session_state.get("username","")
    st.markdown("""
    <div style="margin-bottom:20px;">
        <div style="font-family:'Syne',sans-serif;font-size:24px;font-weight:800;color:#1a0533;">🎯 Daily Missions</div>
        <div style="color:#888;font-size:13px;">Complete missions to earn bonus XP — resets every day</div>
    </div>
    """, unsafe_allow_html=True)

    missions = get_missions(username)
    completed = sum(1 for m in missions if m["status"]=="completed")
    total_xp_possible = sum(m["xp"] for m in missions)

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#6d28d9,#7c3aed);border-radius:16px;
         padding:20px 24px;color:white;margin-bottom:20px;display:flex;justify-content:space-between;align-items:center;">
        <div>
            <div style="font-size:13px;color:rgba(255,255,255,0.7);">Today's Progress</div>
            <div style="font-size:28px;font-weight:800;">{completed}/{len(missions)} Missions</div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:13px;color:rgba(255,255,255,0.7);">Potential XP</div>
            <div style="font-size:28px;font-weight:800;">+{total_xp_possible}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for m in missions:
        pct  = min(int(m["current"]/max(m["target"],1)*100),100)
        done = m["status"] == "completed"
        border = "#16a34a" if done else "#7c3aed"
        st.markdown(f"""
        <div class="mission-card" style="border-left:3px solid {border};">
            <div class="mission-icon" style="background:{'#dcfce7' if done else '#f0ebff'};">{m['emoji']}</div>
            <div style="flex:1;">
                <div class="mission-label">{m['label']}</div>
                <div class="mission-sub">{m['current']}/{m['target']} completed · +{m['xp']} XP reward</div>
                <div class="xp-bar-wrap" style="margin-top:8px;">
                    <div class="xp-bar-fill" style="width:{pct}%;background:{'#16a34a' if done else 'linear-gradient(90deg,#7c3aed,#a78bfa)'};"></div>
                </div>
            </div>
            {"<div class='mission-done'>✓ Completed</div>" if done else f"<div class='mission-pct'>{pct}%</div>"}
        </div>
        """, unsafe_allow_html=True)


def page_badges():
    username = st.session_state.get("username","")
    st.markdown("""
    <div style="margin-bottom:20px;">
        <div style="font-family:'Syne',sans-serif;font-size:24px;font-weight:800;color:#1a0533;">🏅 My Badges</div>
        <div style="color:#888;font-size:13px;">Earn badges by completing challenges and milestones</div>
    </div>
    """, unsafe_allow_html=True)

    earned = get_badges(username)
    earned_keys = [b["name"] for b in earned]

    cols = st.columns(3)
    for i, (name, emoji, key, desc) in enumerate(BADGE_DEFINITIONS):
        is_earned = name in earned_keys
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:{'white' if is_earned else '#fafafa'};border-radius:16px;padding:20px;
                 text-align:center;margin-bottom:12px;border:{'2px solid #7c3aed' if is_earned else '1px solid #e5e7eb'};
                 opacity:{'1' if is_earned else '0.5'};">
                <div style="font-size:36px;margin-bottom:8px;">{emoji}</div>
                <div style="font-weight:700;font-size:13px;color:#1a0533;">{name}</div>
                <div style="font-size:11px;color:#888;margin-top:4px;">{desc}</div>
                {'<div style="background:#f0ebff;color:#7c3aed;padding:4px 12px;border-radius:20px;font-size:11px;font-weight:700;margin-top:10px;display:inline-block;">✓ Earned</div>' if is_earned else ''}
            </div>
            """, unsafe_allow_html=True)


def page_leaderboard():
    username = st.session_state.get("username","")
    st.markdown("""
    <div style="margin-bottom:20px;">
        <div style="font-family:'Syne',sans-serif;font-size:24px;font-weight:800;color:#1a0533;">🏆 Leaderboard</div>
        <div style="color:#888;font-size:13px;">Compete with classmates · Updated live</div>
    </div>
    """, unsafe_allow_html=True)

    period = st.radio("", ["all","week","today"],
        format_func=lambda x:{"all":"All Time","week":"This Week","today":"Today"}[x],
        horizontal=True, label_visibility="collapsed")

    lb = get_leaderboard(period)
    if not lb:
        st.info("No data yet.")
        return

    main, right = st.columns([2.4,1])
    with main:
        # Podium
        if len(lb) >= 3:
            p2,p1,p3 = st.columns(3)
            for col, idx, medal, color, mt in [
                (p1,0,"🥇","#f9a825","0px"),
                (p2,1,"🥈","#9e9e9e","20px"),
                (p3,2,"🥉","#bf6c00","20px")
            ]:
                e   = lb[idx]
                you = " ✦" if e["username"]==username else ""
                with col:
                    st.markdown(f"""
                    <div style="background:white;border-radius:16px;padding:20px;text-align:center;
                         margin-top:{mt};border-top:3px solid {color};
                         box-shadow:0 4px 16px rgba(0,0,0,0.06);">
                        <div style="font-size:32px;">{medal}</div>
                        <div style="font-weight:700;font-size:14px;color:#1a0533;margin:6px 0 2px;">{e['full_name']}{you}</div>
                        <div style="font-size:11px;color:#888;margin-bottom:10px;">@{e['username']}</div>
                        <div style="font-size:22px;font-weight:800;color:{color};">{e['score']}</div>
                        <div style="font-size:11px;color:#aaa;">points</div>
                        <div style="margin-top:10px;font-size:11px;color:#888;">
                            ⏱ {e['focus_hrs']}h · ✅ {e['topics_done']} · 🌳 {e['trees']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        for entry in lb:
            is_me  = entry["username"] == username
            bg     = "background:#f0ebff;" if is_me else ""
            border = "border:1px solid #7c3aed;" if is_me else "border:1px solid rgba(0,0,0,0.05);"
            you    = " ✦" if is_me else ""
            st.markdown(f"""
            <div class="lb-row" style="{bg}{border}">
                <div style="font-weight:800;font-size:16px;color:#7c3aed;width:28px;">{entry['medal']}</div>
                <div class="lb-avatar">{entry['full_name'][0]}</div>
                <div style="flex:1;">
                    <div class="lb-name">{entry['full_name']}{you}</div>
                    <div class="lb-sub">@{entry['username']} · ⏱{entry['focus_hrs']}h · 🌳{entry['trees']}</div>
                </div>
                <div class="lb-pts">{entry['score']} pts</div>
            </div>
            """, unsafe_allow_html=True)

    with right:
        right_profile_panel()


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
def main():
    init_db()

    if not st.session_state.get("logged_in"):
        show_login_page()
        return

    # Init daily missions
    init_daily_missions(st.session_state.get("username",""))
    # daily login tracked passively

    inject_css()
    page = render_sidebar()

    # Wrap content
    st.markdown('<div class="eq-content">', unsafe_allow_html=True)

    if   page == "Dashboard":     page_dashboard()
    elif page == "Learning Path":  page_learning_path()
    elif page == "Challenge":      page_challenge()
    elif page == "Visualizer":     visualizer_page()
    elif page == "AI Tutor":       page_ai_tutor()
    elif page == "Notebook":       notebook_page()
    elif page == "Focus Timer":    forest_page()
    elif page == "Music":          music_player_page()
    elif page == "Daily News":     news_page()
    elif page == "Leaderboard":    page_leaderboard()
    elif page == "Analytics":
        try:
            from analytics import analytics_page
            analytics_page()
        except:
            st.info("Analytics module coming soon!")
    elif page == "Missions":       page_missions()
    elif page == "Badges":         page_badges()

    st.markdown('</div>', unsafe_allow_html=True)


main()
