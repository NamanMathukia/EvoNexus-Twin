"""
app/views/0_Home.py
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

apply_custom_css()

# ── Main Content ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 10px 0 28px 0;">
    <div style="font-size:0.72rem; letter-spacing:0.18em; text-transform:uppercase;
                color:#475569; margin-bottom:10px;">Profile Configuration</div>
    <h1 style="margin:0; font-size:2.4rem; font-weight:800;
               font-family:'Space Grotesk',sans-serif;
               background: linear-gradient(90deg, #3b82f6, #a78bfa, #06b6d4);
               -webkit-background-clip: text; -webkit-text-fill-color: transparent;
               letter-spacing:-0.02em;">
        Student Profile
    </h1>
    <p style="color:#64748b; font-size:1rem; margin-top:10px; max-width:600px;">
        Configure your academic and professional profile to generate a twin-driven placement prediction.
    </p>
</div>
""", unsafe_allow_html=True)

import json

USERS_FILE = os.path.join(os.path.dirname(__file__), "..", "users.json")

def load_user_profile(email):
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f).get(email, {})
    except:
        return {}

def save_user_profile(email, profile_data):
    users = {}
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                users = json.load(f)
        except:
            pass
    users[email] = profile_data
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

user_email = st.session_state.get("user_info", {}).get("email", "unknown")
profile_data = load_user_profile(user_email)
is_new_user = not bool(profile_data)

# ── Profile Input Form ────────────────────────────────────────────────────────
with st.form("profile_form"):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Academic Profile</div>', unsafe_allow_html=True)
        cgpa = st.slider("CGPA", 4.0, 10.0, float(profile_data.get("cgpa", 7.5)), 0.1)
        academic_consistency = st.slider("Academic Consistency (0-1)", 0.0, 1.0, float(profile_data.get("academic_consistency", 0.75)), 0.01)

        st.markdown('<div class="section-header">Skills & Demand</div>', unsafe_allow_html=True)
        skills = st.slider("Skill Breadth Score (0-1)", 0.0, 1.0, float(profile_data.get("skills", 0.45)), 0.01)
        skill_list = st.multiselect(
            "Acquired Skills", SKILL_VOCABULARY,
            default=profile_data.get("skill_list", ["python", "sql", "machine_learning"])
        )
        skill_demand_score = st.slider("Target Market Demand (0-1)", 0.0, 1.0, float(profile_data.get("skill_demand_score", 0.72)), 0.01)

    with col2:
        st.markdown('<div class="section-header">Professional Experience</div>', unsafe_allow_html=True)
        intern_index = 0 if profile_data.get("internship", 0) == 1 else 1
        internship = st.selectbox("Have you completed an internship?", [1, 0], index=intern_index, format_func=lambda x: "Yes" if x else "No")
        intern_count_val = int(profile_data.get("internship_count", 1 if internship else 0))
        internship_count = st.number_input("Number of Internships", 0, 5, intern_count_val)
        internship_quality = st.slider("Average Internship Quality (0-1)", 0.0, 1.0, float(profile_data.get("internship_quality", 0.65)), 0.01)

        st.markdown('<div class="section-header">Career Portal Engagement</div>', unsafe_allow_html=True)
        portal_activity = st.slider("Platform Activity Level (0-1)", 0.0, 1.0, float(profile_data.get("portal_activity", 0.5)), 0.01)
        resume_updates = st.number_input("Resume Update Count", 0, 15, int(profile_data.get("resume_updates", 3)))
        interviews = st.number_input("Mock Interviews Completed", 0, 25, int(profile_data.get("interviews", 5)))

    st.markdown("<br>", unsafe_allow_html=True)
    btn_text = "SAVE PROFILE & GENERATE REPORT" if is_new_user else "UPDATE PROFILE & GENERATE REPORT"
    predict_btn = st.form_submit_button(btn_text, use_container_width=True)

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

    save_user_profile(user_email, sample)

    from src.predict import predict_full
    try:
        with st.spinner("Analyzing profile via ENT Neural Engine..."):
            result = predict_full(sample)
            st.session_state.result = result
            st.session_state.sample = sample
            if is_new_user:
                st.success("Profile saved — redirecting to dashboard...")
                st.balloons()
                import time
                time.sleep(2)
                st.rerun()
            else:
                st.success("Profile updated — Intelligence Report generated.")
    except Exception as e:
        st.error(f"Error during prediction: {e}")

# ── Architecture Overview ─────────────────────────────────────────────────────
st.markdown('<div class="section-header">ENT Architecture Overview</div>', unsafe_allow_html=True)
cols = st.columns(4)
arch_items = [
    ("TD", "Temporal Data",    "Trajectory generation with semester-wise triplets."),
    ("KG", "Knowledge Graph",  "NetworkX-based student-skill-job relationship mapping."),
    ("NM", "Neural Models",    "LSTM sequence analysis & LGDESetNet skill interaction."),
    ("SR", "Survival & Risk",  "WeibullAFT time-to-job & XGBoost/LGBM ensemble."),
]
for col, (abbr, title, desc) in zip(cols, arch_items):
    col.markdown(f"""
    <div class="metric-card">
        <div style="font-family:'Space Grotesk',sans-serif; font-size:1.6rem; font-weight:800;
                    background:linear-gradient(135deg,#3b82f6,#a78bfa);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                    margin-bottom:8px;">{abbr}</div>
        <div style="font-weight:600; color:#e2e8f0; margin-bottom:6px; font-size:0.9rem;">{title}</div>
        <div style="font-size:0.8rem; color:#64748b; line-height:1.5;">{desc}</div>
    </div>
    """, unsafe_allow_html=True)