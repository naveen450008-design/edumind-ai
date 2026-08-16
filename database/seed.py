import sqlite3
import os
import random
from datetime import datetime, timedelta
from db import init_db, get_db_connection

def seed_database():
    # Make sure tables exist
    init_db()
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear existing data
    tables = ['notifications', 'interventions', 'study_tasks', 'marks', 'examinations',
              'assignment_submissions', 'assignments', 'attendance', 'enrollments',
              'courses', 'classes', 'teachers', 'students']
    for t in tables:
        cursor.execute(f"DELETE FROM {t};")
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{t}';")

    print("Seeding Classes...")
    cursor.execute('''
        INSERT INTO classes (id, class_name, department, semester, academic_year)
        VALUES (1, 'B.Tech CSE - 4th Sem', 'Computer Science', 4, '2025-2026');
    ''')

    print("Seeding Teachers...")
    teachers_data = [
        (1, 'Prof. John Smith', 'smith@edumind.ai', 'teacher123', 'Computer Science', 'Professor'),
        (2, 'Dr. Sarah Jenkins', 'jenkins@edumind.ai', 'teacher123', 'Mathematics', 'Associate Professor'),
        (3, 'Prof. Robert Davis', 'davis@edumind.ai', 'teacher123', 'Physics & Electronics', 'Assistant Professor'),
    ]
    cursor.executemany('''
        INSERT INTO teachers (id, name, email, password, department, designation)
        VALUES (?, ?, ?, ?, ?, ?);
    ''', teachers_data)

    print("Seeding Courses...")
    courses_data = [
        (1, 'CS101', 'Mathematics for Computing', 4, 2, 'Mathematics'),
        (2, 'CS102', 'Data Structures & Programming', 4, 1, 'Computer Science'),
        (3, 'PH101', 'Applied Physics', 3, 3, 'Physics'),
        (4, 'CS103', 'Database Management Systems', 4, 1, 'Computer Science'),
        (5, 'EC101', 'Basic Electronics', 3, 3, 'Electronics')
    ]
    cursor.executemany('''
        INSERT INTO courses (id, course_code, course_name, credits, teacher_id, department)
        VALUES (?, ?, ?, ?, ?, ?);
    ''', courses_data)

    print("Seeding 10 Students...")
    students_data = [
        (1, 'CS202601', 'Arun Kumar', 'arun@edumind.ai', 'student123', 'Computer Science', 1),
        (2, 'CS202602', 'Rahul Sharma', 'rahul@edumind.ai', 'student123', 'Computer Science', 1),
        (3, 'CS202603', 'Priya Patel', 'priya@edumind.ai', 'student123', 'Computer Science', 1),
        (4, 'CS202604', 'Varun Verma', 'varun@edumind.ai', 'student123', 'Computer Science', 1),
        (5, 'CS202605', 'Sneha Reddy', 'sneha@edumind.ai', 'student123', 'Computer Science', 1),
        (6, 'CS202606', 'Ananya Roy', 'ananya@edumind.ai', 'student123', 'Computer Science', 1),
        (7, 'CS202607', 'Karthik S.', 'karthik@edumind.ai', 'student123', 'Computer Science', 1),
        (8, 'CS202608', 'Divya N.', 'divya@edumind.ai', 'student123', 'Computer Science', 1),
        (9, 'CS202609', 'Manoj P.', 'manoj@edumind.ai', 'student123', 'Computer Science', 1),
        (10, 'CS202610', 'Swetha M.', 'swetha@edumind.ai', 'student123', 'Computer Science', 1),
    ]
    cursor.executemany('''
        INSERT INTO students (id, roll_no, name, email, password, department, class_id)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    ''', students_data)

    # Enroll all 10 students into all 5 courses
    print("Seeding Enrollments...")
    enrollments = []
    e_id = 1
    for s_id in range(1, 11):
        for c_id in range(1, 6):
            enrollments.append((e_id, s_id, c_id))
            e_id += 1
    cursor.executemany('''
        INSERT INTO enrollments (id, student_id, course_id) VALUES (?, ?, ?);
    ''', enrollments)

    print("Seeding Attendance Records...")
    # Generate 20 class dates for attendance per course
    start_date = datetime.now() - timedelta(days=60)
    attendance_records = []
    att_id = 1

    # Student specific attendance target percentages:
    # Arun: 68%, Rahul: 92%, Priya: 73%, Varun: 82%, Sneha: 79%, Ananya: 84%, Karthik: 62%, Divya: 96%, Manoj: 55%, Swetha: 74%
    att_targets = {
        1: 0.68, 2: 0.92, 3: 0.73, 4: 0.82, 5: 0.79,
        6: 0.84, 7: 0.62, 8: 0.96, 9: 0.55, 10: 0.74
    }

    for c_id in range(1, 6):
        for day in range(20):
            att_date = (start_date + timedelta(days=day*3)).strftime('%Y-%m-%d')
            for s_id in range(1, 11):
                prob = att_targets[s_id]
                # Lower math attendance for Arun
                if s_id == 1 and c_id == 1:
                    prob = 0.52
                status = 'Present' if random.random() < prob else 'Absent'
                attendance_records.append((att_id, s_id, c_id, att_date, status))
                att_id += 1

    cursor.executemany('''
        INSERT INTO attendance (id, student_id, course_id, date, status)
        VALUES (?, ?, ?, ?, ?);
    ''', attendance_records)

    print("Seeding Assignments & Submissions...")
    assignments_data = [
        (1, 1, 'Math Assignment 1: Discrete Calculus', 'Solve 10 problems on graph theory & relations.', 100, '2026-02-15'),
        (2, 2, 'Programming Assignment 1: Binary Search Tree', 'Implement BST insert, delete & traversals in C++.', 100, '2026-02-18'),
        (3, 3, 'Physics Lab Report: Optics Experiment', 'Submit lab report on laser diffraction.', 100, '2026-02-20'),
        (4, 4, 'DBMS Assignment 1: SQL Queries & Normalization', 'Write complex SQL queries for college schema.', 100, '2026-02-22'),
        (5, 5, 'Electronics Lab: Logic Gates Design', 'Design 4-bit adder circuit diagram.', 100, '2026-02-25'),
    ]
    cursor.executemany('''
        INSERT INTO assignments (id, course_id, title, description, max_marks, due_date)
        VALUES (?, ?, ?, ?, ?, ?);
    ''', assignments_data)

    # Submissions score profile mapping
    # Arun: 55%, Rahul: 90%, Priya: 68%, Varun: 75%, Sneha: 72%, Ananya: 82% (Math 45%), Karthik: 75%, Divya: 95%, Manoj: 42%, Swetha: 65%
    submissions = []
    sub_id = 1
    for a_id, c_id, _, _, max_m, _ in assignments_data:
        for s_id in range(1, 11):
            if s_id == 1: # Arun
                score = 52.0 if c_id == 1 else 57.0
            elif s_id == 2: # Rahul
                score = 92.0
            elif s_id == 3: # Priya
                score = 68.0
            elif s_id == 4: # Varun
                score = 76.0
            elif s_id == 5: # Sneha
                score = 70.0
            elif s_id == 6: # Ananya
                score = 45.0 if c_id == 1 else 90.0
            elif s_id == 7: # Karthik
                score = 75.0
            elif s_id == 8: # Divya
                score = 96.0
            elif s_id == 9: # Manoj
                score = 42.0
            elif s_id == 10: # Swetha
                score = 65.0

            submissions.append((sub_id, a_id, s_id, f"Submission content for assignment {a_id} by student {s_id}", score, "Good effort"))
            sub_id += 1

    cursor.executemany('''
        INSERT INTO assignment_submissions (id, assignment_id, student_id, submission_text, marks_obtained, feedback)
        VALUES (?, ?, ?, ?, ?, ?);
    ''', submissions)

    print("Seeding Examinations & Marks...")
    exams_data = [
        # Internal 1 Exams (Course 1 to 5)
        (1, 1, 'Math Mid-Term 1', 'Internal 1', 100, '2026-01-20'),
        (2, 2, 'Programming Mid-Term 1', 'Internal 1', 100, '2026-01-22'),
        (3, 3, 'Physics Mid-Term 1', 'Internal 1', 100, '2026-01-24'),
        (4, 4, 'DBMS Mid-Term 1', 'Internal 1', 100, '2026-01-26'),
        (5, 5, 'Electronics Mid-Term 1', 'Internal 1', 100, '2026-01-28'),

        # Internal 2 Exams (Course 1 to 5)
        (6, 1, 'Math Mid-Term 2', 'Internal 2', 100, '2026-02-10'),
        (7, 2, 'Programming Mid-Term 2', 'Internal 2', 100, '2026-02-12'),
        (8, 3, 'Physics Mid-Term 2', 'Internal 2', 100, '2026-02-14'),
        (9, 4, 'DBMS Mid-Term 2', 'Internal 2', 100, '2026-02-16'),
        (10, 5, 'Electronics Mid-Term 2', 'Internal 2', 100, '2026-02-18'),

        # Final Exams (Course 1 to 5)
        (11, 1, 'Mathematics Final Exam', 'Final Exam', 100, '2026-03-01'),
        (12, 2, 'Programming Final Exam', 'Final Exam', 100, '2026-03-03'),
        (13, 3, 'Physics Final Exam', 'Final Exam', 100, '2026-03-05'),
        (14, 4, 'DBMS Final Exam', 'Final Exam', 100, '2026-03-07'),
        (15, 5, 'Electronics Final Exam', 'Final Exam', 100, '2026-03-09'),

        # Previous Semester Exam (For Trend Detection)
        (16, 1, 'Previous Sem Math Exam', 'Previous Exam', 100, '2025-11-15'),
        (17, 2, 'Previous Sem Programming Exam', 'Previous Exam', 100, '2025-11-17'),
    ]
    cursor.executemany('''
        INSERT INTO examinations (id, course_id, exam_name, exam_type, max_marks, exam_date)
        VALUES (?, ?, ?, ?, ?, ?);
    ''', exams_data)

    marks_records = []
    m_id = 1

    for exam in exams_data:
        ex_id = exam[0]
        c_id = exam[1]
        ex_type = exam[3]

        for s_id in range(1, 11):
            # Target Exam Profiles
            if s_id == 1: # Arun (High Risk: Internal ~62%, Final ~51%, Weak Math 52%)
                if c_id == 1: # Math
                    mark = 52.0 if ex_type == 'Final Exam' else 58.0
                elif c_id == 2: # Programming
                    mark = 84.0 if ex_type == 'Final Exam' else 80.0
                elif c_id == 3: # Physics
                    mark = 67.0 if ex_type == 'Final Exam' else 65.0
                else:
                    mark = 51.0 if ex_type == 'Final Exam' else 60.0

            elif s_id == 2: # Rahul (Top Performer: ~95%)
                mark = random.choice([92.0, 94.0, 96.0, 98.0])

            elif s_id == 3: # Priya (Medium Risk: ~64% Internal, ~68% Final)
                mark = 64.0 if 'Internal' in ex_type else 68.0

            elif s_id == 4: # Varun (Improving Student: Previous 55%, Recent 78%)
                if ex_type == 'Previous Exam':
                    mark = 55.0
                else:
                    mark = 78.0

            elif s_id == 5: # Sneha (Declining Student: Previous 88%, Recent 62%)
                if ex_type == 'Previous Exam':
                    mark = 88.0
                else:
                    mark = 62.0

            elif s_id == 6: # Ananya (Weak Math: Math 45%, Programming 90%)
                if c_id == 1:
                    mark = 45.0
                elif c_id == 2:
                    mark = 92.0
                else:
                    mark = 78.0

            elif s_id == 7: # Karthik (Low Att 62%, Exam 82%)
                mark = 82.0

            elif s_id == 8: # Divya (Top Performer: ~94%)
                mark = 94.0

            elif s_id == 9: # Manoj (Severe At-Risk: ~45%)
                mark = 45.0 if ex_type == 'Final Exam' else 48.0

            elif s_id == 10: # Swetha (Medium Risk: ~66%)
                mark = 66.0

            marks_records.append((m_id, s_id, ex_id, mark))
            m_id += 1

    cursor.executemany('''
        INSERT INTO marks (id, student_id, exam_id, marks_obtained)
        VALUES (?, ?, ?, ?);
    ''', marks_records)

    # 11. Seed Notifications & Parent Risk Alerts
    notifications_data = [
        (1, 1, 'Academic High Risk Warning', 'Arun Kumar has been flagged as HIGH RISK (Score: 60.7%, Attendance: 61.0%). Attendance is below the mandatory 75% threshold.', 'HIGH_RISK', 'AI Engine', 'Parent & Student', '2026-02-10 10:00:00'),
        (2, 1, 'Mathematics Remedial Class Scheduled', 'Prof. John Smith assigned compulsory peer tutoring & remedial sessions for Mathematics for Computing.', 'ACADEMIC_INTERVENTION', 'Prof. John Smith', 'Parent & Student', '2026-02-12 14:30:00'),
        (3, 9, 'Critical Academic Risk & Parent Counseling Notice', 'Manoj S. overall score is 46.2%. Mandatory parent-teacher conference requested.', 'HIGH_RISK', 'AI Engine', 'Parent & Student', '2026-02-14 09:15:00'),
        (4, 3, 'Medium Risk Alert - Attendance Drop', 'Priya N. attendance dropped to 72.0% in Basic Electronics.', 'MEDIUM_RISK', 'AI Engine', 'Parent & Student', '2026-02-15 11:00:00')
    ]

    cursor.executemany('''
        INSERT INTO notifications (id, student_id, title, message, alert_type, sender_role, recipient, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    ''', notifications_data)

    # 12. Seed Interventions
    interventions_data = [
        (1, 1, 'Prof. John Smith', 'Mathematics Intensive Remedial Tutoring', 'Assigned 3 hours of weekly peer mentoring for Mathematics for Computing.', 'Attend Tuesday & Thursday tutoring sessions at 4:00 PM', 'Assigned', '2026-02-12 14:30:00'),
        (2, 9, 'Prof. John Smith', 'Parent-Teacher Academic Risk Conference', 'Mandatory academic counseling session regarding 46.2% overall performance.', 'Parent meeting scheduled for Friday 10:00 AM', 'In Progress', '2026-02-14 09:15:00'),
        (3, 3, 'Dr. Sarah Jenkins', 'Basic Electronics Lab Extra Sessions', 'Assigned lab practice sessions to improve practical understanding.', 'Complete 2 pending lab assignments', 'Assigned', '2026-02-15 11:00:00')
    ]

    cursor.executemany('''
        INSERT INTO interventions (id, student_id, teacher_name, title, description, action_required, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    ''', interventions_data)

    conn.commit()
    conn.close()
    print("Database seeded successfully with 10 detailed student profiles, notifications & interventions!")

if __name__ == '__main__':
    seed_database()

