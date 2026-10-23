"""Populate the professor's CRUD checklist fixture for GUI/report exploration.

This script only writes the named checklist records. It never deletes rows.
It creates the checklist's final expected state, so it is for exploration and
report testing, not for scoring the live checklist's create/update scenarios.
"""

import argparse
from datetime import date

from config.database import get_db_connection
from repository.grade_repository import GradeRepository
from service.grading_service import GradingService


SCHOOL_YEAR = "2026-2027"
SEMESTER = "1st"

STUDENTS = [
    ("2026-0001", "Juan", "Dela Cruz", "BSCS", 2),
    ("2026-0002", "Pedro", "Reyes", "BSCS", 2),
    ("2026-0003", "Ana", "Garcia", "BSCS", 2),
    ("2026-0098", "Carlo", "Mendoza", "BSIT", 1),
    ("2026-0004", "Kevin", "O'Brien", "BSIT", 1),
]

TEACHERS = [
    ("T-1001", "Maria", "Santos", "Information Technology Department"),
    ("T-1002", "Jose", "Ramos", "Physical Education Department"),
]

SUBJECTS = [
    ("CSPC 103", "Object Oriented Programming",
     "Object-oriented analysis, design and programming in Java", 3),
    ("PATHFIT 3", "Physical Activity Towards Health and Fitness 3", None, 2),
]

CLASSES = [
    ("CSPC103-A", "CSPC 103", "T-1001", "A", "TTh 1:00–2:30", "CS-202"),
    ("PATHFIT3-A", "PATHFIT 3", "T-1002", "A", "TTh 3:00–5:00", "Gym"),
]

PERIODS = [("Midterm", 1), ("Finals", 2)]
COMPONENTS = [
    ("Midterm", "Midterm Quiz", "Quiz", 50),
    ("Midterm", "Midterm Laboratory/Project", "Laboratory", 100),
    ("Midterm", "Midterm Examination", "Exam", 100),
    ("Finals", "Final Quiz", "Quiz", 50),
    ("Finals", "Final Laboratory/Project", "Laboratory", 100),
    ("Finals", "Final Examination", "Exam", 100),
]

# Checklist's final state after GR-03: CSPC 103 midterm weights have been
# recalculated to 30/30/40; the other periods use 20/30/50.
WEIGHTS = {
    "CSPC103-A": {"Midterm": (30, 30, 40), "Finals": (20, 30, 50)},
    "PATHFIT3-A": {"Midterm": (20, 30, 50), "Finals": (20, 30, 50)},
}

# Raw scores are the checklist values after Juan's 57 -> 75 correction and
# Ana's deleted/re-entered Final Quiz score. Carlo is intentionally not enrolled.
SCORES = {
    ("2026-0001", "CSPC103-A"): (40, 90, 75, 45, 85, 80),
    ("2026-0002", "CSPC103-A"): (20, 60, 55, 30, 70, 65),
    ("2026-0003", "CSPC103-A"): (50, 100, 100, 48, 95, 92),
    ("2026-0001", "PATHFIT3-A"): (45, 90, 90, 45, 90, 90),
}

def seed_load_test_data(extra_students: int = 0) -> dict[str, int]:
    """Insert or refresh the exact checklist fixture and optional extra students."""
    if not 0 <= extra_students <= 100:
        raise ValueError("Extra student count must be between 0 and 100.")

    conn = get_db_connection()
    grade_repo = GradeRepository()
    counts = {"students": 0, "teachers": 0, "subjects": 0, "classes": 0,
              "enrollments": 0, "components": 0, "weights": 0,
              "scores": 0, "grades": 0}
    try:
        with conn.cursor() as cur:
            today = date.today()
            student_rows = [(sid, first, last, None, program, year, "Active")
                            for sid, first, last, program, year in STUDENTS]
            student_rows.extend(
                (f"LOAD-{today:%Y%m%d}-{n:03d}", f"Test{n:03d}", f"Learner{n:03d}",
                 f"load{today:%Y%m%d}{n:03d}@example.test", "BSCS" if n % 2 else "BSIT",
                 (n % 4) + 1, "Active")
                for n in range(1, extra_students + 1)
            )
            cur.executemany(
                """INSERT INTO student (student_id, first_name, last_name, email, program, year_level, status)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)
                   ON CONFLICT (student_id) DO UPDATE SET first_name=EXCLUDED.first_name,
                   last_name=EXCLUDED.last_name, email=EXCLUDED.email, program=EXCLUDED.program,
                   year_level=EXCLUDED.year_level, status=EXCLUDED.status""",
                student_rows,
            )
            counts["students"] = cur.rowcount

            cur.executemany(
                """INSERT INTO teacher (teacher_id, first_name, last_name, department, status)
                   VALUES (%s,%s,%s,%s,'Active')
                   ON CONFLICT (teacher_id) DO UPDATE SET first_name=EXCLUDED.first_name,
                   last_name=EXCLUDED.last_name, department=EXCLUDED.department, status=EXCLUDED.status""",
                TEACHERS,
            )
            counts["teachers"] = cur.rowcount

            cur.executemany(
                """INSERT INTO subject (subject_code, subject_name, description, units)
                   VALUES (%s,%s,%s,%s)
                   ON CONFLICT (subject_code) DO UPDATE SET subject_name=EXCLUDED.subject_name,
                   description=EXCLUDED.description, units=EXCLUDED.units""",
                SUBJECTS,
            )
            counts["subjects"] = cur.rowcount
            cur.execute("SELECT subject_id, subject_code FROM subject WHERE subject_code = ANY(%s)",
                        ([row[0] for row in SUBJECTS],))
            subject_ids = {code: ident for ident, code in cur.fetchall()}

            class_rows = [(code, subject_ids[subject_code], teacher_id, section, SCHOOL_YEAR,
                           SEMESTER, schedule, room)
                          for code, subject_code, teacher_id, section, schedule, room in CLASSES]
            cur.executemany(
                """INSERT INTO class_offering
                   (class_code, subject_id, teacher_id, section, school_year, semester, schedule, room)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                   ON CONFLICT (class_code) DO UPDATE SET subject_id=EXCLUDED.subject_id,
                   teacher_id=EXCLUDED.teacher_id, section=EXCLUDED.section,
                   school_year=EXCLUDED.school_year, semester=EXCLUDED.semester,
                   schedule=EXCLUDED.schedule, room=EXCLUDED.room""",
                class_rows,
            )
            counts["classes"] = cur.rowcount
            cur.execute("SELECT class_id, class_code FROM class_offering WHERE class_code = ANY(%s)",
                        ([row[0] for row in CLASSES],))
            class_ids = {code: ident for ident, code in cur.fetchall()}

            cur.executemany(
                """INSERT INTO enrollment (student_id, class_id, enroll_date, status)
                   VALUES (%s,%s,%s,'Enrolled')
                   ON CONFLICT (student_id, class_id) DO UPDATE SET enroll_date=EXCLUDED.enroll_date,
                   status=EXCLUDED.status""",
                [(student_id, class_ids[class_code], today)
                 for student_id, class_code in (
                     ("2026-0001", "CSPC103-A"), ("2026-0002", "CSPC103-A"),
                     ("2026-0003", "CSPC103-A"), ("2026-0001", "PATHFIT3-A"))],
            )
            counts["enrollments"] = cur.rowcount
            fixture_enrollments = [
                ("2026-0001", class_ids["CSPC103-A"]),
                ("2026-0002", class_ids["CSPC103-A"]),
                ("2026-0003", class_ids["CSPC103-A"]),
                ("2026-0001", class_ids["PATHFIT3-A"]),
            ]
            enrollment_predicate = " OR ".join(
                "(student_id=%s AND class_id=%s)" for _ in fixture_enrollments)
            cur.execute("SELECT enrollment_id, student_id, class_id FROM enrollment WHERE " + enrollment_predicate,
                        tuple(value for pair in fixture_enrollments for value in pair))
            enrollment_ids = {(student_id, class_id): enrollment_id
                              for enrollment_id, student_id, class_id in cur.fetchall()}

            cur.executemany(
                """INSERT INTO grading_period (name, period_order, school_year, semester)
                   VALUES (%s,%s,%s,%s)
                   ON CONFLICT (name, school_year, semester) DO UPDATE
                   SET period_order=EXCLUDED.period_order""",
                [(name, order, SCHOOL_YEAR, SEMESTER) for name, order in PERIODS],
            )
            cur.execute("""SELECT period_id, name FROM grading_period
                WHERE name = ANY(%s) AND school_year=%s AND semester=%s""",
                ([name for name, _ in PERIODS], SCHOOL_YEAR, SEMESTER))
            period_ids = {name: ident for ident, name in cur.fetchall()}

            cur.executemany(
                """INSERT INTO grade_component (period_id, name, type, max_score)
                   VALUES (%s,%s,%s,%s)
                   ON CONFLICT (period_id, name) DO UPDATE SET type=EXCLUDED.type,
                   max_score=EXCLUDED.max_score""",
                [(period_ids[period], name, kind, maximum)
                 for period, name, kind, maximum in COMPONENTS],
            )
            counts["components"] = cur.rowcount
            cur.execute("""SELECT gc.component_id, gp.name, gc.name FROM grade_component gc
                JOIN grading_period gp USING(period_id)
                WHERE gp.name = ANY(%s) AND gp.school_year=%s AND gp.semester=%s
                AND gc.name = ANY(%s)""",
                ([name for name, _ in PERIODS], SCHOOL_YEAR, SEMESTER,
                 [name for _period, name, _kind, _max in COMPONENTS]))
            component_ids = {(period, name): ident for ident, period, name in cur.fetchall()}

            weight_rows = []
            for class_code, periods in WEIGHTS.items():
                for period, percent_values in periods.items():
                    for component, percentage in zip(
                            [row[1] for row in COMPONENTS if row[0] == period], percent_values):
                        weight_rows.append((class_ids[class_code], component_ids[(period, component)], percentage))
            cur.executemany(
                """INSERT INTO grade_percentage (class_id, component_id, percentage)
                   VALUES (%s,%s,%s)
                   ON CONFLICT (class_id, component_id) DO UPDATE SET percentage=EXCLUDED.percentage""",
                weight_rows,
            )
            counts["weights"] = cur.rowcount

            score_rows = []
            for (student_id, class_code), values in SCORES.items():
                enrollment_id = enrollment_ids[(student_id, class_ids[class_code])]
                for (_period, component, _kind, _maximum), score in zip(COMPONENTS, values):
                    score_rows.append((enrollment_id, period_ids[_period],
                                       component_ids[(_period, component)], score))

        conn.commit()
        conn.close()

        # Use the application's validated persistence paths so seeded scores
        # and calculated grades also create genuine audit entries.
        for enrollment_id, period_id, component_id, score in score_rows:
            grade_repo.save_component_score(
                enrollment_id, period_id, component_id, score, changed_by="CRUD checklist seed")
        counts["scores"] = len(score_rows)

        grading_service = GradingService(grade_repo)
        for (student_id, class_code), _scores in SCORES.items():
            enrollment_id = enrollment_ids[(student_id, class_ids[class_code])]
            grading_service.calculate_and_save_period_grade(
                enrollment_id=enrollment_id, class_id=class_ids[class_code])
        counts["grades"] = len(SCORES)
        return counts
    except Exception:
        if not conn.closed:
            conn.rollback()
        raise
    finally:
        if not conn.closed:
            conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed the CRUD checklist's final report-ready records (no rows are deleted).")
    parser.add_argument("--extra-students", type=int, default=0,
                        help="also add 0-100 un-enrolled LOAD- students for list/search testing")
    args = parser.parse_args()
    counts = seed_load_test_data(args.extra_students)
    print("CRUD checklist fixture is ready. No records were deleted.")
    for name, count in counts.items():
        print(f"  {name.title()}: {count} inserted or updated")
    print("This matches the checklist's final report-ready state, including updates and score corrections.")
    if args.extra_students:
        print("Additional un-enrolled synthetic students use LOAD- IDs.")


if __name__ == "__main__":
    main()

