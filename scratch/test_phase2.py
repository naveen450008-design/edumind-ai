import sys, os
sys.path.insert(0, os.path.abspath('.'))
from database.db import get_db_connection

def test_phase2():
    conn = get_db_connection()
    cursor = conn.cursor()

    tables = ['students', 'teachers', 'courses', 'classes', 'enrollments',
              'attendance', 'assignments', 'assignment_submissions', 'examinations', 'marks']
    
    print("--- Database Verification ---")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        print(f"Table '{table}': {count} rows")
        assert count > 0, f"Table {table} is empty!"
    
    # Check Arun Kumar (Student ID 1) metrics query
    cursor.execute("""
        SELECT s.name, s.email, c.class_name
        FROM students s
        JOIN classes c ON s.class_id = c.id
        WHERE s.id = 1;
    """)
    arun = cursor.fetchone()
    assert arun['name'] == 'Arun Kumar'
    print(f"[PASS] Queried Student: {arun['name']} ({arun['email']}) in {arun['class_name']}")

    conn.close()
    print("[PASS] Phase 2 DB Seeding & Verification Passed!")

if __name__ == '__main__':
    test_phase2()
