from config.database import get_db_connection

class OfferingRepository:
    def add_teacher(self, teacher_id: str, first_name: str, last_name: str, email: str, department: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO teacher (teacher_id, first_name, last_name, email, department)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (teacher_id) DO UPDATE SET
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    email = EXCLUDED.email,
                    department = EXCLUDED.department;
            """, (teacher_id, first_name, last_name, email, department))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def create_class_offering(self, offering_id: str, subject_code: str, teacher_id: str,
                              class_code: str, section: str, schedule: str,
                              school_year: str, semester: str, room: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO classoffering 
                (offering_id, subject_code, teacher_id, class_code, section, schedule, school_year, semester, room)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (offering_id, subject_code, teacher_id, class_code, section, schedule, school_year, semester, room))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def get_all_teachers(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT teacher_id, first_name || ' ' || last_name AS full_name FROM teacher;")
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()