"""
app/views/1_Overview.py
High-level KPIs and Executive Summary.
"""
import streamlit as st
from utils import apply_custom_css, risk_color

apply_custom_css()

if "result" not in st.session_state:
    st.warning("No profile data found. Please go to the Profile page and run the prediction first.")
    st.stop()

result = st.session_state.result
risk   = result["risk"]
salary = result["salary"]
time_j = result["time_to_job"]

st.markdown(f"""
<div style="padding: 10px 0 28px 0;">
    <div style="font-size:0.72rem; letter-spacing:0.18em; text-transform:uppercase;
                color:#475569; margin-bottom:10px;">Dashboard</div>
    <h1 style="margin:0; font-size:2.4rem; font-weight:800;
               font-family:'Space Grotesk',sans-serif; color:#e2e8f0;
               letter-spacing:-0.02em;">
        Placement Overview
    </h1>
    <p style="color:#64748b; font-size:1rem; margin-top:10px;">
        High-level career indicators and executive intelligence summary.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Risk Badge ────────────────────────────────────────────────────────────────
rc = risk_color(risk)
badge_cls = f"risk-{risk.lower()}"
risk_dot_color = "#ef4444" if risk == "High" else "#f59e0b" if risk == "Medium" else "#22c55e"
st.markdown(f"""
<div style="text-align:center; margin-bottom:32px;">
    <span class="risk-badge {badge_cls}">
        <span style="display:inline-block; width:8px; height:8px; border-radius:50%;
                     background:{risk_dot_color}; margin-right:8px;
                     box-shadow: 0 0 6px {risk_dot_color};"></span>
        {risk} Risk Profile
    </span>
</div>
""", unsafe_allow_html=True)

# ── KPI Metrics ───────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
metrics = [
    ("Salary (LPA)",    f"Rs.{salary:.1f}", "#3b82f6"),
    ("Time to Job",     f"{time_j:.1f} Mo",  "#a78bfa"),
    ("LSTM Probability",  f"{result['lstm_prob']*100:.1f}%",     "#06b6d4"),
    ("SetNet Probability", f"{result['set_net_prob']*100:.1f}%", "#f59e0b"),
]
for col, (label, val, color) in zip([c1, c2, c3, c4], metrics):
    col.markdown(f"""
    <div class="metric-card">
        <div style="font-size:0.72rem; letter-spacing:0.12em; text-transform:uppercase;
                    color:#475569; margin-bottom:10px;">{label}</div>
        <div style="font-size:1.9rem; font-weight:700; color:{color};
                    font-family:'Space Grotesk',sans-serif;">{val}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Executive Summary ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Executive Intelligence Summary</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="summary-box">
    {result.get('summary', '')}
</div>
""", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.info("Navigate the top bar to explore Risk Analysis, Career Roadmaps, and Placement Strategies.")
