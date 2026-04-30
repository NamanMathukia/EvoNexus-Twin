"""
app/app.py
EvoNexus-Twin | Multi-Page Career Intelligence Engine
Entry point: Profile Configuration & Prediction
"""
import sys
import os
import streamlit as st

# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data.generator import SKILL_VOCABULARY
from utils import apply_custom_css

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EvoNexus-Twin | Profile Configuration",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_css()

# ── Sidebar Intro ─────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="text-align:center; padding: 10px 0 20px 0;">
    <div style="font-size: 2.5rem;">🧬</div>
    <div style="font-size: 1.5rem; font-weight: 700; color: #e2e8f0;">EvoNexus-Twin</div>
    <div style="font-size: 0.85rem; color: #94a3b8;">Career Intelligence Engine</div>
</div>
""", unsafe_allow_html=True)

# ── Main Content ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 10px 0 24px 0;">
    <h1 style="margin:0; font-size:2.5rem; font-weight:700;
               background: linear-gradient(90deg, #3b82f6, #a78bfa, #06b6d4);
               -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        🧬 Student Profile Configuration
    </h1>
    <p style="color:#94a3b8; font-size: 1.1rem; margin-top:10px;">
        Configure your academic and professional profile to generate a twin-driven placement prediction.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Profile Input Form ────────────────────────────────────────────────────────
with st.form("profile_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎓 Academic Profile")
        cgpa = st.slider("CGPA", 4.0, 10.0, 7.5, 0.1)
        academic_consistency = st.slider("Academic Consistency (0–1)", 0.0, 1.0, 0.75, 0.01)
        
        st.markdown("### 🛠 Skills & Demand")
        skills = st.slider("Skill Breadth Score (0–1)", 0.0, 1.0, 0.45, 0.01)
        skill_list = st.multiselect(
            "Acquired Skills", SKILL_VOCABULARY,
            default=["python", "sql", "machine_learning"]
        )
        skill_demand_score = st.slider("Target Market Demand (0–1)", 0.0, 1.0, 0.72, 0.01)

    with col2:
        st.markdown("### 💼 Professional Experience")
        internship = st.selectbox("Have you completed an internship?", [1, 0], format_func=lambda x: "Yes" if x else "No")
        internship_count = st.number_input("Number of Internships", 0, 5, 1 if internship else 0)
        internship_quality = st.slider("Average Internship Quality (0–1)", 0.0, 1.0, 0.65, 0.01)
        
        st.markdown("### 🎯 Career Portal Engagement")
        portal_activity = st.slider("Platform Activity Level (0–1)", 0.0, 1.0, 0.5, 0.01)
        resume_updates = st.number_input("Resume Update Count", 0, 15, 3)
        interviews = st.number_input("Mock Interviews Completed", 0, 25, 5)

    st.markdown("<br>", unsafe_allow_html=True)
    predict_btn = st.form_submit_button("⚡ Generate ENT Intelligence Report", use_container_width=True)

if predict_btn:
    sample = {
        "cgpa": cgpa,
        "skills": skills,
        "academic_consistency": academic_consistency,
        "internship": internship,
        "internship_count": internship_count,
        "internship_quality": internship_quality,
        "portal_activity": portal_activity,
        "resume_updates": resume_updates,
        "interviews": interviews,
        "skill_list": skill_list,
        "skill_demand_score": skill_demand_score,
        "market_demand": skill_demand_score,
    }
    
    from src.predict import predict_full
    try:
        with st.spinner("Analyzing profile via ENT Neural Engine..."):
            result = predict_full(sample)
            st.session_state.result = result
            st.session_state.sample = sample
            st.success("✅ Intelligence Report Generated! Navigate to the 'Dashboard' in the sidebar to view results.")
            st.balloons()
    except Exception as e:
        st.error(f"Error during prediction: {e}")

# ── Architecture Info ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🏗 ENT Architecture Overview</div>', unsafe_allow_html=True)
cols = st.columns(4)
arch_items = [
    ("📊", "Temporal Data", "Trajectory generation with semester-wise triplets."),
    ("🕸", "Knowledge Graph", "NetworkX-based student-skill-job relationship mapping."),
    ("🧠", "Neural Models", "LSTM sequence analysis & LGDESetNet skill interaction."),
    ("📉", "Survival & Risk", "WeibullAFT time-to-job & XGBoost/LGBM ensemble.")
]
for col, (icon, title, desc) in zip(cols, arch_items):
    col.markdown(f"""
    <div class="metric-card">
        <div style="font-size:2rem">{icon}</div>
        <div style="font-weight:600; color:#e2e8f0; margin:8px 0 4px">{title}</div>
        <div style="font-size:0.85rem; color:#94a3b8">{desc}</div>
    </div>
    """, unsafe_allow_html=True)