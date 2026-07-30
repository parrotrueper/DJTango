import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from ttvttm.tableModels import milongaSource
from ttvttm.TTVTTM import (
    apply_track_type_color,
    get_contrast_color,
    track_type_key_from_row,
)


class DummyColor:
    def __init__(self, r, g, b, a):
        self._r = r
        self._g = g
        self._b = b
        self._a = a

    def red(self):
        return self._r

    def green(self):
        return self._g

    def blue(self):
        return self._b

    def alpha(self):
        return self._a


def test_tango_type_key_from_row_valid():
    assert track_type_key_from_row(0) == 1
    assert track_type_key_from_row(2) == 3


def test_tango_type_key_from_row_no_selection():
    with pytest.raises(ValueError):
        track_type_key_from_row(-1)


def test_apply_tango_type_color_updates_type():
    TYPE = {1: ("unknown", "Unknown", 1, 2, 3, 255)}
    new_color = DummyColor(100, 150, 200, 180)

    result = apply_track_type_color(TYPE, 0, new_color)

    assert result == (TYPE[1][0], TYPE[1][1], 100, 150, 200, 180)
    assert TYPE[1] == result


def test_apply_tango_type_color_invalid_row():
    TYPE = {1: ("unknown", "Unknown", 1, 2, 3, 255)}
    new_color = DummyColor(100, 150, 200, 180)

    with pytest.raises(KeyError):
        apply_track_type_color(TYPE, 1, new_color)


def test_table_model_foreground_role_uses_saved_font_color():
    TYPE = {
        3: ("milonga", "Milonga", 10, 20, 30, 40, 1, 2, 3, 255)
    }

    model = milongaSource(None, [[None, None, None, None, None, 3]],
                         ["c0", "c1", "c2", "c3", "c4", "c5"], TYPE)
    index = model.createIndex(0, 0)
    color = model.data(index, Qt.ForegroundRole)

    assert color is not None
    assert color.red() == 1
    assert color.green() == 2
    assert color.blue() == 3
    assert color.alpha() == 255


def test_get_contrast_color_dark_background():
    color = QColor(10, 10, 10)
    assert get_contrast_color(color).name() == QColor(255, 255, 255).name()


def test_get_contrast_color_light_background():
    color = QColor(250, 250, 250)
    assert get_contrast_color(color).name() == QColor(0, 0, 0).name()
