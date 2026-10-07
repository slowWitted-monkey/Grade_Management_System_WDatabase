from typing import List, Dict, Any
from config.database import get_db_connection

class ReportService:

    def get_class_list(self, offering_id: str) -> List[Dict[str, Any]]:
        """Returns student roster as a list of dictionaries for gui_app.py."""
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT s.student_id, s.first_name, s.last_name, s.program, s.email, e.status
            FROM enrollment e
            JOIN student s ON e.student_id = s.student_id
            WHERE e.offering_id = %s
            ORDER BY s.last_name, s.first_name;
        """
        cursor.execute(query, (offering_id,))
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        students = []
        for r in rows:
            if isinstance(r, dict):
                students.append(r)
            else:
                students.append({
                    "student_id": r[0],
                    "first_name": r[1],
                    "last_name": r[2],
                    "program": r[3],
                    "email": r[4],
                    "status": r[5]
                })
        return students

    def get_class_grade_sheet(self, offering_id: str) -> List[Dict[str, Any]]:
        """Returns class grades as a list of dictionaries for gui_app.py."""
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT s.student_id, s.first_name, s.last_name,
                   g.final_grade, g.remarks, gp.name AS period_name
            FROM enrollment e
            JOIN student s ON e.student_id = s.student_id
            LEFT JOIN grade g ON e.enrollment_id = g.enrollment_id
            LEFT JOIN gradingperiod gp ON g.period_id = gp.period_id
            WHERE e.offering_id = %s
            ORDER BY s.last_name, s.first_name;
        """
        cursor.execute(query, (offering_id,))
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        grades = []
        for r in rows:
            if isinstance(r, dict):
                grades.append(r)
            else:
                grades.append({
                    "student_id": r[0],
                    "first_name": r[1],
                    "last_name": r[2],
                    "final_grade": r[3],
                    "remarks": r[4],
                    "period_name": r[5]
                })
        return grades

    def get_student_grade_report(self, student_id: str) -> List[Dict[str, Any]]:
        """Returns student course grades as a list of dictionaries for gui_app.py."""
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT e.offering_id, sub.subject_code, gp.name AS period_name,
                   g.final_grade, g.remarks
            FROM enrollment e
            JOIN classoffering co ON e.offering_id = co.offering_id
            JOIN subject sub ON co.subject_id = sub.subject_id
            LEFT JOIN grade g ON e.enrollment_id = g.enrollment_id
            LEFT JOIN gradingperiod gp ON g.period_id = gp.period_id
            WHERE e.student_id = %s;
        """
        cursor.execute(query, (student_id,))
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        records = []
        for r in rows:
            if isinstance(r, dict):
                records.append(r)
            else:
                records.append({
                    "offering_id": r[0],
                    "subject_code": r[1],
                    "period_name": r[2],
                    "final_grade": r[3],
                    "remarks": r[4]
                })
        return records