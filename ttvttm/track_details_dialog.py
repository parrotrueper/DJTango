from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from ttvttm.UI_details import Ui_details


class TrackDetailsDialogMixin:
    def _setup_track_details_window(self):
        self.propWindow = QWidget()
        self.detailsContent = Ui_details()
        self.detailsContent.setupUi(self.propWindow)
        self.propWindow.setWindowFlags(Qt.FramelessWindowHint)

        for i in range(1, len(self.TYPE) + 1):
            self.detailsContent.comboBoxTangoType.insertItem(i - 1, self.TYPE[i][1].title())
