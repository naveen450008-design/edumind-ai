import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# Initialize ML model trained on synthetic historical academic dataset
def train_risk_model():
    # Features: [attendance_pct, assign_score, internal_score, final_score, min_subject_score, trend_delta]
    X_train = np.array([
        [95, 92, 90, 94, 88, 5],   # Low Risk (0)
        [88, 85, 82, 86, 78, 2],   # Low Risk (0)
        [80, 78, 75, 80, 70, 0],   # Low Risk (0)
        [74, 68, 64, 68, 60, -2],  # Medium Risk (1)
        [72, 65, 66, 64, 58, -4],  # Medium Risk (1)
        [78, 70, 72, 60, 52, -1],  # Medium Risk (1)
        [68, 55, 62, 51, 52, -6],  # High Risk (2)
        [55, 42, 50, 45, 40, -10], # High Risk (2)
        [62, 75, 70, 82, 65, 0],   # Medium Risk (1 - Low Att)
        [84, 45, 60, 78, 45, -5],  # High Risk (2 - Weak Math)
        [79, 72, 70, 62, 60, -26], # High Risk (2 - Steep drop)
    ])
    y_train = np.array([0, 0, 0, 1, 1, 1, 2, 2, 1, 2, 2])
    
    rf = RandomForestClassifier(n_estimators=10, random_state=42)
    rf.fit(X_train, y_train)
    return rf

# Train model globally
_MODEL = train_risk_model()

def evaluate_academic_risk(perf):
    if not perf:
        return {
            'risk_level': 'LOW RISK',
            'status_label': 'LOW RISK',
            'risk_badge': 'badge-risk-low',
            'bg_class': 'badge-risk-low',
            'risk_code': 'low',
            'status_color': '#10b981',
            'risk_score': 15,
            'health_score': 85,
            'reasons': ['No student data available.'],
            'ai_insight': 'Academic health is stable.',
            'root_cause_analysis': None
        }

    att = float(perf['att_pct'])
    assign = float(perf['assign_score'])
    internal = float(perf['internal_score'])
    final = float(perf['final_score'])
    overall = float(perf['overall_score'])
    weak_subs = perf.get('weak_subjects', [])
    trend_status = perf.get('trend_status', 'Stable')
    trend_delta = float(perf.get('trend_delta', 0.0))

    min_sub_score = min([s['score'] for s in perf.get('subject_performance', [])]) if perf.get('subject_performance') else 70.0

    # 1. ML Model Prediction
    X_test = np.array([[att, assign, internal, final, min_sub_score, trend_delta]])
    ml_pred = _MODEL.predict(X_test)[0] # 0: Low, 1: Medium, 2: High

    # 2. Compute Precise 0-100 Risk Score
    raw_risk = 0.0
    if att < 75.0:
        raw_risk += (75.0 - att) * 1.0
    if assign < 70.0:
        raw_risk += (70.0 - assign) * 0.5
    if final < 70.0:
        raw_risk += (70.0 - final) * 0.5
    if overall < 75.0:
        raw_risk += (75.0 - overall) * 0.5
    
    raw_risk += len(weak_subs) * 10.0
    if trend_delta < 0:
        raw_risk += min(15.0, abs(trend_delta) * 0.5)

    # Force minimum risk tier if ML model flags High or if overall score is low
    if ml_pred == 2 or overall < 55.0 or (att < 70.0 and final < 60.0):
        raw_risk = max(raw_risk, 60.0)
    elif ml_pred == 1 or att < 75.0 or overall < 70.0:
        raw_risk = max(raw_risk, 35.0)

    # Critical risk override for severe cases (e.g. Manoj: score < 50% or 4+ weak subjects)
    if overall < 50.0 or (att < 50.0 and final < 50.0) or len(weak_subs) >= 4:
        raw_risk = max(raw_risk, 82.0)

    risk_score = int(round(max(0.0, min(100.0, raw_risk))))
    health_score = int(round(max(0.0, min(100.0, 100 - risk_score))))

    # 3. Categorize into 4 Tiers:
    # 0-30 = LOW, 31-55 = MEDIUM, 56-75 = HIGH, 76-100 = CRITICAL
    if risk_score >= 76:
        risk_level = "CRITICAL RISK"
        risk_badge = "badge-risk-critical"
        risk_code = "critical"
        status_color = "#dc2626"
    elif risk_score >= 56:
        risk_level = "HIGH RISK"
        risk_badge = "badge-risk-high"
        risk_code = "high"
        status_color = "#ef4444"
    elif risk_score >= 31:
        risk_level = "MEDIUM RISK"
        risk_badge = "badge-risk-med"
        risk_code = "medium"
        status_color = "#f59e0b"
    else:
        risk_level = "LOW RISK"
        risk_badge = "badge-risk-low"
        risk_code = "low"
        status_color = "#10b981"

    # 4. Explainable Root Cause Analysis & Reasons Generation
    reasons = []
    secondary_causes = []
    primary_cause = "Academic parameters meet institutional expectations."

    if att < 75.0:
        msg = f"Attendance is {att}%, which is below the mandatory 75.0% cutoff."
        reasons.append(msg)
        if "Attendance" not in primary_cause:
            primary_cause = f"Attendance Deficit ({att}% vs 75.0% required)"

    if weak_subs:
        weak_names = ", ".join([f"{w['course_name']} ({w['score']}%)" for w in weak_subs])
        msg = f"Subject performance is critically low in: {weak_names}."
        reasons.append(msg)
        if primary_cause.startswith("Academic parameters"):
            primary_cause = f"Weak Subject Scores in {weak_subs[0]['course_name']} ({weak_subs[0]['score']}%)"
        else:
            secondary_causes.append(f"Low marks in {weak_names}")

    if assign < 60.0:
        msg = f"Continuous assessment score ({assign}%) is below 60.0%."
        reasons.append(msg)
        secondary_causes.append(f"Assignment average at {assign}%")

    if final < 60.0:
        msg = f"Final examination score ({final}%) is below 60.0%."
        reasons.append(msg)
        secondary_causes.append(f"Final exam marks at {final}%")

    if trend_status == "Declining":
        msg = f"Academic trajectory is declining (dropped by {abs(trend_delta)}% compared to prior exam)."
        reasons.append(msg)
        secondary_causes.append(f"Performance trend declined by {abs(trend_delta)}%")

    if not reasons:
        reasons.append("Academic performance is strong across attendance, assignments, and examinations.")
        secondary_causes.append("All metrics within top target thresholds.")

    # Recommended Actions
    recommended_actions = []
    if att < 75.0:
        recommended_actions.append("Prioritize attending all upcoming lectures to restore attendance above 75%.")
    if weak_subs:
        recommended_actions.append(f"Attend remedial tutoring sessions for {weak_subs[0]['course_name']}.")
    if assign < 60.0:
        recommended_actions.append("Complete and submit pending assignments immediately.")
    if not recommended_actions:
        recommended_actions.append("Maintain current study regimen and participate in honors mentorship.")

    root_cause_analysis = {
        'primary_cause': primary_cause,
        'secondary_causes': secondary_causes,
        'evidence': {
            'Attendance': f"{att}%",
            'Assignment Average': f"{assign}%",
            'Internal Exam Avg': f"{internal}%",
            'Final Exam Avg': f"{final}%",
            'Overall Score': f"{overall}%",
            'Trajectory Delta': f"{trend_delta:+}%"
        },
        'recommended_actions': recommended_actions
    }

    # Prominent AI Banner Insight
    if risk_code in ['high', 'critical']:
        if weak_subs:
            ai_insight = f"{weak_subs[0]['course_name']} is currently your highest priority weak subject. Your attendance ({att}%) requires immediate improvement."
        else:
            ai_insight = f"Your overall academic risk is elevated due to attendance at {att}%. Immediate faculty intervention is advised."
    elif risk_code == 'medium':
        ai_insight = f"Your performance is moderate (Overall Score: {overall}%). Raising attendance from {att}% to 80% will reduce your risk level to LOW."
    else:
        ai_insight = f"Great work! Your Academic Health Score is {health_score}/100. You are maintaining strong performance across all subjects."

    return {
        'risk_level': risk_level,
        'status_label': risk_level,
        'risk_badge': risk_badge,
        'bg_class': risk_badge,
        'risk_code': risk_code,
        'status_color': status_color,
        'risk_score': risk_score,
        'health_score': health_score,
        'reasons': reasons,
        'ai_insight': ai_insight,
        'root_cause_analysis': root_cause_analysis
    }

