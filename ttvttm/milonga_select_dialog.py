from PySide6.QtWidgets import QDialog

from ttvttm.UI_selectmilonga import Ui_selectmilonga


class MilongaSelectDialogMixin:
    def _setup_milonga_select_dialog(self):
        self.selectMilongaListWindow = QDialog()
        self.selectMilongaListContent = Ui_selectmilonga()
        self.selectMilongaListContent.setupUi(self.selectMilongaListWindow)
