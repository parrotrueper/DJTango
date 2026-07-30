import sys

from PySide6.QtCore import QItemSelectionModel, QModelIndex, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QDialog

from ttvttm.UI_preferences import Ui_preferences


class PreferencesMixin:
    def _setup_preferences_window(self):
        self.prefWindow = QDialog()
        self.prefContent = Ui_preferences()
        self.prefContent.setupUi(self.prefWindow)
        self.prefContent.lineEditSongDir.setText(self.audioPath)
        self.prefContent.spinBoxFadeOut.setValue(int(self.durationFadOut / 1000))
        self.prefContent.spinBoxCortinaDuration.setValue(int(self.FadOutTime / 1000))
        self.prefContent.checkBoxWriteTags.setCheckState(Qt.Checked if self.writeTag else Qt.Unchecked)
        self.prefContent.checkBoxNormalize.setCheckState(Qt.Checked if self.normalize else Qt.Unchecked)

        for i in self.TYPE.keys():
            self.prefContent.listWidgetTangoType.insertItem(i - 1, self.TYPE[i][1])
            R = self.TYPE[i][2]
            G = self.TYPE[i][3]
            B = self.TYPE[i][4]
            T = self.TYPE[i][5]
            self.colorDialog.setCustomColor(i, QColor(R, G, B, T))

    def _handelPrefClose(self):
        self.prefWindow.exec()
        if self.prefWindow.result() == 0:
            return

        sys.stdout.write(str(self.prefWindow.result()))
        self._tangoList.songpath = self.prefContent.lineEditSongDir.text()
        self.durationFadOut = self.prefContent.spinBoxFadeOut.value() * 1000
        self.FadOutTime = self.prefContent.spinBoxCortinaDuration.value() * 1000
        self.stepFadOut = self.durationFadOut / (
            self.player.notifyInterval() if hasattr(self.player, "notifyInterval") else 100
        )
        self.writeTag = self.prefContent.checkBoxWriteTags.checkState()
        self.normalize = self.prefContent.checkBoxNormalize.checkState()

        self.djData.updateProperties(self.durationFadOut, self.FadOutTime, self.writeTag, self.normalize, self.TYPE)
        if self.destModel.rowCount(QModelIndex()) > 1:
            self.updateMilongaInfos()

    def _addTangoType(self):
        text = self.prefContent.lineEditTangoType.text()
        if text == "":
            self._showInfo("put some text in the field")
            return

        self.prefContent.listWidgetTangoType.addItem(text)
        self.prefContent.lineEditTangoType.setText("")
        lastRow = self.prefContent.listWidgetTangoType.count() - 1
        self.TYPE[lastRow + 1] = (lastRow + 1, text, 42, 42, 42, 255)
        self.prefContent.listWidgetTangoType.setCurrentRow(lastRow, QItemSelectionModel.ClearAndSelect)

    def _removeTangoType(self):
        row = self.prefContent.listWidgetTangoType.currentRow()
        if row > 4:
            self.prefContent.listWidgetTangoType.takeItem(row)
        else:
            self._showInfo("this item is not removable")
