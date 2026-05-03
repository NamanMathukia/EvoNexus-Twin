"""
app/utils.py
Shared utilities and styles for the EvoNexus-Twin multi-page app.
"""
import streamlit as st
import plotly.graph_objects as go


def apply_custom_css():
    st.markdown("""
    <style>
    /* ── Google Fonts ─────────────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    /* ── Global Reset & Base ──────────────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        -webkit-font-smoothing: antialiased;
    }

    /* ── HIDE NATIVE STREAMLIT UI CHROME ──────────────────────────────────── */
    [data-testid="stSidebar"]          { display: none !important; }
    [data-testid="stHeader"]           { display: none !important; }
    [data-testid="stToolbar"]          { display: none !important; }
    [data-testid="stDecoration"]       { display: none !important; }
    #MainMenu                          { visibility: hidden !important; }
    footer                             { visibility: hidden !important; }
    .stDeployButton                    { display: none !important; }

    /* ── MAIN BACKGROUND ──────────────────────────────────────────────────── */
    .stApp {
        background: #070b14 !important;
        background-image:
            radial-gradient(ellipse at 20% 10%, rgba(59,130,246,0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 80%, rgba(167,139,250,0.06) 0%, transparent 50%);
    }
    .main .block-container {
        padding-top: 90px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1400px !important;
    }

    /* ── STICKY TOP NAVIGATION BAR ────────────────────────────────────────── */
    .ent-topbar {
        position: fixed;
        top: 0; left: 0; right: 0;
        z-index: 9999;
        height: 62px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 2rem;
        background: rgba(7, 11, 20, 0.82);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(59, 130, 246, 0.18);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
    }
    .ent-topbar-brand {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        background: linear-gradient(90deg, #3b82f6, #a78bfa, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-decoration: none;
        white-space: nowrap;
    }
    .ent-topbar-nav {
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    .ent-nav-link {
        color: #94a3b8;
        text-decoration: none;
        font-size: 0.82rem;
        font-weight: 500;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 6px 14px;
        border-radius: 6px;
        border: 1px solid transparent;
        transition: color 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease, background 0.25s ease;
        white-space: nowrap;
    }
    .ent-nav-link:hover {
        color: #e2e8f0;
        background: rgba(59, 130, 246, 0.1);
        border-color: rgba(59, 130, 246, 0.35);
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.2);
    }
    .ent-nav-link.active {
        color: #60a5fa;
        background: rgba(59, 130, 246, 0.12);
        border-color: rgba(59, 130, 246, 0.4);
    }
    .ent-topbar-right {
        display: flex;
        align-items: center;
        gap: 0.85rem;
    }
    .ent-user-chip {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(51, 65, 85, 0.8);
        border-radius: 20px;
        padding: 4px 12px 4px 8px;
    }
    .ent-user-avatar {
        width: 26px; height: 26px;
        background: linear-gradient(135deg, #3b82f6, #a78bfa);
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.7rem; font-weight: 700; color: white;
        flex-shrink: 0;
    }
    .ent-user-name {
        font-size: 0.78rem;
        font-weight: 500;
        color: #cbd5e1;
        max-width: 120px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    /* ── GLASSMORPHISM CONTAINERS ─────────────────────────────────────────── */
    [data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"],
    [data-testid="column"] > div[data-testid="stVerticalBlock"] {
        background: rgba(15, 23, 42, 0.55);
        border: 1px solid rgba(51, 65, 85, 0.45);
        border-radius: 14px;
        padding: 1px;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        transition: border-color 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
    }
    [data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:hover,
    [data-testid="column"] > div[data-testid="stVerticalBlock"]:hover {
        border-color: rgba(59, 130, 246, 0.35);
        box-shadow: 0 0 22px rgba(59, 130, 246, 0.12), 0 8px 32px rgba(0,0,0,0.35);
    }

    /* ── METRIC CARDS ─────────────────────────────────────────────────────── */
    .metric-card {
        background: linear-gradient(135deg, rgba(31,41,55,0.9) 0%, rgba(17,24,39,0.9) 100%);
        border: 1px solid rgba(55, 65, 81, 0.7);
        border-radius: 14px;
        padding: 22px;
        text-align: center;
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
        backdrop-filter: blur(8px);
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.45), 0 0 20px rgba(59,130,246,0.15);
        border-color: rgba(59, 130, 246, 0.4);
    }

    /* ── RISK BADGES ──────────────────────────────────────────────────────── */
    .risk-high   { background: linear-gradient(135deg,rgba(127,29,29,0.85),rgba(153,27,27,0.85)); color:#fca5a5; border: 1px solid rgba(239,68,68,0.6); }
    .risk-medium { background: linear-gradient(135deg,rgba(120,53,15,0.85),rgba(146,64,14,0.85)); color:#fcd34d; border: 1px solid rgba(245,158,11,0.6); }
    .risk-low    { background: linear-gradient(135deg,rgba(20,83,45,0.85),rgba(22,101,52,0.85)); color:#86efac; border: 1px solid rgba(34,197,94,0.6); }
    .risk-badge  { padding: 9px 24px; border-radius: 20px; font-weight: 700; font-size: 1.05rem; display: inline-block; letter-spacing: 0.05em; backdrop-filter: blur(8px); }

    /* ── AGENT CARDS ──────────────────────────────────────────────────────── */
    .agent-card {
        background: linear-gradient(135deg, rgba(30,41,59,0.85) 0%, rgba(15,23,42,0.85) 100%);
        border: 1px solid rgba(51, 65, 85, 0.7);
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 12px;
        height: 100%;
        backdrop-filter: blur(10px);
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
    .agent-card:hover {
        border-color: rgba(59, 130, 246, 0.4);
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.12);
    }

    /* ── SECTION HEADERS ──────────────────────────────────────────────────── */
    .section-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #60a5fa;
        border-bottom: 1px solid rgba(59, 130, 246, 0.3);
        padding-bottom: 8px;
        margin: 28px 0 16px 0;
    }

    /* ── TIMELINE ─────────────────────────────────────────────────────────── */
    .timeline-item {
        border-left: 2px solid #3b82f6;
        padding-left: 18px;
        margin-bottom: 24px;
        position: relative;
        transition: border-color 0.25s ease;
    }
    .timeline-item:hover { border-left-color: #60a5fa; }
    .timeline-dot {
        width: 10px; height: 10px;
        background: #3b82f6;
        border-radius: 50%;
        position: absolute; left: -6px; top: 6px;
        box-shadow: 0 0 8px rgba(59, 130, 246, 0.6);
    }

    /* ── SKILL PILLS ──────────────────────────────────────────────────────── */
    .skill-pill {
        display: inline-block;
        background: rgba(30, 58, 95, 0.7);
        color: #93c5fd;
        border: 1px solid rgba(59, 130, 246, 0.4);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.82rem;
        margin: 4px;
        transition: background 0.2s ease, box-shadow 0.2s ease;
    }
    .skill-pill:hover {
        background: rgba(59, 130, 246, 0.2);
        box-shadow: 0 0 8px rgba(59, 130, 246, 0.3);
    }

    /* ── SUMMARY BOX ──────────────────────────────────────────────────────── */
    .summary-box {
        background: linear-gradient(135deg, rgba(30,58,95,0.6) 0%, rgba(15,39,68,0.6) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 14px;
        padding: 26px;
        color: #e2e8f0;
        line-height: 1.85;
        font-size: 1.05rem;
        backdrop-filter: blur(8px);
    }

    /* ── STREAMLIT NATIVE WIDGET OVERRIDES ────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(15, 23, 42, 0.6);
        border-radius: 10px;
        padding: 4px;
        border: 1px solid rgba(51, 65, 85, 0.5);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #64748b;
        transition: color 0.2s, background 0.2s;
        padding: 8px 18px;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(59, 130, 246, 0.15) !important;
        color: #60a5fa !important;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.15);
    }
    div[data-testid="stMetric"] {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(55, 65, 81, 0.6);
        border-radius: 12px;
        padding: 16px 20px;
        transition: box-shadow 0.25s ease;
    }
    div[data-testid="stMetric"]:hover {
        box-shadow: 0 0 16px rgba(59, 130, 246, 0.15);
    }
    div[data-testid="stMetric"] label { color: #64748b !important; font-size: 0.78rem !important; letter-spacing: 0.08em; text-transform: uppercase; }
    div[data-testid="stMetricValue"]  { color: #e2e8f0 !important; font-family: 'Space Grotesk', sans-serif; }
    div[data-testid="stExpander"] {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(51, 65, 85, 0.5) !important;
        border-radius: 10px !important;
        transition: border-color 0.25s ease;
    }
    div[data-testid="stExpander"]:hover {
        border-color: rgba(59, 130, 246, 0.35) !important;
    }
    textarea, input[type="text"], input[type="number"], .stTextArea textarea {
        background: rgba(17, 24, 39, 0.8) !important;
        border: 1px solid rgba(55, 65, 81, 0.7) !important;
        border-radius: 8px !important;
        color: #e2e8f0 !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    textarea:focus, input[type="text"]:focus {
        border-color: rgba(59, 130, 246, 0.6) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        letter-spacing: 0.04em !important;
        transition: box-shadow 0.25s ease, transform 0.15s ease !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 25px rgba(59, 130, 246, 0.5) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button:not([kind="primary"]) {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(51, 65, 85, 0.7) !important;
        color: #94a3b8 !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        border-color: rgba(59, 130, 246, 0.4) !important;
        color: #e2e8f0 !important;
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.15) !important;
    }
    .stFileUploader {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px dashed rgba(59, 130, 246, 0.35) !important;
        border-radius: 10px !important;
        padding: 8px !important;
    }
    div[data-baseweb="select"] > div {
        background: rgba(17, 24, 39, 0.8) !important;
        border: 1px solid rgba(55, 65, 81, 0.7) !important;
        border-radius: 8px !important;
    }
    .stSlider [data-baseweb="slider"] { }
    .stSlider [data-baseweb="thumb"] {
        background: #3b82f6 !important;
        box-shadow: 0 0 8px rgba(59, 130, 246, 0.5) !important;
    }
    .stAlert {
        border-radius: 10px !important;
        border-left-width: 3px !important;
    }
    hr { border-color: rgba(51, 65, 85, 0.5) !important; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; }

    /* ── SCROLLBAR ────────────────────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #070b14; }
    ::-webkit-scrollbar-thumb { background: rgba(59,130,246,0.35); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(59,130,246,0.6); }
    </style>
    """, unsafe_allow_html=True)


def render_topbar(user_info: dict, logout_key: str = "topbar_logout"):
    """
    Renders the sticky glassmorphic top navigation bar.
    Returns True if the logout button was clicked.
    """
    name = (user_info or {}).get("name", "User")
    initials = "".join(p[0].upper() for p in name.split()[:2]) if name else "U"

    st.markdown(f"""
    <div class="ent-topbar">
        <a class="ent-topbar-brand" href="/" target="_self">EVONEXUS-TWIN</a>
        <nav class="ent-topbar-nav">
            <a class="ent-nav-link" href="/Overview"         target="_self">Overview</a>
            <a class="ent-nav-link" href="/Risk-Analysis"    target="_self">Risk Analysis</a>
            <a class="ent-nav-link" href="/Career-Roadmap"   target="_self">Career Roadmap</a>
            <a class="ent-nav-link" href="/Placement-Strategy" target="_self">Placement</a>
            <a class="ent-nav-link" href="/"                 target="_self">Profile</a>
        </nav>
        <div class="ent-topbar-right">
            <div class="ent-user-chip">
                <div class="ent-user-avatar">{initials}</div>
                <span class="ent-user-name">{name}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Real Streamlit logout button — hidden visually under the bar but functional
    # We place it in a zero-height div trick so layout isn't disturbed
    st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"]:has(> div > .ent-logout-wrapper) {
        position: fixed; top: 14px; right: 14px; z-index: 10000;
        width: auto !important; padding: 0 !important;
        background: transparent !important; border: none !important;
        box-shadow: none !important; backdrop-filter: none !important;
    }
    .ent-logout-wrapper { display: contents; }
    div[data-testid="stVerticalBlock"]:has(> div > .ent-logout-wrapper) > div {
        background: transparent !important; border: none !important;
        box-shadow: none !important; backdrop-filter: none !important;
    }
    </style>
    <div class="ent-logout-wrapper"></div>
    """, unsafe_allow_html=True)

    return st.button("Logout", key=logout_key, type="secondary")


def gauge_chart(value: float, title: str, color: str, min_val=0, max_val=100):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"color": "#e2e8f0", "size": 15, "family": "Space Grotesk"}},
        gauge={
            "axis":  {"range": [min_val, max_val], "tickcolor": "#475569", "tickfont": {"color": "#475569"}},
            "bar":   {"color": color},
            "bgcolor": "rgba(0,0,0,0)",
            "bordercolor": "rgba(0,0,0,0)",
            "steps": [
                {"range": [0,  33], "color": "rgba(15,23,42,0.8)"},
                {"range": [33, 66], "color": "rgba(20,30,55,0.8)"},
                {"range": [66, 100], "color": "rgba(15,40,60,0.8)"},
            ],
            "threshold": {
                "line": {"color": color, "width": 2},
                "thickness": 0.75,
                "value": value,
            },
        },
        number={"font": {"color": color, "size": 30, "family": "Space Grotesk"}, "suffix": ""},
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        height=240,
        margin=dict(l=20, r=20, t=50, b=10),
        transition={"duration": 500, "easing": "cubic-in-out"},
    )
    return fig


def risk_color(risk: str) -> str:
    return {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"}.get(risk, "#94a3b8")
