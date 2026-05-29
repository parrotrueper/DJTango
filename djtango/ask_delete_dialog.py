from djtango.UI_askDelete import Ui_DialogAskDelete
from djtango.qt_compat import QDialog


class AskDeleteDialogMixin:
    def _setup_ask_delete_dialog(self):
        self.milongaAskDelete = QDialog()
        self.milongaAskDeleteContent = Ui_DialogAskDelete()
        self.milongaAskDeleteContent.setupUi(self.milongaAskDelete)
