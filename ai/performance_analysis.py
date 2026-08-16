from database.db import get_db_connection

def calculate_student_performance(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Fetch Student Details
    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    student = cursor.fetchone()
    if not student:
        conn.close()
        return None

    # 2. Calculate Attendance Percentage
    cursor.execute("""
        SELECT COUNT(*) as total, 
               SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present
        FROM attendance
        WHERE student_id = ?;
    """, (student_id,))
    att_row = cursor.fetchone()
    total_att = att_row['total'] or 0
    present_att = att_row['present'] or 0
    att_pct = round((present_att / total_att * 100), 1) if total_att > 0 else 75.0

    # 3. Calculate Assignment Score
    cursor.execute("""
        SELECT AVG(marks_obtained) as avg_assign
        FROM assignment_submissions
        WHERE student_id = ?;
    """, (student_id,))
    assign_row = cursor.fetchone()
    assign_score = round(assign_row['avg_assign'], 1) if assign_row['avg_assign'] is not None else 70.0

    # 4. Calculate Internal Marks (Internal 1 + Internal 2)
    cursor.execute("""
        SELECT AVG(m.marks_obtained) as avg_internal
        FROM marks m
        JOIN examinations e ON m.exam_id = e.id
        WHERE m.student_id = ? AND e.exam_type IN ('Internal 1', 'Internal 2');
    """, (student_id,))
    internal_row = cursor.fetchone()
    internal_score = round(internal_row['avg_internal'], 1) if internal_row['avg_internal'] is not None else 70.0

    # 5. Calculate Final Exam Marks
    cursor.execute("""
        SELECT AVG(m.marks_obtained) as avg_final
        FROM marks m
        JOIN examinations e ON m.exam_id = e.id
        WHERE m.student_id = ? AND e.exam_type = 'Final Exam';
    """, (student_id,))
    final_row = cursor.fetchone()
    final_score = round(final_row['avg_final'], 1) if final_row['avg_final'] is not None else 65.0

    # 6. Overall Performance Score Calculation
    # Formula: 20% Attendance + 20% Assignment + 20% Internal + 40% Final Exam
    overall_score = round(
        (att_pct * 0.20) + 
        (assign_score * 0.20) + 
        (internal_score * 0.20) + 
        (final_score * 0.40), 1
    )

    # 7. Performance Classification
    if overall_score >= 80:
        perf_category = "Excellent"
    elif overall_score >= 70:
        perf_category = "Good"
    elif overall_score >= 60:
        perf_category = "Average"
    elif overall_score >= 50:
        perf_category = "Needs Improvement"
    else:
        perf_category = "At Risk"

    # 8. Subject-Wise Breakdown
    cursor.execute("""
        SELECT c.id as course_id, c.course_code, c.course_name,
               AVG(m.marks_obtained) as avg_mark
        FROM courses c
        JOIN enrollments e ON c.id = e.course_id
        LEFT JOIN examinations ex ON c.id = ex.course_id
        LEFT JOIN marks m ON ex.id = m.exam_id AND m.student_id = ?
        WHERE e.student_id = ?
        GROUP BY c.id;
    """, (student_id, student_id))
    course_rows = cursor.fetchall()

    subject_performance = []
    weak_subjects = []
    
    for row in course_rows:
        score = round(row['avg_mark'], 1) if row['avg_mark'] is not None else 70.0
        if score < 60:
            status_icon = "🔴"
            status_label = "Weak"
            weak_subjects.append({
                'course_code': row['course_code'],
                'course_name': row['course_name'],
                'score': score
            })
        elif score < 75:
            status_icon = "🟡"
            status_label = "Average"
        else:
            status_icon = "🟢"
            status_label = "Strong"

        subject_performance.append({
            'course_id': row['course_id'],
            'course_code': row['course_code'],
            'course_name': row['course_name'],
            'score': score,
            'status_icon': status_icon,
            'status_label': status_label
        })

    # 9. Performance Trend (Previous vs Recent Exam)
    cursor.execute("""
        SELECT e.exam_type, m.marks_obtained
        FROM marks m
        JOIN examinations e ON m.exam_id = e.id
        WHERE m.student_id = ? AND e.exam_type IN ('Previous Exam', 'Final Exam');
    """, (student_id,))
    trend_rows = cursor.fetchall()
    
    prev_mark = None
    recent_mark = None
    for r in trend_rows:
        if r['exam_type'] == 'Previous Exam':
            prev_mark = r['marks_obtained']
        elif r['exam_type'] == 'Final Exam':
            recent_mark = r['marks_obtained']

    trend_status = "Stable"
    trend_delta = 0.0
    if prev_mark is not None and recent_mark is not None:
        trend_delta = round(recent_mark - prev_mark, 1)
        if trend_delta <= -5.0:
            trend_status = "Declining"
        elif trend_delta >= 5.0:
            trend_status = "Improving"

    conn.close()

    return {
        'student_id': student['id'],
        'student_name': student['name'],
        'email': student['email'],
        'roll_no': student['roll_no'],
        'department': student['department'],
        'att_pct': att_pct,
        'assign_score': assign_score,
        'internal_score': internal_score,
        'final_score': final_score,
        'overall_score': overall_score,
        'perf_category': perf_category,
        'subject_performance': subject_performance,
        'weak_subjects': weak_subjects,
        'trend_status': trend_status,
        'trend_delta': trend_delta,
        'prev_mark': prev_mark,
        'recent_mark': recent_mark
    }
