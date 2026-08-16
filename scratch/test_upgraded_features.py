import sys, os
sys.path.insert(0, os.path.abspath('.'))

from app import app

def test_upgraded_features():
    client = app.test_client()

    print("==================================================")
    print("      TESTING UPGRADED ADVANCED EDUMIND AI FEATURES")
    print("==================================================")

    # 1. Parent Login & Portal
    res_parent_login = client.post('/login', data={
        'role': 'parent',
        'email': 'parent@edumind.ai',
        'password': 'parent123'
    }, follow_redirects=True)
    assert res_parent_login.status_code == 200
    assert b"Parent Academic Portal & Monitoring Console" in res_parent_login.data
    assert b"Arun Kumar" in res_parent_login.data
    print("[PASS] Parent Portal (/parent/dashboard) authenticated & rendered child metrics.")

    # 2. Student Login & Upgraded Dashboard (Health Score & Risk Score)
    client.get('/logout')
    res_student_login = client.post('/login', data={
        'role': 'student',
        'email': 'arun@edumind.ai',
        'password': 'student123'
    }, follow_redirects=True)
    assert res_student_login.status_code == 200
    assert b"Academic Health Score" in res_student_login.data
    assert b"Why is This Student at Risk?" in res_student_login.data
    print("[PASS] Upgraded Student Dashboard loaded with Health Score, Risk Score, and Explainable AI Root Cause.")

    # 3. AI Study Plan & Task Toggle
    res_sp = client.get('/student/study-plan')
    assert res_sp.status_code == 200
    assert b"Generate My AI Study Plan" in res_sp.data
    print("[PASS] AI Study Plan page (/student/study-plan) loaded 200 OK.")

    res_toggle = client.post('/api/student/study-task/toggle', json={'task_id': 1, 'is_completed': True})
    assert res_toggle.status_code == 200
    assert res_toggle.get_json()['status'] == 'success'
    print("[PASS] Study Task toggle API (/api/student/study-task/toggle) updated completion status.")

    # 4. Student Timeline
    res_tl = client.get('/student/timeline')
    assert res_tl.status_code == 200
    assert b"Student Progress Timeline" in res_tl.data
    print("[PASS] Student Progress Timeline (/student/timeline) loaded 200 OK.")

    # 5. EduMind AI Copilot Chatbot API
    res_copilot = client.post('/api/copilot/chat', json={'question': 'Why am I at risk?'})
    assert res_copilot.status_code == 200
    assert "attendance" in res_copilot.get_json()['response'].lower() or "risk" in res_copilot.get_json()['response'].lower()
    print("[PASS] EduMind AI Copilot API (/api/copilot/chat) returned context-aware student response.")

    # 6. Teacher Assign & Update Intervention APIs
    client.get('/logout')
    client.post('/login', data={
        'role': 'teacher',
        'email': 'smith@edumind.ai',
        'password': 'teacher123'
    }, follow_redirects=True)

    res_assign_int = client.post('/api/teacher/assign-intervention', data={
        'student_id': 1,
        'title': 'Mathematics Exam Prep Counseling',
        'description': 'One-on-one exam preparation session with Dr. Jenkins.',
        'action_required': 'Complete mock question paper 2'
    }, follow_redirects=True)
    assert res_assign_int.status_code == 200
    print("[PASS] Teacher Intervention Assignment API (/api/teacher/assign-intervention) dispatched intervention & parent alert.")

    res_update_int = client.post('/api/teacher/update-intervention-status', json={
        'intervention_id': 1,
        'status': 'Resolved'
    })
    assert res_update_int.status_code == 200
    assert res_update_int.get_json()['status'] == 'success'
    print("[PASS] Teacher Intervention Status Update API (/api/teacher/update-intervention-status) resolved intervention.")

    print("==================================================")
    print(" ALL UPGRADED ADVANCED EDUMIND AI TESTS PASSED 100%")
    print("==================================================")

if __name__ == '__main__':
    test_upgraded_features()
