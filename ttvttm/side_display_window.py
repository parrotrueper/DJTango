from PySide6.QtWidgets import QWidget

from ttvttm.UI_sideDisplay import Ui_sideDisplay


class SideDisplayWindowMixin:
    def _setup_side_window(self):
        self.sideWindow = QWidget()
        self.sideContent = Ui_sideDisplay()
        self.sideContent.setupUi(self.sideWindow)
        self.sideContent.PBLayout.addWidget(self.bar)
