from djtango.qt_compat import QIcon


class VisibilityControlsMixin:
    def _handelHideSource(self):
        if self._dialog.milongaSource.isVisible():
            self._dialog.pushButtonHideDest.setVisible(False)
            self._dialog.pushButtonHideSource.setIcon(QIcon('./djtango/img/hide-right.png'))
            self._dialog.milongaSource.setVisible(False)
            self._dialog.pushButtonClearFilter.setVisible(False)
            self._dialog.comboBoxArtist.setVisible(False)
            self._dialog.comboBoxAlbum.setVisible(False)
            self._dialog.comboBoxGenre.setVisible(False)
            self._dialog.lineEditFilter.setVisible(False)
            self._dialog.pushButtonRandom.setVisible(False)
            self._dialog.labelsongNB_source.setVisible(False)
        else:
            self._dialog.pushButtonHideDest.setVisible(True)
            self._dialog.pushButtonHideSource.setIcon(QIcon('./djtango/img/hide-left.png'))
            self._dialog.milongaSource.setVisible(True)
            self._dialog.pushButtonClearFilter.setVisible(True)
            self._dialog.comboBoxArtist.setVisible(True)
            self._dialog.comboBoxAlbum.setVisible(True)
            self._dialog.comboBoxGenre.setVisible(True)
            self._dialog.lineEditFilter.setVisible(True)
            self._dialog.pushButtonRandom.setVisible(True)
            self._dialog.labelsongNB_source.setVisible(True)

    def _handelHideDest(self):
        if self._dialog.milongaDest.isVisible():
            self._dialog.pushButtonHideSource.setVisible(False)
            self._dialog.pushButtonHideDest.setIcon(QIcon('./djtango/img/hide-left.png'))
            self._dialog.milongaDest.setVisible(False)
            self._dialog.pushButtonMilongaClear.setVisible(False)
            self._dialog.labelMilongaName.setVisible(False)
            self._dialog.pushButtonLoadMilonga.setVisible(False)
            self._dialog.pushButtonDeleteMilonga.setVisible(False)
            self._dialog.pushButtonSaveMilonga.setVisible(False)
            self._dialog.labelSizeDuration.setVisible(False)
            self._dialog.pushButtonInfoMilonga.setVisible(False)
            self._dialog.pushButtonSaveMilongaAs.setVisible(False)
        else:
            self._dialog.pushButtonHideSource.setVisible(True)
            self._dialog.pushButtonHideDest.setIcon(QIcon('./djtango/img/hide-right.png'))
            self._dialog.milongaDest.setVisible(True)
            self._dialog.pushButtonMilongaClear.setVisible(True)
            self._dialog.labelMilongaName.setVisible(True)
            self._dialog.pushButtonLoadMilonga.setVisible(True)
            self._dialog.pushButtonDeleteMilonga.setVisible(True)
            self._dialog.pushButtonSaveMilonga.setVisible(True)
            self._dialog.labelSizeDuration.setVisible(True)
            self._dialog.pushButtonInfoMilonga.setVisible(True)
            self._dialog.pushButtonSaveMilongaAs.setVisible(True)

    def resizeHeaderSource(self, event):
        sizeList = {
            '#': 50,
            'play': 35,
            'genre': 120,
            'year': 50,
            'bpm': 50,
            'duration': 50,
        }

        total = sum(sizeList.values())
        tableSize = self._dialog.milongaSource.width()
        size = int((tableSize - total - 20) / 3)

        self._dialog.milongaSource.horizontalHeader().resizeSection(0, sizeList['#'])
        self._dialog.milongaSource.horizontalHeader().resizeSection(1, sizeList['play'])
        self._dialog.milongaSource.horizontalHeader().resizeSection(2, size)
        self._dialog.milongaSource.horizontalHeader().resizeSection(3, size)
        self._dialog.milongaSource.horizontalHeader().resizeSection(4, size)
        self._dialog.milongaSource.horizontalHeader().resizeSection(5, sizeList['genre'])
        self._dialog.milongaSource.horizontalHeader().resizeSection(6, sizeList['year'])
        self._dialog.milongaSource.horizontalHeader().resizeSection(7, sizeList['bpm'])
        self._dialog.milongaSource.horizontalHeader().resizeSection(8, sizeList['duration'])
