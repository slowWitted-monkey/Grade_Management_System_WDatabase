"""Add a clearly labeled, repeatable dataset for exercising the GUI and reports.

This script only inserts LOAD-TEST records. It never deletes or resets data.
Run it only against a development database such as MockDataBase2.
"""

import argparse
from datetime import date

from config.database import get_db_connection


def seed_load_test_data(student_count: int = 30) -> dict[str, int]:
    """Insert synthetic students, class data, enrollments, and component scores."""
    if not 1 <= student_count <= 100:
        raise ValueError("Student count must be between 1 and 100.")

    tag = date.today().strftime("%Y%m%d")
    student_ids = [f"LOAD-{tag}-{number:03d}" for number in range(1, student_count + 1)]
    teacher_ids = [f"LOAD-T{tag[-4:]}-{number:02d}" for number in range(1, 4)]
    programs = ("BSCS", "BSIT")
    departments = (
        "Computer Studies Department",
        "Information Technology Department",
        "Physical Education Department",
    )
    courses = (
        ("Programming Fundamentals", 3),
        ("Database Management", 3),
        ("Data Structures", 3),
        ("Web Development", 3),
        ("Computer Networks", 3),
        ("Physical Fitness", 2),
    )
    term_year, semester = "2026-2027", "1st"
    period_names = (("Load Test Midterm", 1), ("Load Test Finals", 2))
    components = (("Load Test Quiz", "Quiz", 30),
                  ("Load Test Assignment", "Assignment", 30),
                  ("Load Test Exam", "Exam", 40))

    conn = get_db_connection()
    counts = {"students": 0, "teachers": 0, "subjects": 0, "classes": 0,
              "enrollments": 0, "scores": 0}
    try:
        with conn.cursor() as cur:
            cur.executemany(
                """INSERT INTO student (student_id, first_name, last_name, email, program, year_level)
                   VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (student_id) DO NOTHING""",
                [(ident, f"Test{n:03d}", f"Learner{n:03d}",
                  f"load{tag}{n:03d}@example.test", programs[(n - 1) % len(programs)],
                  ((n - 1) % 4) + 1)
                 for n, ident in enumerate(student_ids, 1)],
            )
            counts["students"] = cur.rowcount

            cur.executemany(
                """INSERT INTO teacher (teacher_id, first_name, last_name, email, department)
                   VALUES (%s, %s, %s, %s, %s) ON CONFLICT (teacher_id) DO NOTHING""",
                [(ident, f"LoadTest{n}", f"Instructor{n}",
                  f"loadteacher{tag}{n}@example.test", departments[(n - 1) % len(departments)])
                 for n, ident in enumerate(teacher_ids, 1)],
            )
            counts["teachers"] = cur.rowcount

            subject_codes = [f"L{tag[-6:]}{n:02d}" for n in range(1, len(courses) + 1)]
            cur.executemany(
                """INSERT INTO subject (subject_code, subject_name, description, units)
                   VALUES (%s, %s, %s, %s) ON CONFLICT (subject_code) DO NOTHING""",
                [(code, name, "Synthetic load-test course", units)
                 for code, (name, units) in zip(subject_codes, courses)],
            )
            counts["subjects"] = cur.rowcount
            cur.execute("SELECT subject_id, subject_code FROM subject WHERE subject_code = ANY(%s)",
                        (subject_codes,))
            subject_ids = {code: ident for ident, code in cur.fetchall()}

            class_codes = [f"LOAD-{tag}-{n:02d}" for n in range(1, len(courses) + 1)]
            class_rows = []
            for n, (code, subject_code) in enumerate(zip(class_codes, subject_codes)):
                class_rows.append((code, subject_ids[subject_code], teacher_ids[n % len(teacher_ids)],
                                   f"LOAD-{n + 1:02d}", term_year, semester,
                                   "Mon/Wed 09:00-10:30", f"LOAD-{100 + n}"))
            cur.executemany(
                """INSERT INTO class_offering
                   (class_code, subject_id, teacher_id, section, school_year, semester, schedule, room)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                   ON CONFLICT (class_code) DO NOTHING""",
                class_rows,
            )
            counts["classes"] = cur.rowcount
            cur.execute("SELECT class_id, class_code FROM class_offering WHERE class_code = ANY(%s)",
                        (class_codes,))
            class_ids = {code: ident for ident, code in cur.fetchall()}

            cur.executemany(
                """INSERT INTO grading_period (name, period_order, school_year, semester)
                   VALUES (%s, %s, %s, %s)
                   ON CONFLICT (name, school_year, semester) DO NOTHING""",
                [(name, order, term_year, semester) for name, order in period_names],
            )
            cur.execute(
                "SELECT period_id, name FROM grading_period WHERE name = ANY(%s) AND school_year=%s AND semester=%s",
                ([name for name, _order in period_names], term_year, semester),
            )
            period_ids = {name: ident for ident, name in cur.fetchall()}

            component_rows = []
            for period_name, _order in period_names:
                for component_name, component_type, _weight in components:
                    component_rows.append((period_ids[period_name], component_name,
                                           component_type, 100, "Synthetic load-test component"))
            cur.executemany(
                """INSERT INTO grade_component (period_id, name, type, max_score, description)
                   VALUES (%s, %s, %s, %s, %s)
                   ON CONFLICT (period_id, name) DO NOTHING""",
                component_rows,
            )
            cur.execute("""SELECT gc.component_id, gp.name, gc.name FROM grade_component gc
                JOIN grading_period gp USING(period_id)
                WHERE gp.name = ANY(%s) AND gp.school_year=%s AND gp.semester=%s
                AND gc.name = ANY(%s)""",
                ([name for name, _order in period_names], term_year, semester,
                 [name for name, _type, _weight in components]))
            component_ids = {(period, component): ident
                             for ident, period, component in cur.fetchall()}

            enrollment_rows = [(ident, class_ids[code])
                               for ident in student_ids for code in class_codes]
            cur.executemany(
                """INSERT INTO enrollment (student_id, class_id)
                   VALUES (%s, %s) ON CONFLICT (student_id, class_id) DO NOTHING""",
                enrollment_rows,
            )
            counts["enrollments"] = cur.rowcount
            cur.execute("SELECT enrollment_id, student_id, class_id FROM enrollment WHERE student_id = ANY(%s)",
                        (student_ids,))
            enrollments = cur.fetchall()

            weight_rows = [(class_ids[code], component_ids[(period_name, component_name)], weight)
                           for code in class_codes
                           for period_name, _order in period_names
                           for component_name, _kind, weight in components]
            cur.executemany(
                """INSERT INTO grade_percentage (class_id, component_id, percentage)
                   VALUES (%s, %s, %s) ON CONFLICT (class_id, component_id) DO NOTHING""",
                weight_rows,
            )

            score_rows = []
            for enrollment_id, student_id, class_id in enrollments:
                student_number = int(student_id.rsplit("-", 1)[1])
                class_number = next(i for i, code in enumerate(class_codes, 1)
                                    if class_ids[code] == class_id)
                for period_name, period_order in period_names:
                    for component_index, (component_name, _kind, _weight) in enumerate(components, 1):
                        component_id = component_ids[(period_name, component_name)]
                        score = 58 + ((student_number * 7 + class_number * 5
                                       + period_order * 3 + component_index * 4) % 43)
                        score_rows.append((enrollment_id, component_id, score,
                                           "Synthetic load-test score"))
            cur.executemany(
                """INSERT INTO grade_component_score (enrollment_id, component_id, score, remarks)
                   VALUES (%s, %s, %s, %s)
                   ON CONFLICT (enrollment_id, component_id) DO NOTHING""",
                score_rows,
            )
            counts["scores"] = cur.rowcount
        conn.commit()
        return counts
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Add synthetic load-test rows without deleting existing records.")
    parser.add_argument("--students", type=int, default=30,
                        help="number of synthetic students to add (1-100; default: 30)")
    args = parser.parse_args()
    counts = seed_load_test_data(args.students)
    print("Load-test data added. No existing rows were deleted.")
    for name, count in counts.items():
        print(f"  {name.title()}: {count} new rows")
    print("Synthetic IDs use the LOAD- prefix; use your GUI search to find them.")


if __name__ == "__main__":
    main()

