"""
app/views/3_Career_Roadmap.py
Skill Coach, Interview Mentor, and Milestone Timeline.
"""
import streamlit as st
from utils import apply_custom_css

apply_custom_css()

if "result" not in st.session_state:
    st.warning("No data found. Run the prediction on the Profile page first.")
    st.stop()

result    = st.session_state.result
actions   = result["actions"]
skill_out = actions.get("skill_coach", {})
mentor_out = actions.get("interview_mentor", {})

st.markdown("""
<div style="padding: 10px 0 28px 0;">
    <div style="font-size:0.72rem; letter-spacing:0.18em; text-transform:uppercase;
                color:#475569; margin-bottom:10px;">Growth Intelligence</div>
    <h1 style="margin:0; font-size:2.4rem; font-weight:800;
               font-family:'Space Grotesk',sans-serif; color:#e2e8f0;
               letter-spacing:-0.02em;">
        Career Roadmap
    </h1>
    <p style="color:#64748b; font-size:1rem; margin-top:10px;">
        Agent-driven skill gap analysis, interview preparation, and development timeline.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Agent Cards ───────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="agent-card">
        <div style="font-size:0.7rem; letter-spacing:0.14em; text-transform:uppercase;
                    color:#3b82f6; margin-bottom:10px;">Agent</div>
        <h3 style="color:#60a5fa; margin-top:0; font-family:'Space Grotesk',sans-serif;
                   font-size:1.1rem;">Skill Coach</h3>
        <p style="color:#94a3b8; font-size:0.93rem; line-height:1.65;">{skill_out.get('gap_analysis', '')}</p>
        <div style="margin: 14px 0;">
            <b style="color:#e2e8f0; font-size:0.82rem; letter-spacing:0.06em; text-transform:uppercase;">
                Priority Certifications
            </b>
    """, unsafe_allow_html=True)
    for cert in skill_out.get("certifications", [])[:3]:
        st.markdown(f"- **{cert['skill'].upper()}**: {cert['certification']}")
    st.markdown(f"""
            <br><b style="color:#e2e8f0; font-size:0.82rem; letter-spacing:0.06em; text-transform:uppercase;">
                Core Focus Clusters
            </b><br>
    """, unsafe_allow_html=True)
    for cluster in skill_out.get("priority_skills", []):
        st.markdown(f"- {cluster['cluster']}: {', '.join(cluster['missing_skills'])}")
    st.markdown(f"""
        </div>
        <p style='color:#64748b; font-size:0.85rem;'>
            Estimated Upskilling: <b style="color:#e2e8f0;">{skill_out.get('timeline_weeks', '?')} Weeks</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="agent-card">
        <div style="font-size:0.7rem; letter-spacing:0.14em; text-transform:uppercase;
                    color:#a78bfa; margin-bottom:10px;">Agent</div>
        <h3 style="color:#c4b5fd; margin-top:0; font-family:'Space Grotesk',sans-serif;
                   font-size:1.1rem;">Interview Mentor</h3>
        <p style="color:#94a3b8;">
            Readiness: <b style="color:#e2e8f0;">{mentor_out.get('readiness_label', '?')}</b>
            &nbsp;({mentor_out.get('readiness_score', 0)}/100)
        </p>
        <div style="margin: 14px 0;">
            <b style="color:#e2e8f0; font-size:0.82rem; letter-spacing:0.06em; text-transform:uppercase;">
                Weekly Preparation Plan
            </b>
    """, unsafe_allow_html=True)
    for step in mentor_out.get("weekly_plan", []):
        st.markdown(f"- {step}")
    st.markdown("<br><b style='color:#e2e8f0; font-size:0.82rem; letter-spacing:0.06em; text-transform:uppercase;'>Critical Readiness Gaps</b>", unsafe_allow_html=True)
    for gap in mentor_out.get("critical_gaps", []):
        st.markdown(f"""
        <div style="background:rgba(239,68,68,0.08); border-left:2px solid #ef4444;
                    padding:6px 12px; border-radius:0 6px 6px 0; margin:4px 0;
                    color:#fca5a5; font-size:0.88rem;">
            {gap}
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

# ── Milestone Timeline ────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Implementation Timeline & Milestones</div>', unsafe_allow_html=True)
roadmap = actions.get("improvement_roadmap", [])
for i, milestone in enumerate(roadmap):
    color = ["#3b82f6", "#a78bfa", "#06b6d4", "#22c55e"][i % 4]
    st.markdown(f"""
    <div class="timeline-item" style="border-left-color:{color}">
        <div class="timeline-dot" style="background:{color}"></div>
        <div style="font-weight:700; color:{color}; font-size:0.75rem; letter-spacing:0.1em;
                    text-transform:uppercase;">{milestone['phase']}</div>
        <div style="font-weight:600; color:#e2e8f0; font-size:1.05rem; margin-top:4px;
                    font-family:'Space Grotesk',sans-serif;">{milestone['focus']}</div>
        <div style="color:#94a3b8; font-size:0.93rem; margin-top:6px; line-height:1.65;">{milestone['actions']}</div>
    </div>
    """, unsafe_allow_html=True)
