"""
app/views/2_🔍_Risk_Analysis.py
Reactive Dashboard with Dynamic Timeline and Strategy Orchestration.
Supports both Text Input and File Upload (PDF/DOCX).
Features Local History Caching.
"""
import os
import json
import uuid
from datetime import datetime, date
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

# --- GLOBALS & CONFIG ---
HISTORY_FILE = "history.json"
COURSE_MAP = {"BBA": 3, "BCA": 3, "Engineering": 4, "MBA": 2, "Nursing": 4}
MONTH_MAP = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

# --- HISTORY & STATE SYSTEM ---
def get_current_user_email():
    if "user_info" in st.session_state and st.session_state["user_info"]:
        return st.session_state["user_info"].get("email", "unknown")
    return "unknown"

def load_history():
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
    user_history = [h for h in all_history if h.get("user_email", "unknown") == user_email][:10]
    other_history = [h for h in all_history if h.get("user_email", "unknown") != user_email]
    
    with open(HISTORY_FILE, "w") as f:
        json.dump(user_history + other_history, f)

# THE FIX: This function forces Streamlit's widgets to adopt the AI's parsed timeline instantly
def update_ui_timeline(sample_data, result_data=None):
    """Overwrites the UI state variables directly based on the newly analyzed resume."""
    raw_course = str(sample_data.get("course", "Engineering"))
    matched_course = next((k for k in COURSE_MAP if k.lower() in raw_course.lower()), "Engineering")
    st.session_state.timeline_course = matched_course
    course_duration = COURSE_MAP.get(matched_course, 4)
    
    target_year = None
    try:
        # Check for graduation year first (from updated LLM prompt)
        if sample_data.get("graduation_year"):
            target_year = int(str(sample_data["graduation_year"])[:4])
        elif sample_data.get("admission_year"):
            # Fallback for older caches using admission_year
            target_year = int(str(sample_data["admission_year"])[:4]) + course_duration
    except Exception:
        pass

    today = date.today()
    target_month_index = 6 # Default to June
    
    is_past = False
    if target_year is not None:
        if target_year < today.year or (target_year == today.year and target_month_index < today.month):
            is_past = True
            
    if target_year is None or is_past:
        if result_data and result_data.get("time_to_job") is not None:
            time_to_job_months = float(result_data.get("time_to_job", 0))
            if time_to_job_months > 0:
                future_months = today.month + int(time_to_job_months)
                target_year = today.year + (future_months - 1) // 12
                target_month_index = ((future_months - 1) % 12) + 1
            else:
                target_year = today.year
                target_month_index = today.month
        else:
            target_year = today.year + 1
            target_month_index = 6
        
    st.session_state.timeline_year = int(target_year)
    st.session_state.timeline_month = MONTH_MAP[target_month_index - 1]
    st.session_state.current_analysis_id = str(uuid.uuid4()) # Nuke cache


# --- PDF Generation Function ---
def create_pdf_report(result_data, filename="ENT_Report.pdf"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("EvoNexus-Twin: Placement Risk Analysis", styles['Title']))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Executive Summary", styles['Heading2']))
    story.append(Paragraph(f"<b>Predicted Salary:</b> ₹{result_data.get('salary', 'N/A')} LPA", styles['Normal']))
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


# ── SIDEBAR HISTORY PANEL ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🕒 Recent Analyses")
    history_data = load_history()
    
    if not history_data:
        st.info("No recent analyses. Upload a resume to get started!")
    else:
        for item in history_data:
            button_label = f"📄 {item['source'][:15]}... \n{item['timestamp']} | {item['tier']}"
            if st.button(button_label, key=item['id'], use_container_width=True):
                st.session_state.result = item["result"]
                st.session_state.sample = item["sample"]
                
                # Update UI immediately on history click
                update_ui_timeline(st.session_state.sample, st.session_state.result)
                
                st.session_state.history_source_type = "text" if item.get("input_text") else "file" if item.get("file_path") else "profile" if item.get("input_text") == "System Profile Data" else None
                st.session_state.history_input_text = item.get("input_text")
                st.session_state.history_file_path = item.get("file_path")
                st.session_state.history_file_name = item.get("file_name")
                st.rerun() 
                
        st.markdown("---")
        
        # Clear History Button
        if st.button("🗑️ Clear History", use_container_width=True, type="secondary"):
            user_email = get_current_user_email()
            if os.path.exists(HISTORY_FILE):
                try:
                    with open(HISTORY_FILE, "r") as f:
                        all_history = json.load(f)
                    other_history = [h for h in all_history if h.get("user_email", "unknown") != user_email]
                    with open(HISTORY_FILE, "w") as f:
                        json.dump(other_history, f)
                except Exception as e:
                    pass
            # Wipe variables completely
            for key in ["result", "sample", "current_analysis_id", "timeline_course", "timeline_year", "timeline_month"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


# ── MAIN HEADER ────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 10px 0 24px 0;">
    <h1 style="margin:0; font-size:2.5rem; font-weight:700; color:#e2e8f0;">
        🔍 Risk & Performance Drivers
    </h1>
    <p style="color:#94a3b8; font-size: 1.1rem; margin-top:10px;">
        Provide a candidate's resume via text, file, or profile to generate a real-time risk assessment and intervention roadmap.
    </p>
</div>
""", unsafe_allow_html=True)


# ── 1. Input Section (Tabs for Text, File, or Saved Profile) ───────────────
tab1, tab2, tab3 = st.tabs(["📄 Paste Text", "📎 Upload File", "👤 Analyze Saved Profile"])

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
                        
                        # Force timeline reset!
                        update_ui_timeline(st.session_state.sample, st.session_state.result)
                        
                        st.session_state.history_source_type = "text"
                        st.session_state.history_input_text = resume_input
                        st.session_state.history_file_path = None
                        st.session_state.history_file_name = None
                        
                        save_to_history("Pasted Text", st.session_state.result, st.session_state.sample, input_text=resume_input)
                        st.rerun() 
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
                        
                        # Force timeline reset!
                        update_ui_timeline(st.session_state.sample, st.session_state.result)
                        
                        os.makedirs("history_files", exist_ok=True)
                        unique_id = uuid.uuid4().hex
                        save_path = os.path.join("history_files", f"{unique_id}_{uploaded_file.name}")
                        with open(save_path, "wb") as f:
                            f.write(uploaded_file.getvalue())
                            
                        st.session_state.history_source_type = "file"
                        st.session_state.history_input_text = None
                        st.session_state.history_file_path = save_path
                        st.session_state.history_file_name = uploaded_file.name
                        
                        save_to_history(uploaded_file.name, st.session_state.result, st.session_state.sample, file_path=save_path, file_name=uploaded_file.name)
                        st.rerun() 
                    else:
                        st.error(f"API Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"Could not connect to the engine: {e}")
        else:
            st.warning("Please upload a file first.")

with tab3:
    user_email = get_current_user_email()
    if user_email == "unknown":
        st.warning("Please log in to use your saved profile.")
    else:
        USERS_FILE = os.path.join(os.path.dirname(__file__), "..", "users.json")
        saved_profile = {}
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, "r") as f:
                    saved_profile = json.load(f).get(user_email, {})
            except:
                pass
                
        if not saved_profile:
            st.info("No saved profile found. Please complete the setup on the Home page.")
        else:
            st.success("✅ Profile Loaded Successfully")
            c1, c2, c3 = st.columns(3)
            c1.metric("Current CGPA", saved_profile.get("cgpa", "N/A"))
            c2.metric("Internships", saved_profile.get("internship_count", "N/A"))
            c3.metric("Skill Depth", round(saved_profile.get("skills", 0.0), 2))
            
            if st.button("⚡ Generate Dashboard from Profile", type="primary", use_container_width=True):
                with st.spinner("Pushing profile through ENT Neural Engine..."):
                    try:
                        from src.predict import predict_full
                        result_data = predict_full(saved_profile)
                        
                        st.session_state.result = result_data
                        st.session_state.sample = saved_profile
                        
                        # Force timeline reset!
                        update_ui_timeline(st.session_state.sample, st.session_state.result)
                        
                        st.session_state.history_source_type = "profile"
                        st.session_state.history_input_text = "Generated directly from User Profile"
                        st.session_state.history_file_path = None
                        st.session_state.history_file_name = None
                        
                        save_to_history("Saved Profile", st.session_state.result, st.session_state.sample, input_text="System Profile Data")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Engine prediction failed: {e}")

# ── 2. Display Results (Only if data exists) ────────────────────────────────
if "result" in st.session_state and "sample" in st.session_state:
    result = st.session_state.result
    sample = st.session_state.sample
    drivers = result.get("drivers", [])

    st.markdown("---")
    
    # --- Display Input Source ---
    source_type = st.session_state.get("history_source_type")
    if source_type:
        with st.expander("📄 View Input Source"):
            if source_type == "text" or source_type == "profile":
                st.text_area("Original Input Text", value=st.session_state.get("history_input_text", ""), height=200, disabled=True)
            elif source_type == "file":
                file_path = st.session_state.get("history_file_path")
                file_name = st.session_state.get("history_file_name", "Resume")
                if file_path and os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        file_bytes = f.read()
                    st.download_button(
                        label=f"⬇️ Download Original File ({file_name})",
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
    
    # --- 🎓 DYNAMIC PLACEMENT CONTEXT ---
    st.markdown('<div class="section-header">🎓 Target Placement Timeline</div>', unsafe_allow_html=True)
    col_t1, col_t2, col_t3 = st.columns(3)

    # Make sure variables exist on first load
    if "timeline_course" not in st.session_state:
        st.session_state.timeline_course = "Engineering"
    if "timeline_year" not in st.session_state:
        st.session_state.timeline_year = date.today().year + 1
    if "timeline_month" not in st.session_state:
        st.session_state.timeline_month = "June"

    with col_t1:
        # Binding purely to session_state key, no "value" parameter needed!
        st.selectbox("Course Type", list(COURSE_MAP.keys()), key="timeline_course")

    with col_t2:
        st.number_input("Target Placement Year", min_value=2015, max_value=2030, key="timeline_year")

    with col_t3:
        st.selectbox("Target Month", MONTH_MAP, key="timeline_month")

    # Calculation based directly on session state
    target_date = date(st.session_state.timeline_year, MONTH_MAP.index(st.session_state.timeline_month) + 1, 1)
    today = date.today()
    months_remaining = (target_date.year - today.year) * 12 + (target_date.month - today.month)

    # TIER-1 FIX
    salary = result.get('salary', 0)
    if salary >= 12.0:
        calculated_tier = "Tier-1"
    elif salary >= 8.0:
        calculated_tier = "Tier-2"
    else:
        calculated_tier = "Tier-3"

    if "actions" not in st.session_state.result:
        st.session_state.result["actions"] = {}
    if "placement_advisor" not in st.session_state.result["actions"]:
        st.session_state.result["actions"]["placement_advisor"] = {}
    st.session_state.result["actions"]["placement_advisor"]["target_tier"] = calculated_tier

    # --- THE SYNC TRIGGER ---
    analysis_id = st.session_state.get("current_analysis_id", "default")
    state_key = f"sync_{analysis_id}_{months_remaining}_{st.session_state.timeline_course}_{calculated_tier}"
    
    if state_key not in st.session_state:
        st.session_state[state_key] = True
        
        if months_remaining > 0:
            effective_months = max(0.25, months_remaining) 
            with st.spinner(f"🔄 Aligning Agentic Roadmap to {calculated_tier}..."):
                from src.llm_parser import generate_dynamic_roadmap
                new_roadmap = generate_dynamic_roadmap(
                    effective_months, 
                    sample.get("skill_list", []), 
                    calculated_tier
                )
                st.session_state.result["actions"]["improvement_roadmap"] = new_roadmap
                st.session_state.result["time_to_job"] = round(effective_months, 2)
        else:
            st.session_state.result["actions"]["improvement_roadmap"] = []
            st.session_state.result["time_to_job"] = result.get('time_to_job', 0)

    time_to_job = st.session_state.result["time_to_job"]
    st.markdown("---")

    # Metrics Section
    baseline_salary = 12.0 if calculated_tier == "Tier-1" else 9.0 if calculated_tier == "Tier-2" else 6.0
    baseline_time = 2.0 if calculated_tier == "Tier-1" else 4.0 if calculated_tier == "Tier-2" else 6.0
    
    salary_delta = f"{salary - baseline_salary:+.1f} LPA vs Avg" if salary else None
    time_delta = f"{time_to_job - baseline_time:+.1f} Mo vs Avg" if time_to_job is not None else None

    rcol1, rcol2, rcol3 = st.columns(3)
    rcol1.metric("Predicted Salary", f"₹{salary} LPA", salary_delta)
    
    if months_remaining <= 0:
        time_display = f"{time_to_job} Months" 
    elif months_remaining <= 0.25:
        time_display = "7 Days (Immediate)"
    elif months_remaining < 1:
        weeks = int(months_remaining * 4)
        time_display = "1 Week" if weeks <= 1 else f"{weeks} Weeks"
    else:
        time_display = f"{int(months_remaining)} Months"
        
    rcol2.metric("Time to Placement", time_display, time_delta, delta_color="inverse")
    rcol3.metric("Target Tier", calculated_tier)

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
        st.markdown('<div class="section-header">🧬 SHAP Risk Drivers (Waterfall)</div>', unsafe_allow_html=True)
        features = [d[0].replace("_", " ") for d in drivers][::-1]
        values   = [d[1] for d in drivers][::-1]

        fig = go.Figure(go.Waterfall(
            name="SHAP", orientation="h",
            measure=["relative"] * len(features),
            y=features, x=values,
            textposition="outside",
            text=[f"{v:+.3f}" for v in values],
            decreasing={"marker":{"color":"#22c55e"}},
            increasing={"marker":{"color":"#ef4444"}},
            totals={"marker":{"color":"#3b82f6"}}
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,0.6)",
            font_color="#e2e8f0",
            xaxis={"title": "SHAP Impact (Risk Contribution)", "gridcolor": "#374151"},
            yaxis={"gridcolor": "#374151"},
            height=450,
            margin=dict(l=20, r=80, t=20, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Row 3: Interactions & What-If Simulator
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
        st.markdown('<div class="section-header">🔮 What-If Simulator</div>', unsafe_allow_html=True)
        st.markdown("<p style='color:#94a3b8; font-size: 0.9rem;'>Test how improving your profile affects your predicted salary.</p>", unsafe_allow_html=True)
        
        with st.form("what_if_form"):
            sim_cgpa = st.slider("Target CGPA", 4.0, 10.0, float(sample.get("cgpa", 7.0)), 0.1)
            sim_interns = st.number_input("Add Internships", 0, 5, int(sample.get("internship_count", 0)))
            sim_skills = st.slider("Improve Skills Score", 0.0, 1.0, float(sample.get("skills", 0.4)), 0.05)
            
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
                    new_risk = sim_result.get('risk', 'Unknown')
                    
                    st.success(f"**New Projected Salary:** ₹{new_salary} LPA ({(new_salary - salary):+.1f} LPA)")
                    st.info(f"**New Risk Level:** {new_risk}")
                except Exception as e:
                    st.error("Simulation failed.")

    # ── Agentic Roadmap & Download ───────────────────────────────────────────
    if months_remaining > 0:
        st.markdown('<div class="section-header">🤖 Agentic Intervention Roadmap</div>', unsafe_allow_html=True)
        roadmap = st.session_state.result["actions"].get("improvement_roadmap", [])
        if roadmap:
            for step in roadmap:
                with st.expander(f"📌 {step.get('phase', 'Phase')}: {step.get('focus', 'Focus')}"):
                    st.write(step.get('actions', ''))
    else:
        st.markdown('<div class="section-header">🎓 Alumni Status Detected</div>', unsafe_allow_html=True)
        st.info("The target graduation date has already passed. The candidate is considered an alumni, so a student preparation roadmap is not required.")

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