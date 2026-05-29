from djtango.UI_infos import Ui_infos
from djtango.qt_compat import QWidget, Qt


class InfoWindowMixin:
    def _setup_info_window(self):
        self.infoWindow = QWidget()
        self.infoContent = Ui_infos()
        self.infoContent.setupUi(self.infoWindow)
        self.infoWindow.setWindowFlags(Qt.FramelessWindowHint)
