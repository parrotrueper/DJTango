from PySide6.QtWidgets import QDialog

from ttvttm.UI_milongaName import Ui_DialogMilongaName


class MilongaNameDialogMixin:
    def _setup_milonga_name_dialog(self):
        self.milongaNameWindow = QDialog()
        self.milongaNameContent = Ui_DialogMilongaName()
        self.milongaNameContent.setupUi(self.milongaNameWindow)
