import csv

from config.database import get_db_connection


class ReportService:
    def get_class_list(self, class_id):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""SELECT st.student_id, st.first_name, st.last_name, st.program,
                    st.email, e.status FROM enrollment e JOIN student st USING (student_id)
                    WHERE e.class_id=%s AND e.status='Enrolled'
                    ORDER BY st.last_name, st.first_name""", (class_id,))
                return [dict(student_id=r[0], first_name=r[1], last_name=r[2], program=r[3], email=r[4], status=r[5]) for r in cursor.fetchall()]
        finally:
            conn.close()

    def _class_header(self, cursor, class_id):
        cursor.execute("""SELECT co.class_id, co.class_code, co.section, co.school_year, co.semester,
            co.schedule, co.room, s.subject_code, s.subject_name, t.first_name, t.last_name, t.department
            FROM class_offering co JOIN subject s USING(subject_id) JOIN teacher t USING(teacher_id)
            WHERE co.class_id=%s""", (class_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Class offering {class_id} was not found.")
        return {"class_id": row[0], "class_code": row[1], "section": row[2], "school_year": row[3],
                "semester": row[4], "schedule": row[5], "room": row[6], "subject_code": row[7],
                "subject_name": row[8], "teacher_name": f"{row[9]} {row[10]}", "department": row[11]}

    def get_class_list_report(self, class_id):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                header = self._class_header(cursor, class_id)
            return {"header": header, "records": self.get_class_list(class_id)}
        finally:
            conn.close()

    def get_class_grade_sheet(self, class_id):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""SELECT st.student_id, st.first_name, st.last_name, st.program,
                    g.midterm_equiv, g.final_equiv, g.remarks FROM enrollment e
                    JOIN student st USING(student_id) LEFT JOIN grade g USING(enrollment_id)
                    WHERE e.class_id=%s AND e.status='Enrolled'
                    ORDER BY st.last_name, st.first_name""", (class_id,))
                return [dict(student_id=r[0], first_name=r[1], last_name=r[2], program=r[3],
                             midterm_equiv=r[4], final_equiv=r[5], remarks=r[6]) for r in cursor.fetchall()]
        finally:
            conn.close()

    def get_grade_sheet_report(self, class_id):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                header = self._class_header(cursor, class_id)
            return {"header": header, "records": self.get_class_grade_sheet(class_id)}
        finally:
            conn.close()

    def get_student_grade_report(self, student_id):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""SELECT co.class_id, s.subject_code, s.subject_name,
                    t.first_name || ' ' || t.last_name, s.units, g.final_equiv, g.remarks
                    FROM enrollment e JOIN class_offering co USING(class_id)
                    JOIN subject s USING(subject_id) JOIN teacher t USING(teacher_id)
                    LEFT JOIN grade g USING(enrollment_id)
                    WHERE e.student_id=%s AND e.status='Enrolled'
                    ORDER BY s.subject_code""", (student_id,))
                rows = cursor.fetchall()
                cursor.execute("SELECT first_name, last_name, program, year_level FROM student WHERE student_id=%s", (student_id,))
                student = cursor.fetchone()
                if not student:
                    raise ValueError(f"Student {student_id} was not found.")
                records, total_units, weighted = [], 0, 0.0
                for row in rows:
                    units, grade = row[4], row[5]
                    records.append({"offering_id": row[0], "subject_code": row[1], "subject_name": row[2],
                                    "description": row[2], "teacher_name": row[3], "units": units,
                                    "final_equiv": grade, "final_grade": grade, "remarks": row[6]})
                    if grade is not None:
                        total_units += units
                        weighted += float(grade) * units
                return {"student": {"first_name": student[0], "last_name": student[1], "program": student[2], "year_level": student[3]},
                        "records": records, "total_units": total_units, "no_of_subjects": len(records),
                        "gwa": round(weighted / total_units, 2) if total_units else None}
        finally:
            conn.close()

    def export_report_to_csv(self, filepath, headers, rows, title=""):
        with open(filepath, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if title:
                writer.writerow([title])
                writer.writerow([])
            writer.writerow(headers)
            writer.writerows(rows)
