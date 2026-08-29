from PySide6 import QtCore


class PreferencesHelperMixin:
    def _addTangoType(self):
        text = self.prefContent.lineEditTangoType.text()
        if text == "":
            self._showInfo("put some text in the field")
            return

        self.prefContent.listWidgetTangoType.addItem(text)
        self.prefContent.lineEditTangoType.setText("")
        lastRow = self.prefContent.listWidgetTangoType.count() - 1
        self.TYPE[lastRow + 1] = (lastRow + 1, text, 42, 42, 42, 255)
        self.prefContent.listWidgetTangoType.setCurrentRow(lastRow, QtCore.QItemSelectionModel.ClearAndSelect)

    def _removeTangoType(self):
        row = self.prefContent.listWidgetTangoType.currentRow()
        if row > 4:
            self.prefContent.listWidgetTangoType.takeItem(row)
        else:
            self._showInfo("this item is not removable")

    def handle_cortina_checkbox(self):
        if self._dialog.checkBoxLetCortinaUntilEnd.isChecked:
            self.bar.setRange(0, self.duration * 1000)
        else:
            self.bar.setRange(0, self.FadeOutTime)
