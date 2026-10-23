import psycopg2

from config.database import get_db_connection


class EnrolmentRepository:
    def get_all_offering_ids(self):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT class_id FROM class_offering ORDER BY class_id")
                return [str(row[0]) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_classes(self):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""SELECT co.class_id, co.class_code, co.section, s.subject_code,
                    t.first_name || ' ' || t.last_name, co.school_year, co.semester, co.schedule, co.room
                    FROM class_offering co JOIN subject s USING(subject_id) JOIN teacher t USING(teacher_id)
                    ORDER BY co.class_code, co.section""")
                return cursor.fetchall()
        finally:
            conn.close()

    def save_offering(self, offering_id=None, teacher_id=None, subject_id=None, class_code=None,
                      schedule=None, school_year=None, semester=None, section=None, room=None):
        """Create a class using real subject/teacher records; never invent fallbacks."""
        class_code = (class_code or offering_id or "").strip()
        if not class_code or not teacher_id or not subject_id or not section or not school_year or not semester:
            raise ValueError("Class code, subject, teacher, section, school year, and semester are required.")
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT subject_id FROM subject WHERE subject_code=%s OR subject_id::text=%s", (str(subject_id), str(subject_id)))
                subject = cursor.fetchone()
                if not subject:
                    raise ValueError(f"Subject '{subject_id}' was not found.")
                cursor.execute("""INSERT INTO class_offering
                    (class_code, subject_id, teacher_id, section, school_year, semester, schedule, room)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING class_id""",
                    (class_code, subject[0], teacher_id, section.strip(), school_year.strip(), semester.strip(), schedule, room))
                class_id = cursor.fetchone()[0]
            conn.commit()
            return class_id
        except psycopg2.errors.UniqueViolation as exc:
            conn.rollback()
            raise ValueError(f"Class code '{class_code}' already exists.") from exc
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def enroll_student(self, enrollment_id, student_id, offering_id, status="Enrolled"):
        """Create an enrollment; its database-generated ID is the authoritative ID."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT class_id FROM class_offering WHERE class_id::text=%s OR class_code=%s", (str(offering_id), str(offering_id)))
                cls = cursor.fetchone()
                if not cls:
                    raise ValueError(f"Class offering '{offering_id}' was not found.")
                cursor.execute("SELECT 1 FROM student WHERE student_id=%s", (student_id,))
                if not cursor.fetchone():
                    raise ValueError(f"Student '{student_id}' was not found.")
                cursor.execute("""INSERT INTO enrollment (student_id, class_id, status)
                    VALUES (%s,%s,%s) RETURNING enrollment_id""", (student_id, cls[0], status))
                result = cursor.fetchone()[0]
            conn.commit()
            return result
        except psycopg2.errors.UniqueViolation as exc:
            conn.rollback()
            raise ValueError("This student is already enrolled in the selected class.") from exc
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def list_enrollments(self, class_id=None):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = """SELECT e.enrollment_id, e.student_id, e.class_id, e.enroll_date, e.status,
                    s.first_name, s.last_name FROM enrollment e JOIN student s USING(student_id)"""
                params = ()
                if class_id is not None:
                    query += " WHERE e.class_id=%s"
                    params = (class_id,)
                cursor.execute(query + " ORDER BY s.last_name, s.first_name", params)
                return cursor.fetchall()
        finally:
            conn.close()

    def update_enrollment_status(self, enrollment_id, status):
        if status not in {"Enrolled", "Dropped"}:
            raise ValueError("Enrollment status must be Enrolled or Dropped.")
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE enrollment SET status=%s WHERE enrollment_id=%s", (status, enrollment_id))
                if not cursor.rowcount:
                    raise ValueError("Enrollment was not found.")
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def delete_enrollment(self, enrollment_id):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM enrollment WHERE enrollment_id=%s", (enrollment_id,))
                if not cursor.rowcount:
                    raise ValueError("Enrollment was not found.")
            conn.commit()
        except psycopg2.errors.ForeignKeyViolation as exc:
            conn.rollback()
            raise ValueError("Enrollment cannot be removed while grade scores depend on it.") from exc
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
