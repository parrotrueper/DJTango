from djtango.qt_compat import QColor, QDesktopWidget, QFont, QFontMetrics, QModelIndex, QtCore
from djtango.ui_utils import get_contrast_color, get_type_font_color
from djtango.ui_theme import qss_color, side_display_frame_style, side_display_label_style

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class SideDisplayMixin:
    def _handelDisplaySideScreen(self):
        self._updateSideScreen()
        self.desk = QDesktopWidget()

        mainAppDeskID = self.desk.screenNumber(self)
        sideDispDeskID = 0
        if self.desk.screenCount() > 1:
            sideDispDeskID = 1 if mainAppDeskID == 0 else 0

        if not self.sideWindow.isVisible():
            geom = self.desk.availableGeometry(sideDispDeskID)
            if self.desk.screenCount() > 1:
                self.sideWindow.move(geom.x(), geom.y())
                self.sideWindow.showFullScreen()
            else:
                width = max(int(geom.width() * 0.45), 600)
                height = max(int(geom.height() * 0.85), 400)
                x = geom.x() + geom.width() - width - 20
                y = geom.y() + 20
                self.sideWindow.setGeometry(x, y, width, height)
                self.sideWindow.show()
            self._dialog.actionDisplay_side_screen.setChecked(True)
        else:
            self.sideWindow.hide()
            self._dialog.actionDisplay_side_screen.setChecked(False)

    def _handelFullScren(self):
        if not self.isFullScreen():
            self.showFullScreen()
        else:
            self.showNormal()

    def _updateSideScreen(self, lastsong=False):
        if self.curTango is not None:
            nextTanda = self.getNextTanda()
            self.sideContent.labelArtist.setText(self.curTango.artist)
            if self.curTango.type == 4:
                self.sideContent.labelType.setText(self.TYPE[self.curTango.type][1].upper())
            else:
                if not self._isMilongaPlaying:
                    self.sideContent.labelType.setText(self.TYPE[self.curTango.type][1].upper())
                else:
                    self.sideContent.labelType.setText(
                        self.TYPE[self.curTango.type][1].upper()
                        + " - "
                        + str(nextTanda['nbintanda'] - nextTanda['num'] + 1)
                        + "/"
                        + str(nextTanda['nbintanda'])
                    )

            if self.curTango.year == 0:
                self.sideContent.labelTitle.setText(self.curTango.title)
            else:
                self.sideContent.labelTitle.setText(self.curTango.title + " ( " + str(self.curTango.year) + " )")

            if not self._isMilongaPlaying:
                self.sideContent.labelNextTanda.setText("LIST PLAYING :-)")
            elif nextTanda['type'] == 'last':
                self.sideContent.labelNextTanda.setText("LAST TANDA :-(")
            else:
                self.sideContent.labelNextTanda.setText("NEXT TANDA  |  " + str(nextTanda['type']))

            R = self.TYPE[self.curTango.type][2]
            G = self.TYPE[self.curTango.type][3]
            B = self.TYPE[self.curTango.type][4]
            T = self.TYPE[self.curTango.type][5]
            self.sideContent.frameType.setStyleSheet(
                _fromUtf8(side_display_frame_style(QColor(R, G, B, T)))
            )

            fontColor = get_type_font_color(self.TYPE.get(self.curTango.type))
            if fontColor is None:
                fontColor = get_contrast_color(QColor(R, G, B, T))
            self._currentSideLabelColor = fontColor
            self.sideContent.labelType.setStyleSheet(
                _fromUtf8(side_display_label_style(fontColor))
            )
            self._updateLabelSize()
        else:
            self.sideContent.labelType.setText('NO TRACK')
            self.sideContent.labelArtist.setText('')
            self.sideContent.labelTitle.setText('No track selected')
            self.sideContent.labelSinger.setText('')
            self.sideContent.labelNextTanda.setText('')
            self.sideContent.frameType.setStyleSheet(
                _fromUtf8(side_display_frame_style(QColor(0, 0, 0, 255)))
            )
            self.sideContent.labelType.setStyleSheet(
                _fromUtf8(side_display_label_style(QColor(0, 255, 255, 255)))
            )

    def _updateLabelSize(self):
        size1 = 100
        size2 = 70
        nextTandaSize = 70
        recalculate = True
        coef = 0.9

        while recalculate:
            font1 = QFont("sans", size1)
            font2 = QFont("sans", size2)
            metrics = QFontMetrics(font2)
            if metrics.boundingRect(str(self.sideContent.labelTitle.text())).width() > self.sideWindow.width() * coef:
                recalculate = True
            else:
                recalculate = False

            if not recalculate:
                metrics = QFontMetrics(font1)
                if metrics.boundingRect(self.sideContent.labelArtist.text()).width() > self.sideWindow.width() * coef:
                    recalculate = True
                elif metrics.boundingRect(self.sideContent.labelType.text()).width() > self.sideWindow.width() * coef:
                    recalculate = True
                else:
                    recalculate = False

            if recalculate:
                size1 -= 1
                size2 = round(size1 * 0.7)

        recalculate = True
        while recalculate:
            font1 = QFont("sans, bold", nextTandaSize)
            metrics = QFontMetrics(font1)
            if metrics.boundingRect(self.sideContent.labelNextTanda.text()).width() > self.sideWindow.width() * coef:
                recalculate = True
            else:
                recalculate = False
            nextTandaSize -= 1

        self.sideContent.labelArtist.setStyleSheet(_fromUtf8(
            "QLabel{\n margin-top: 30px;\n margin-left: 20px;\n margin-bottom: 25px;\n  font-weight: bold;\n color: white;\n font-size: "
            + str(size1)
            + "px;\n   font-family: \"sans\"\n}"
        ))
        label_color = getattr(self, '_currentSideLabelColor', QColor(255, 255, 255))
        self.sideContent.labelType.setStyleSheet(_fromUtf8(
            f"background-color: \"transparent\";\n font-weight: bold;\n    color: {qss_color(label_color)};\n font-size: {size1 - 3}px;\n margin-left: 20px;\n    font-family: \"sans\"\n"
        ))
        self.sideContent.labelTitle.setStyleSheet(_fromUtf8(
            "QLabel{\n  margin-left: 20px;\n    color: white;\n font-size: "
            + str(size2)
            + "px;\n  font-family: \"sans\"\n}"
        ))
        self.sideContent.labelNextTanda.setStyleSheet(_fromUtf8(
            "QLabel{\n font-family: \"sans\";\n  font-weight: bold;\n color: white;\n font-size: "
            + str(nextTandaSize)
            + "px;\n}"
        ))
