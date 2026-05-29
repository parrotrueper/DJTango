from djtango.UI_sideDisplay import Ui_sideDisplay
from djtango.qt_compat import QWidget


class SideDisplayWindowMixin:
    def _setup_side_window(self):
        self.sideWindow = QWidget()
        self.sideContent = Ui_sideDisplay()
        self.sideContent.setupUi(self.sideWindow)
        self.sideContent.PBLayout.addWidget(self.bar)
