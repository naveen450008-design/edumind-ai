import sys, os
sys.path.insert(0, os.path.abspath('.'))

from ai.performance_analysis import calculate_student_performance
from ai.risk_prediction import evaluate_academic_risk
from ai.recommendations import generate_personalized_recommendations
from ai.assistant import answer_student_query

def test_ai_engine():
    # Test Student 1 (Arun Kumar - Expected HIGH RISK)
    arun_perf = calculate_student_performance(1)
    arun_risk = evaluate_academic_risk(arun_perf)
    arun_recs = generate_personalized_recommendations(arun_perf, arun_risk)

    print(f"--- Arun Kumar AI Evaluation ---")
    print(f"Overall Score: {arun_perf['overall_score']}%")
    print(f"Attendance: {arun_perf['att_pct']}%")
    print(f"Assignments: {arun_perf['assign_score']}%")
    print(f"Final Exam: {arun_perf['final_score']}%")
    print(f"Risk Level: {arun_risk['risk_level']}")
    print(f"Weak Subjects: {[w['course_name'] for w in arun_perf['weak_subjects']]}")
    
    assert arun_risk['risk_level'] == 'HIGH RISK', f"Expected HIGH RISK for Arun, got {arun_risk['risk_level']}"
    assert len(arun_recs) >= 3, "Expected personalized recommendations for Arun"
    print("[PASS] Arun Risk & Recommendation Analysis Verified!")

    # Test Assistant Q&A for Arun
    q1 = answer_student_query(1, "Why is my performance low?")
    print(f"\nStudent Query: 'Why is my performance low?'\nAI Reply: {q1}")
    assert "68" in q1 or "attendance" in q1.lower()

    q2 = answer_student_query(1, "What should I improve first?")
    print(f"\nStudent Query: 'What should I improve first?'\nAI Reply: {q2}")
    assert "Mathematics" in q2 or "priority" in q2.lower()

    # Test Student 2 (Rahul Sharma - Expected LOW RISK)
    rahul_perf = calculate_student_performance(2)
    rahul_risk = evaluate_academic_risk(rahul_perf)
    assert rahul_risk['risk_level'] == 'LOW RISK', f"Expected LOW RISK for Rahul, got {rahul_risk['risk_level']}"
    print(f"\n[PASS] Rahul Risk Analysis Verified (LOW RISK: {rahul_perf['overall_score']}%)")

    print("\nPhase 7, 8, 9, 10 AI Core Engine Verification Passed Completely!")

if __name__ == '__main__':
    test_ai_engine()
