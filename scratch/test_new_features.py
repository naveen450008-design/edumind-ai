import sys, os
sys.path.insert(0, os.path.abspath('.'))

from app import app

def test_new_features():
    client = app.test_client()

    print("==================================================")
    print("      TESTING NEW EDUMIND AI FEATURES")
    print("==================================================")

    # 1. Login as Student (Arun Kumar)
    res_login = client.post('/login', data={
        'role': 'student',
        'email': 'arun@edumind.ai',
        'password': 'student123'
    }, follow_redirects=True)
    assert res_login.status_code == 200
    print("[PASS] Student authentication successful.")

    # 2. Test Export Report Route
    res_report = client.get('/student/export-report')
    assert res_report.status_code == 200
    assert b"Official Academic Diagnostic & Risk Evaluation Report" in res_report.data
    assert b"Arun Kumar" in res_report.data
    print("[PASS] Student Printable/Export Report page loads 200 OK.")

    # 3. Test Grade Predictor Route & API
    res_pred_page = client.get('/student/grade-predictor')
    assert res_pred_page.status_code == 200
    assert b"What-If Grade & Risk Predictor" in res_pred_page.data
    print("[PASS] Grade Predictor page loads 200 OK.")

    res_api = client.post('/api/student/predict-grade', json={
        'att': 85.0,
        'assign': 80.0,
        'internal': 75.0,
        'final': 80.0
    })
    assert res_api.status_code == 200
    data = res_api.get_json()
    assert data['status'] == 'success'
    pred = data['prediction']
    # Formula: 85*0.2 + 80*0.2 + 75*0.2 + 80*0.4 = 17 + 16 + 15 + 32 = 80.0
    assert pred['predicted_overall'] == 80.0
    print("DEBUG PREDICTED RISK:", pred['predicted_risk'])
    assert pred['predicted_risk']['risk_code'] in ['low', 'medium', 'high']
    print(f"[PASS] Grade Predictor API simulation: 85% att + 80% final -> Predicted Score {pred['predicted_overall']}%, Risk Tier {pred['predicted_risk']['status_label']}.")

    # 4. Test Student Notifications Inbox
    res_notif = client.get('/student/notifications')
    assert res_notif.status_code == 200
    assert b"Parent & Student Risk Alerts Inbox" in res_notif.data
    assert b"Academic High Risk Warning" in res_notif.data
    print("[PASS] Student Risk Alerts Inbox page loads 200 OK with seeded notifications.")

    # 5. Logout & Login as Teacher (Prof. Smith)
    client.get('/logout')
    client.post('/login', data={
        'role': 'teacher',
        'email': 'smith@edumind.ai',
        'password': 'teacher123'
    }, follow_redirects=True)

    # 6. Test Teacher Export Report for Student 1
    res_t_report = client.get('/teacher/student/1/export-report')
    assert res_t_report.status_code == 200
    assert b"Arun Kumar" in res_t_report.data
    print("[PASS] Teacher viewed Arun's printable diagnostic report.")

    # 7. Test Teacher Dispatch Notification
    res_t_notif_get = client.get('/teacher/notifications')
    assert res_t_notif_get.status_code == 200

    res_t_dispatch = client.post('/teacher/notifications', data={
        'student_id': 1,
        'alert_type': 'ACADEMIC_INTERVENTION',
        'title': 'Compulsory Peer Tutoring Scheduled',
        'message': 'Arun has been assigned 3 hours of weekly math peer mentoring.'
    }, follow_redirects=True)
    assert res_t_dispatch.status_code == 200
    assert b"Compulsory Peer Tutoring Scheduled" in res_t_dispatch.data
    print("[PASS] Teacher successfully dispatched a risk alert & parent intervention notice.")

    print("==================================================")
    print(" ALL NEW FEATURE TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == '__main__':
    test_new_features()
