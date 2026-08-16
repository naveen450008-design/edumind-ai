from ai.performance_analysis import calculate_student_performance
from ai.risk_prediction import evaluate_academic_risk
from database.db import query_db

def answer_student_query(student_id, question):
    question_lower = question.lower()

    perf = calculate_student_performance(student_id)
    if not perf:
        return "I could not locate your academic records at the moment. Please contact system support."

    risk_info = evaluate_academic_risk(perf)
    
    att = perf['att_pct']
    assign = perf['assign_score']
    internal = perf['internal_score']
    final = perf['final_score']
    overall = perf['overall_score']
    weak_subs = perf['weak_subjects']
    weak_names = ", ".join([w['course_name'] for w in weak_subs]) if weak_subs else None

    # 1. "Create my study plan" / "study plan"
    if any(k in question_lower for k in ['study plan', 'schedule', 'timetable', 'plan']):
        if weak_names:
            return f"I have compiled a custom AI study plan for you! Focus heavily on {weak_names} on Mondays and Wednesdays for 45 minutes, followed by practice problems."
        else:
            return f"Your custom AI study plan allocates 45 minutes daily across Data Structures and Physics with Friday revision sessions to keep your Academic Health Score at {risk_info['health_score']}/100."

    # 2. "What happens if my attendance reaches 90%?" / "attendance reaches" / "predictor"
    if '90%' in question_lower or 'attendance reaches' in question_lower:
        new_overall = round((90.0 * 0.20) + (assign * 0.20) + (internal * 0.20) + (final * 0.40), 1)
        return f"If your attendance reaches 90%, your overall performance score will increase to {new_overall}%, reducing your academic risk score."

    # 3. "Why is my performance low?" or "why am i at risk?" or "why is my risk high?"
    if any(k in question_lower for k in ['why', 'low', 'reason', 'cause', 'affect', 'risk']):
        reasons_list = []
        if att < 75.0:
            reasons_list.append(f"{att}% attendance (below 75%)")
        if weak_names:
            reasons_list.append(f"low marks in {weak_names}")
        if final < 60.0:
            reasons_list.append(f"{final}% examination score")
        if assign < 60.0:
            reasons_list.append(f"{assign}% assignment average")

        if reasons_list:
            reasons_str = ", ".join(reasons_list)
            return f"Your current performance ({overall}%) is mainly affected by your {reasons_str}. Your overall risk level is {risk_info['risk_level']}."
        else:
            return f"Your performance is actually strong at {overall}%! Your attendance is {att}%, and exam score is {final}%."

    # 4. "What should I improve first?" or "priority" / "how can i improve"
    if any(k in question_lower for k in ['first', 'priority', 'start', 'begin', 'improve my score', 'improve']):
        priorities = []
        if weak_names:
            priorities.append(f"focusing on {weak_names}")
        if final < 60.0:
            priorities.append("examination preparation")
        if att < 75.0:
            priorities.append("improving your attendance above 75%")

        if priorities:
            p_str = " and ".join(priorities)
            return f"Your highest priority should be {p_str} to lower your academic risk level."
        else:
            return "Your current academic metrics are well balanced. Maintain your regular study schedule and focus on mastering advanced concepts!"

    # 5. "Which subject should I focus on?" or "weak subjects"
    if any(k in question_lower for k in ['subject', 'focus', 'weak area', 'weak subject', 'weakest']):
        if weak_subs:
            detail = ", ".join([f"{w['course_name']} ({w['score']}%)" for w in weak_subs])
            return f"You should focus primarily on your weak subjects: {detail}. Spending 1-2 extra practice hours on these subjects will significantly raise your overall GPA."
        else:
            return "You do not currently have any failing or weak subjects! All your subject scores are above 60%."

    # 6. "How can I improve my attendance?" or "attendance"
    if any(k in question_lower for k in ['attendance', 'absent', 'class']):
        if att < 75.0:
            needed_classes = int((75 - att) * 0.4) + 3
            return f"Your current attendance is {att}%. To reach the mandatory 75% threshold, you should attend the next {needed_classes} consecutive classes without missing any."
        else:
            return f"Your attendance is healthy at {att}%. Keep attending lectures regularly to maintain your eligibility for final examinations."

    # Generic fallback
    return (
        f"Based on your latest academic data: your overall performance is {overall}%, attendance is {att}%, "
        f"assignment score is {assign}%, and final exam score is {final}%. Your academic risk is {risk_info['risk_level']}. "
        f"Feel free to ask 'Why am I at risk?' or 'Create my study plan'."
    )

def answer_teacher_query(question):
    question_lower = question.lower()
    students_raw = query_db("SELECT id, name, roll_no FROM students;")

    high_risk_list = []
    med_risk_list = []

    for s in students_raw:
        perf = calculate_student_performance(s['id'])
        risk = evaluate_academic_risk(perf)
        if risk['risk_code'] in ['high', 'critical']:
            high_risk_list.append(f"{s['name']} ({s['roll_no']}) - Risk Score: {risk['risk_score']}/100")
        elif risk['risk_code'] == 'medium':
            med_risk_list.append(s['name'])

    if any(k in question_lower for k in ['immediate', 'attention', 'at-risk', 'high risk', 'critical']):
        if high_risk_list:
            high_str = "; ".join(high_risk_list)
            return f"Students requiring immediate attention: {high_str}. Primary issues stem from low attendance (<75%) and weak scores in Mathematics and Databases."
        else:
            return "No students are currently at Critical or High Academic Risk."

    if any(k in question_lower for k in ['factor', 'cause', 'reason']):
        return "The primary risk factors across your roster are: 1) Attendance dropping below the 75% mandatory cutoff, 2) Mathematics for Computing exam scores, and 3) Pending assignment submissions."

    if any(k in question_lower for k in ['recommend', 'intervention', 'action']):
        return "Recommended faculty interventions: 1) Assign 3-hour weekly peer tutoring for Mathematics, 2) Issue mandatory parent notification for students below 75% attendance, 3) Conduct a midterm remedial review class."

    return f"Institution Overview: {len(high_risk_list)} student(s) at High/Critical Risk, {len(med_risk_list)} student(s) at Medium Risk. Ask 'Which students need immediate attention?' or 'Recommend interventions'."
