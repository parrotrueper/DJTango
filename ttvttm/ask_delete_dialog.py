from PySide6.QtWidgets import QDialog

from ttvttm.UI_askDelete import Ui_DialogAskDelete


class AskDeleteDialogMixin:
    def _setup_ask_delete_dialog(self):
        self.milongaAskDelete = QDialog()
        self.milongaAskDeleteContent = Ui_DialogAskDelete()
        self.milongaAskDeleteContent.setupUi(self.milongaAskDelete)
