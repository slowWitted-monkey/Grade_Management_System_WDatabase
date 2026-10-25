from datetime import date

import pytest

from ui.gui_app import GradeManagementGUI


@pytest.mark.parametrize(
    ("today", "expected"),
    [
        (date(2026, 5, 31), "2025-2026"),
        (date(2026, 6, 1), "2026-2027"),
        (date(2027, 2, 15), "2026-2027"),
    ],
)
def test_current_school_year_tracks_academic_year(today, expected):
    assert GradeManagementGUI._current_school_year(today) == expected


@pytest.mark.parametrize(
    ("today", "expected"),
    [
        (date(2026, 5, 31), "2nd"),
        (date(2026, 6, 1), "Summer"),
        (date(2026, 7, 31), "Summer"),
        (date(2026, 8, 1), "1st"),
        (date(2026, 12, 31), "1st"),
    ],
)
def test_current_semester_suggests_term_from_date(today, expected):
    assert GradeManagementGUI._current_semester(today) == expected

