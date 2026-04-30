"""
app/pages/4_💼_Placement_Strategy.py
Placement Advisor, Target Companies, and Negotiation Strategy.
"""
import streamlit as st
from utils import apply_custom_css

st.set_page_config(page_title="ENT | Placement Strategy", page_icon="💼", layout="wide")
apply_custom_css()

if "result" not in st.session_state:
    st.warning("⚠️ No data found. Run the prediction on the **Home** page first.")
    st.stop()

result = st.session_state.result
advisor_out = result["actions"].get("placement_advisor", {})

st.markdown("""
<div style="padding: 10px 0 24px 0;">
    <h1 style="margin:0; font-size:2.5rem; font-weight:700; color:#e2e8f0;">
        💼 Placement & Outreach Strategy
    </h1>
    <p style="color:#94a3b8; font-size: 1.1rem; margin-top:10px;">
        Tier-based company targeting, application cadence, and salary negotiation tactics.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Advisor Strategy Card ─────────────────────────────────────────────────────
st.markdown(f"""
<div class="agent-card" style="border-left: 5px solid #06b6d4;">
    <h2 style="color:#06b6d4; margin-top:0;">🏢 Placement Advisor Agent</h2>
    <div style="display:flex; gap:40px; margin-top:20px;">
        <div style="flex:1;">
            <p style="color:#94a3b8; margin-bottom:4px;">RECOMMENDED TARGET TIER</p>
            <div style="font-size:2rem; font-weight:700; color:#e2e8f0;">{advisor_out.get('target_tier', '?')}</div>
        </div>
        <div style="flex:1;">
            <p style="color:#94a3b8; margin-bottom:4px;">APPLICATION CADENCE</p>
            <div style="font-size:2rem; font-weight:700; color:#3b82f6;">{advisor_out.get('applications_per_week', 0)} / Week</div>
        </div>
        <div style="flex:1;">
            <p style="color:#94a3b8; margin-bottom:4px;">EXPECTED SALARY (LPA)</p>
            <div style="font-size:2rem; font-weight:700; color:#22c55e;">₹{result['salary']:.1f}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Detailed Strategy ─────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">🎯 Target Company Intelligence</div>', unsafe_allow_html=True)
    st.markdown(f"**Recommended {advisor_out.get('target_tier', 'Tier')} Companies:**")
    for co in advisor_out.get("target_companies", []):
        st.markdown(f"• {co}")
    
    st.markdown("<br>**Preferred Application Channels:**", unsafe_allow_html=True)
    for plat in advisor_out.get("platforms", []):
        st.markdown(f"🔗 {plat}")

with col2:
    st.markdown('<div class="section-header">🚀 Execution Strategy</div>', unsafe_allow_html=True)
    for strategy in advisor_out.get("application_strategy", []):
        st.markdown(f"⚡ {strategy}")
    
    st.markdown('<div class="section-header">💰 Salary Negotiation Tactics</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#111827; border:1px solid #374151; border-radius:12px; padding:20px; color:#e2e8f0; font-size:1rem;">
        💡 {advisor_out.get('salary_negotiation', 'Focus on establishing core competence before negotiating.')}
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.success(f"Estimated time to secure an offer: **{result['time_to_job']:.1f} Months**")
