from djtango.UI_selectmilonga import Ui_selectmilonga
from djtango.qt_compat import QDialog


class MilongaSelectDialogMixin:
    def _setup_milonga_select_dialog(self):
        self.selectMilongaListWindow = QDialog()
        self.selectMilongaListContent = Ui_selectmilonga()
        self.selectMilongaListContent.setupUi(self.selectMilongaListWindow)
