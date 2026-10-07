import psycopg2
from config.database import get_db_connection

def reset_and_seed_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("Clearing existing database tables...")
    cursor.execute("""
        TRUNCATE TABLE grade, enrollment, classoffering, subject, teacher, student, gradingperiod RESTART IDENTITY CASCADE;
    """)

    print("Inserting Grading Periods...")
    periods = [
        ('PRD001', 'Midterm', '2025-08-15', '2025-10-15', '2025-2026', '1st Semester'),
        ('PRD002', 'Finals', '2025-10-16', '2025-12-18', '2025-2026', '1st Semester')
    ]
    cursor.executemany("""
        INSERT INTO gradingperiod (period_id, name, start_date, end_date, school_year, semester)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, periods)

    print("Inserting fresh Subjects...")
    subjects = [
        ('CS103', 'CSCC 103', 'Intermediate Programming', 'Object-Oriented Design & GUI Development', 3),
        ('IT101', 'ITEC 101', 'Introduction to Computing', 'Fundamentals of Hardware, Software, & Networks', 3),
        ('CS104', 'CSCC 104', 'Data Structures and Algorithms', 'Arrays, Linked Lists, Trees, Graphs, & Sorting', 3)
    ]
    cursor.executemany("""
        INSERT INTO subject (subject_id, subject_code, subject_name, description, units)
        VALUES (%s, %s, %s, %s, %s);
    """, subjects)

    print("Inserting fresh Students...")
    students = [
        ('2025-001', 'Andrae John', 'Almodiente', 'BSCS', 'andrae.almodiente@ndmu.edu.ph', 'Enrolled'),
        ('2025-002', 'Maria', 'Santos', 'BSCS', 'maria.santos@ndmu.edu.ph', 'Enrolled'),
        ('2025-003', 'Juan', 'Dela Cruz', 'BSIT', 'juan.delacruz@ndmu.edu.ph', 'Enrolled'),
        ('2025-004', 'Clarissa', 'Reyes', 'BSCS', 'clarissa.reyes@ndmu.edu.ph', 'Enrolled'),
        ('2025-005', 'Mark', 'Gonzales', 'BSIS', 'mark.gonzales@ndmu.edu.ph', 'Enrolled'),
        ('2025-006', 'Bea', 'Aquino', 'BSEMC', 'bea.aquino@ndmu.edu.ph', 'Enrolled'),
        ('2025-007', 'Joshua', 'Mendoza', 'BSIT', 'joshua.mendoza@ndmu.edu.ph', 'Enrolled')
    ]
    cursor.executemany("""
        INSERT INTO student (student_id, first_name, last_name, program, email, status)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, students)

    print("Inserting fresh Teachers...")
    teachers = [
        ('TCH001', 'Alan', 'Turing', 'alan.turing@ndmu.edu.ph', 'Computer Studies'),
        ('TCH002', 'Grace', 'Hopper', 'grace.hopper@ndmu.edu.ph', 'Computer Studies'),
        ('TCH003', 'Ada', 'Lovelace', 'ada.lovelace@ndmu.edu.ph', 'Information Technology')
    ]
    cursor.executemany("""
        INSERT INTO teacher (teacher_id, first_name, last_name, email, department)
        VALUES (%s, %s, %s, %s, %s);
    """, teachers)

    print("Inserting Class Offerings...")
    offerings = [
        ('OFF001', 'CSCC 103', 'MWF 09:00 AM - 10:30 AM', '2025-2026', '1st', 'TCH001', 'CS103'),
        ('OFF002', 'ITEC 101', 'TTH 01:00 PM - 02:30 PM', '2025-2026', '1st', 'TCH002', 'IT101'),
        ('OFF003', 'CSCC 104', 'MWF 01:00 PM - 02:30 PM', '2025-2026', '1st', 'TCH003', 'CS104')
    ]
    cursor.executemany("""
        INSERT INTO classoffering (offering_id, class_code, schedule, school_year, semester, teacher_id, subject_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """, offerings)

    print("Enrolling Students...")
    enrollments = [
        ('ENR001', '2025-001', 'OFF001', '2025-08-15', 'Enrolled'),
        ('ENR002', '2025-002', 'OFF001', '2025-08-15', 'Enrolled'),
        ('ENR003', '2025-004', 'OFF001', '2025-08-16', 'Enrolled'),
        ('ENR004', '2025-003', 'OFF002', '2025-08-16', 'Enrolled'),
        ('ENR005', '2025-007', 'OFF002', '2025-08-17', 'Enrolled'),
        ('ENR006', '2025-001', 'OFF003', '2025-08-15', 'Enrolled'),
        ('ENR007', '2025-005', 'OFF003', '2025-08-18', 'Enrolled'),
        ('ENR008', '2025-006', 'OFF003', '2025-08-18', 'Enrolled')
    ]
    cursor.executemany("""
        INSERT INTO enrollment (enrollment_id, student_id, offering_id, enrollment_date, status)
        VALUES (%s, %s, %s, %s, %s);
    """, enrollments)

    print("Inserting Grade Records...")
    # Uses 'PRD002' (Finals) to satisfy foreign key constraint fk_grade_period
    grades = [
        ('GRD001', 'ENR001', 'PRD002', 94.50, 'Passed', '2025-10-01'),
        ('GRD002', 'ENR002', 'PRD002', 88.25, 'Passed', '2025-10-01'),
        ('GRD003', 'ENR003', 'PRD002', 78.00, 'Passed', '2025-10-01'),
        ('GRD004', 'ENR004', 'PRD002', 91.00, 'Passed', '2025-10-01'),
        ('GRD005', 'ENR005', 'PRD002', 82.50, 'Passed', '2025-10-01'),
        ('GRD006', 'ENR006', 'PRD002', 96.00, 'Passed', '2025-10-01'),
        ('GRD007', 'ENR007', 'PRD002', 85.00, 'Passed', '2025-10-01'),
        ('GRD008', 'ENR008', 'PRD002', 89.75, 'Passed', '2025-10-01')
    ]
    cursor.executemany("""
        INSERT INTO grade (grade_id, enrollment_id, period_id, final_grade, remarks, date_encoded)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, grades)

    conn.commit()
    cursor.close()
    conn.close()
    print("Database reset and populated successfully!")

if __name__ == "__main__":
    reset_and_seed_database()