# 🏆 EduMind AI – Advanced Academic Intelligence Platform

**Team Name**: Team Unique  
**Project**: EduMind AI – Advanced AI-Powered Education Management & Academic Intelligence Platform  
**Team Leader**: J. Pravin  
**Team Members**: J. Pravin, Ashith T., Naveenprasath V., Varshini R.R.  

---

## 📌 Project Overview

Traditional Student Information Systems (SIS) function as static repositories for marks and attendance without providing proactive intervention or early warning capabilities. **EduMind AI** transforms educational records into **explainable, real-time academic intelligence**.

Using a hybrid architecture of Machine Learning (**Scikit-Learn RandomForestClassifier**) and a Composite Multi-Factor Evaluation Engine, **EduMind AI** calculates real-time Academic Risk Scores (0–100) and Academic Health Scores (0–100), provides explainable **Root Cause Analysis**, generates interactive **AI Study Plans**, runs real-time **What-If Grade & Target Goal Simulations**, powers a **Parent Command Center**, dispatches **Teacher Remedial Interventions**, tracks **Student Progress Timelines**, and provides an **EduMind AI Copilot** assistant.

---

## ✨ Key Features

1. **Explainable AI Early Warning Engine**:
   - Calculates a 0–100 **Academic Risk Score** and positive **Academic Health Score** (`Health = 100 - Risk`).
   - Categorizes risk across 4 distinct tiers:
     - **`0–30`**: **LOW RISK 🟢**
     - **`31–55`**: **MEDIUM RISK 🟡**
     - **`56–75`**: **HIGH RISK 🔴**
     - **`76–100`**: **CRITICAL RISK 🚨**
   - Explains *"Why is this student at risk?"* with Primary Cause, Secondary Factors, Empirical Evidence, and AI Action Items.

2. **What-If Grade & Target Goal Predictor**:
   - Interactive slider simulation of attendance %, assignments %, internal marks %, and final exam target goals.
   - Calculates required final exam delta (*"You need approx +8.5 marks in Final Exam to reach target"*).
   - Visual `CURRENT vs PREDICTED vs TARGET` comparison bar chart.

3. **Personalized AI Study Plan**:
   - Custom weekly study schedule prioritizing weak subjects with target study duration, practice task lists, and interactive completion checkboxes.

4. **Parent Command Center**:
   - Dedicated parent portal (`/parent/dashboard`) displaying child Academic Health Score, Risk Level, Root Cause Analysis, Teacher Alerts, and Remedial Intervention status.

5. **Teacher AI Risk Command Center & Intervention Workflow**:
   - Real-time searching and filtering by risk level and student name/roll number.
   - One-click **Assign Intervention Modal** dialog that dispatches remedial instructions to students and parents with persistent tracking (`Assigned` → `In Progress` → `Completed` → `Resolved`).

6. **Student Progress Timeline**:
   - Visual trajectory tracing events from Initial Risk Detection → Alert Dispatched → Teacher Intervention Assigned → Task Completed → Risk Reduced.

7. **EduMind AI Copilot**:
   - Context-aware chatbot assistant for students and teachers with one-click suggested question chips.

8. **Printable PDF Diagnostic Reports**:
   - Official scorecards with `@media print` styling containing student diagnostic analysis, subject matrices, and AI action plans.

9. **Dark / Light Mode Theme Switching**:
   - Seamless, persistent UI theme switcher stored in `localStorage`.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.x, Flask 3.0
- **Machine Learning & Analytics**: Scikit-Learn (RandomForestClassifier), NumPy, Pandas
- **Database**: SQLite 3
- **Frontend**: HTML5, CSS3 (Custom Glassmorphism Design System), JavaScript (ES6+), Bootstrap 5, Chart.js

---

## 📁 Project Structure

```
buildthon/
│
├── ai/                         # AI & Machine Learning Engines
│   ├── assistant.py            # EduMind AI Copilot Chatbot Engine
│   ├── performance_analysis.py # Multi-factor Academic Metric Calculator
│   ├── predictor.py            # What-If Grade Simulation Engine
│   ├── recommendations.py     # AI Action Plan Generator
│   └── risk_prediction.py      # ML RandomForest & 0-100 Risk Engine
│
├── database/                   # Database Infrastructure
│   ├── db.py                   # SQLite Helper Functions & Schema Definitions
│   └── seed.py                 # Demo Data Seeder Script
│
├── static/                     # Static Frontend Assets
│   ├── css/style.css           # Glassmorphism & Theme Switching Styles
│   └── js/main.js              # Theme Persistence & Copilot Handlers
│
├── templates/                  # Jinja2 HTML Templates
│   ├── base.html               # Master HTML Base
│   ├── dashboard_base.html     # Dashboard Base with Role Sidebar
│   ├── index.html              # Landing Page
│   ├── login.html              # Login Page with 1-Click Presets
│   ├── parent_dashboard.html   # Parent Command Center
│   ├── student_dashboard.html  # Upgraded Student Portal
│   ├── student_predictor.html  # What-If Grade & Target Predictor
│   ├── student_report.html     # Printable Diagnostic Report
│   ├── student_study_plan.html # AI Personalized Study Plan
│   ├── student_timeline.html   # Student Progress Timeline
│   ├── teacher_dashboard.html  # Teacher AI Risk Command Center
│   ├── teacher_student_detail.html # Detailed AI Student Diagnosis
│   └── ...                     # Additional Sub-pages
│
├── scratch/                    # Automated Verification Test Scripts
│   ├── test_full_demo.py       # E2E Workflow Test
│   ├── test_new_features.py   # Predictor & Report Test
│   └── test_upgraded_features.py # Parent, Study Plan, & Timeline Test
│
├── app.py                      # Flask Application Controller & Routes
├── database.db                 # Seeded SQLite Database (Demo Ready)
├── .env.example                # Safe Environment Variables Template
├── .gitignore                  # Git Exclusion Rules
├── requirements.txt            # Python Dependencies
├── README.md                   # Repository Documentation
└── HACKATHON_SUBMISSION.md     # Hackathon Submission Sheet
```

---

## ⚡ Installation & Setup Instructions

### 1. Clone the Repository
```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd buildthon
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Seed Database (Optional - Pre-seeded database.db included)
```bash
python database/seed.py
```

### 5. Launch Application
```bash
python app.py
```
Open **`http://127.0.0.1:5000`** in your web browser.

---

## 🔑 1-Click Demo Login Presets

- **Student (High Risk)**: `arun@edumind.ai` / `student123`  
  *Metrics*: Risk Score: 72/100 (🔴 High Risk), Health: 28/100, Weak Math & DB.
- **Parent Portal**: `parent@edumind.ai` / `parent123`  
  *Role*: Parent of Arun Kumar | Monitoring Console & Teacher Alerts.
- **Student (Low Risk)**: `rahul@edumind.ai` / `student123`  
  *Metrics*: Risk Score: 12/100 (🟢 Low Risk), Health: 88/100.
- **Teacher**: `smith@edumind.ai` / `teacher123`  
  *Faculty*: Computer Science Instructor, AI Risk Command Center.
- **Admin**: `admin@edumind.ai` / `admin123`  
  *Role*: System Administrator & Analytics.

---

## 🧪 Automated E2E Testing

Verify full system functionality by running the automated test suite:

```bash
python scratch/test_full_demo.py
python scratch/test_new_features.py
python scratch/test_upgraded_features.py
```

**All tests pass 100% with zero errors.**

---

## 👥 Team Unique

- **J. Pravin** (Team Leader)
- **Ashith T.**
- **Naveenprasath V.**
- **Varshini R.R.**

*Developed for the Hackathon.*
