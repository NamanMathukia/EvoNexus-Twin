"""
app/views/4_Placement_Strategy.py
Placement Advisor, Target Companies, and Negotiation Strategy.
"""
import streamlit as st
from utils import apply_custom_css

apply_custom_css()

if "result" not in st.session_state:
    st.warning("No data found. Run the prediction on the Profile page first.")
    st.stop()

result      = st.session_state.result
advisor_out = result["actions"].get("placement_advisor", {})

st.markdown("""
<div style="padding: 10px 0 28px 0;">
    <div style="font-size:0.72rem; letter-spacing:0.18em; text-transform:uppercase;
                color:#475569; margin-bottom:10px;">Placement Intelligence</div>
    <h1 style="margin:0; font-size:2.4rem; font-weight:800;
               font-family:'Space Grotesk',sans-serif; color:#e2e8f0;
               letter-spacing:-0.02em;">
        Placement & Outreach Strategy
    </h1>
    <p style="color:#64748b; font-size:1rem; margin-top:10px;">
        Tier-based company targeting, application cadence, and salary negotiation tactics.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Advisor Strategy Card ─────────────────────────────────────────────────────
st.markdown(f"""
<div class="agent-card" style="border-left: 3px solid #06b6d4;">
    <div style="font-size:0.7rem; letter-spacing:0.14em; text-transform:uppercase;
                color:#06b6d4; margin-bottom:10px;">Agent</div>
    <h2 style="color:#22d3ee; margin-top:0; font-family:'Space Grotesk',sans-serif;
               font-size:1.2rem;">Placement Advisor</h2>
    <div style="display:flex; gap:40px; margin-top:20px; flex-wrap:wrap;">
        <div style="flex:1; min-width:120px;">
            <p style="color:#475569; margin-bottom:4px; font-size:0.72rem;
                      letter-spacing:0.1em; text-transform:uppercase;">Recommended Tier</p>
            <div style="font-size:2rem; font-weight:800; color:#e2e8f0;
                        font-family:'Space Grotesk',sans-serif;">
                {advisor_out.get('target_tier', '?')}
            </div>
        </div>
        <div style="flex:1; min-width:120px;">
            <p style="color:#475569; margin-bottom:4px; font-size:0.72rem;
                      letter-spacing:0.1em; text-transform:uppercase;">Application Cadence</p>
            <div style="font-size:2rem; font-weight:800; color:#3b82f6;
                        font-family:'Space Grotesk',sans-serif;">
                {advisor_out.get('applications_per_week', 0)} / Week
            </div>
        </div>
        <div style="flex:1; min-width:120px;">
            <p style="color:#475569; margin-bottom:4px; font-size:0.72rem;
                      letter-spacing:0.1em; text-transform:uppercase;">Expected Salary (LPA)</p>
            <div style="font-size:2rem; font-weight:800; color:#22c55e;
                        font-family:'Space Grotesk',sans-serif;">
                Rs.{result['salary']:.1f}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Detailed Strategy ─────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">Target Company Intelligence</div>', unsafe_allow_html=True)
    st.markdown(f"**Recommended {advisor_out.get('target_tier', 'Tier')} Companies:**")
    for co in advisor_out.get("target_companies", []):
        st.markdown(f"- {co}")

    st.markdown("<br>**Preferred Application Channels:**", unsafe_allow_html=True)
    for plat in advisor_out.get("platforms", []):
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px; padding:6px 0;
                    border-bottom:1px solid rgba(51,65,85,0.3);">
            <div style="width:6px; height:6px; border-radius:50%; background:#06b6d4;
                        box-shadow:0 0 6px #06b6d4; flex-shrink:0;"></div>
            <span style="color:#94a3b8; font-size:0.9rem;">{plat}</span>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-header">Execution Strategy</div>', unsafe_allow_html=True)
    for strategy in advisor_out.get("application_strategy", []):
        st.markdown(f"""
        <div style="display:flex; gap:10px; padding:8px 0;
                    border-bottom:1px solid rgba(51,65,85,0.3);">
            <div style="color:#3b82f6; font-weight:700; flex-shrink:0; margin-top:1px;">&rsaquo;</div>
            <span style="color:#94a3b8; font-size:0.9rem; line-height:1.5;">{strategy}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Salary Negotiation Tactics</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:rgba(15,23,42,0.7); border:1px solid rgba(59,130,246,0.2);
                border-radius:12px; padding:20px; color:#cbd5e1;
                font-size:0.95rem; line-height:1.7; backdrop-filter:blur(8px);">
        {advisor_out.get('salary_negotiation', 'Focus on establishing core competence before negotiating.')}
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.success(f"Estimated time to secure an offer: **{result['time_to_job']:.1f} Months**")
