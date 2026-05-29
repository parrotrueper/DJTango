from djtango.qt_compat import QAbstractItemView, QModelIndex, Qt


class TrackPropertiesMixin:
    def enableTableView(self):
        self._dialog.milongaSource.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def disabledTableView(self):
        self._dialog.milongaSource.setSelectionMode(QAbstractItemView.NoSelection)

    def handelOpenPropWidow(self):
        self.disabledTableView()
        self._dialog.milongaSource.setSortingEnabled(False)
        self.updateTangoProp()
        self.TangoBeforeChange = self._tangoList.tangos[self.curTangoEditing]
        self.propWindow.show()
        self.scanningDir = True

    def _handlePropWindowClose(self):
        self.updateTangoSong()
        self.TangoBeforeChange = self._tangoList.tangos[self.curTangoEditing]
        self.propWindow.close()
        self._dialog.milongaSource.setSortingEnabled(True)
        self.enableTableView()
        self.scanningDir = False
        self._dialog.labelsongNB_source.setText(str(self.sourceProxyModel.rowCount(QModelIndex())) + ' song(s)')

    def _handlePropWindowNext(self):
        self.enableTableView()
        self.updateTangoSong()
        self.TangoBeforeChange = self._tangoList.tangos[self.curTangoEditing]
        if self.curLibraryRow + 1 < self.sourceProxyModel.rowCount(QModelIndex()):
            self.curLibraryRow += 1
            index = self.sourceProxyModel.index(self.curLibraryRow, 0)
            self.curTangoEditing = self.sourceProxyModel.data(index, Qt.DisplayRole)
            self._dialog.milongaSource.selectRow(self.curLibraryRow)
            self.updateTangoProp()
        self._dialog.labelsongNB_source.setText(str(self.sourceProxyModel.rowCount(QModelIndex())) + ' song(s)')
        self.disabledTableView()
        self.scanningDir = True

    def _handlePropWindowPrevious(self):
        self.enableTableView()
        self.updateTangoSong()
        if self.curLibraryRow > 0:
            self.curLibraryRow -= 1
            self._dialog.milongaSource.selectRow(self.curLibraryRow)
            index = self.sourceProxyModel.index(self.curLibraryRow, 0)
            self.curTangoEditing = self.sourceProxyModel.data(index, Qt.DisplayRole)
            self.updateTangoProp()
        self.disabledTableView()
        self.scanningDir = True
        self._dialog.labelsongNB_source.setText(str(self.sourceProxyModel.rowCount(QModelIndex())) + ' song(s)')

    def updateTangoProp(self):
        indexes = self._dialog.milongaSource.selectionModel().selectedRows()
        if len(indexes) > 1:
            self.detailsContent.nextButton.setVisible(False)
            self.detailsContent.previousButton.setVisible(False)
            self.detailsContent.textPath.setText('')
        else:
            self.detailsContent.nextButton.setVisible(True)
            self.detailsContent.previousButton.setVisible(True)
            self.curTangoEditing = self.sourceProxyModel.data(indexes[0], Qt.DisplayRole)
            self.curLibraryRow = indexes[0].row()
            self.detailsContent.textPath.setText(self._tangoList.tangos[self.curTangoEditing].path)
            if self.detailsContent.checkBoxPlayMusic.isChecked():
                self._isClicked = True
                self.curTango = self._tangoList.tangos[self.curTangoEditing]
                self._load_new_media()
                self._play_media()
        sameFieldValue = self.getSameFieldInfos(indexes)
        if sameFieldValue['artist'] is False:
            self.detailsContent.lineEditArtist.setText('-')
        elif sameFieldValue['artist'] != 'Unknown':
            self.detailsContent.lineEditArtist.setText(sameFieldValue['artist'])
        else:
            self.detailsContent.lineEditArtist.setText('')
        if sameFieldValue['title'] is False:
            self.detailsContent.lineEditTitle.setText('-')
        elif sameFieldValue['title'] != 'Unknown':
            self.detailsContent.lineEditTitle.setText(sameFieldValue['title'])
        else:
            self.detailsContent.lineEditTitle.setText('')
        if sameFieldValue['album'] is False:
            self.detailsContent.lineEditAlbum.setText('-')
        elif sameFieldValue['album'] != 'Unknown':
            self.detailsContent.lineEditAlbum.setText(sameFieldValue['album'])
        else:
            self.detailsContent.lineEditAlbum.setText('')
        if sameFieldValue['type'] is False:
            self.detailsContent.comboBoxTangoType.setCurrentIndex(-1)
        else:
            self.detailsContent.comboBoxTangoType.setCurrentIndex(sameFieldValue['type'] - 1)
        if sameFieldValue['year'] is False:
            self.detailsContent.spinBoxYear.setValue(-1)
        else:
            self.detailsContent.spinBoxYear.setValue(sameFieldValue['year'])

    def getSameFieldInfos(self, indexes):
        sameFieldValue = {}
        for index in indexes:
            tangoID = self.sourceProxyModel.data(index, Qt.DisplayRole)
            tango = self._tangoList.tangos[tangoID]
            sameFieldValue['artist'] = tango.artist if 'artist' not in sameFieldValue else sameFieldValue['artist'] if sameFieldValue['artist'] == tango.artist else False
            sameFieldValue['album'] = tango.album if 'album' not in sameFieldValue else sameFieldValue['album'] if sameFieldValue['album'] == tango.album else False
            sameFieldValue['type'] = tango.type if 'type' not in sameFieldValue else sameFieldValue['type'] if sameFieldValue['type'] == tango.type else False
            sameFieldValue['year'] = tango.year if 'year' not in sameFieldValue else sameFieldValue['year'] if sameFieldValue['year'] == tango.year else False
            sameFieldValue['title'] = tango.title if 'title' not in sameFieldValue else sameFieldValue['title'] if sameFieldValue['title'] == tango.title else False
        return sameFieldValue

    def isSomethingChanged(self):
        return not (
            self.TangoBeforeChange.artist == self.detailsContent.lineEditArtist.text() and
            self.TangoBeforeChange.title == self.detailsContent.lineEditTitle.text() and
            self.TangoBeforeChange.year == self.detailsContent.spinBoxYear.value() and
            self.TangoBeforeChange.type == self.detailsContent.comboBoxTangoType.currentIndex() + 1 and
            self.TangoBeforeChange.album == self.detailsContent.lineEditAlbum.text()
        )

    def updateTangoSong(self):
        if not self.isSomethingChanged():
            return
        self.scanningDir = True
        indexes = self._dialog.milongaSource.selectionModel().selectedRows()
        for index in indexes:
            tangoID = self.sourceProxyModel.data(index, Qt.DisplayRole)
            tango = self._tangoList.tangos[tangoID]
            artist = self.detailsContent.lineEditArtist.text()
            title = self.detailsContent.lineEditTitle.text()
            album = self.detailsContent.lineEditAlbum.text()
            if artist != '-':
                tango.artist = artist or 'Unknown'
            if title != '-':
                tango.title = title or 'Unknown'
            if self.detailsContent.spinBoxYear.value() > 0:
                tango.year = self.detailsContent.spinBoxYear.value()
            if album != '-':
                tango.album = album or 'Unknown'
            if self.detailsContent.comboBoxTangoType.currentIndex() > -1:
                tango.type = self.detailsContent.comboBoxTangoType.currentIndex() + 1
            if self.normalize == 2:
                self._tangoList.normalizeTango(tangoID, self.TYPE)
            if self.writeTag == 2:
                tango.writeTags(self.TYPE)
            data = tango.list()
            for count, cdata in enumerate(data):
                list_index = self.sourceProxyModel.index(index.row(), count)
                self.sourceProxyModel.setData(list_index, cdata, Qt.EditRole)
            self.djData.updateTango(tango)
            self.update_tango_infos(tango)
        self.scanningDir = False
