import csv
from config.database import get_db_connection

class ReportService:

    def get_class_list(self, offering_id: str) -> list:
        """Fetches class list records as a list of dictionaries sorted alphabetically (RP-01)."""
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
        """Fetches class grade sheet records with MG and FG grade equivalents (RP-02)."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT st.student_id, st.first_name, st.last_name, st.program,
                       g.midterm_equiv, g.final_equiv, g.remarks
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
                    "program": r[3],
                    "midterm_equiv": r[4],
                    "final_equiv": r[5],
                    "remarks": r[6]
                })
            return result
        finally:
            cursor.close()
            conn.close()

    def get_student_grade_report(self, student_id: str) -> dict:
        """Fetches student grade records and computes exact Grade Weighted Average (RP-03, RP-04)."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT co.offering_id, s.subject_code, s.subject_name, 
                       CONCAT(t.first_name, ' ', t.last_name) AS teacher_name, 
                       s.units, g.final_equiv, g.remarks
                FROM enrollment e
                JOIN classoffering co ON e.offering_id = co.offering_id
                JOIN subject s ON co.subject_id = s.subject_id
                JOIN teacher t ON co.teacher_id = t.teacher_id
                LEFT JOIN grade g ON e.enrollment_id = g.enrollment_id
                WHERE e.student_id = %s AND e.status = 'Enrolled';
            """, (student_id,))
            rows = cursor.fetchall()

            records = []
            total_units = 0
            weighted_sum = 0.0

            for r in rows:
                units = r[4] or 0
                f_grade = float(r[5]) if r[5] is not None else 0.0

                if r[5] is not None:
                    total_units += units
                    weighted_sum += f_grade * units

                records.append({
                    "offering_id": r[0],
                    "subject_code": r[1],
                    "description": r[2],
                    "teacher_name": r[3],
                    "units": units,
                    "final_equiv": r[5],
                    "remarks": r[6]
                })

            gwa = round(weighted_sum / total_units, 2) if total_units > 0 else 0.0

            return {
                "records": records,
                "total_units": total_units,
                "no_of_subjects": len(records),
                "gwa": gwa
            }
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