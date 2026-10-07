from config.database import get_db_connection
from datetime import date

class GradeRepository:
    def save_or_update_grade(self, grade_id: str, student_id: str, offering_id: str, period_name: str, final_grade: float, remarks: str):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 1. Fetch enrollment_id matching student_id and offering_id
            cursor.execute("""
                SELECT enrollment_id 
                FROM enrollment 
                WHERE student_id = %s AND offering_id = %s;
            """, (student_id, offering_id))

            enrollment_row = cursor.fetchone()
            if not enrollment_row:
                raise Exception(f"No enrollment record found for Student '{student_id}' in Offering '{offering_id}'. Please enroll the student first.")

            enrollment_id = enrollment_row['enrollment_id'] if isinstance(enrollment_row, dict) else enrollment_row[0]

            # 2. Fetch the actual period_id from gradingperiod matching period_name
            cursor.execute("""
                SELECT period_id 
                FROM gradingperiod 
                WHERE LOWER(name) LIKE LOWER(%s) || '%%' 
                   OR LOWER(name) = LOWER(%s) 
                   OR period_id = %s;
            """, (period_name, period_name, period_name))

            period_row = cursor.fetchone()
            if not period_row:
                raise Exception(f"Grading period '{period_name}' not found in database.")

            period_id = period_row['period_id'] if isinstance(period_row, dict) else period_row[0]

            # 3. Insert or update grade using period_id
            query = """
                INSERT INTO grade (grade_id, enrollment_id, period_id, final_grade, remarks, date_encoded)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (grade_id) DO UPDATE SET
                    enrollment_id = EXCLUDED.enrollment_id,
                    period_id = EXCLUDED.period_id,
                    final_grade = EXCLUDED.final_grade,
                    remarks = EXCLUDED.remarks,
                    date_encoded = EXCLUDED.date_encoded;
            """
            cursor.execute(query, (grade_id, enrollment_id, period_id, final_grade, remarks, date.today()))
            conn.commit()

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def get_scores_for_grade(self, student_id: str, offering_id: str) -> list:
        """Retrieves score and max_score records for calculating student grades in a given offering."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT cs.score, a.max_score
                FROM componentscore cs
                JOIN assessment a ON cs.assessment_id = a.assessment_id
                JOIN enrollment e ON cs.enrollment_id = e.enrollment_id
                WHERE e.student_id = %s AND e.offering_id = %s;
            """, (student_id, offering_id))
            rows = cursor.fetchall()

            scores = []
            for r in rows:
                if isinstance(r, dict):
                    scores.append({"score": r["score"], "max_score": r["max_score"]})
                else:
                    scores.append({"score": r[0], "max_score": r[1]})
            return scores
        except Exception as e:
            print(f"Error fetching scores for grade: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    def get_student_id_by_grade_id(self, grade_id: str) -> str:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT e.student_id
                FROM grade g
                JOIN enrollment e ON g.enrollment_id = e.enrollment_id
                WHERE g.grade_id = %s;
            """, (grade_id,))
            row = cursor.fetchone()
            if row:
                return row[0] if isinstance(row, tuple) else row['student_id']
            raise ValueError(f"No student found for Grade ID: {grade_id}")
        finally:
            cursor.close()
            conn.close()