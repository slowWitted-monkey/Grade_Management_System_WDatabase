"""Class offering queries using the UML-aligned schema."""

from config.database import get_db_connection


class ClassRepository:
    def find_all(self):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""SELECT class_id, class_code, subject_id, teacher_id, section,
                    school_year, semester, schedule, room FROM class_offering ORDER BY class_code""")
                return cursor.fetchall()
        finally:
            conn.close()

    def find_by_id(self, class_id):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""SELECT class_id, class_code, subject_id, teacher_id, section,
                    school_year, semester, schedule, room FROM class_offering WHERE class_id=%s""", (class_id,))
                return cursor.fetchone()
        finally:
            conn.close()
