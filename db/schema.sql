-- Student Grade Management System
-- Safe to run repeatedly on an empty/new project database. It does not erase data.

CREATE TABLE IF NOT EXISTS student (
    student_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL CHECK (btrim(first_name) <> ''),
    last_name VARCHAR(50) NOT NULL CHECK (btrim(last_name) <> ''),
    email VARCHAR(100),
    program VARCHAR(30) NOT NULL CHECK (btrim(program) <> ''),
    year_level SMALLINT NOT NULL DEFAULT 1 CHECK (year_level BETWEEN 1 AND 8),
    status VARCHAR(20) NOT NULL DEFAULT 'Active'
);

CREATE TABLE IF NOT EXISTS teacher (
    teacher_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL CHECK (btrim(first_name) <> ''),
    last_name VARCHAR(50) NOT NULL CHECK (btrim(last_name) <> ''),
    email VARCHAR(100),
    department VARCHAR(100) NOT NULL CHECK (btrim(department) <> ''),
    status VARCHAR(20) NOT NULL DEFAULT 'Active'
);

CREATE TABLE IF NOT EXISTS subject (
    subject_id SERIAL PRIMARY KEY,
    subject_code VARCHAR(20) NOT NULL UNIQUE CHECK (btrim(subject_code) <> ''),
    subject_name VARCHAR(100) NOT NULL CHECK (btrim(subject_name) <> ''),
    description TEXT,
    units SMALLINT NOT NULL CHECK (units > 0)
);

CREATE TABLE IF NOT EXISTS class_offering (
    class_id SERIAL PRIMARY KEY,
    class_code VARCHAR(50) NOT NULL UNIQUE,
    subject_id INTEGER NOT NULL REFERENCES subject(subject_id) ON DELETE RESTRICT,
    teacher_id VARCHAR(20) NOT NULL REFERENCES teacher(teacher_id) ON DELETE RESTRICT,
    section VARCHAR(20) NOT NULL CHECK (btrim(section) <> ''),
    school_year VARCHAR(20) NOT NULL CHECK (btrim(school_year) <> ''),
    semester VARCHAR(30) NOT NULL CHECK (btrim(semester) <> ''),
    schedule VARCHAR(100),
    room VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS enrollment (
    enrollment_id SERIAL PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL REFERENCES student(student_id) ON DELETE RESTRICT,
    class_id INTEGER NOT NULL REFERENCES class_offering(class_id) ON DELETE RESTRICT,
    enroll_date DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'Enrolled',
    CONSTRAINT unique_student_class UNIQUE (student_id, class_id)
);

CREATE TABLE IF NOT EXISTS grading_period (
    period_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL CHECK (btrim(name) <> ''),
    period_order SMALLINT NOT NULL CHECK (period_order > 0),
    start_date DATE,
    end_date DATE,
    school_year VARCHAR(20) NOT NULL,
    semester VARCHAR(30) NOT NULL,
    CONSTRAINT unique_period_term UNIQUE (name, school_year, semester),
    CHECK (start_date IS NULL OR end_date IS NULL OR start_date <= end_date)
);

CREATE TABLE IF NOT EXISTS grade_component (
    component_id SERIAL PRIMARY KEY,
    period_id INTEGER NOT NULL REFERENCES grading_period(period_id) ON DELETE RESTRICT,
    name VARCHAR(100) NOT NULL CHECK (btrim(name) <> ''),
    type VARCHAR(30) NOT NULL,
    max_score NUMERIC(8,2) NOT NULL CHECK (max_score > 0),
    description TEXT,
    CONSTRAINT unique_component_period UNIQUE (period_id, name)
);

CREATE TABLE IF NOT EXISTS grade_percentage (
    percentage_id SERIAL PRIMARY KEY,
    class_id INTEGER NOT NULL REFERENCES class_offering(class_id) ON DELETE RESTRICT,
    component_id INTEGER NOT NULL REFERENCES grade_component(component_id) ON DELETE RESTRICT,
    percentage NUMERIC(5,2) NOT NULL CHECK (percentage >= 0 AND percentage <= 100),
    CONSTRAINT unique_class_component_weight UNIQUE (class_id, component_id)
);

CREATE TABLE IF NOT EXISTS grade_component_score (
    score_id SERIAL PRIMARY KEY,
    enrollment_id INTEGER NOT NULL REFERENCES enrollment(enrollment_id) ON DELETE RESTRICT,
    component_id INTEGER NOT NULL REFERENCES grade_component(component_id) ON DELETE RESTRICT,
    score NUMERIC(8,2) NOT NULL CHECK (score >= 0),
    remarks TEXT,
    date_recorded DATE NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT unique_enrollment_component_score UNIQUE (enrollment_id, component_id)
);

CREATE TABLE IF NOT EXISTS grade (
    grade_id SERIAL PRIMARY KEY,
    enrollment_id INTEGER NOT NULL UNIQUE REFERENCES enrollment(enrollment_id) ON DELETE RESTRICT,
    midterm_grade NUMERIC(5,2),
    finals_grade NUMERIC(5,2),
    overall_grade NUMERIC(5,2),
    midterm_equiv NUMERIC(3,2),
    final_equiv NUMERIC(3,2),
    remarks VARCHAR(100),
    date_encoded DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS audit_log (
    log_id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    record_id VARCHAR(50) NOT NULL,
    action VARCHAR(10) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_by VARCHAR(50) NOT NULL DEFAULT 'tester',
    changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_enrollment_class_status ON enrollment(class_id, status);
CREATE INDEX IF NOT EXISTS ix_grade_score_enrollment ON grade_component_score(enrollment_id);
CREATE INDEX IF NOT EXISTS ix_audit_changed_at ON audit_log(changed_at);
