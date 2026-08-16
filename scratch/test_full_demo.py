import sys, os
sys.path.insert(0, os.path.abspath('.'))

from app import app

def run_hackathon_demo_flow():
    client = app.test_client()

    print("==================================================")
    print("      EDUMIND AI - HACKATHON E2E DEMO VERIFICATION")
    print("==================================================")

    # 1. Landing Page
    res_land = client.get('/')
    assert res_land.status_code == 200
    assert b"EduMind AI" in res_land.data
    assert b"Unique" in res_land.data
    print("[PASS] Step 1: Landing Page loaded perfectly with Team Unique branding.")

    # 2. Login as Student (Arun Kumar - High Risk)
    res_s_login = client.post('/login', data={
        'role': 'student',
        'email': 'arun@edumind.ai',
        'password': 'student123'
    }, follow_redirects=True)
    assert res_s_login.status_code == 200
    assert b"Arun Kumar" in res_s_login.data
    assert b"HIGH RISK" in res_s_login.data
    print("[PASS] Step 2: Student Login (Arun Kumar) authenticated.")

    # 3. Verify Student Dashboard AI Data
    assert b"Mathematics for Computing" in res_s_login.data
    assert b"AI Academic Insight" in res_s_login.data
    print("[PASS] Step 3 & 4: Student Dashboard displayed scores, risk level (HIGH RISK), and weak subjects.")

    # 4. Test AI Chatbot REST API
    res_chat1 = client.post('/api/student/ai-chat', json={'question': 'Why is my performance low?'})
    assert res_chat1.status_code == 200
    reply1 = res_chat1.get_json()['response']
    assert "attendance" in reply1.lower() or "risk" in reply1.lower()
    print(f"[PASS] Step 5: AI Assistant Q1 Reply: '{reply1}'")

    res_chat2 = client.post('/api/student/ai-chat', json={'question': 'What should I improve first?'})
    assert res_chat2.status_code == 200
    reply2 = res_chat2.get_json()['response']
    assert "priority" in reply2.lower() or "focus" in reply2.lower()
    print(f"[PASS] Step 6: AI Assistant Q2 Reply: '{reply2}'")

    # 5. Test Student Sub-Pages
    assert client.get('/student/courses').status_code == 200
    assert client.get('/student/attendance').status_code == 200
    assert client.get('/student/assignments').status_code == 200
    assert client.get('/student/results').status_code == 200
    assert client.get('/student/ai-recommendations').status_code == 200
    print("[PASS] Step 7: All Student sub-pages (/courses, /attendance, /assignments, /results, /ai-recommendations) loaded 200 OK.")

    # 6. Logout
    client.get('/logout')

    # 7. Login as Teacher (Prof. Smith)
    res_t_login = client.post('/login', data={
        'role': 'teacher',
        'email': 'smith@edumind.ai',
        'password': 'teacher123'
    }, follow_redirects=True)
    assert res_t_login.status_code == 200
    assert b"Prof. John Smith" in res_t_login.data
    assert b"High-Risk Students" in res_t_login.data
    print("[PASS] Step 8: Teacher Login (Prof. Smith) authenticated & dashboard rendered.")

    # 8. Open Student Detailed AI Analysis
    res_detail = client.get('/teacher/student/1/ai-analysis')
    assert res_detail.status_code == 200
    assert b"Detailed AI Diagnosis: Arun Kumar" in res_detail.data
    print("[PASS] Step 9: Teacher viewed Arun's detailed AI analysis page.")

    # 9. Teacher Sub-Pages
    assert client.get('/teacher/students').status_code == 200
    assert client.get('/teacher/attendance').status_code == 200
    assert client.get('/teacher/assignments').status_code == 200
    assert client.get('/teacher/examinations').status_code == 200
    print("[PASS] Step 10: All Teacher sub-pages (/students, /attendance, /assignments, /examinations) loaded 200 OK.")

    # 10. Logout & Login as Admin
    client.get('/logout')
    res_a_login = client.post('/login', data={
        'role': 'admin',
        'email': 'admin@edumind.ai',
        'password': 'admin123'
    }, follow_redirects=True)
    assert res_a_login.status_code == 200
    assert b"Institution Intelligence Console" in res_a_login.data
    print("[PASS] Step 11: Admin Login authenticated & Overview rendered.")

    # 11. Admin Sub-Pages
    assert client.get('/admin/management').status_code == 200
    assert client.get('/admin/analytics').status_code == 200
    print("[PASS] Step 12: Admin management & AI analytics report loaded 200 OK.")

    print("\n==================================================")
    print(" ALL HACKATHON DEMO STEPS PASSED SUCCESSFULLY")
    print("==================================================")

if __name__ == '__main__':
    run_hackathon_demo_flow()
