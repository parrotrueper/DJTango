from djtango.UI_milongaName import Ui_DialogMilongaName
from djtango.qt_compat import QDialog


class MilongaNameDialogMixin:
    def _setup_milonga_name_dialog(self):
        self.milongaNameWindow = QDialog()
        self.milongaNameContent = Ui_DialogMilongaName()
        self.milongaNameContent.setupUi(self.milongaNameWindow)
