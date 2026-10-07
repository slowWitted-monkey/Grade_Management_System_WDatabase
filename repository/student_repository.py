from config.database import get_db_connection
from domain.student import Student

class StudentRepository:
    def save(self, student: Student):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO student (student_id, first_name, last_name, email, program, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (student_id) DO UPDATE SET
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    email = EXCLUDED.email,
                    program = EXCLUDED.program,
                    status = EXCLUDED.status;
            """
            cursor.execute(query, (
                student.student_id,
                student.first_name,
                student.last_name,
                student.email,
                student.program,
                student.status
            ))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def delete(self, student_id: str):
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

    def find_all(self) -> list:
        conn = get_db_connection()
        cursor = conn.cursor()
        students = []
        try:
            cursor.execute("SELECT student_id, first_name, last_name, email, program, status FROM student ORDER BY student_id ASC;")
            rows = cursor.fetchall()
            for r in rows:
                if isinstance(r, dict):
                    students.append(Student(
                        student_id=r["student_id"],
                        first_name=r["first_name"],
                        last_name=r["last_name"],
                        email=r["email"],
                        program=r["program"],
                        status=r["status"]
                    ))
                else:
                    students.append(Student(
                        student_id=r[0],
                        first_name=r[1],
                        last_name=r[2],
                        email=r[3],
                        program=r[4],
                        status=r[5]
                    ))
            return students
        except Exception as e:
            print(f"Error fetching students: {e}")
            return []
        finally:
            cursor.close()
            conn.close()