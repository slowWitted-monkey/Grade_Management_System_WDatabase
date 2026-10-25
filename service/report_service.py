import csv
from dataclasses import dataclass
from datetime import datetime

from config.database import get_db_connection


@dataclass(frozen=True)
class ReportDocument:
    """Structured report content shared by the on-screen preview and later exporters."""

    report_type: str
    title: str
    generated_at: datetime
    metadata: tuple[tuple[str, str], ...]
    columns: tuple[tuple[str, str], ...]
    rows: tuple[tuple[str, ...], ...]
    summary: tuple[tuple[str, str], ...] = ()


class ReportService:
    @staticmethod
    def _report_text(value):
        return "—" if value is None or str(value).strip() == "" else str(value)

    @staticmethod
    def _report_grade(value):
        return "Incomplete" if value is None else f"{float(value):.2f}"

    @classmethod
    def _report_semester(cls, value):
        semester = cls._report_text(value)
        if semester == "—":
            return semester
        standard = {"1st": "1st Semester", "2nd": "2nd Semester", "summer": "Summer"}
        return standard.get(semester.casefold(), semester if "semester" in semester.casefold()
                            or semester.casefold() == "summer" else semester + " Semester")

    def build_print_document(self, kind, data, *, generated_at=None):
        """Convert report query results into a UI/export-ready, immutable document."""
        generated_at = generated_at or datetime.now().astimezone()
        if kind in {"Class list", "Grade sheet"}:
            header = data["header"]
            semester = self._report_semester(header.get("semester"))
            metadata = (
                ("Class", self._report_text(header.get("class_code"))),
                ("Subject", f"{self._report_text(header.get('subject_code'))} — "
                             f"{self._report_text(header.get('subject_name'))}"),
                ("Section", self._report_text(header.get("section"))),
                ("Teacher", self._report_text(header.get("teacher_name"))),
                ("Department", self._report_text(header.get("department"))),
                ("School Year", self._report_text(header.get("school_year"))),
                ("Semester", semester),
                ("Schedule", self._report_text(header.get("schedule"))),
                ("Room", self._report_text(header.get("room"))),
            )
            records = data["records"]
            if kind == "Class list":
                columns = (("number", "No."), ("student_id", "Student ID"),
                           ("student", "Student Name"), ("program", "Program"))
                rows = tuple((str(index), self._report_text(record.get("student_id")),
                              f"{self._report_text(record.get('last_name'))}, "
                              f"{self._report_text(record.get('first_name'))}",
                              self._report_text(record.get("program")))
                             for index, record in enumerate(records, 1))
                summary = (("Enrolled Students", str(len(rows))),)
            else:
                columns = (("number", "No."), ("student_id", "Student ID"),
                           ("student", "Student Name"), ("program", "Program"),
                           ("midterm", "Midterm Grade"), ("finals", "Final Grade"),
                           ("remarks", "Remarks"))
                rows = tuple((str(index), self._report_text(record.get("student_id")),
                              f"{self._report_text(record.get('last_name'))}, "
                              f"{self._report_text(record.get('first_name'))}",
                              self._report_text(record.get("program")),
                              self._report_grade(record.get("midterm_equiv")),
                              self._report_grade(record.get("final_equiv")),
                              self._report_text(record.get("remarks")))
                             for index, record in enumerate(records, 1))
                summary = (("Students", str(len(rows))),)
            return ReportDocument(
                report_type=kind, title=kind.title(), generated_at=generated_at,
                metadata=metadata, columns=columns, rows=rows, summary=summary,
            )

        if kind == "Student grade report":
            student = data["student"]
            year_level = int(student["year_level"])
            ordinal = (f"{year_level}{'st' if year_level == 1 else 'nd' if year_level == 2 else 'rd' if year_level == 3 else 'th'} year")
            columns = (("school_year", "School Year"), ("semester", "Semester"),
                       ("subject_code", "Subject Code"), ("subject", "Subject"),
                       ("teacher", "Instructor"), ("units", "Units"),
                       ("grade", "Final Grade"), ("remarks", "Remarks"))
            rows = tuple((self._report_text(record.get("school_year")),
                          self._report_semester(record.get("semester")),
                          self._report_text(record.get("subject_code")),
                          self._report_text(record.get("subject_name")),
                          self._report_text(record.get("teacher_name")),
                          self._report_text(record.get("units")),
                          self._report_grade(record.get("final_grade")),
                          self._report_text(record.get("remarks")))
                         for record in data["records"])
            metadata = (
                ("Student", f"{self._report_text(student.get('last_name'))}, "
                            f"{self._report_text(student.get('first_name'))}"),
                ("Program", self._report_text(student.get("program"))),
                ("Year Level", ordinal),
            )
            summary = (
                ("Total Units", str(data["total_units"])),
                ("Subjects", str(data["no_of_subjects"])),
                ("Grade Weighted Average", self._report_grade(data["gwa"])),
            )
            return ReportDocument(
                report_type=kind, title=kind.title(), generated_at=generated_at,
                metadata=metadata, columns=columns, rows=rows, summary=summary,
            )

        raise ValueError(f"Unsupported report type: {kind}")

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
                cursor.execute("""SELECT co.class_id, co.school_year, co.semester,
                    s.subject_code, s.subject_name,
                    t.first_name || ' ' || t.last_name, s.units, g.final_equiv, g.remarks
                    FROM enrollment e JOIN class_offering co USING(class_id)
                    JOIN subject s USING(subject_id) JOIN teacher t USING(teacher_id)
                    LEFT JOIN grade g USING(enrollment_id)
                    WHERE e.student_id=%s AND e.status='Enrolled'
                    ORDER BY co.school_year, co.semester, s.subject_code""", (student_id,))
                rows = cursor.fetchall()
                cursor.execute("SELECT first_name, last_name, program, year_level FROM student WHERE student_id=%s", (student_id,))
                student = cursor.fetchone()
                if not student:
                    raise ValueError(f"Student {student_id} was not found.")
                records, total_units, weighted = [], 0, 0.0
                for row in rows:
                    units, grade = row[6], row[7]
                    records.append({"offering_id": row[0], "school_year": row[1], "semester": row[2],
                                    "subject_code": row[3], "subject_name": row[4],
                                    "description": row[4], "teacher_name": row[5], "units": units,
                                    "final_equiv": grade, "final_grade": grade, "remarks": row[8]})
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

