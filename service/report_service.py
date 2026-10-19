from config.database import get_db_connection

class ReportService:

    def get_class_list_report(self, offering_id: str) -> dict:
        """Generates Class List Report (RP-01) ordered alphabetically by Last Name, First Name."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Query class header details
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

            # Query enrolled students sorted ALPHABETICALLY by last name, then first name
            cursor.execute("""
                SELECT st.student_id, st.last_name || ', ' || st.first_name AS student_name, st.program
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
                SELECT s.subject_code, s.subject_name,
                       t.first_name || ' ' || t.last_name AS teacher_name,
                       s.units, g.final_equiv
                FROM enrollment e
                JOIN classoffering co ON e.offering_id = co.offering_id
                JOIN subject s ON co.subject_id = s.subject_id
                JOIN teacher t ON co.teacher_id = t.teacher_id
                LEFT JOIN grade g ON e.enrollment_id = g.enrollment_id
                WHERE e.student_id = %s AND e.status = 'Enrolled';
            """, (student_id,))
            rows = cursor.fetchall()

            total_units = 0
            total_weighted_points = 0.0
            records = []

            for row in rows:
                subj_code, desc, teacher, units, final_equiv = row

                fg_val = float(final_equiv) if final_equiv is not None else None
                if fg_val is not None:
                    total_units += units
                    total_weighted_points += (fg_val * units)

                records.append({
                    "subject_code": subj_code,
                    "description": desc,
                    "teacher": teacher,
                    "units": units,
                    "final_equiv": f"{fg_val:.2f}" if fg_val is not None else "N/A"
                })

            # Calculate exact GWA (Grade Weighted Average)
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