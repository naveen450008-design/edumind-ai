# 🏆 Advanced EduMind AI – Hackathon Submission Document

**Team Name**: Unique  
**Project Title**: EduMind AI – Advanced Education Management & Academic Intelligence Platform  
**Team Leader**: J. Pravin  
**Team Members**: J. Pravin, Ashith T., Naveenprasath V., Varshini R.R.  

---

## 🎯 Executive Summary

Traditional Student Information Systems (SIS) act as static repositories for grades and attendance without offering early intervention capabilities. **EduMind AI** transforms static educational records into **explainable, real-time academic intelligence**.

Using a hybrid architecture of **Machine Learning (Scikit-Learn RandomForestClassifier)** and a **Composite Multi-Factor Evaluation Engine**, Advanced EduMind AI calculates real-time academic risk scores (0–100), Academic Health Scores (0–100), provides explainable **Root Cause Analysis**, generates interactive **AI Study Plans**, runs real-time **What-If Grade & Target Goal Simulations**, powers a **Parent Portal**, dispatches **Teacher Remedial Interventions**, tracks **Student Progress Timelines**, and connects users to an **EduMind AI Copilot**.

---

## 💡 Key Upgraded Features & Solved Pain Points

1. **Explainable AI Early Warning & Risk Tiers (0–100 Score)**:
   - Evaluates students across 4 risk tiers: **LOW (0–30) 🟢**, **MEDIUM (31–55) 🟡**, **HIGH (56–75) 🔴**, and **CRITICAL (76–100) 🚨**.
   - Calculates a positive **Academic Health Score (0–100)** (`Health = 100 - Risk`).
   - Explains *"Why is this student at risk?"* with Primary Cause, Secondary Factors, Quantitative Empirical Evidence, and AI Action Items.

2. **AI Personalized Study Plan (`/student/study-plan`)**:
   - Generates daily study schedules (Monday–Friday) tailored to each student's weak subjects with duration, practice problem sets, and interactive task checkboxes.

3. **Interactive "What-If" Grade & Target Goal Predictor (`/student/grade-predictor`)**:
   - Real-time simulation of attendance %, assignments %, internal marks %, and final exam target goals with delta calculation (*"You need approximately +8.5 marks in Final Exam to reach your target"*).
   - Visual `CURRENT vs PREDICTED vs TARGET` comparison bar chart.

4. **Parent Command Center (`/parent/dashboard`)**:
   - Dedicated parent portal (`parent@edumind.ai` / `parent123`) showing child academic health, risk level, teacher alerts, intervention status, and recommended parent actions.

5. **Teacher Risk Command Center & Intervention Workflow (`/teacher/dashboard`)**:
   - Real-time searching and filtering by risk level and student name.
   - One-click **Assign Intervention** modal dialog that dispatches remedial instructions to students & parents with persistent tracking.

6. **Student Progress Timeline (`/student/timeline`)**:
   - Visual trajectory tracing events from Initial Risk Detection → Alert Dispatched → Teacher Intervention Assigned → Task Completed → Risk Reduced.

7. **EduMind AI Copilot**:
   - Upgraded context-aware AI chatbot assistant for students and teachers with one-click suggested question chips.

8. **Official Printable PDF Diagnostic Reports**:
   - Print-ready scorecards with `@media print` styling containing student diagnostic analysis, subject matrices, and AI action plans.

---

## 🛠️ Technical Architecture

```
                                  ┌─────────────────────────────┐
                                  │      EduMind AI Frontend    │
                                  │ (HTML5, Glassmorphism CSS,  │
                                  │  Dark/Light Theme Switcher, │
                                  │   JS ES6+, Chart.js, B5)    │
                                  └──────────────┬──────────────┘
                                                 │ REST / Jinja2
                                  ┌──────────────▼──────────────┐
                                  │       Flask Web Engine      │
                                  │          (app.py)           │
                                  └──────────────┬──────────────┘
                                                 │
          ┌──────────────────────────────────────┼──────────────────────────────────────┐
          │                                      │                                      │
┌─────────▼──────────┐                 ┌─────────▼──────────┐                 ┌─────────▼──────────┐
│  AI Metric Engine  │                 │  ML Risk Evaluator │                 │ SQLite Database    │
│ (performance_      │                 │ (risk_prediction.py│                 │   (database.db)    │
│   analysis.py +    │                 │   + RandomForest)  │                 │                    │
│   predictor.py)    │                 │                    │                 │                    │
└────────────────────┘                 └────────────────────┘                 └────────────────────┘
```

---

## 🔑 Hackathon Demo Presets

Try these 1-Click login presets on **`http://127.0.0.1:5000/login`**:

- **Student Persona (High Risk)**: `arun@edumind.ai` / `student123`  
  *Metrics*: Risk Score: 72/100 (🔴 High Risk), Health: 28/100, Weak Math & DB.
- **Parent Persona**: `parent@edumind.ai` / `parent123`  
  *Role*: Parent of Arun Kumar | Monitoring Console & Teacher Alerts.
- **Student Persona (Low Risk Top Performer)**: `rahul@edumind.ai` / `student123`  
  *Metrics*: Risk Score: 12/100 (🟢 Low Risk), Health: 88/100.
- **Teacher Persona**: `smith@edumind.ai` / `teacher123`  
  *Faculty*: Computer Science Instructor, AI Risk Command Center & Intervention Modal.
- **Admin Console**: `admin@edumind.ai` / `admin123`  
  *Role*: System Administrator & College Chart.js Analytics.

---

## 🧪 E2E Verification & Test Suite

Run full automated test scripts:

```bash
python scratch/test_full_demo.py
python scratch/test_new_features.py
python scratch/test_upgraded_features.py
```

*Results*: **100% PASS** across all student, parent, teacher, admin portals, predictor, report generator, intervention APIs, and AI chatbot REST endpoints.

---

**Built with ❤️ by Team Unique for the Hackathon.**
