from PySide6.QtWidgets import QWidget

from ttvttm.UI_tapbpm import Ui_tapDialog


class TapDialogMixin:
    def _setup_tap_window(self):
        self.tapWindow = QWidget()
        self.tapContent = Ui_tapDialog()
        self.tapContent.setupUi(self.tapWindow)
