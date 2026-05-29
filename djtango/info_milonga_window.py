from djtango.UI_infosMilonga import Ui_infosMilonga
from djtango.qt_compat import QWidget, Qt


class InfoMilongaWindowMixin:
    def _setup_info_milonga_window(self):
        self.infoMilongaWindow = QWidget()
        self.infoMilongaContent = Ui_infosMilonga()
        self.infoMilongaContent.setupUi(self.infoMilongaWindow)
        self.infoMilongaWindow.setWindowFlags(Qt.FramelessWindowHint)
