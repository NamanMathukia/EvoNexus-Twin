"""
app/pages/1_📊_Overview.py
High-level KPIs and Executive Summary.
"""
import os
import json
import streamlit as st
from utils import apply_custom_css, risk_color

st.set_page_config(page_title="ENT | Overview", page_icon="📊", layout="wide")
apply_custom_css()

# --- AUTO-LOADER: Fetch saved profile on fresh login ---
if "result" not in st.session_state or "sample" not in st.session_state:
    # 1. Grab the current user's email
    user_info = st.session_state.get("user_info")
    user_email = user_info.get("email") if user_info else None
    
    profile_loaded = False
    
    if user_email:
        # 2. Check the local database (users.json)
        USERS_FILE = os.path.join(os.path.dirname(__file__), "..", "users.json")
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, "r") as f:
                    saved_profile = json.load(f).get(user_email, {})
                
                # 3. If they have a saved profile, run the ML engine instantly
                if saved_profile:
                    with st.spinner("Rebuilding your dashboard..."):
                        from src.predict import predict_full
                        result = predict_full(saved_profile)
                        
                        # 4. Save to session state so the charts can render
                        st.session_state.sample = saved_profile
                        st.session_state.result = result
                        profile_loaded = True
            except Exception as e:
                st.error(f"Error loading saved profile: {e}")

    # 5. Failsafe: If they STILL have no data (e.g. brand new user), stop the page
    if not profile_loaded:
        st.warning("⚠️ No profile data found. Please go to the **Home** page and complete your profile setup first.")
        st.stop()
# -------------------------------------------------------

# By the time the code reaches here, it is 100% guaranteed to have the data!
result = st.session_state.result
risk = result["risk"]
salary = result["salary"]
time_j = result["time_to_job"]

st.markdown(f"""
<div style="padding: 10px 0 24px 0;">
    <h1 style="margin:0; font-size:2.5rem; font-weight:700; color:#e2e8f0;">
        📊 Placement Overview
    </h1>
    <p style="color:#94a3b8; font-size: 1.1rem; margin-top:10px;">
        High-level career indicators and executive intelligence summary.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Risk Badge ────────────────────────────────────────────────────────────────
rc = risk_color(risk)
badge_cls = f"risk-{risk.lower()}"
st.markdown(f"""
<div style="text-align:center; margin-bottom:30px;">
    <span class="risk-badge {badge_cls}">
        {'🔴' if risk=='High' else '🟡' if risk=='Medium' else '🟢'} {risk} Risk Profile
    </span>
</div>
""", unsafe_allow_html=True)

# ── KPI Metrics ───────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
metrics = [
    ("💰 Salary (LPA)", f"Rs.{salary:.1f}", "#3b82f6"),
    ("⏱ Time to Job", f"{time_j:.1f} Months", "#a78bfa"),
    ("🧠 LSTM Prob", f"{result['lstm_prob']*100:.1f}%", "#06b6d4"),
    ("🎯 SetNet Prob", f"{result['set_net_prob']*100:.1f}%", "#f59e0b"),
]
for col, (label, val, color) in zip([c1, c2, c3, c4], metrics):
    col.markdown(f"""
    <div class="metric-card">
        <div style="font-size:0.9rem; color:#94a3b8; margin-bottom:8px">{label}</div>
        <div style="font-size:1.8rem; font-weight:700; color:{color}">{val}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Executive Summary ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📝 Executive Intelligence Summary</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="summary-box">
    {result.get('summary', '')}
</div>
""", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.info("💡 Explore the sidebar for in-depth Risk Analysis, Career Roadmaps, and Placement Strategies.")
