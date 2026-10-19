import psycopg2

from config.database import get_db_connection
from domain.teacher import Teacher


class TeacherRepository:
    def find_all(self):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT teacher_id, first_name, last_name, email, department, status FROM teacher ORDER BY last_name, first_name")
                return [Teacher(*row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def save(self, teacher_or_id, first_name=None, last_name=None, email=None, department=None, status="Active"):
        teacher = teacher_or_id if isinstance(teacher_or_id, Teacher) else Teacher(
            teacher_or_id, first_name or "", last_name or "", email, department or "", status
        )
        self._validate(teacher)
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""INSERT INTO teacher
                    (teacher_id, first_name, last_name, email, department, status)
                    VALUES (%s,%s,%s,%s,%s,%s)""",
                    (teacher.teacher_id, teacher.first_name.strip(), teacher.last_name.strip(),
                     teacher.email or None, teacher.department.strip(), teacher.status or "Active"))
            conn.commit()
        except psycopg2.errors.UniqueViolation as exc:
            conn.rollback()
            raise ValueError(f"Teacher ID '{teacher.teacher_id}' already exists.") from exc
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def update(self, teacher: Teacher):
        self._validate(teacher)
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""UPDATE teacher SET first_name=%s, last_name=%s, email=%s,
                    department=%s, status=%s WHERE teacher_id=%s""",
                    (teacher.first_name.strip(), teacher.last_name.strip(), teacher.email or None,
                     teacher.department.strip(), teacher.status or "Active", teacher.teacher_id))
                if not cursor.rowcount:
                    raise ValueError(f"Teacher '{teacher.teacher_id}' was not found.")
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def _validate(teacher):
        if not teacher.teacher_id.strip() or not teacher.first_name.strip() or not teacher.last_name.strip():
            raise ValueError("Teacher ID, first name, and last name are required.")
        if not teacher.department.strip():
            raise ValueError("Department is required.")

    def delete_by_id(self, teacher_id: str):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM teacher WHERE teacher_id=%s", (teacher_id,))
                if not cursor.rowcount:
                    raise ValueError(f"Teacher '{teacher_id}' was not found.")
            conn.commit()
        except psycopg2.errors.ForeignKeyViolation as exc:
            conn.rollback()
            raise ValueError("Teacher cannot be deleted while a class offering depends on the record.") from exc
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
