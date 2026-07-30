from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from ttvttm.UI_infosMilonga import Ui_infosMilonga


class InfoMilongaWindowMixin:
    def _setup_info_milonga_window(self):
        self.infoMilongaWindow = QWidget()
        self.infoMilongaContent = Ui_infosMilonga()
        self.infoMilongaContent.setupUi(self.infoMilongaWindow)
        self.infoMilongaWindow.setWindowFlags(Qt.FramelessWindowHint)
