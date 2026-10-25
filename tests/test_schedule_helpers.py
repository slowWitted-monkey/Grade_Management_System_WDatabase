import pytest

from ui.gui_app import GradeManagementGUI


def test_schedule_format_uses_existing_display_format():
    assert GradeManagementGUI._format_schedule("Mon/Wed", "09:00", "10:30") == "Mon/Wed 09:00-10:30"


def test_schedule_parser_restores_picker_choices():
    assert GradeManagementGUI._parse_schedule("Tue/Thu 13:30-15:00") == (
        "Tue/Thu", "13:30", "15:00")


def test_schedule_parser_preserves_unrecognized_legacy_format():
    assert GradeManagementGUI._parse_schedule("MWF, 9:00 AM to 10:00 AM") is None


def test_schedule_rejects_end_time_not_after_start():
    with pytest.raises(ValueError, match="later"):
        GradeManagementGUI._format_schedule("Mon", "10:00", "10:00")


def test_schedule_rejects_unknown_day_choice():
    with pytest.raises(ValueError, match="day"):
        GradeManagementGUI._format_schedule("Funday", "09:00", "10:00")


def test_schedule_rejects_time_outside_available_interval():
    with pytest.raises(ValueError, match="30-minute"):
        GradeManagementGUI._format_schedule("Mon", "09:15", "10:00")

