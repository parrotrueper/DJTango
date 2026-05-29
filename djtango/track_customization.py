import logging

from djtango.gui_helpers import TrackAppearanceDialog
from djtango.qt_compat import QColor, QColorDialog, QDialog, Qt
from djtango.ui_theme import button_style
from djtango.ui_utils import apply_tango_type_color, get_contrast_color

logger = logging.getLogger(__name__)


class TrackCustomizationMixin:
    def _setup_track_customization(self):
        self.colorDialog = QColorDialog()
        self.colorDialog.setOption(QColorDialog.ShowAlphaChannel, True)
        self.colorDialog.setWindowModality(Qt.WindowModal)
        self._colorSelectionMode = 'track'
        self._currentTrackColor = QColor(42, 42, 42, 255)
        self._currentFontColor = None

        self.colorDialog.accepted.connect(self._finalizeColorSelection)
        if hasattr(self.colorDialog, 'currentColorChanged'):
            self.colorDialog.currentColorChanged.connect(self._previewColorDialog)

    def _openTrackAppearanceDialog(self):
        dialog = TrackAppearanceDialog(self.TYPE, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.TYPE.clear()
            self.TYPE.update(dialog.TYPE)
            self.djData.updateType(self.TYPE)
            self._showInfo('Track appearance saved')
            self._updateSideScreen()

    def _selectTangoColor(self):
        color = self.colorDialog.currentColor()
        self._currentTrackColor = color
        self._applyTrackButtonPreview()
        item = self.prefContent.listWidgetTangoType.currentRow()
        try:
            apply_tango_type_color(self.TYPE, item, color)
        except ValueError as err:
            logger.warning('Color selection failed: %s', err)
            self._showInfo(str(err))
        except KeyError as err:
            logger.error('Color selection failed: %s', err)
            self._showInfo('Selected tango type is invalid')

    def _selectTangoFontColor(self):
        color = self.colorDialog.currentColor()
        self._currentFontColor = color
        self._applyTrackButtonPreview()

    def _finalizeColorSelection(self):
        if self._colorSelectionMode == 'font':
            self._selectTangoFontColor()
        else:
            self._selectTangoColor()

    def _contrastColor(self, color):
        luminance = (0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue())
        return '#000000' if luminance > 186 else '#ffffff'

    def _previewColorDialog(self, color):
        if self._colorSelectionMode == 'font':
            self._currentFontColor = color
        else:
            self._currentTrackColor = color
        self._applyTrackButtonPreview()

    def _openColorDialog(self, mode):
        self._colorSelectionMode = mode
        if mode == 'track' and self._currentTrackColor is not None:
            try:
                self.colorDialog.setCurrentColor(self._currentTrackColor)
            except Exception:
                pass
        elif mode == 'font' and self._currentFontColor is not None:
            try:
                self.colorDialog.setCurrentColor(self._currentFontColor)
            except Exception:
                pass
        self.colorDialog.show()

    def _applyTrackButtonPreview(self):
        if self._currentTrackColor is None:
            return

        if self._currentFontColor is None:
            self._currentFontColor = get_contrast_color(self._currentTrackColor)
        if hasattr(self.prefContent, 'selectColorButton'):
            self.prefContent.selectColorButton.setStyleSheet(
                button_style(self._currentTrackColor, get_contrast_color(self._currentTrackColor))
            )
        if hasattr(self.prefContent, 'selectFontColorButton'):
            self.prefContent.selectFontColorButton.setStyleSheet(
                button_style(self._currentFontColor, get_contrast_color(self._currentFontColor))
            )

    def _selectTangoChange(self):
        item = self.prefContent.listWidgetTangoType.currentRow()
        if item < 0:
            logger.debug('_selectTangoChange called with no selection')
            return

        key = item + 1
        if key not in self.TYPE:
            logger.error('_selectTangoChange invalid tango type key: %s', key)
            return

        R = self.TYPE[key][2]
        G = self.TYPE[key][3]
        B = self.TYPE[key][4]
        T = self.TYPE[key][5]
        self._currentTrackColor = QColor(R, G, B, T)
        self._applyTrackButtonPreview()
