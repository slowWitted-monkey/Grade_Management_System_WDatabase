import psycopg2
from config.database import get_db_connection
from domain.student import Student

class StudentRepository:

    def save(self, student: Student):
        """Inserts a new student. Raises an error if student_id already exists."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO student (student_id, first_name, last_name, email, program, status)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (
                student.student_id, student.first_name, student.last_name,
                student.email, student.program, student.status
            ))
            conn.commit()
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            # If it already exists, let's treat it as an update when saving from the form!
            self.update(student)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def update(self, student: Student):
        """Updates an existing student record."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE student 
                SET first_name = %s, last_name = %s, email = %s, program = %s, status = %s
                WHERE student_id = %s;
            """, (
                student.first_name, student.last_name, student.email,
                student.program, student.status, student.student_id
            ))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def find_all(self) -> list:
        """Retrieves all student records."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT student_id, first_name, last_name, email, program, status FROM student;")
            rows = cursor.fetchall()
            students = []
            for r in rows:
                students.append(Student(
                    student_id=r[0], first_name=r[1], last_name=r[2],
                    email=r[3], program=r[4], status=r[5]
                ))
            return students
        finally:
            cursor.close()
            conn.close()

    def delete(self, student_id: str):
        """Deletes a student by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM student WHERE student_id = %s;", (student_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()