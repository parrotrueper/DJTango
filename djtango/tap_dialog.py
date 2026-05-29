from djtango.UI_tapbpm import Ui_tapDialog
from djtango.qt_compat import QWidget


class TapDialogMixin:
    def _setup_tap_window(self):
        self.tapWindow = QWidget()
        self.tapContent = Ui_tapDialog()
        self.tapContent.setupUi(self.tapWindow)
