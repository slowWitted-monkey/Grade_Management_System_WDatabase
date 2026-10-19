import csv
from config.database import get_db_connection

class ReportService:

    def get_class_list(self, offering_id: str) -> list:
        """Fetches class list records as a list of dictionaries for GUI rendering."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT st.student_id, st.first_name, st.last_name, st.program, st.email, e.status
                FROM enrollment e
                JOIN student st ON e.student_id = st.student_id
                WHERE e.offering_id = %s AND e.status = 'Enrolled'
                ORDER BY st.last_name ASC, st.first_name ASC;
            """, (offering_id,))
            rows = cursor.fetchall()
            result = []
            for r in rows:
                result.append({
                    "student_id": r[0],
                    "first_name": r[1],
                    "last_name": r[2],
                    "program": r[3],
                    "email": r[4],
                    "status": r[5]
                })
            return result
        finally:
            cursor.close()
            conn.close()

    def get_class_grade_sheet(self, offering_id: str) -> list:
        """Fetches class grade sheet records as a list of dictionaries."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT st.student_id, st.first_name, st.last_name, 
                       COALESCE(g.period_id, 'Finals') AS period_name, 
                       g.final_grade, g.remarks
                FROM enrollment e
                JOIN student st ON e.student_id = st.student_id
                LEFT JOIN grade g ON e.enrollment_id = g.enrollment_id
                WHERE e.offering_id = %s AND e.status = 'Enrolled'
                ORDER BY st.last_name ASC, st.first_name ASC;
            """, (offering_id,))
            rows = cursor.fetchall()
            result = []
            for r in rows:
                result.append({
                    "student_id": r[0],
                    "first_name": r[1],
                    "last_name": r[2],
                    "period_name": r[3],
                    "final_grade": r[4],
                    "remarks": r[5]
                })
            return result
        finally:
            cursor.close()
            conn.close()

    def get_student_grade_report(self, student_id: str) -> list:
        """Fetches student grade report records as a list of dictionaries."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT co.offering_id, s.subject_code, 
                       COALESCE(g.period_id, 'Finals') AS period_name, 
                       g.final_grade, g.remarks
                FROM enrollment e
                JOIN classoffering co ON e.offering_id = co.offering_id
                JOIN subject s ON co.subject_id = s.subject_id
                LEFT JOIN grade g ON e.enrollment_id = g.enrollment_id
                WHERE e.student_id = %s AND e.status = 'Enrolled';
            """, (student_id,))
            rows = cursor.fetchall()
            result = []
            for r in rows:
                result.append({
                    "offering_id": r[0],
                    "subject_code": r[1],
                    "period_name": r[2],
                    "final_grade": r[3],
                    "remarks": r[4]
                })
            return result
        finally:
            cursor.close()
            conn.close()

    def export_report_to_csv(self, filepath: str, headers: list, rows: list, title: str = ""):
        """Exports report records into a CSV file."""
        with open(filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if title:
                writer.writerow([title])
                writer.writerow([])
            writer.writerow(headers)
            for row in rows:
                writer.writerow(row)