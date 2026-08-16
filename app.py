import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

from database.db import (get_db_connection, query_db, execute_db, get_user_by_email_and_role,
                         create_notification, get_notifications_for_student, create_intervention,
                         get_interventions_for_student, get_all_interventions, update_intervention_status,
                         get_study_tasks, toggle_study_task)
from ai.performance_analysis import calculate_student_performance
from ai.risk_prediction import evaluate_academic_risk
from ai.recommendations import generate_personalized_recommendations
from ai.assistant import answer_student_query
from ai.predictor import predict_performance_and_risk

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'edumind_ai_unique_secret_key_2026')

# Helper decorator for role checking
def role_required(allowed_roles):
    def decorator(f):
        def wrapped(*args, **kwargs):
            if 'user' not in session or session['user']['role'] not in allowed_roles:
                flash('Unauthorized access. Please login with appropriate credentials.', 'warning')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        wrapped.__name__ = f.__name__
        return wrapped
    return decorator

# ----------------------------
# AUTH & PUBLIC ROUTES
# ----------------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = get_user_by_email_and_role(email, role)
        if user:
            session['user'] = {
                'id': user['id'],
                'student_id': user.get('student_id', user['id']),
                'name': user['name'],
                'email': user['email'],
                'role': role,
                'department': user.get('department', 'General')
            }
            flash(f"Welcome back, {user['name']}!", 'success')
            if role == 'student':
                return redirect(url_for('student_dashboard'))
            elif role == 'parent':
                return redirect(url_for('parent_dashboard'))
            elif role == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            elif role == 'admin':
                return redirect(url_for('admin_dashboard'))
        else:
            flash(f"Invalid credentials or no {role} account found for {email}", 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ----------------------------
# STUDENT PORTAL ROUTES
# ----------------------------

@app.route('/student/dashboard')
@role_required(['student'])
def student_dashboard():
    student_id = session['user']['id']
    perf = calculate_student_performance(student_id)
    risk = evaluate_academic_risk(perf)
    recommendations = generate_personalized_recommendations(perf, risk)

    return render_template('student_dashboard.html',
                           active_page='student_dashboard',
                           perf=perf,
                           risk=risk,
                           recommendations=recommendations)

@app.route('/student/courses')
@role_required(['student'])
def student_courses():
    student_id = session['user']['id']
    perf = calculate_student_performance(student_id)
    
    courses_raw = query_db("""
        SELECT c.*, t.name as teacher_name
        FROM courses c
        JOIN enrollments e ON c.id = e.course_id
        LEFT JOIN teachers t ON c.teacher_id = t.id
        WHERE e.student_id = ?;
    """, (student_id,))

    courses = []
    subject_map = {s['course_id']: s['score'] for s in perf['subject_performance']}
    
    for c in courses_raw:
        c_dict = dict(c)
        c_dict['current_score'] = subject_map.get(c['id'], 70.0)
        courses.append(c_dict)

    return render_template('student_courses.html',
                           active_page='student_courses',
                           courses=courses)

@app.route('/student/attendance')
@role_required(['student'])
def student_attendance():
    student_id = session['user']['id']
    perf = calculate_student_performance(student_id)

    # Subject wise breakdown
    course_att_raw = query_db("""
        SELECT c.course_code, c.course_name,
               COUNT(*) as total,
               SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) as present
        FROM attendance a
        JOIN courses c ON a.course_id = c.id
        WHERE a.student_id = ?
        GROUP BY c.id;
    """, (student_id,))

    course_att = []
    for r in course_att_raw:
        tot = r['total']
        pres = r['present']
        pct = round((pres / tot * 100), 1) if tot > 0 else 0
        course_att.append({
            'course_code': r['course_code'],
            'course_name': r['course_name'],
            'total': tot,
            'present': pres,
            'absent': tot - pres,
            'pct': pct
        })

    # Recent attendance logs
    logs_raw = query_db("""
        SELECT a.date, a.status, c.course_code, c.course_name
        FROM attendance a
        JOIN courses c ON a.course_id = c.id
        WHERE a.student_id = ?
        ORDER BY a.date DESC
        LIMIT 25;
    """, (student_id,))

    return render_template('student_attendance.html',
                           active_page='student_attendance',
                           perf=perf,
                           course_att=course_att,
                           logs=logs_raw)

@app.route('/student/assignments')
@role_required(['student'])
def student_assignments():
    student_id = session['user']['id']
    perf = calculate_student_performance(student_id)

    assignments_raw = query_db("""
        SELECT a.id, a.title, a.description, a.max_marks, a.due_date,
               c.course_code, c.course_name,
               sub.marks_obtained, sub.feedback
        FROM assignments a
        JOIN courses c ON a.course_id = c.id
        JOIN enrollments e ON c.id = e.course_id
        LEFT JOIN assignment_submissions sub ON a.id = sub.assignment_id AND sub.student_id = ?
        WHERE e.student_id = ?;
    """, (student_id, student_id))

    return render_template('student_assignments.html',
                           active_page='student_assignments',
                           perf=perf,
                           assignments=assignments_raw)

@app.route('/student/submit-assignment', methods=['POST'])
@role_required(['student'])
def student_submit_assignment():
    student_id = session['user']['id']
    assignment_id = request.form.get('assignment_id')
    submission_text = request.form.get('submission_text')

    # Check if already submitted
    existing = query_db("SELECT id FROM assignment_submissions WHERE assignment_id = ? AND student_id = ?",
                        (assignment_id, student_id), one=True)
    if existing:
        execute_db("""
            UPDATE assignment_submissions 
            SET submission_text = ?, submission_date = CURRENT_TIMESTAMP
            WHERE id = ?;
        """, (submission_text, existing['id']))
    else:
        execute_db("""
            INSERT INTO assignment_submissions (assignment_id, student_id, submission_text, marks_obtained, feedback)
            VALUES (?, ?, ?, 75.0, 'Submitted successfully');
        """, (assignment_id, student_id, submission_text))

    flash('Assignment solution submitted successfully!', 'success')
    return redirect(url_for('student_assignments'))

@app.route('/student/results')
@role_required(['student'])
def student_results():
    student_id = session['user']['id']
    perf = calculate_student_performance(student_id)

    exam_marks = query_db("""
        SELECT c.course_code, c.course_name, e.exam_name, e.exam_type, e.max_marks, m.marks_obtained
        FROM marks m
        JOIN examinations e ON m.exam_id = e.id
        JOIN courses c ON e.course_id = c.id
        WHERE m.student_id = ?
        ORDER BY e.exam_type, c.course_code;
    """, (student_id,))

    return render_template('student_results.html',
                           active_page='student_results',
                           perf=perf,
                           exam_marks=exam_marks)

@app.route('/student/ai-recommendations')
@role_required(['student'])
def student_ai_recommendations():
    student_id = session['user']['id']
    perf = calculate_student_performance(student_id)
    risk = evaluate_academic_risk(perf)
    recommendations = generate_personalized_recommendations(perf, risk)

    return render_template('student_ai_recommendations.html',
                           active_page='student_ai_recommendations',
                           perf=perf,
                           risk=risk,
                           recommendations=recommendations)

@app.route('/api/student/ai-chat', methods=['POST'])
@role_required(['student'])
def api_student_ai_chat():
    student_id = session['user']['id']
    data = request.get_json() or {}
    question = data.get('question', '')

    response_text = answer_student_query(student_id, question)
    return jsonify({'response': response_text})

@app.route('/student/grade-predictor')
@role_required(['student'])
def student_grade_predictor():
    student_id = session['user']['id']
    perf = calculate_student_performance(student_id)
    return render_template('student_predictor.html',
                           active_page='student_grade_predictor',
                           perf=perf)

@app.route('/api/student/predict-grade', methods=['POST'])
@role_required(['student'])
def api_student_predict_grade():
    student_id = session['user']['id']
    data = request.get_json() or {}
    
    att = data.get('att')
    assign = data.get('assign')
    internal = data.get('internal')
    final = data.get('final')

    prediction = predict_performance_and_risk(student_id, att, assign, internal, final)
    return jsonify({
        'status': 'success',
        'prediction': prediction
    })

@app.route('/student/notifications')
@role_required(['student'])
def student_notifications():
    student_id = session['user']['id']
    notifications = get_notifications_for_student(student_id)
    return render_template('student_notifications.html',
                           active_page='student_notifications',
                           notifications=notifications)

@app.route('/student/export-report')
@role_required(['student'])
def student_export_report():
    student_id = session['user']['id']
    perf = calculate_student_performance(student_id)
    risk = evaluate_academic_risk(perf)
    recommendations = generate_personalized_recommendations(perf, risk)
    now_date = datetime.now().strftime('%Y-%m-%d %H:%M')

    return render_template('student_report.html',
                           perf=perf,
                           risk=risk,
                           recommendations=recommendations,
                           now_date=now_date)

@app.route('/teacher/student/<int:student_id>/export-report')
@role_required(['teacher', 'admin'])
def teacher_student_export_report(student_id):
    perf = calculate_student_performance(student_id)
    if not perf:
        flash('Student not found.', 'danger')
        return redirect(url_for('teacher_students'))
    
    risk = evaluate_academic_risk(perf)
    recommendations = generate_personalized_recommendations(perf, risk)
    now_date = datetime.now().strftime('%Y-%m-%d %H:%M')

    return render_template('student_report.html',
                           perf=perf,
                           risk=risk,
                           recommendations=recommendations,
                           now_date=now_date)

@app.route('/teacher/notifications', methods=['GET', 'POST'])
@role_required(['teacher', 'admin'])
def teacher_notifications():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        alert_type = request.form.get('alert_type', 'GENERAL')
        title = request.form.get('title')
        message = request.form.get('message')
        sender = session['user']['name'] + " (" + session['user']['role'].capitalize() + ")"

        create_notification(student_id, title, message, alert_type, sender_role=sender)
        flash('Risk alert & parent notification dispatched successfully!', 'success')
        return redirect(url_for('teacher_notifications'))

    students = query_db("SELECT id, name, roll_no, department FROM students ORDER BY name;")
    all_notifications = query_db("""
        SELECT n.*, s.name as student_name
        FROM notifications n
        JOIN students s ON n.student_id = s.id
        ORDER BY n.created_at DESC;
    """)

    return render_template('teacher_notifications.html',
                           active_page='teacher_notifications',
                           students=students,
                           all_notifications=all_notifications)

@app.route('/parent/dashboard')
@role_required(['parent'])
def parent_dashboard():
    student_id = session['user']['student_id']
    perf = calculate_student_performance(student_id)
    risk = evaluate_academic_risk(perf)
    recommendations = generate_personalized_recommendations(perf, risk)
    notifications = get_notifications_for_student(student_id)
    interventions = get_interventions_for_student(student_id)
    study_tasks = get_study_tasks(student_id)
    return render_template('parent_dashboard.html',
                           active_page='parent_dashboard',
                           perf=perf,
                           risk=risk,
                           recommendations=recommendations,
                           notifications=notifications,
                           interventions=interventions,
                           study_tasks=study_tasks)

@app.route('/student/study-plan')
@role_required(['student'])
def student_study_plan():
    student_id = session['user']['id']
    perf = calculate_student_performance(student_id)
    risk = evaluate_academic_risk(perf)
    study_tasks = get_study_tasks(student_id)
    completed_count = sum(1 for t in study_tasks if t['is_completed'])
    total_count = len(study_tasks)
    pct_completed = round((completed_count / total_count * 100), 1) if total_count > 0 else 0
    return render_template('student_study_plan.html',
                           active_page='student_study_plan',
                           perf=perf,
                           risk=risk,
                           study_tasks=study_tasks,
                           completed_count=completed_count,
                           total_count=total_count,
                           pct_completed=pct_completed)

@app.route('/api/student/study-task/toggle', methods=['POST'])
@role_required(['student'])
def api_student_study_task_toggle():
    data = request.get_json() or {}
    task_id = data.get('task_id')
    is_completed = data.get('is_completed', False)
    toggle_study_task(task_id, is_completed)
    return jsonify({'status': 'success'})

@app.route('/student/timeline')
@role_required(['student'])
def student_timeline():
    student_id = session['user']['id']
    perf = calculate_student_performance(student_id)
    risk = evaluate_academic_risk(perf)
    notifications = get_notifications_for_student(student_id)
    interventions = get_interventions_for_student(student_id)
    return render_template('student_timeline.html',
                           active_page='student_timeline',
                           perf=perf,
                           risk=risk,
                           notifications=notifications,
                           interventions=interventions)

@app.route('/api/copilot/chat', methods=['POST'])
def api_copilot_chat():
    data = request.get_json() or {}
    question = data.get('question', '')
    role = session.get('user', {}).get('role', 'student')
    if role in ['teacher', 'admin']:
        from ai.assistant import answer_teacher_query
        reply = answer_teacher_query(question)
    else:
        student_id = session.get('user', {}).get('student_id', session.get('user', {}).get('id', 1))
        reply = answer_student_query(student_id, question)
    return jsonify({'response': reply})

@app.route('/api/teacher/assign-intervention', methods=['POST'])
@role_required(['teacher', 'admin'])
def api_teacher_assign_intervention():
    student_id = request.form.get('student_id')
    title = request.form.get('title')
    description = request.form.get('description')
    action_required = request.form.get('action_required')
    teacher_name = session['user']['name']
    create_intervention(student_id, teacher_name, title, description, action_required)
    flash('Academic intervention assigned & parent alert dispatched successfully!', 'success')
    return redirect(request.referrer or url_for('teacher_dashboard'))

@app.route('/api/teacher/update-intervention-status', methods=['POST'])
@role_required(['teacher', 'admin', 'student', 'parent'])
def api_teacher_update_intervention_status():
    data = request.get_json() or {}
    intervention_id = data.get('intervention_id')
    status = data.get('status', 'Resolved')
    update_intervention_status(intervention_id, status)
    return jsonify({'status': 'success'})



# ----------------------------
# TEACHER PORTAL ROUTES
# ----------------------------

@app.route('/teacher/dashboard')
@role_required(['teacher'])
def teacher_dashboard():
    students_raw = query_db("SELECT id, name, email, roll_no FROM students;")
    
    student_roster = []
    high_risk_count = 0
    med_risk_count = 0
    low_risk_count = 0

    high_risk_students = []

    total_att_sum = 0
    total_score_sum = 0

    for s in students_raw:
        perf = calculate_student_performance(s['id'])
        risk = evaluate_academic_risk(perf)

        total_att_sum += perf['att_pct']
        total_score_sum += perf['overall_score']

        s_item = {
            'id': s['id'],
            'name': s['name'],
            'email': s['email'],
            'roll_no': s['roll_no'],
            'att_pct': perf['att_pct'],
            'overall_score': perf['overall_score'],
            'trend_status': perf['trend_status'],
            'weak_subjects': perf['weak_subjects'],
            'risk_level': risk['risk_level'],
            'risk_badge': risk['risk_badge'],
            'risk_code': risk['risk_code']
        }

        if risk['risk_code'] == 'high':
            high_risk_count += 1
            high_risk_students.append(s_item)
        elif risk['risk_code'] == 'medium':
            med_risk_count += 1
        else:
            low_risk_count += 1

        student_roster.append(s_item)

    total_students = len(students_raw)
    avg_attendance = round(total_att_sum / total_students, 1) if total_students > 0 else 0
    avg_performance = round(total_score_sum / total_students, 1) if total_students > 0 else 0

    return render_template('teacher_dashboard.html',
                           active_page='teacher_dashboard',
                           total_students=total_students,
                           avg_attendance=avg_attendance,
                           avg_performance=avg_performance,
                           high_risk_count=high_risk_count,
                           med_risk_count=med_risk_count,
                           low_risk_count=low_risk_count,
                           high_risk_students=high_risk_students,
                           student_roster=student_roster)

@app.route('/teacher/students')
@role_required(['teacher'])
def teacher_students():
    filter_risk = request.args.get('risk', '').lower()

    students_raw = query_db("SELECT id, name, email, roll_no FROM students;")
    student_list = []

    for s in students_raw:
        perf = calculate_student_performance(s['id'])
        risk = evaluate_academic_risk(perf)

        if filter_risk and risk['risk_code'] != filter_risk:
            continue

        student_list.append({
            'id': s['id'],
            'name': s['name'],
            'email': s['email'],
            'roll_no': s['roll_no'],
            'att_pct': perf['att_pct'],
            'overall_score': perf['overall_score'],
            'weak_subjects': perf['weak_subjects'],
            'risk_level': risk['risk_level'],
            'risk_badge': risk['risk_badge'],
            'risk_code': risk['risk_code']
        })

    return render_template('teacher_students.html',
                           active_page='teacher_students',
                           filter_risk=filter_risk,
                           students=student_list)

@app.route('/teacher/student/<int:student_id>/ai-analysis')
@role_required(['teacher', 'admin'])
def teacher_student_detail(student_id):
    perf = calculate_student_performance(student_id)
    if not perf:
        flash('Student record not found', 'danger')
        return redirect(url_for('teacher_students'))

    risk = evaluate_academic_risk(perf)
    recommendations = generate_personalized_recommendations(perf, risk)

    return render_template('teacher_student_detail.html',
                           active_page='teacher_students',
                           perf=perf,
                           risk=risk,
                           recommendations=recommendations)

@app.route('/teacher/attendance', methods=['GET'])
@role_required(['teacher'])
def teacher_attendance():
    courses = query_db("SELECT id, course_code, course_name FROM courses;")
    students = query_db("SELECT id, roll_no, name FROM students;")
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('teacher_attendance.html',
                           active_page='teacher_attendance',
                           courses=courses,
                           students=students,
                           today=today)

@app.route('/teacher/record-attendance', methods=['POST'])
@role_required(['teacher'])
def teacher_record_attendance():
    course_id = request.form.get('course_id')
    att_date = request.form.get('att_date')

    students = query_db("SELECT id FROM students;")
    for s in students:
        s_id = s['id']
        status = request.form.get(f'status_{s_id}', 'Present')
        execute_db("""
            INSERT INTO attendance (student_id, course_id, date, status)
            VALUES (?, ?, ?, ?);
        """, (s_id, course_id, att_date, status))

    flash(f"Attendance recorded for {len(students)} students on {att_date}.", 'success')
    return redirect(url_for('teacher_attendance'))

@app.route('/teacher/assignments')
@role_required(['teacher'])
def teacher_assignments():
    courses = query_db("SELECT id, course_code, course_name FROM courses;")
    assignments_raw = query_db("""
        SELECT a.*, c.course_code, c.course_name,
               (SELECT COUNT(*) FROM assignment_submissions sub WHERE sub.assignment_id = a.id) as submission_count
        FROM assignments a
        JOIN courses c ON a.course_id = c.id;
    """)
    return render_template('teacher_assignments.html',
                           active_page='teacher_assignments',
                           courses=courses,
                           assignments=assignments_raw)

@app.route('/teacher/create-assignment', methods=['POST'])
@role_required(['teacher'])
def teacher_create_assignment():
    course_id = request.form.get('course_id')
    title = request.form.get('title')
    description = request.form.get('description')
    max_marks = request.form.get('max_marks', 100)
    due_date = request.form.get('due_date')

    execute_db("""
        INSERT INTO assignments (course_id, title, description, max_marks, due_date)
        VALUES (?, ?, ?, ?, ?);
    """, (course_id, title, description, max_marks, due_date))

    flash(f"Assignment '{title}' published successfully!", 'success')
    return redirect(url_for('teacher_assignments'))

@app.route('/teacher/examinations')
@role_required(['teacher'])
def teacher_examinations():
    examinations = query_db("""
        SELECT e.id, e.exam_name, e.exam_type, c.course_code, c.course_name
        FROM examinations e
        JOIN courses c ON e.course_id = c.id;
    """)
    students = query_db("SELECT id, roll_no, name FROM students;")
    return render_template('teacher_examinations.html',
                           active_page='teacher_examinations',
                           examinations=examinations,
                           students=students)

@app.route('/teacher/save-marks', methods=['POST'])
@role_required(['teacher'])
def teacher_save_marks():
    exam_id = request.form.get('exam_id')
    students = query_db("SELECT id FROM students;")

    for s in students:
        s_id = s['id']
        mark_val = request.form.get(f'mark_{s_id}')
        if mark_val is not None and mark_val != '':
            mark_float = float(mark_val)
            existing = query_db("SELECT id FROM marks WHERE student_id = ? AND exam_id = ?", (s_id, exam_id), one=True)
            if existing:
                execute_db("UPDATE marks SET marks_obtained = ? WHERE id = ?", (mark_float, existing['id']))
            else:
                execute_db("INSERT INTO marks (student_id, exam_id, marks_obtained) VALUES (?, ?, ?)", (s_id, exam_id, mark_float))

    flash("Examination marks recorded successfully!", 'success')
    return redirect(url_for('teacher_examinations'))

# ----------------------------
# ADMIN PORTAL ROUTES
# ----------------------------

@app.route('/admin/dashboard')
@role_required(['admin'])
def admin_dashboard():
    total_students = query_db("SELECT COUNT(*) FROM students;", one=True)[0]
    total_teachers = query_db("SELECT COUNT(*) FROM teachers;", one=True)[0]
    total_courses = query_db("SELECT COUNT(*) FROM courses;", one=True)[0]

    students_raw = query_db("SELECT id, name, email, roll_no FROM students;")
    
    high_risk_count = 0
    med_risk_count = 0
    low_risk_count = 0
    high_risk_list = []

    total_att_sum = 0
    total_score_sum = 0

    for s in students_raw:
        perf = calculate_student_performance(s['id'])
        risk = evaluate_academic_risk(perf)

        total_att_sum += perf['att_pct']
        total_score_sum += perf['overall_score']

        if risk['risk_code'] == 'high':
            high_risk_count += 1
            high_risk_list.append({
                'name': s['name'],
                'email': s['email'],
                'att_pct': perf['att_pct'],
                'overall_score': perf['overall_score'],
                'weak_subjects': perf['weak_subjects']
            })
        elif risk['risk_code'] == 'medium':
            med_risk_count += 1
        else:
            low_risk_count += 1

    avg_attendance = round(total_att_sum / total_students, 1) if total_students > 0 else 0
    avg_performance = round(total_score_sum / total_students, 1) if total_students > 0 else 0

    # Course performance breakdown
    courses_raw = query_db("""
        SELECT c.id, c.course_code, c.course_name, AVG(m.marks_obtained) as avg_score
        FROM courses c
        LEFT JOIN examinations ex ON c.id = ex.course_id
        LEFT JOIN marks m ON ex.id = m.exam_id
        GROUP BY c.id;
    """)

    course_analytics = []
    for cr in courses_raw:
        course_analytics.append({
            'course_code': cr['course_code'],
            'course_name': cr['course_name'],
            'avg_score': round(cr['avg_score'], 1) if cr['avg_score'] is not None else 70.0
        })

    return render_template('admin_dashboard.html',
                           active_page='admin_dashboard',
                           total_students=total_students,
                           total_teachers=total_teachers,
                           total_courses=total_courses,
                           avg_attendance=avg_attendance,
                           avg_performance=avg_performance,
                           high_risk_count=high_risk_count,
                           med_risk_count=med_risk_count,
                           low_risk_count=low_risk_count,
                           high_risk_list=high_risk_list,
                           course_analytics=course_analytics)

@app.route('/admin/management')
@role_required(['admin'])
def admin_management():
    students = query_db("SELECT * FROM students;")
    teachers = query_db("SELECT * FROM teachers;")
    courses = query_db("""
        SELECT c.*, t.name as teacher_name
        FROM courses c
        LEFT JOIN teachers t ON c.teacher_id = t.id;
    """)
    return render_template('admin_management.html',
                           active_page='admin_management',
                           students=students,
                           teachers=teachers,
                           courses=courses)

@app.route('/admin/add-student', methods=['POST'])
@role_required(['admin'])
def admin_add_student():
    roll_no = request.form.get('roll_no')
    name = request.form.get('name')
    email = request.form.get('email')
    department = request.form.get('department', 'Computer Science')

    execute_db("""
        INSERT INTO students (roll_no, name, email, password, department, class_id)
        VALUES (?, ?, ?, 'student123', ?, 1);
    """, (roll_no, name, email, department))

    flash(f"Student '{name}' registered successfully!", 'success')
    return redirect(url_for('admin_management'))

@app.route('/admin/analytics')
@role_required(['admin'])
def admin_analytics():
    students_raw = query_db("SELECT id, name, email, roll_no FROM students;")
    
    all_student_evals = []
    high_risk_count = 0
    med_risk_count = 0
    low_risk_count = 0
    total_att_sum = 0
    total_score_sum = 0

    for s in students_raw:
        perf = calculate_student_performance(s['id'])
        risk = evaluate_academic_risk(perf)

        total_att_sum += perf['att_pct']
        total_score_sum += perf['overall_score']

        if risk['risk_code'] == 'high':
            high_risk_count += 1
        elif risk['risk_code'] == 'medium':
            med_risk_count += 1
        else:
            low_risk_count += 1

        all_student_evals.append({
            'id': s['id'],
            'name': s['name'],
            'roll_no': s['roll_no'],
            'att_pct': perf['att_pct'],
            'assign_score': perf['assign_score'],
            'final_score': perf['final_score'],
            'overall_score': perf['overall_score'],
            'risk_level': risk['risk_level'],
            'risk_badge': risk['risk_badge'],
            'risk_code': risk['risk_code']
        })

    total_students = len(students_raw)
    avg_attendance = round(total_att_sum / total_students, 1) if total_students > 0 else 0
    avg_performance = round(total_score_sum / total_students, 1) if total_students > 0 else 0

    return render_template('admin_analytics.html',
                           active_page='admin_analytics',
                           total_students=total_students,
                           avg_attendance=avg_attendance,
                           avg_performance=avg_performance,
                           high_risk_count=high_risk_count,
                           med_risk_count=med_risk_count,
                           low_risk_count=low_risk_count,
                           all_student_evals=all_student_evals)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
