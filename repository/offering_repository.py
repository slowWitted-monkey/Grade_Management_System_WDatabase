"""Repository helpers for teachers and class offerings."""

from config.database import get_db_connection
from repository.enrollment_repository import EnrolmentRepository


class OfferingRepository:
    def add_teacher(self, teacher_id, first_name, last_name, email, department):
        """Insert a teacher; duplicate IDs are reported instead of silently overwritten."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""INSERT INTO teacher
                    (teacher_id, first_name, last_name, email, department)
                    VALUES (%s,%s,%s,%s,%s)""",
                    (teacher_id, first_name, last_name, email or None, department))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def create_class_offering(self, offering_id=None, subject_code=None, teacher_id=None,
                              class_code=None, section=None, schedule=None,
                              school_year=None, semester=None, room=None, subject_id=None):
        """Create using the current class_offering schema; return its generated class ID."""
        return EnrolmentRepository().save_offering(
            offering_id=offering_id or class_code,
            class_code=class_code or offering_id,
            teacher_id=teacher_id,
            subject_id=subject_id or subject_code,
            section=section,
            schedule=schedule,
            school_year=school_year,
            semester=semester,
            room=room,
        )

    def get_all_teachers(self):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT teacher_id, first_name || ' ' || last_name FROM teacher ORDER BY last_name, first_name")
                return cursor.fetchall()
        finally:
            conn.close()
