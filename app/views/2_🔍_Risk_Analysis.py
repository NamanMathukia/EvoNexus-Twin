"""
app/views/2_🔍_Risk_Analysis.py
In-depth risk drivers, interactions, and trajectory analysis driven by Live Resume Input.
Supports both Text Input and File Upload (PDF/DOCX).
Features Local History Caching.
"""
import os
import json
from datetime import datetime
import streamlit as st
import plotly.graph_objects as go
import requests
from utils import apply_custom_css, gauge_chart
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="ENT | Risk Analysis", page_icon="🔍", layout="wide")
apply_custom_css()

# --- HISTORY SYSTEM ---
HISTORY_FILE = "history.json"

def get_current_user_email():
    if "user_info" in st.session_state and st.session_state["user_info"]:
        return st.session_state["user_info"].get("email", "unknown")
    return "unknown"

def load_history():
    """Loads the analysis history from a local JSON file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            all_history = json.load(f)
            user_email = get_current_user_email()
            # If a history record doesn't have an email, it will default to None, so only unknown/matched emails are returned
            return [h for h in all_history if h.get("user_email", "unknown") == user_email]
    except:
        return []

def save_to_history(source_name, result_data, sample_data):
    """Saves the current analysis to the history file."""
    user_email = get_current_user_email()
    if not os.path.exists(HISTORY_FILE):
        all_history = []
    else:
        try:
            with open(HISTORY_FILE, "r") as f:
                all_history = json.load(f)
        except:
            all_history = []
            
    new_record = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "timestamp": datetime.now().strftime("%b %d, %I:%M %p"),
        "source": source_name,
        "risk": result_data.get("risk", "Unknown"),
        "tier": result_data.get("actions", {}).get("placement_advisor", {}).get("target_tier", "Unknown"),
        "result": result_data,
        "sample": sample_data,
        "user_email": user_email
    }
    
    all_history.insert(0, new_record)
    
    # Keep last 10 for the current user, while preserving other users' histories
    user_history = [h for h in all_history if h.get("user_email", "unknown") == user_email][:10]
    other_history = [h for h in all_history if h.get("user_email", "unknown") != user_email]
    
    with open(HISTORY_FILE, "w") as f:
        json.dump(user_history + other_history, f)


# --- PDF Generation Function ---
def create_pdf_report(result_data, filename="ENT_Report.pdf"):
    """Generates a PDF report from the API analysis data."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("EvoNexus-Twin: Placement Risk Analysis", styles['Title']))
    story.append(Spacer(1, 12))

    # Executive Summary
    story.append(Paragraph("Executive Summary", styles['Heading2']))
    story.append(Paragraph(f"<b>Predicted Salary:</b> ₹{result_data.get('salary', 'N/A')} LPA", styles['Normal']))
    story.append(Paragraph(f"<b>Time to Placement:</b> {result_data.get('time_to_job', 'N/A')} Months", styles['Normal']))
    story.append(Paragraph(f"<b>Risk Level:</b> {result_data.get('risk', 'N/A')}", styles['Normal']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(result_data.get("summary", ""), styles['Normal']))
    story.append(Spacer(1, 12))

    # Agentic Roadmap
    story.append(Paragraph("Agentic Intervention Roadmap", styles['Heading2']))
    roadmap = result_data.get("actions", {}).get("improvement_roadmap", [])
    for step in roadmap:
        story.append(Paragraph(f"<b>{step.get('phase', '')}: {step.get('focus', '')}</b>", styles['Heading3']))
        story.append(Paragraph(step.get('actions', ''), styles['Normal']))
        story.append(Spacer(1, 6))

    doc.build(story)
    buffer.seek(0)
    return buffer


# ── SIDEBAR HISTORY PANEL ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🕒 Recent Analyses")
    history_data = load_history()
    
    if not history_data:
        st.info("No recent analyses. Upload a resume to get started!")
    else:
        for item in history_data:
            # Create a nice card-like button for each history item
            button_label = f"📄 {item['source'][:15]}... \n{item['timestamp']} | {item['tier']}"
            if st.button(button_label, key=item['id'], use_container_width=True):
                # When clicked, load this data into the main session state
                st.session_state.result = item["result"]
                st.session_state.sample = item["sample"]
                st.rerun() # Force the page to refresh and show this data


# ── MAIN HEADER ────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 10px 0 24px 0;">
    <h1 style="margin:0; font-size:2.5rem; font-weight:700; color:#e2e8f0;">
        🔍 Risk & Performance Drivers
    </h1>
    <p style="color:#94a3b8; font-size: 1.1rem; margin-top:10px;">
        Provide a candidate's resume via text or file to generate a real-time risk assessment and intervention roadmap.
    </p>
</div>
""", unsafe_allow_html=True)


# ── 1. Input Section (Tabs for Text or File) ────────────────────────────────
tab1, tab2 = st.tabs(["📄 Paste Text", "📎 Upload File"])

with tab1:
    resume_input = st.text_area("Paste Candidate Resume / Profile Text", height=150)
    if st.button("Analyze Text", type="primary", use_container_width=True):
        if not resume_input.strip():
            st.warning("Please paste a resume to analyze.")
        else:
            with st.spinner("EvoNexus-Twin is analyzing profile..."):
                try:
                    response = requests.post("http://127.0.0.1:8000/evaluate", json={"resume_text": resume_input})
                    if response.status_code == 200:
                        api_data = response.json()
                        st.session_state.result = api_data.get("analysis", {})
                        st.session_state.sample = api_data.get("extracted_data", {})
                        st.success("Analysis Complete!")
                        
                        # Save to history
                        save_to_history("Pasted Text", st.session_state.result, st.session_state.sample)
                    else:
                        st.error(f"API Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"Could not connect to the engine: {e}")

with tab2:
    uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
    if st.button("Analyze File", type="primary", use_container_width=True):
        if uploaded_file is not None:
            with st.spinner("Extracting text and analyzing profile..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post("http://127.0.0.1:8000/evaluate_file", files=files)
                    
                    if response.status_code == 200:
                        api_data = response.json()
                        st.session_state.result = api_data.get("analysis", {})
                        st.session_state.sample = api_data.get("extracted_data", {})
                        st.success(f"Successfully analyzed {uploaded_file.name}")
                        
                        # Save to history
                        save_to_history(uploaded_file.name, st.session_state.result, st.session_state.sample)
                    else:
                        st.error(f"API Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"Could not connect to the engine: {e}")
        else:
            st.warning("Please upload a file first.")


# ── 2. Display Results (Only if data exists) ────────────────────────────────
if "result" in st.session_state and "sample" in st.session_state:
    result = st.session_state.result
    sample = st.session_state.sample
    drivers = result.get("drivers", [])

    st.markdown("---")

    # Top-Level Metrics
    rcol1, rcol2, rcol3 = st.columns(3)
    rcol1.metric("Predicted Salary", f"₹{result.get('salary', 'N/A')} LPA")
    rcol2.metric("Time to Placement", f"{result.get('time_to_job', 'N/A')} Months")
    rcol3.metric("Target Tier", result.get("actions", {}).get("placement_advisor", {}).get("target_tier", "N/A"))
    
    st.subheader(f"Risk Level: {result.get('risk', 'N/A')}")
    st.info(result.get("summary", "Summary not available."))

    st.markdown("---")

    # Row 1: Gauges
    c1, c2, c3 = st.columns(3)
    with c1:
        readiness = result.get("actions", {}).get("interview_mentor", {}).get("readiness_score", 50)
        st.plotly_chart(gauge_chart(readiness, "Interview Readiness", "#3b82f6"), use_container_width=True)
    with c2:
        st.plotly_chart(gauge_chart(result.get("lstm_prob", 0) * 100, "LSTM Placement %", "#a78bfa"), use_container_width=True)
    with c3:
        st.plotly_chart(gauge_chart(result.get("set_net_prob", 0) * 100, "SetNet Placement %", "#06b6d4"), use_container_width=True)

    # Row 2: SHAP Waterfall
    if drivers:
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

    # Row 3: Interactions & Trajectory
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="section-header">🔗 Feature Interactions</div>', unsafe_allow_html=True)
        interactions = result.get("interactions", [])
        if interactions:
            for pair, val in interactions:
                direction = "🔴 High Risk Synergy" if val > 0 else "🟢 Protective Interaction"
                st.markdown(f"""
                <div style="background:#1e293b; border:1px solid #334155; border-radius:8px;
                            padding:12px 16px; margin-bottom:10px; display:flex; justify-content:space-between;">
                    <span style="color:#94a3b8; font-weight:500;">{pair}</span>
                    <span style="color:{'#ef4444' if val>0 else '#22c55e'}; font-weight:600;">{direction}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("No interactions detected.")

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

    # ── Agentic Roadmap & Download ───────────────────────────────────────────
    st.markdown('<div class="section-header">🤖 Agentic Intervention Roadmap</div>', unsafe_allow_html=True)
    roadmap = result.get("actions", {}).get("improvement_roadmap", [])
    if roadmap:
        for step in roadmap:
            with st.expander(f"📌 {step.get('phase', 'Phase')}: {step.get('focus', 'Focus')}"):
                st.write(step.get('actions', ''))
                
        # --- PDF DOWNLOAD BUTTON ---
        st.markdown("---")
        pdf_buffer = create_pdf_report(result)
        st.download_button(
            label="📄 Download Full PDF Report",
            data=pdf_buffer,
            file_name="ENT_Placement_Report.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
    else:
        st.write("No specific roadmap generated.")