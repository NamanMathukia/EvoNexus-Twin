"""
app/pages/2_🔍_Risk_Analysis.py
In-depth risk drivers, interactions, and trajectory analysis.
"""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
from utils import apply_custom_css, gauge_chart

st.set_page_config(page_title="ENT | Risk Analysis", page_icon="🔍", layout="wide")
apply_custom_css()

if "result" not in st.session_state:
    st.warning("⚠️ No data found. Run the prediction on the **Home** page first.")
    st.stop()

result = st.session_state.result
sample = st.session_state.sample
drivers = result["drivers"]

st.markdown("""
<div style="padding: 10px 0 24px 0;">
    <h1 style="margin:0; font-size:2.5rem; font-weight:700; color:#e2e8f0;">
        🔍 Risk & Performance Drivers
    </h1>
    <p style="color:#94a3b8; font-size: 1.1rem; margin-top:10px;">
        Deep dive into SHAP values, feature interactions, and semester-wise trajectories.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Row 1: Gauges ─────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1:
    readiness = result["actions"].get("interview_mentor", {}).get("readiness_score", 50)
    st.plotly_chart(gauge_chart(readiness, "Interview Readiness", "#3b82f6"), use_container_width=True)
with c2:
    st.plotly_chart(gauge_chart(result["lstm_prob"] * 100, "LSTM Placement %", "#a78bfa"), use_container_width=True)
with c3:
    st.plotly_chart(gauge_chart(result["set_net_prob"] * 100, "SetNet Placement %", "#06b6d4"), use_container_width=True)

# ── Row 2: SHAP Waterfall ─────────────────────────────────────────────────────
st.markdown('<div class="section-header">🧬 SHAP Risk Drivers (Impact Analysis)</div>', unsafe_allow_html=True)
features = [d[0].replace("_", " ") for d in drivers]
values   = [d[1] for d in drivers]
colors   = ["#ef4444" if v > 0 else "#22c55e" for v in values]

fig = go.Figure(go.Bar(
    x=values, y=features, orientation="h",
    marker_color=colors,
    text=[f"{v:+.4f}" for v in values],
    textposition="outside",
    textfont={"color": "#e2e8f0", "size": 12},
))
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,23,42,0.6)",
    font_color="#e2e8f0",
    xaxis={"title": "SHAP Value (Contribution to Risk)", "gridcolor": "#374151"},
    yaxis={"gridcolor": "#374151", "autorange": "reversed"},
    height=400,
    margin=dict(l=20, r=80, t=20, b=20),
)
st.plotly_chart(fig, use_container_width=True)

# ── Row 3: Interactions & Trajectory ──────────────────────────────────────────
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="section-header">🔗 Feature Interactions</div>', unsafe_allow_html=True)
    for pair, val in result["interactions"]:
        direction = "🔴 High Risk Synergy" if val > 0 else "🟢 Protective Interaction"
        st.markdown(f"""
        <div style="background:#1e293b; border:1px solid #334155; border-radius:8px;
                    padding:12px 16px; margin-bottom:10px; display:flex; justify-content:space-between;">
            <span style="color:#94a3b8; font-weight:500;">{pair}</span>
            <span style="color:{'#ef4444' if val>0 else '#22c55e'}; font-weight:600;">{direction}</span>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-header">📈 Simulated Trajectory</div>', unsafe_allow_html=True)
    sems = list(range(1, 9))
    cgpa = sample.get("cgpa", 7.0)
    skill = sample.get("skills", 0.3)
    cgpa_vals  = [round(cgpa * (0.88 + 0.015 * s), 2) for s in sems]
    skill_vals = [round(skill * (s / 8), 3) for s in sems]

    fig_t = go.Figure()
    fig_t.add_trace(go.Scatter(x=sems, y=cgpa_vals, name="CGPA", line={"color": "#3b82f6", "width": 3}))
    fig_t.add_trace(go.Scatter(x=sems, y=[v * 10 for v in skill_vals], name="Skills x10", line={"color": "#a78bfa", "width": 3, "dash": "dot"}))
    fig_t.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.6)",
        font_color="#e2e8f0", height=300,
        xaxis={"title": "Semester", "gridcolor": "#374151"},
        yaxis={"title": "Metric Value", "gridcolor": "#374151"},
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig_t, use_container_width=True)
