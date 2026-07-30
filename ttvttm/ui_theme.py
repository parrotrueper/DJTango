
from PySide6.QtGui import QColor

APP_STYLE = """
QWidget, QMenuBar, QMenu, QToolTip {
    background-color: #000000;
    color: #00ffff;
}
QMainWindow, QDialog, QMessageBox, QProgressDialog {
    background-color: #000000;
    color: #00ffff;
}
QPushButton {
    background-color: #111111;
    color: #00ffff;
    border: 1px solid #006666;
    border-radius: 4px;
    padding: 4px 8px;
}
QPushButton:hover {
    background-color: #003333;
}
QPushButton:pressed {
    background-color: #005555;
}
QLineEdit, QSpinBox, QListWidget, QComboBox, QTableView, QHeaderView, QAbstractItemView {
    background-color: #000000;
    color: #00ffff;
    border: 1px solid #006666;
}
QComboBox::drop-down {
    border-left: 1px solid #006666;
}
QComboBox QListView {
    background-color: #000000;
    color: #00ffff;
}
QTableView {
    gridline-color: #003333;
}
QTableView::item:selected, QListWidget::item:selected, QAbstractItemView::item:selected {
    background-color: rgb(121,194,255);
    color: rgb(255,255,255);
}
QHeaderView::section {
    background-color: #001a1a;
    color: #00ffff;
    border: 1px solid #006666;
}
QMenuBar {
    background-color: #000000;
}
QMenuBar::item {
    background: transparent;
    color: #00ffff;
}
QMenuBar::item:selected {
    background: #003333;
}
QMenu {
    background-color: #000000;
    color: #00ffff;
    border: 1px solid #006666;
}
QMenu::item:selected {
    background-color: #003333;
    color: #00ffff;
}
QProgressBar {
    border: 1px solid #00ffff;
    border-radius: 5px;
    background-color: #000000;
    color: #00ffff;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #00ffff;
    width: 20px;
}
QSlider::groove:horizontal {
    border: 1px solid #006666;
    height: 10px;
    background: #000000;
}
QSlider::handle:horizontal {
    background: #00ffff;
    border: 1px solid #006666;
    width: 10px;
    margin: -2px -2px;
    border-radius: 5px;
}
QSlider::sub-page:horizontal {
    background: #00ffff;
}
"""

DIALOG_STYLE = APP_STYLE
PROGRESS_DIALOG_STYLE = APP_STYLE


def load_app_theme(app):
    if app is not None:
        app.setStyleSheet(APP_STYLE)


def dialog_style():
    return DIALOG_STYLE


def progress_dialog_style():
    return PROGRESS_DIALOG_STYLE


def _css_alpha(alpha):
    if alpha is None:
        return "1"
    if isinstance(alpha, float):
        return str(alpha)
    if isinstance(alpha, int):
        return str(round(alpha / 255.0, 3))
    return str(alpha)


def qss_color(color):
    if isinstance(color, QColor):
        if color.alpha() == 255:
            return f"rgb({color.red()},{color.green()},{color.blue()})"
        return f"rgba({color.red()},{color.green()},{color.blue()},{_css_alpha(color.alpha())})"
    return str(color)


def track_preview_style(background_color, font_color):
    return (
        f"background-color: {qss_color(background_color)}; color: {qss_color(font_color)}; border: 1px solid #5a5a5a; padding: 10px;"
    )


def button_style(background_color, font_color):
    return (
        f"background-color: {qss_color(background_color)}; color: {qss_color(font_color)}; border: 1px solid #5a5a5a; padding: 6px 12px;"
    )


def side_display_frame_style(background_color):
    return (
        f"QFrame{{ background-color: {qss_color(background_color)}; border: 0px; margin-right: 0px; margin-bottom: 0px; "
        "margin-left: 0px; spacing: 0px; padding: 0px; }} QFrame::layout {{ margin: 0px }}"
    )


def side_display_label_style(font_color):
    return (
        f'font-weight: bold; color: {qss_color(font_color)}; font-size: 100px; font-family: "sans"; '
        'background-color: transparent;'
    )
