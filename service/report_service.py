import csv
from config.database import get_db_connection

class ReportService:

    def get_class_list_report(self, offering_id: str) -> dict:
        """Generates Class List Report (RP-01) ordered alphabetically by Last Name, First Name."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT s.subject_code, s.subject_name, co.section,
                       t.first_name || ' ' || t.last_name AS teacher_name, t.department,
                       co.school_year, co.semester, co.schedule, co.room
                FROM classoffering co
                JOIN subject s ON co.subject_id = s.subject_id
                JOIN teacher t ON co.teacher_id = t.teacher_id
                WHERE co.offering_id = %s;
            """, (offering_id,))
            header = cursor.fetchone()

            cursor.execute("""
                SELECT st.student_id, st.last_name || ', ' || st.first_name AS student_name, st.program, st.email, e.status
                FROM enrollment e
                JOIN student st ON e.student_id = st.student_id
                WHERE e.offering_id = %s AND e.status = 'Enrolled'
                ORDER BY st.last_name ASC, st.first_name ASC;
            """, (offering_id,))
            students = cursor.fetchall()

            return {
                "header": header,
                "students": students
            }
        finally:
            cursor.close()
            conn.close()

    def get_class_list(self, offering_id: str) -> dict:
        """Alias for get_class_list_report to match GUI expectations."""
        return self.get_class_list_report(offering_id)

    def get_class_grade_sheet(self, offering_id: str) -> dict:
        """Generates Grade Sheet (RP-02) with Grade Points (MG, FG) in Alphabetical Order."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT st.student_id, st.last_name || ', ' || st.first_name AS student_name, st.program,
                       g.midterm_equiv, g.final_equiv, g.remarks
                FROM enrollment e
                JOIN student st ON e.student_id = st.student_id
                LEFT JOIN grade g ON e.enrollment_id = g.enrollment_id
                WHERE e.offering_id = %s AND e.status = 'Enrolled'
                ORDER BY st.last_name ASC, st.first_name ASC;
            """, (offering_id,))
            rows = cursor.fetchall()

            records = []
            for r in rows:
                records.append({
                    "student_id": r[0],
                    "student_name": r[1],
                    "program": r[2],
                    "midterm_equiv": f"{float(r[3]):.2f}" if r[3] is not None else "N/A",
                    "final_equiv": f"{float(r[4]):.2f}" if r[4] is not None else "N/A",
                    "remarks": r[5] if r[5] else "N/A"
                })
            return {"records": records}
        finally:
            cursor.close()
            conn.close()

    def get_student_grade_report(self, student_id: str) -> dict:
        """
        Generates Student Grade Report (RP-03 & RP-04).
        Calculates exact Grade Weighted Average (GWA) = sum(FG * Units) / sum(Units).
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT st.first_name || ' ' || st.last_name AS student_name, st.program, st.year_level
                FROM student st WHERE st.student_id = %s;
            """, (student_id,))
            info = cursor.fetchone()

            cursor.execute("""
                SELECT co.offering_id, s.subject_code, 
                       COALESCE(g.period_id, 'Finals') AS period_id, 
                       g.final_grade, g.remarks, s.units, g.final_equiv
                FROM enrollment e
                JOIN classoffering co ON e.offering_id = co.offering_id
                JOIN subject s ON co.subject_id = s.subject_id
                LEFT JOIN grade g ON e.enrollment_id = g.enrollment_id
                WHERE e.student_id = %s AND e.status = 'Enrolled';
            """, (student_id,))
            rows = cursor.fetchall()

            total_units = 0
            total_weighted_points = 0.0
            records = []

            for row in rows:
                offering_id, subj_code, period_id, final_grade, remarks, units, final_equiv = row

                fg_val = float(final_equiv) if final_equiv is not None else None
                if fg_val is not None and units is not None:
                    total_units += units
                    total_weighted_points += (fg_val * units)

                records.append({
                    "offering_id": offering_id,
                    "subject_code": subj_code,
                    "period_id": period_id,
                    "final_grade": f"{float(final_grade):.2f}" if final_grade is not None else "N/A",
                    "remarks": remarks if remarks else "N/A"
                })

            gwa = round(total_weighted_points / total_units, 2) if total_units > 0 else 0.00

            return {
                "student_info": info,
                "records": records,
                "total_units": total_units,
                "num_subjects": len(records),
                "gwa": f"{gwa:.2f}"
            }
        finally:
            cursor.close()
            conn.close()

    def export_report_to_csv(self, filepath: str, headers: list, rows: list, title: str = ""):
        """Exports any list of records and headers into a CSV file."""
        with open(filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if title:
                writer.writerow([title])
                writer.writerow([])
            writer.writerow(headers)
            for row in rows:
                writer.writerow(row)