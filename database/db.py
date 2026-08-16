import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Students Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            department TEXT NOT NULL,
            class_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (class_id) REFERENCES classes (id)
        )
    ''')

    # 2. Teachers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            department TEXT NOT NULL,
            designation TEXT DEFAULT 'Assistant Professor',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. Classes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL,
            department TEXT NOT NULL,
            semester INTEGER NOT NULL,
            academic_year TEXT NOT NULL
        )
    ''')

    # 4. Courses Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT UNIQUE NOT NULL,
            course_name TEXT NOT NULL,
            credits INTEGER DEFAULT 3,
            teacher_id INTEGER,
            department TEXT NOT NULL,
            FOREIGN KEY (teacher_id) REFERENCES teachers (id)
        )
    ''')

    # 5. Enrollments Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            enrollment_date DATE DEFAULT (DATE('now')),
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (course_id) REFERENCES courses (id)
        )
    ''')

    # 6. Attendance Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            date DATE NOT NULL,
            status TEXT CHECK(status IN ('Present', 'Absent', 'Late')) NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (course_id) REFERENCES courses (id)
        )
    ''')

    # 7. Assignments Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            max_marks INTEGER DEFAULT 100,
            due_date DATE NOT NULL,
            FOREIGN KEY (course_id) REFERENCES courses (id)
        )
    ''')

    # 8. Assignment Submissions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assignment_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            submission_text TEXT,
            submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            marks_obtained REAL,
            feedback TEXT,
            status TEXT DEFAULT 'Graded',
            FOREIGN KEY (assignment_id) REFERENCES assignments (id),
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')

    # 9. Examinations Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS examinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            exam_name TEXT NOT NULL,
            exam_type TEXT CHECK(exam_type IN ('Internal 1', 'Internal 2', 'Final Exam', 'Previous Exam')) NOT NULL,
            max_marks INTEGER DEFAULT 100,
            exam_date DATE,
            FOREIGN KEY (course_id) REFERENCES courses (id)
        )
    ''')

    # 10. Marks Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            exam_id INTEGER NOT NULL,
            marks_obtained REAL NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (exam_id) REFERENCES examinations (id)
        )
    ''')

    # 11. Notifications / Parent Risk Alerts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            alert_type TEXT CHECK(alert_type IN ('HIGH_RISK', 'MEDIUM_RISK', 'LOW_RISK', 'ACADEMIC_INTERVENTION', 'GENERAL', 'CRITICAL_RISK', 'ATTENDANCE_ALERT', 'PERFORMANCE_ALERT', 'ACHIEVEMENT')) DEFAULT 'GENERAL',
            sender_role TEXT DEFAULT 'AI Engine',
            recipient TEXT DEFAULT 'Parent & Student',
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')

    # 12. Interventions Workflow Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interventions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            teacher_name TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            action_required TEXT NOT NULL,
            status TEXT CHECK(status IN ('Assigned', 'In Progress', 'Completed', 'Resolved')) DEFAULT 'Assigned',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')

    # 13. AI Personalized Study Plan Tasks Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            day_name TEXT NOT NULL,
            subject_name TEXT NOT NULL,
            duration_minutes INTEGER DEFAULT 45,
            task_description TEXT NOT NULL,
            is_completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database tables initialized successfully.")

# Helper queries
def query_db(query, args=(), one=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, args)
    conn.commit()
    lastid = cursor.lastrowid
    conn.close()
    return lastid

def get_user_by_email_and_role(email, role):
    conn = get_db_connection()
    cursor = conn.cursor()
    user = None
    if role == 'student':
        cursor.execute("SELECT * FROM students WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            user = dict(row)
            user['role'] = 'student'
    elif role == 'teacher':
        cursor.execute("SELECT * FROM teachers WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            user = dict(row)
            user['role'] = 'teacher'
    elif role == 'parent':
        # Default parent account linked to Arun (student_id: 1) or look up by email
        if email == 'parent@edumind.ai':
            cursor.execute("SELECT * FROM students WHERE id = 1;")
            row = cursor.fetchone()
            if row:
                s_dict = dict(row)
                user = {
                    'id': 1,
                    'student_id': 1,
                    'name': f"Parent of {s_dict['name']}",
                    'email': 'parent@edumind.ai',
                    'role': 'parent',
                    'student_name': s_dict['name'],
                    'student_roll': s_dict['roll_no'],
                    'department': s_dict['department']
                }
        else:
            cursor.execute("SELECT * FROM students WHERE email = ?", (email,))
            row = cursor.fetchone()
            if row:
                s_dict = dict(row)
                user = {
                    'id': s_dict['id'],
                    'student_id': s_dict['id'],
                    'name': f"Parent of {s_dict['name']}",
                    'email': email,
                    'role': 'parent',
                    'student_name': s_dict['name'],
                    'student_roll': s_dict['roll_no'],
                    'department': s_dict['department']
                }
    elif role == 'admin':
        if email == 'admin@edumind.ai':
            user = {
                'id': 999,
                'name': 'System Administrator',
                'email': 'admin@edumind.ai',
                'role': 'admin',
                'department': 'Administration'
            }
        else:
            cursor.execute("SELECT * FROM teachers WHERE email = ?", (email,))
            row = cursor.fetchone()
            if row:
                user = dict(row)
                user['role'] = 'admin'
    conn.close()
    return user

def create_notification(student_id, title, message, alert_type='GENERAL', sender_role='AI Engine', recipient='Parent & Student'):
    return execute_db("""
        INSERT INTO notifications (student_id, title, message, alert_type, sender_role, recipient)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (student_id, title, message, alert_type, sender_role, recipient))

def get_notifications_for_student(student_id):
    return query_db("""
        SELECT * FROM notifications
        WHERE student_id = ?
        ORDER BY created_at DESC
    """, (student_id,))

def create_intervention(student_id, teacher_name, title, description, action_required, status='Assigned'):
    # Also trigger automatic notification for student and parent
    create_notification(
        student_id,
        f"Teacher Intervention: {title}",
        f"{teacher_name} assigned an academic intervention: {description}. Required action: {action_required}",
        alert_type='ACADEMIC_INTERVENTION',
        sender_role=teacher_name,
        recipient='Parent & Student'
    )
    return execute_db("""
        INSERT INTO interventions (student_id, teacher_name, title, description, action_required, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (student_id, teacher_name, title, description, action_required, status))

def get_interventions_for_student(student_id):
    return query_db("""
        SELECT * FROM interventions
        WHERE student_id = ?
        ORDER BY created_at DESC
    """, (student_id,))

def get_all_interventions():
    return query_db("""
        SELECT i.*, s.name as student_name, s.roll_no as student_roll
        FROM interventions i
        JOIN students s ON i.student_id = s.id
        ORDER BY i.created_at DESC
    """)

def update_intervention_status(intervention_id, status):
    resolved_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S') if status in ['Completed', 'Resolved'] else None
    return execute_db("""
        UPDATE interventions
        SET status = ?, resolved_at = ?
        WHERE id = ?
    """, (status, resolved_at, intervention_id))

def ensure_student_study_plan(student_id):
    existing = query_db("SELECT COUNT(*) as count FROM study_tasks WHERE student_id = ?", (student_id,), one=True)
    if existing['count'] == 0:
        from ai.performance_analysis import calculate_student_performance
        perf = calculate_student_performance(student_id)
        weak_names = [w['course_name'] for w in perf.get('weak_subjects', [])] if perf else []
        main_weak = weak_names[0] if weak_names else 'Mathematics for Computing'
        sec_weak = weak_names[1] if len(weak_names) > 1 else 'Database Management Systems'

        tasks = [
            (student_id, 'Monday', main_weak, 45, 'Complete 20 practice problem set questions & review core formulas'),
            (student_id, 'Tuesday', 'Data Structures & Programming', 60, 'Solve 5 hands-on coding exercises on arrays & lists'),
            (student_id, 'Wednesday', sec_weak, 45, 'Review ER diagrams & SQL query execution plans'),
            (student_id, 'Thursday', 'Applied Physics', 45, 'Read Chapter 4 notes and solve numerical problems'),
            (student_id, 'Friday', 'Comprehensive Revision', 60, 'Complete weekly mock practice test and review weak topics')
        ]
        for t in tasks:
            execute_db("""
                INSERT INTO study_tasks (student_id, day_name, subject_name, duration_minutes, task_description)
                VALUES (?, ?, ?, ?, ?)
            """, t)

def get_study_tasks(student_id):
    ensure_student_study_plan(student_id)
    return query_db("""
        SELECT * FROM study_tasks
        WHERE student_id = ?
        ORDER BY id ASC
    """, (student_id,))

def toggle_study_task(task_id, is_completed):
    val = 1 if is_completed else 0
    execute_db("UPDATE study_tasks SET is_completed = ? WHERE id = ?", (val, task_id))



