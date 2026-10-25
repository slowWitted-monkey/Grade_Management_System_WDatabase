import psycopg2

from config.database import get_db_connection
from domain.student import Student


class StudentRepository:
    def save(self, student: Student) -> int:
        self._validate(student)
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO student
                       (student_id, first_name, last_name, email, program, year_level, status)
                       VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING student_id""",
                    (student.student_id, student.first_name.strip(), student.last_name.strip(),
                     student.email or None, student.program.strip(), student.year_level,
                     student.status or "Active"),
                )
                result = cursor.fetchone()[0]
            conn.commit()
            return result
        except psycopg2.errors.UniqueViolation as exc:
            conn.rollback()
            raise ValueError(f"Student number '{student.student_id}' already exists.") from exc
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def update(self, student: Student) -> None:
        self._validate(student)
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """UPDATE student SET first_name=%s, last_name=%s, email=%s,
                       program=%s, year_level=%s, status=%s WHERE student_id=%s""",
                    (student.first_name.strip(), student.last_name.strip(), student.email or None,
                     student.program.strip(), student.year_level, student.status or "Active",
                     student.student_id),
                )
                if cursor.rowcount == 0:
                    raise ValueError(f"Student '{student.student_id}' was not found.")
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def _validate(student: Student) -> None:
        if not student.student_id.strip() or not student.first_name.strip() or not student.last_name.strip():
            raise ValueError("Student number, first name, and last name are required.")
        if not student.program or not student.program.strip():
            raise ValueError("Program is required.")
        if not isinstance(student.year_level, int) or not 1 <= student.year_level <= 8:
            raise ValueError("Year level must be a whole number from 1 to 8.")

    def find_all(self) -> list[Student]:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""SELECT student_id, first_name, last_name, email, program,
                                  year_level, status FROM student ORDER BY last_name, first_name""")
                return [Student(*row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def find_by_id(self, student_id: str):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT student_id, first_name, last_name, email, program, year_level, status FROM student WHERE student_id=%s", (student_id,))
                row = cursor.fetchone()
                return Student(*row) if row else None
        finally:
            conn.close()

    def search(self, query: str) -> list[Student]:
        """Search uses bound parameters so user input is always treated as text."""
        needle = f"%{query}%"
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""SELECT student_id, first_name, last_name, email, program,
                                  year_level, status FROM student
                                  WHERE student_id ILIKE %s OR first_name ILIKE %s OR last_name ILIKE %s
                                  ORDER BY last_name, first_name""", (needle, needle, needle))
                return [Student(*row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def delete(self, student_id: str) -> None:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM student WHERE student_id=%s", (student_id,))
                if cursor.rowcount == 0:
                    raise ValueError(f"Student '{student_id}' was not found.")
            conn.commit()
        except psycopg2.errors.ForeignKeyViolation as exc:
            conn.rollback()
            raise ValueError("Student cannot be deleted while enrollments depend on the record.") from exc
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
