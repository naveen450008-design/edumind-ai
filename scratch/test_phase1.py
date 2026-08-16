import sys, os
sys.path.insert(0, os.path.abspath('.'))
from app import app

def test_phase1():
    client = app.test_client()
    
    # Test index page
    res_index = client.get('/')
    assert res_index.status_code == 200, f"Expected 200 on /, got {res_index.status_code}"
    assert b"EduMind AI" in res_index.data
    assert b"SynaptiX" in res_index.data
    print("[PASS] Landing page (/) tested successfully!")

    # Test login page
    res_login = client.get('/login')
    assert res_login.status_code == 200, f"Expected 200 on /login, got {res_login.status_code}"
    assert b"Select User Role" in res_login.data
    print("[PASS] Login page (/login) tested successfully!")

    # Test login POST
    res_post = client.post('/login', data={
        'role': 'student',
        'email': 'arun@edumind.ai',
        'password': 'password123'
    }, follow_redirects=True)
    assert res_post.status_code == 200
    assert b"Student Dashboard (Phase 1 Ready)" in res_post.data
    print("[PASS] Login POST & session redirect tested successfully!")

if __name__ == '__main__':
    test_phase1()
    print("Phase 1 Tests Passed Completely!")
