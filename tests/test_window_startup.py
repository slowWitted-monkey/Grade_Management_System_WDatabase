import pytest

from ui.gui_app import GradeManagementGUI


@pytest.mark.parametrize(
    ("screen", "expected"),
    [
        ((1920, 1080), ((1450, 900), (900, 560))),
        ((1280, 720), ((1240, 640), (900, 560))),
        ((800, 500), ((760, 480), (760, 480))),
    ],
)
def test_startup_window_sizes_fit_display_and_allow_resizing(screen, expected):
    assert GradeManagementGUI._startup_window_size(*screen) == expected

