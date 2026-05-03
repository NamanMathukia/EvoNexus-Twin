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
        padding-top: 80px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1400px !important;
    }

    /* ── STICKY TOP NAVIGATION BAR ────────────────────────────────────────── */
    .ent-topbar {
        position: fixed;
        top: 0; left: 0; right: 0;
        z-index: 9999;
        height: 70px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 3rem;
        background: rgba(7, 11, 20, 0.75);
        backdrop-filter: blur(24px) saturate(180%);
        -webkit-backdrop-filter: blur(24px) saturate(180%);
        border-bottom: 1px solid rgba(59, 130, 246, 0.15);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }
    .ent-topbar-brand {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.3rem;
        font-weight: 800;
        letter-spacing: 0.05em;
        background: linear-gradient(90deg, #3b82f6, #a78bfa, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-decoration: none;
        white-space: nowrap;
    }
    .ent-topbar-nav {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .ent-nav-link {
        color: #64748b;
        text-decoration: none;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 8px 18px;
        border-radius: 8px;
        border: 1px solid transparent;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        white-space: nowrap;
    }
    .ent-nav-link:hover {
        color: #e2e8f0;
        background: rgba(59, 130, 246, 0.08);
        border-color: rgba(59, 130, 246, 0.25);
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.1);
    }
    .ent-nav-link.active {
        color: #60a5fa;
        background: rgba(59, 130, 246, 0.12);
        border-color: rgba(59, 130, 246, 0.4);
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.15);
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
    [data-testid="column"] > div[data-testid="stVerticalBlock"],
    .stTabs, [data-testid="stExpander"] {
        background: rgba(15, 23, 42, 0.4) !important;
        border: 1px solid rgba(51, 65, 85, 0.4) !important;
        border-radius: 20px !important;
        padding: 24px !important;
        backdrop-filter: blur(16px) saturate(120%) !important;
        -webkit-backdrop-filter: blur(16px) saturate(120%) !important;
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2) !important;
    }
    
    [data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:hover,
    [data-testid="column"] > div[data-testid="stVerticalBlock"]:hover {
        border-color: rgba(59, 130, 246, 0.4) !important;
        box-shadow: 0 0 30px rgba(59, 130, 246, 0.15), 0 12px 40px rgba(0,0,0,0.4) !important;
        transform: translateY(-2px);
    }

    /* ── METRIC CARDS ─────────────────────────────────────────────────────── */
    .metric-card {
        background: rgba(30, 41, 59, 0.45);
        border: 1px solid rgba(55, 65, 81, 0.5);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        border-color: rgba(59, 130, 246, 0.5);
        box-shadow: 0 0 25px rgba(59, 130, 246, 0.2);
    }

    /* ── RISK BADGES ──────────────────────────────────────────────────────── */
    .risk-high   { background: linear-gradient(135deg,rgba(127,29,29,0.85),rgba(153,27,27,0.85)); color:#fca5a5; border: 1px solid rgba(239,68,68,0.6); }
    .risk-medium { background: linear-gradient(135deg,rgba(120,53,15,0.85),rgba(146,64,14,0.85)); color:#fcd34d; border: 1px solid rgba(245,158,11,0.6); }
    .risk-low    { background: linear-gradient(135deg,rgba(20,83,45,0.85),rgba(22,101,52,0.85)); color:#86efac; border: 1px solid rgba(34,197,94,0.6); }
    .risk-badge  { padding: 9px 24px; border-radius: 20px; font-weight: 700; font-size: 1.05rem; display: inline-block; letter-spacing: 0.05em; backdrop-filter: blur(8px); }

    /* ── AGENT CARDS ──────────────────────────────────────────────────────── */
    .agent-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(51, 65, 85, 0.45);
        border-radius: 20px;
        padding: 24px;
        backdrop-filter: blur(12px);
        transition: all 0.3s ease;
    }
    .agent-card:hover {
        border-color: rgba(59, 130, 246, 0.4);
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.12);
    }

    /* ── SECTION HEADERS ──────────────────────────────────────────────────── */
    .section-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #60a5fa;
        margin: 32px 0 16px 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .section-header::after {
        content: "";
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(59, 130, 246, 0.3), transparent);
    }

    /* ── TIMELINE ─────────────────────────────────────────────────────────── */
    .timeline-item {
        border-left: 2px solid #3b82f6;
        padding-left: 20px;
        margin-bottom: 28px;
        position: relative;
        transition: border-color 0.3s ease;
    }
    .timeline-dot {
        width: 12px; height: 12px;
        background: #3b82f6;
        border-radius: 50%;
        position: absolute; left: -7px; top: 6px;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.6);
    }

    /* ── SKILL PILLS ──────────────────────────────────────────────────────── */
    .skill-pill {
        display: inline-block;
        background: rgba(59, 130, 246, 0.1);
        color: #93c5fd;
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 20px;
        padding: 5px 15px;
        font-size: 0.8rem;
        margin: 4px;
        transition: all 0.2s ease;
    }
    .skill-pill:hover {
        background: rgba(59, 130, 246, 0.2);
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
    }

    /* ── SUMMARY BOX ──────────────────────────────────────────────────────── */
    .summary-box {
        background: rgba(15, 23, 42, 0.3);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 20px;
        padding: 30px;
        color: #e2e8f0;
        line-height: 1.8;
        font-size: 1rem;
        backdrop-filter: blur(10px);
    }

    /* ── STREAMLIT WIDGET OVERRIDES ───────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid rgba(51, 65, 85, 0.5) !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 0.75rem !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        color: #64748b !important;
    }
    .stTabs [aria-selected="true"] {
        color: #60a5fa !important;
        border-bottom-color: #3b82f6 !important;
    }
    
    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.4) !important;
        border: 1px solid rgba(51, 65, 85, 0.4) !important;
        padding: 20px !important;
        border-radius: 16px !important;
    }

    .stButton > button {
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        font-size: 0.75rem !important;
    }

    /* ── SCROLLBAR ────────────────────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(59,130,246,0.2); border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(59,130,246,0.5); }
    </style>
    """, unsafe_allow_html=True)


def render_topbar(user_info: dict, logout_key: str = "topbar_logout"):
    """
    Renders the sticky glassmorphic top navigation bar.
    Using standard links for maximum visual stability.
    """
    name = (user_info or {}).get("name", "User")
    initials = "".join(p[0].upper() for p in name.split()[:2]) if name else "U"
    current_nav = st.query_params.get("nav", "Overview")

    nav_items = [
        ("Overview", "Overview"),
        ("Risk-Analysis", "Risk"),
        ("Career-Roadmap", "Roadmap"),
        ("Placement-Strategy", "Placement"),
        ("Profile", "Profile")
    ]

    nav_html = ""
    for nav_id, label in nav_items:
        active_class = "active" if current_nav == nav_id else ""
        nav_html += f'<a class="ent-nav-link {active_class}" href="/?nav={nav_id}" target="_self">{label}</a>'

    st.markdown(f"""
    <div class="ent-topbar">
        <a class="ent-topbar-brand" href="/?nav=Overview" target="_self">EVONEXUS</a>
        <nav class="ent-topbar-nav">
            {nav_html}
        </nav>
        <div class="ent-topbar-right">
            <div class="ent-user-chip">
                <div class="ent-user-avatar">{initials}</div>
                <span class="ent-user-name">{name}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Hidden functional logout button
    st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"]:has(> div > .ent-logout-wrapper) {
        position: fixed; top: 18px; right: 2rem; z-index: 10000;
        width: auto !important; padding: 0 !important;
        background: transparent !important; border: none !important;
        box-shadow: none !important; backdrop-filter: none !important;
    }
    .ent-logout-wrapper { display: contents; }
    div[data-testid="stVerticalBlock"]:has(> div > .ent-logout-wrapper) > div {
        background: transparent !important; border: none !important;
        box-shadow: none !important; backdrop-filter: none !important;
    }
    .stButton > button[kind="secondary"] {
        background: rgba(239, 68, 68, 0.1) !important;
        color: #f87171 !important;
        border: 1px solid rgba(239, 68, 68, 0.2) !important;
        font-size: 0.65rem !important;
        padding: 4px 12px !important;
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
