def generate_personalized_recommendations(perf, risk_info):
    if not perf:
        return []

    recommendations = []
    
    att = perf['att_pct']
    assign = perf['assign_score']
    final = perf['final_score']
    weak_subs = perf['weak_subjects']
    trend_status = perf['trend_status']
    trend_delta = perf['trend_delta']

    # 1. Attendance recommendation
    if att < 75.0:
        recommendations.append({
            'category': 'Attendance Warning',
            'icon': 'bi-calendar-x-fill',
            'color': 'danger',
            'action': f"Your attendance is currently {att}%, which is below the mandatory 75% requirement. Attend upcoming classes regularly to catch up on missed lectures."
        })
    elif att < 80.0:
        recommendations.append({
            'category': 'Attendance Improvement',
            'icon': 'bi-calendar-check',
            'color': 'warning',
            'action': f"Your attendance is {att}%. Maintaining consistent class participation will strengthen your internal evaluation."
        })

    # 2. Assignment recommendation
    if assign < 60.0:
        recommendations.append({
            'category': 'Continuous Assessment',
            'icon': 'bi-journal-x',
            'color': 'danger',
            'action': f"Your assignment score average is {assign}%. Complete pending assignments and review feedback to improve continuous internal marks."
        })

    # 3. Exam preparation recommendation
    if final < 60.0:
        recommendations.append({
            'category': 'Exam Preparation',
            'icon': 'bi-pencil-square',
            'color': 'danger',
            'action': f"Your final examination score ({final}%) needs significant improvement. Focus on solving previous year exam question papers and revising core formulas."
        })

    # 4. Weak subject specific recommendation
    if weak_subs:
        for w in weak_subs:
            recommendations.append({
                'category': 'Subject Focus',
                'icon': 'bi-exclamation-triangle-fill',
                'color': 'warning',
                'action': f"{w['course_name']} ({w['course_code']}) is currently your weakest subject ({w['score']}%). Allocate at least 1.5 extra study hours daily for practice in {w['course_name']}."
            })

    # 5. Trend recommendation
    if trend_status == "Declining":
        recommendations.append({
            'category': 'Performance Trajectory',
            'icon': 'bi-graph-down-arrow',
            'color': 'danger',
            'action': f"Your performance declined by {abs(trend_delta)}% compared to your previous assessment. Schedule a one-on-one consultation with your subject faculty."
        })

    # Default positive recommendation if student is performing well
    if not recommendations or perf['overall_score'] >= 80.0:
        recommendations.append({
            'category': 'Excellence Maintenance',
            'icon': 'bi-award-fill',
            'color': 'success',
            'action': f"Excellent work! Your overall performance is {perf['overall_score']}%. Continue your study routine and consider peer mentoring weaker classmates."
        })

    return recommendations
