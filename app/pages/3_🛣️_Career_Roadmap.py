"""
app/pages/3_🛣️_Career_Roadmap.py
Skill Coach, Interview Mentor, and Milestone Timeline.
"""
import streamlit as st
from utils import apply_custom_css

st.set_page_config(page_title="ENT | Career Roadmap", page_icon="🛣️", layout="wide")
apply_custom_css()

if "result" not in st.session_state:
    st.warning("⚠️ No data found. Run the prediction on the **Home** page first.")
    st.stop()

result = st.session_state.result
actions = result["actions"]
skill_out = actions.get("skill_coach", {})
mentor_out = actions.get("interview_mentor", {})

st.markdown("""
<div style="padding: 10px 0 24px 0;">
    <h1 style="margin:0; font-size:2.5rem; font-weight:700; color:#e2e8f0;">
        🛣️ Growth & Readiness Roadmap
    </h1>
    <p style="color:#94a3b8; font-size: 1.1rem; margin-top:10px;">
        Agent-driven skill gap analysis, interview preparation, and development timeline.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Top Row: Agent Cards ──────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="agent-card">
        <h3 style="color:#3b82f6; margin-top:0;">🎓 Skill Coach Agent</h3>
        <p style="color:#cbd5e1; font-size:0.95rem;">{skill_out.get('gap_analysis', '')}</p>
        <div style="margin: 15px 0;">
            <b style="color:#e2e8f0;">Priority Certifications:</b>
    """, unsafe_allow_html=True)
    for cert in skill_out.get("certifications", [])[:3]:
        st.markdown(f"• **{cert['skill'].upper()}**: {cert['certification']}")
    st.markdown(f"""
            <br><b style="color:#e2e8f0;">Core Focus Clusters:</b><br>
    """, unsafe_allow_html=True)
    for cluster in skill_out.get("priority_skills", []):
        st.markdown(f"• {cluster['cluster']}: {', '.join(cluster['missing_skills'])}")
    st.markdown(f"</div><p style='color:#94a3b8;'>Estimated Upskilling Time: <b>{skill_out.get('timeline_weeks', '?')} Weeks</b></p></div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="agent-card">
        <h3 style="color:#a78bfa; margin-top:0;">🎤 Interview Mentor Agent</h3>
        <p style="color:#cbd5e1;">Readiness Label: <b>{mentor_out.get('readiness_label', '?')}</b> ({mentor_out.get('readiness_score', 0)}/100)</p>
        <div style="margin: 15px 0;">
            <b style="color:#e2e8f0;">Weekly Preparation Plan:</b>
    """, unsafe_allow_html=True)
    for step in mentor_out.get("weekly_plan", []):
        st.markdown(f"• {step}")
    st.markdown("<br><b style='color:#e2e8f0;'>Critical Readiness Gaps:</b>", unsafe_allow_html=True)
    for gap in mentor_out.get("critical_gaps", []):
        st.markdown(f"⚠️ {gap}")
    st.markdown('</div></div>', unsafe_allow_html=True)

# ── Bottom Row: Milestone Timeline ────────────────────────────────────────────
st.markdown('<div class="section-header">🗓 Implementation Timeline & Milestones</div>', unsafe_allow_html=True)
roadmap = actions.get("improvement_roadmap", [])
for i, milestone in enumerate(roadmap):
    color = ["#3b82f6", "#a78bfa", "#06b6d4", "#22c55e"][i % 4]
    st.markdown(f"""
    <div class="timeline-item" style="border-left-color:{color}">
        <div class="timeline-dot" style="background:{color}"></div>
        <div style="font-weight:700; color:{color}; font-size:1rem; text-transform:uppercase;">{milestone['phase']}</div>
        <div style="font-weight:600; color:#e2e8f0; font-size:1.1rem; margin-top:4px;">{milestone['focus']}</div>
        <div style="color:#94a3b8; font-size:1rem; margin-top:6px; line-height:1.6;">{milestone['actions']}</div>
    </div>
    """, unsafe_allow_html=True)
