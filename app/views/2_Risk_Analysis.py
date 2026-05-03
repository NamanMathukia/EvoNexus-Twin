"""
app/views/2_Risk_Analysis.py
In-depth risk drivers, interactions, and trajectory analysis driven by Live Resume Input.
Supports both Text Input and File Upload (PDF/DOCX).
Features Local History Caching.
"""
import os
import json
import uuid
from datetime import datetime
import streamlit as st
import plotly.graph_objects as go
import requests
from utils import apply_custom_css, gauge_chart
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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
            return [h for h in all_history if h.get("user_email", "unknown") == user_email]
    except:
        return []

def save_to_history(source_name, result_data, sample_data, input_text=None, file_path=None, file_name=None):
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
        "user_email": user_email,
        "input_text": input_text,
        "file_path": file_path,
        "file_name": file_name
    }

    all_history.insert(0, new_record)

    user_history  = [h for h in all_history if h.get("user_email", "unknown") == user_email][:10]
    other_history = [h for h in all_history if h.get("user_email", "unknown") != user_email]

    with open(HISTORY_FILE, "w") as f:
        json.dump(user_history + other_history, f)


# --- PDF Generation ---
def create_pdf_report(result_data, filename="ENT_Report.pdf"):
    """Generates a PDF report from the API analysis data."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("EvoNexus-Twin: Placement Risk Analysis", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Executive Summary", styles['Heading2']))
    story.append(Paragraph(f"<b>Predicted Salary:</b> Rs.{result_data.get('salary', 'N/A')} LPA", styles['Normal']))
    story.append(Paragraph(f"<b>Time to Placement:</b> {result_data.get('time_to_job', 'N/A')} Months", styles['Normal']))
    story.append(Paragraph(f"<b>Risk Level:</b> {result_data.get('risk', 'N/A')}", styles['Normal']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(result_data.get("summary", ""), styles['Normal']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Agentic Intervention Roadmap", styles['Heading2']))
    roadmap = result_data.get("actions", {}).get("improvement_roadmap", [])
    for step in roadmap:
        story.append(Paragraph(f"<b>{step.get('phase', '')}: {step.get('focus', '')}</b>", styles['Heading3']))
        story.append(Paragraph(step.get('actions', ''), styles['Normal']))
        story.append(Spacer(1, 6))

    doc.build(story)
    buffer.seek(0)
    return buffer


# ── HISTORY PANEL (rendered in-page since sidebar is hidden) ──────────────────
history_data = load_history()
if history_data:
    with st.expander("Recent Analyses", expanded=False):
        for item in history_data:
            col_a, col_b = st.columns([4, 1])
            with col_a:
                st.markdown(f"""
                <div style="padding:8px 0; border-bottom:1px solid rgba(51,65,85,0.4);">
                    <div style="font-size:0.85rem; font-weight:600; color:#e2e8f0;">
                        {item['source'][:30]}{'...' if len(item['source'])>30 else ''}
                    </div>
                    <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">
                        {item['timestamp']} &nbsp;|&nbsp; {item['tier']} &nbsp;|&nbsp;
                        <span style="color:{'#ef4444' if item['risk']=='High' else '#f59e0b' if item['risk']=='Medium' else '#22c55e'}">
                            {item['risk']} Risk
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                if st.button("Load", key=f"hist_{item['id']}"):
                    st.session_state.result = item["result"]
                    st.session_state.sample = item["sample"]
                    st.session_state.history_source_type = "text" if item.get("input_text") else "file" if item.get("file_path") else None
                    st.session_state.history_input_text = item.get("input_text")
                    st.session_state.history_file_path  = item.get("file_path")
                    st.session_state.history_file_name  = item.get("file_name")
                    st.rerun()

# ── MAIN HEADER ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 10px 0 28px 0;">
    <div style="font-size:0.72rem; letter-spacing:0.18em; text-transform:uppercase;
                color:#475569; margin-bottom:10px;">Intelligence Layer</div>
    <h1 style="margin:0; font-size:2.4rem; font-weight:800;
               font-family:'Space Grotesk',sans-serif; color:#e2e8f0;
               letter-spacing:-0.02em;">
        Risk & Performance Drivers
    </h1>
    <p style="color:#64748b; font-size:1rem; margin-top:10px; max-width:620px;">
        Provide a candidate's resume via text or file to generate a real-time risk assessment and intervention roadmap.
    </p>
</div>
""", unsafe_allow_html=True)


# ── 1. Input Section ───────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["Paste Text", "Upload File"])

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
                        st.session_state.history_source_type = "text"
                        st.session_state.history_input_text  = resume_input
                        st.session_state.history_file_path   = None
                        st.session_state.history_file_name   = None
                        st.success("Analysis complete.")
                        save_to_history("Pasted Text", st.session_state.result, st.session_state.sample, input_text=resume_input)
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

                        os.makedirs("history_files", exist_ok=True)
                        unique_id = uuid.uuid4().hex
                        save_path = os.path.join("history_files", f"{unique_id}_{uploaded_file.name}")
                        with open(save_path, "wb") as f:
                            f.write(uploaded_file.getvalue())

                        st.session_state.history_source_type = "file"
                        st.session_state.history_input_text  = None
                        st.session_state.history_file_path   = save_path
                        st.session_state.history_file_name   = uploaded_file.name

                        st.success(f"Successfully analyzed {uploaded_file.name}")
                        save_to_history(uploaded_file.name, st.session_state.result, st.session_state.sample, file_path=save_path, file_name=uploaded_file.name)
                    else:
                        st.error(f"API Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"Could not connect to the engine: {e}")
        else:
            st.warning("Please upload a file first.")


# ── 2. Results ─────────────────────────────────────────────────────────────────
if "result" in st.session_state and "sample" in st.session_state:
    result  = st.session_state.result
    sample  = st.session_state.sample
    drivers = result.get("drivers", [])

    st.markdown("---")

    # --- Input Source Viewer ---
    source_type = st.session_state.get("history_source_type")
    if source_type:
        with st.expander("View Input Source"):
            if source_type == "text":
                st.text_area("Original Input Text", value=st.session_state.get("history_input_text", ""), height=200, disabled=True)
            elif source_type == "file":
                file_path = st.session_state.get("history_file_path")
                file_name = st.session_state.get("history_file_name", "Resume")
                if file_path and os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        file_bytes = f.read()
                    st.download_button(
                        label=f"Download Original File ({file_name})",
                        data=file_bytes,
                        file_name=file_name,
                        mime="application/octet-stream",
                        key=f"dl_{file_path}"
                    )
                    if file_name.lower().endswith(".pdf"):
                        import base64
                        base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
                        pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf" id="pdf_{uuid.uuid4().hex}">'
                        st.markdown(pdf_display, unsafe_allow_html=True)
                else:
                    st.warning("Original file could not be found.")

    st.markdown("---")

    # Benchmarks
    salary     = result.get('salary', 0)
    time_to_job = result.get('time_to_job', 0)
    tier       = result.get("actions", {}).get("placement_advisor", {}).get("target_tier", "Tier-3")

    baseline_salary = 12.0 if tier == "Tier-1" else 9.0 if tier == "Tier-2" else 6.0
    baseline_time   = 2.0  if tier == "Tier-1" else 4.0 if tier == "Tier-2" else 6.0

    salary_delta = f"{salary - baseline_salary:+.1f} LPA vs Avg" if salary else None
    time_delta   = f"{time_to_job - baseline_time:+.1f} Mo vs Avg" if time_to_job else None

    rcol1, rcol2, rcol3 = st.columns(3)
    rcol1.metric("Predicted Salary",    f"Rs.{salary} LPA", salary_delta)
    rcol2.metric("Time to Placement",   f"{time_to_job} Months", time_delta, delta_color="inverse")
    rcol3.metric("Target Tier",         tier)

    st.subheader(f"Risk Level: {result.get('risk', 'N/A')}")
    st.info(result.get("summary", "Summary not available."))

    st.markdown("---")

    # Gauges
    c1, c2, c3 = st.columns(3)
    with c1:
        readiness = result.get("actions", {}).get("interview_mentor", {}).get("readiness_score", 50)
        st.plotly_chart(gauge_chart(readiness, "Interview Readiness", "#3b82f6"), use_container_width=True)
    with c2:
        st.plotly_chart(gauge_chart(result.get("lstm_prob", 0) * 100, "LSTM Placement %", "#a78bfa"), use_container_width=True)
    with c3:
        st.plotly_chart(gauge_chart(result.get("set_net_prob", 0) * 100, "SetNet Placement %", "#06b6d4"), use_container_width=True)

    # SHAP Waterfall
    if drivers:
        st.markdown('<div class="section-header">SHAP Risk Drivers — Waterfall</div>', unsafe_allow_html=True)
        features = [d[0].replace("_", " ") for d in drivers][::-1]
        values   = [d[1] for d in drivers][::-1]

        fig = go.Figure(go.Waterfall(
            name="SHAP", orientation="h",
            measure=["relative"] * len(features),
            y=features, x=values,
            textposition="outside",
            text=[f"{v:+.3f}" for v in values],
            decreasing={"marker": {"color": "#22c55e"}},
            increasing={"marker": {"color": "#ef4444"}},
            totals={"marker": {"color": "#3b82f6"}}
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,0.6)",
            font_color="#e2e8f0",
            xaxis={"title": "SHAP Impact (Risk Contribution)", "gridcolor": "#1e293b"},
            yaxis={"gridcolor": "#1e293b"},
            height=450,
            margin=dict(l=20, r=80, t=20, b=20),
            transition={"duration": 400},
        )
        st.plotly_chart(fig, use_container_width=True)

    # Interactions & What-If
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="section-header">Feature Interactions</div>', unsafe_allow_html=True)
        interactions = result.get("interactions", [])
        if interactions:
            for pair, val in interactions:
                direction_label = "High Risk Synergy" if val > 0 else "Protective Interaction"
                direction_color = "#ef4444" if val > 0 else "#22c55e"
                st.markdown(f"""
                <div style="background:rgba(30,41,59,0.7); border:1px solid rgba(51,65,85,0.5);
                            border-radius:8px; padding:12px 16px; margin-bottom:10px;
                            display:flex; justify-content:space-between; align-items:center;
                            transition: border-color 0.2s ease;">
                    <span style="color:#94a3b8; font-weight:500; font-size:0.9rem;">{pair}</span>
                    <span style="color:{direction_color}; font-weight:600; font-size:0.82rem;
                                 text-transform:uppercase; letter-spacing:0.05em;">
                        {direction_label}
                    </span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("No interactions detected.")

    with col2:
        st.markdown('<div class="section-header">What-If Simulator</div>', unsafe_allow_html=True)
        st.markdown("<p style='color:#64748b; font-size:0.88rem;'>Test how improving your profile affects your predicted salary.</p>", unsafe_allow_html=True)

        with st.form("what_if_form"):
            sim_cgpa   = st.slider("Target CGPA",          4.0, 10.0, float(sample.get("cgpa", 7.0)), 0.1)
            sim_interns = st.number_input("Add Internships", 0, 5, int(sample.get("internship_count", 0)))
            sim_skills  = st.slider("Improve Skills Score", 0.0, 1.0, float(sample.get("skills", 0.4)), 0.05)
            sim_btn = st.form_submit_button("Simulate Future", use_container_width=True)

        if sim_btn:
            sim_sample = sample.copy()
            sim_sample["cgpa"] = sim_cgpa
            sim_sample["internship_count"] = sim_interns
            sim_sample["internship"] = 1 if sim_interns > 0 else 0
            sim_sample["skills"] = sim_skills

            with st.spinner("Simulating..."):
                from src.predict import predict_full
                try:
                    sim_result = predict_full(sim_sample)
                    new_salary = sim_result.get('salary', 0)
                    new_risk   = sim_result.get('risk', 'Unknown')
                    st.success(f"**Projected Salary:** Rs.{new_salary} LPA ({(new_salary - salary):+.1f} LPA)")
                    st.info(f"**New Risk Level:** {new_risk}")
                except Exception as e:
                    st.error("Simulation failed.")

    # Roadmap & Download
    st.markdown('<div class="section-header">Agentic Intervention Roadmap</div>', unsafe_allow_html=True)
    roadmap = result.get("actions", {}).get("improvement_roadmap", [])
    if roadmap:
        for step in roadmap:
            with st.expander(f"{step.get('phase', 'Phase')}: {step.get('focus', 'Focus')}"):
                st.write(step.get('actions', ''))

        st.markdown("---")
        pdf_buffer = create_pdf_report(result)
        st.download_button(
            label="Download Full PDF Report",
            data=pdf_buffer,
            file_name="ENT_Placement_Report.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
    else:
        st.write("No specific roadmap generated.")