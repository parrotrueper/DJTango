import threading
import time

from djtango.UI_trackAppearance import Ui_trackAppearance
from djtango.qt_compat import QColor, QColorDialog, QDialog, QThread, QMessageBox, Qt, QtWidgets
from djtango.ui_theme import button_style, track_preview_style
from djtango.ui_utils import get_contrast_color, get_type_font_color, set_type_font_color, apply_track_type_color


class TrackAppearanceDialog(QDialog):
    def __init__(self, TYPE, font_colors=None, parent=None):
        super().__init__(parent)
        self.original_TYPE = TYPE
        self.TYPE = dict(TYPE)
        self.font_colors = dict(font_colors) if font_colors is not None else {}
        for key, type_item in self.TYPE.items():
            font_color = get_type_font_color(type_item)
            if font_color is not None:
                self.font_colors[key] = font_color
        self._colorSelectionMode = 'track'
        self._currentTrackColor = None
        self._currentFontColor = None
        self._currentFont = None
        self._currentRow = 0
        self.colorDialog = QColorDialog(self)
        self.colorDialog.setOption(QColorDialog.ShowAlphaChannel, True)
        self.colorDialog.setWindowModality(Qt.WindowModal)
        self.colorDialog.accepted.connect(self._finalizeColorSelection)
        if hasattr(self.colorDialog, 'currentColorChanged'):
            self.colorDialog.currentColorChanged.connect(self._previewColorDialog)

        self.ui = Ui_trackAppearance()
        self.ui.setupUi(self)
        self.typesList = self.ui.typesList
        self.editTypeField = self.ui.editTypeField
        self.addTypeButton = self.ui.addTypeButton
        self.removeTypeButton = self.ui.removeTypeButton
        self.previewLabel = self.ui.previewLabel
        self.selectColorButton = self.ui.selectColorButton
        self.selectFontColorButton = self.ui.selectFontColorButton
        self.selectFontButton = self.ui.selectFontButton
        self.buttonBox = self.ui.buttonBox

        self.typesList.currentRowChanged.connect(self._selectTangoChange)
        self.addTypeButton.clicked.connect(self._addTangoType)
        self.removeTypeButton.clicked.connect(self._removeTangoType)
        self.selectColorButton.clicked.connect(lambda: self._openColorDialog('track'))
        self.selectFontColorButton.clicked.connect(lambda: self._openColorDialog('font'))
        self.selectFontButton.clicked.connect(self._openFontDialog)
        self.buttonBox.accepted.connect(self._onAccepted)
        self.buttonBox.rejected.connect(self.reject)
        self.applyButton = self.ui.applyButton
        self.applyButton.clicked.connect(self._applyTypeChanges)

        self._populateTypes()

    def _populateTypes(self):
        self.typesList.clear()
        self._typeKeys = sorted(self.TYPE.keys())
        for key in self._typeKeys:
            self.typesList.addItem(self.TYPE[key][1])
        self.typesList.setCurrentRow(0)

    def _getCurrentTypeKey(self):
        row = self.typesList.currentRow()
        return self._typeKeys[row] if 0 <= row < len(self._typeKeys) else None

    def _addTangoType(self):
        text = self.editTypeField.text().strip()
        if not text:
            return
        next_key = max(self.TYPE.keys(), default=0) + 1
        default_color = QColor(42, 42, 42, 255)
        default_font = get_contrast_color(default_color)
        self.TYPE[next_key] = (
            next_key,
            text,
            42,
            42,
            42,
            255,
            default_font.red(),
            default_font.green(),
            default_font.blue(),
            default_font.alpha(),
        )
        self.editTypeField.clear()
        self._populateTypes()
        self.typesList.setCurrentRow(self.typesList.count() - 1)

    def _removeTangoType(self):
        row = self.typesList.currentRow()
        if row < 5:
            QMessageBox.information(self, 'Track Appearance', 'This item is not removable')
            return
        key = self._getCurrentTypeKey()
        if key is None:
            return
        self.typesList.takeItem(row)
        self.TYPE.pop(key, None)
        self._populateTypes()

    def _selectTangoChange(self, row):
        if row < 0:
            return
        self._currentRow = row
        key = self._getCurrentTypeKey()
        type_item = self.TYPE.get(key)
        if not type_item:
            return
        self._currentTrackColor = QColor(type_item[2], type_item[3], type_item[4], type_item[5])
        self._currentFontColor = get_type_font_color(type_item) or self.font_colors.get(key) or get_contrast_color(self._currentTrackColor)
        self._applyTrackButtonPreview()

    def _selectTangoColor(self):
        color = self.colorDialog.currentColor()
        self._currentTrackColor = color
        key = self._getCurrentTypeKey()
        if key is None:
            return
        self._currentFontColor = self.font_colors.get(key, get_contrast_color(color))
        type_entry = self.TYPE[key]
        extra = type_entry[6:] if len(type_entry) > 6 else ()
        self.TYPE[key] = (
            type_entry[0],
            type_entry[1],
            color.red(),
            color.green(),
            color.blue(),
            color.alpha(),
        ) + extra
        self._applyTrackButtonPreview()

    def _selectTangoFontColor(self):
        color = self.colorDialog.currentColor()
        self._currentFontColor = color
        key = self._getCurrentTypeKey()
        if key is None:
            return
        self.font_colors[key] = color
        self.TYPE[key] = set_type_font_color(self.TYPE[key], color)
        self._applyTrackButtonPreview()

    def _finalizeColorSelection(self):
        if self._colorSelectionMode == 'font':
            self._selectTangoFontColor()
        else:
            self._selectTangoColor()

    def _previewColorDialog(self, color):
        if self._colorSelectionMode == 'font':
            self._currentFontColor = color
        else:
            self._currentTrackColor = color
        self._applyTrackButtonPreview()

    def _openColorDialog(self, mode):
        self._colorSelectionMode = mode
        if mode == 'track' and self._currentTrackColor is not None:
            self.colorDialog.setCurrentColor(self._currentTrackColor)
        elif mode == 'font' and self._currentFontColor is not None:
            self.colorDialog.setCurrentColor(self._currentFontColor)
        self.colorDialog.show()

    def _openFontDialog(self):
        current_font = self._currentFont or self.previewLabel.font()
        font_dialog = QtWidgets.QFontDialog(self)
        font_dialog.setCurrentFont(current_font)
        font_dialog.setWindowTitle('Choose font')
        if font_dialog.exec() == QDialog.Accepted:
            self._currentFont = font_dialog.selectedFont()
            self._applyTrackButtonPreview()

    def _applyTrackButtonPreview(self):
        if self._currentTrackColor is None:
            return
        if self._currentFontColor is None:
            self._currentFontColor = get_contrast_color(self._currentTrackColor)
        self.previewLabel.setStyleSheet(track_preview_style(self._currentTrackColor, self._currentFontColor))
        if self._currentFont is not None:
            self.previewLabel.setFont(self._currentFont)
        self.selectColorButton.setStyleSheet(button_style(self._currentTrackColor, get_contrast_color(self._currentTrackColor)))
        self.selectFontColorButton.setStyleSheet(button_style(self._currentFontColor, get_contrast_color(self._currentFontColor)))
        self.selectFontButton.setStyleSheet(button_style(self._currentFontColor, get_contrast_color(self._currentFontColor)))

    def _saveTypeChanges(self):
        """Persist the current dialog TYPE changes back to the original parent TYPE dict."""
        self.original_TYPE.clear()
        self.original_TYPE.update(self.TYPE)

    def _applyGlobalFontToParent(self, parent):
        if self._currentFont is None:
            return
        if hasattr(parent, '_dialog'):
            if hasattr(parent._dialog, 'milongaSource'):
                parent._dialog.milongaSource.setFont(self._currentFont)
            if hasattr(parent._dialog, 'milongaDest'):
                parent._dialog.milongaDest.setFont(self._currentFont)
        parent.trackAppearanceFont = self._currentFont

    def _applyTypeChanges(self):
        self._saveTypeChanges()
        parent = self.parent()
        if parent is not None:
            self._applyGlobalFontToParent(parent)
            if hasattr(parent, 'djData') and hasattr(parent.djData, 'updateType'):
                try:
                    parent.djData.updateType(parent.TYPE)
                except Exception:
                    pass
            if hasattr(parent, '_showInfo'):
                parent._showInfo('Track appearance applied')
            if hasattr(parent, '_updateSideScreen'):
                parent._updateSideScreen()

    def _onAccepted(self):
        self._applyTypeChanges()
        self.accept()


class InfoThreading(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self)
        self.exiting = False
        self.timelaps = 5

    def __del__(self):
        self.exiting = True
        try:
            self.wait()
        except RuntimeError:
            pass

    def render(self, timelaps):
        self.timelaps = timelaps
        self.start()

    def run(self):
        now = time.time()
        while not self.exiting and time.time() - now < self.timelaps:
            time.sleep(1)


class MyTimer:
    def __init__(self, tempo, target, args=None, kwargs=None):
        self._target = target
        self._args = args or []
        self._kwargs = kwargs or {}
        self._tempo = tempo

    def _run(self):
        self._timer = threading.Timer(self._tempo, self._run)
        self._timer.start()
        self._target(*self._args, **self._kwargs)

    def start(self):
        self._timer = threading.Timer(self._tempo, self._run)
        self._timer.start()

    def stop(self):
        self._timer.cancel()
