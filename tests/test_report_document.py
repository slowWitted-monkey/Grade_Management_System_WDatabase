from datetime import datetime, timezone

import pytest

from service.report_service import ReportService
from ui.gui_app import GradeManagementGUI


@pytest.mark.parametrize(
    ("screen_height", "expected"),
    [(1080, 480), (768, 288), (600, 180)],
)
def test_report_preview_keeps_a_usable_table_height(screen_height, expected):
    assert GradeManagementGUI._report_table_min_height(screen_height) == expected


def test_class_list_becomes_an_export_friendly_report_document():
    generated_at = datetime(2026, 10, 26, 2, 30, tzinfo=timezone.utc)
    data = {
        "header": {
            "class_code": "CSPC103-A", "subject_code": "CSPC 103",
            "subject_name": "Programming", "section": "A",
            "teacher_name": "Maria Santos", "department": "Computer Studies",
            "school_year": "2026-2027", "semester": "1st",
            "schedule": "Mon/Wed 09:00-10:00", "room": "Room 101",
        },
        "records": [{"student_id": "2026-0001", "first_name": "Juan",
                     "last_name": "Dela Cruz", "program": "BSCS"}],
    }

    document = ReportService().build_print_document(
        "Class list", data, generated_at=generated_at)

    assert document.title == "Class List"
    assert document.generated_at == generated_at
    assert dict(document.metadata)["Semester"] == "1st Semester"
    assert document.rows == (("1", "2026-0001", "Dela Cruz, Juan", "BSCS"),)
    assert len(document.rows[0]) == len(document.columns)
    assert document.summary == (("Enrolled Students", "1"),)


def test_grade_sheet_formats_missing_grades_as_incomplete():
    data = {
        "header": {"class_code": "C1", "subject_code": "CS1", "subject_name": "Intro",
                   "section": "A", "teacher_name": "Teacher", "department": "Dept",
                   "school_year": "2026-2027", "semester": "1st", "schedule": None,
                   "room": None},
        "records": [{"student_id": "S1", "first_name": "Ana", "last_name": "Reyes",
                     "program": "BSIT", "midterm_equiv": None, "final_equiv": 91.5,
                     "remarks": "Passed"}],
    }

    document = ReportService().build_print_document("Grade sheet", data)

    assert document.rows[0][4:7] == ("Incomplete", "91.50", "Passed")
    assert len(document.rows[0]) == len(document.columns)


def test_student_report_includes_term_columns_and_summary():
    data = {
        "student": {"first_name": "Juan", "last_name": "Dela Cruz",
                    "program": "BSCS", "year_level": 2},
        "records": [{"school_year": "2026-2027", "semester": "1st",
                     "subject_code": "CS1", "subject_name": "Intro",
                     "teacher_name": "Maria Santos", "units": 3,
                     "final_grade": 88, "remarks": None}],
        "total_units": 3, "no_of_subjects": 1, "gwa": 88.0,
    }

    document = ReportService().build_print_document("Student grade report", data)

    assert "school_year" in [key for key, _label in document.columns]
    assert "semester" in [key for key, _label in document.columns]
    assert document.rows[0][1] == "1st Semester"
    assert document.rows[0][-2:] == ("88.00", "—")
    assert len(document.rows[0]) == len(document.columns)
    assert document.summary[-1] == ("Grade Weighted Average", "88.00")

