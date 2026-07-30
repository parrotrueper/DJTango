from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from ttvttm.UI_infos import Ui_infos


class InfoWindowMixin:
    def _setup_info_window(self):
        self.infoWindow = QWidget()
        self.infoContent = Ui_infos()
        self.infoContent.setupUi(self.infoWindow)
        self.infoWindow.setWindowFlags(Qt.FramelessWindowHint)
