import sys, os
sys.path.insert(0, os.path.abspath('.'))
from app import app

def test_phase3():
    client = app.test_client()

    # Test login as Arun Kumar (Student)
    res_arun = client.post('/login', data={
        'role': 'student',
        'email': 'arun@edumind.ai',
        'password': 'student123'
    }, follow_redirects=True)
    assert res_arun.status_code == 200
    assert b"Arun Kumar" in res_arun.data
    print("[PASS] Authenticated Arun Kumar (Student)")

    # Test login as Prof. Smith (Teacher)
    res_teacher = client.post('/login', data={
        'role': 'teacher',
        'email': 'smith@edumind.ai',
        'password': 'teacher123'
    }, follow_redirects=True)
    assert res_teacher.status_code == 200
    assert b"Prof. John Smith" in res_teacher.data
    print("[PASS] Authenticated Prof. John Smith (Teacher)")

    # Test login as Admin
    res_admin = client.post('/login', data={
        'role': 'admin',
        'email': 'admin@edumind.ai',
        'password': 'admin123'
    }, follow_redirects=True)
    assert res_admin.status_code == 200
    assert b"System Administrator" in res_admin.data
    print("[PASS] Authenticated System Administrator (Admin)")

if __name__ == '__main__':
    test_phase3()
    print("Phase 3 Role Authentication Passed!")
