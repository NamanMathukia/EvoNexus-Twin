"""
app/utils.py
Shared utilities and styles for the EvoNexus-Twin multi-page app.
"""
import streamlit as st
import plotly.graph_objects as go

def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%); }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #161b22 0%, #0d1117 100%);
        border-right: 1px solid #30363d;
    }
    .metric-card {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.4); }
    .risk-high   { background: linear-gradient(135deg,#7f1d1d,#991b1b); color:#fca5a5; border: 1px solid #ef4444; }
    .risk-medium { background: linear-gradient(135deg,#78350f,#92400e); color:#fcd34d; border: 1px solid #f59e0b; }
    .risk-low    { background: linear-gradient(135deg,#14532d,#166534); color:#86efac; border: 1px solid #22c55e; }
    .risk-badge  { padding: 8px 20px; border-radius: 20px; font-weight: 700; font-size: 1.1rem; display: inline-block; }
    .agent-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 12px;
        height: 100%;
    }
    .section-header {
        font-size: 1.2rem; font-weight: 600; color: #e2e8f0;
        border-bottom: 2px solid #3b82f6; padding-bottom: 6px; margin: 20px 0 14px 0;
    }
    .timeline-item {
        border-left: 3px solid #3b82f6;
        padding-left: 14px;
        margin-bottom: 20px;
        position: relative;
    }
    .timeline-dot {
        width: 12px; height: 12px;
        background: #3b82f6; border-radius: 50%;
        position: absolute; left: -8px; top: 4px;
    }
    .skill-pill {
        display: inline-block;
        background: #1e3a5f; color: #93c5fd;
        border: 1px solid #3b82f6;
        border-radius: 20px; padding: 4px 12px;
        font-size: 0.85rem; margin: 4px;
    }
    .summary-box {
        background: linear-gradient(135deg, #1e3a5f 0%, #0f2744 100%);
        border: 1px solid #3b82f6;
        border-radius: 12px; padding: 24px;
        color: #e2e8f0; line-height: 1.8;
        font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)

def gauge_chart(value: float, title: str, color: str, min_val=0, max_val=100):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"color": "#e2e8f0", "size": 16}},
        gauge={
            "axis":  {"range": [min_val, max_val], "tickcolor": "#94a3b8"},
            "bar":   {"color": color},
            "bgcolor": "#1f2937",
            "bordercolor": "#374151",
            "steps": [
                {"range": [0,  33], "color": "#1a2535"},
                {"range": [33, 66], "color": "#1e2d40"},
                {"range": [66, 100], "color": "#1a3a4a"},
            ],
        },
        number={"font": {"color": color, "size": 32}},
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        height=250,
        margin=dict(l=30, r=30, t=50, b=20),
    )
    return fig

def risk_color(risk: str) -> str:
    return {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"}.get(risk, "#94a3b8")
