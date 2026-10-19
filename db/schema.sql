-- db/schema.sql

-- Reset schema cleanly if setting up fresh
DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS grade CASCADE;
DROP TABLE IF EXISTS enrollment CASCADE;
DROP TABLE IF EXISTS classoffering CASCADE;
DROP TABLE IF EXISTS teacher CASCADE;
DROP TABLE IF EXISTS subject CASCADE;
DROP TABLE IF EXISTS student CASCADE;
DROP TABLE IF EXISTS gradingperiod CASCADE;

-- Master Tables
CREATE TABLE student (
    student_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    program VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    year_level INT DEFAULT 1,
    status VARCHAR(20) DEFAULT 'Active'
);

CREATE TABLE teacher (
    teacher_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    department VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'Active'
);

CREATE TABLE subject (
    subject_id SERIAL PRIMARY KEY,
    subject_code VARCHAR(20) NOT NULL UNIQUE,
    subject_name VARCHAR(100) NOT NULL,
    description TEXT,
    units INT NOT NULL CHECK (units > 0)
);

CREATE TABLE gradingperiod (
    period_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    start_date DATE,
    end_date DATE,
    school_year VARCHAR(20),
    semester VARCHAR(30)
);

-- Transactional & Association Tables
CREATE TABLE classoffering (
    offering_id VARCHAR(20) PRIMARY KEY,
    class_code VARCHAR(50) NOT NULL,
    schedule VARCHAR(100),
    school_year VARCHAR(20),
    semester VARCHAR(30),
    teacher_id VARCHAR(20) REFERENCES teacher(teacher_id) ON DELETE RESTRICT,
    subject_id INT REFERENCES subject(subject_id) ON DELETE RESTRICT
);

CREATE TABLE enrollment (
    enrollment_id VARCHAR(20) PRIMARY KEY,
    student_id VARCHAR(20) REFERENCES student(student_id) ON DELETE RESTRICT,
    offering_id VARCHAR(20) REFERENCES classoffering(offering_id) ON DELETE RESTRICT,
    enrollment_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'Enrolled',
    CONSTRAINT unique_student_offering UNIQUE (student_id, offering_id)
);

CREATE TABLE grade (
    grade_id VARCHAR(20) PRIMARY KEY,
    enrollment_id VARCHAR(20) REFERENCES enrollment(enrollment_id) ON DELETE CASCADE,
    period_id VARCHAR(20) REFERENCES gradingperiod(period_id),
    midterm_grade NUMERIC(5,2),
    finals_grade NUMERIC(5,2),
    overall_grade NUMERIC(5,2),
    midterm_equiv NUMERIC(3,2),
    final_equiv NUMERIC(3,2),
    remarks VARCHAR(100),
    date_encoded DATE DEFAULT CURRENT_DATE,
    CONSTRAINT unique_enrollment_period UNIQUE (enrollment_id, period_id)
);

-- Audit Logging Table
CREATE TABLE audit_log (
    log_id SERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    record_id VARCHAR(50) NOT NULL,
    action VARCHAR(10) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_by VARCHAR(50) DEFAULT 'tester',
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);