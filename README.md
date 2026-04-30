# 🧬 EvoNexus-Twin (ENT)

**EvoNexus-Twin** is a production-ready, modular career intelligence engine. It combines advanced temporal modelling, graph analytics, and multi-agent orchestration to predict placement outcomes and provide actionable "Next Best Action" (NBA) career roadmaps.

---

## 🏗 System Architecture

The ENT system is built with a 14-layer modular structure:

1.  **Temporal Data Layer**: Synthetic trajectory generator producing semester-wise event triplets.
2.  **Knowledge Graph Layer**: `NetworkX`-based Temporal Knowledge Graph (TKG) modeling Student-Skill-Job relationships.
3.  **Neural Models**: 
    *   **LSTM**: Captures temporal patterns in academic and skill trajectories.
    *   **LGDESetNet**: Learns interaction effects between skill sets using masked mean pooling.
4.  **Ensemble Regression & Classification**:
    *   **XGBoost**: High-accuracy placement risk classification (~90%).
    *   **LightGBM**: Targeted salary prediction trained on placed students.
    *   **WeibullAFT**: Survival analysis for "Time to Job" projections.
5.  **Explainability (XAI)**: SHAP-based feature importance and interaction analysis.
6.  **Agentic NBA Engine**: Multi-agent orchestration (Skill Coach, Placement Advisor, Interview Mentor) synthesizing model outputs into human-readable advice.
7.  **Serving Layer**: FastAPI backend + Streamlit multipage interactive dashboard.

---

## 🚀 Getting Started

### 1. Installation
Ensure you have Python 3.9+ and run:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Training the Models
The system is designed to be trained from scratch using synthetic data:
```bash
python train.py
```
*This will generate ~6,000 synthetic profiles, build the TKG, and train all neural and ensemble models.*

### 3. Running the Dashboard
Launch the high-fidelity multipage Streamlit UI:
```bash
streamlit run app/app.py
```
*   **Home**: Configure student profiles.
*   **Overview**: View KPIs and Executive Summary.
*   **Risk Analysis**: Explore SHAP drivers and Trajectories.
*   **Roadmap**: Get personalized agent advice and timelines.

### 4. Running the API
Serve the intelligence engine via FastAPI:
```bash
uvicorn api.main:app --reload
```
Access docs at `http://localhost:8000/docs`.

---

## 🤖 Multi-Agent Logic

*   **Skill Coach**: Identifies skill gaps and recommends specific certifications based on target market demand.
*   **Placement Advisor**: Suggests company tiers, application cadence, and salary negotiation tactics.
*   **Interview Mentor**: Assesses readiness and provides a weekly DSA/Mock-interview study plan.

---

## 🛠 Project Structure
```text
EvoNexus-Twin/
├── api/             # FastAPI Backend
├── app/             # Streamlit Multipage Dashboard
├── models/          # Persisted model artifacts (.pt, .pkl)
├── src/
│   ├── agents/      # NBA Agent logic
│   ├── data/        # Synthetic generation & schemas
│   ├── graph/       # Temporal KG logic
│   ├── models/      # PyTorch & Sklearn wrappers
│   ├── explain/     # SHAP explainability
│   └── predict.py   # Unified inference pipeline
├── train.py         # Top-level training entrypoint
└── main.py          # CLI Demo entrypoint
```

---

## ✅ Performance Metrics
*   **Placement Risk**: ~90% Accuracy (XGBoost)
*   **Salary MAE**: ~1.3 LPA (LightGBM)
*   **Inference Latency**: <500ms (CPU)
