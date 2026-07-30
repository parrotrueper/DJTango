from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import QAbstractItemView


class TrackPropertiesMixin:
    def enableTableView(self):
        self._dialog.milongaSource.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def disabledTableView(self):
        self._dialog.milongaSource.setSelectionMode(QAbstractItemView.NoSelection)

    def handelOpenPropWidow(self):
        self.disabledTableView()
        self._dialog.milongaSource.setSortingEnabled(False)
        self.updateTrackProp()
        self.TrackBeforeChange = self._tangoList.tracks[self.curTangoEditing]
        self.propWindow.show()
        self.scanningDir = True

    def _handlePropWindowClose(self):
        self.updateTrackSong()
        self.TrackBeforeChange = self._tangoList.tracks[self.curTangoEditing]
        self.propWindow.close()
        self._dialog.milongaSource.setSortingEnabled(True)
        self.enableTableView()
        self.scanningDir = False
        self._dialog.labelsongNB_source.setText(str(self.sourceProxyModel.rowCount(QModelIndex())) + " track(s)")

    def _handlePropWindowNext(self):
        self.enableTableView()
        self.updateTrackSong()
        self.TrackBeforeChange = self._tangoList.tracks[self.curTangoEditing]
        if self.curLibraryRow + 1 < self.sourceProxyModel.rowCount(QModelIndex()):
            self.curLibraryRow += 1
            index = self.sourceProxyModel.index(self.curLibraryRow, 0)
            self.curTangoEditing = self.sourceProxyModel.data(index, Qt.DisplayRole)
            self._dialog.milongaSource.selectRow(self.curLibraryRow)
            self.updateTrackProp()
        self._dialog.labelsongNB_source.setText(str(self.sourceProxyModel.rowCount(QModelIndex())) + " track(s)")
        self.disabledTableView()
        self.scanningDir = True

    def _handlePropWindowPrevious(self):
        self.enableTableView()
        self.updateTrackSong()
        if self.curLibraryRow > 0:
            self.curLibraryRow -= 1
            self._dialog.milongaSource.selectRow(self.curLibraryRow)
            index = self.sourceProxyModel.index(self.curLibraryRow, 0)
            self.curTangoEditing = self.sourceProxyModel.data(index, Qt.DisplayRole)
            self.updateTrackProp()
        self.disabledTableView()
        self.scanningDir = True
        self._dialog.labelsongNB_source.setText(str(self.sourceProxyModel.rowCount(QModelIndex())) + " track(s)")

    def updateTrackProp(self):
        indexes = self._dialog.milongaSource.selectionModel().selectedRows()
        if len(indexes) > 1:
            self._apply_multi_selection_state()
        else:
            self._apply_single_selection_state(indexes[0])

        sameFieldValue = self.getSameFieldInfos(indexes)
        self._set_field_text(self.detailsContent.lineEditArtist, sameFieldValue["artist"])
        self._set_field_text(self.detailsContent.lineEditTitle, sameFieldValue["title"])
        self._set_field_text(self.detailsContent.lineEditAlbum, sameFieldValue["album"])
        self._set_type_combo(sameFieldValue["type"])
        self._set_year_spinbox(sameFieldValue["year"])

    def _apply_multi_selection_state(self):
        self.detailsContent.nextButton.setVisible(False)
        self.detailsContent.previousButton.setVisible(False)
        self.detailsContent.textPath.setText("")

    def _apply_single_selection_state(self, index):
        self.detailsContent.nextButton.setVisible(True)
        self.detailsContent.previousButton.setVisible(True)
        self.curTangoEditing = self.sourceProxyModel.data(index, Qt.DisplayRole)
        self.curLibraryRow = index.row()
        self.detailsContent.textPath.setText(self._tangoList.tracks[self.curTangoEditing].path)
        if self.detailsContent.checkBoxPlayMusic.isChecked():
            self._isClicked = True
            self.curTango = self._tangoList.tracks[self.curTangoEditing]
            self._load_new_media()
            self._play_media()

    def _set_field_text(self, widget, value):
        if value is False:
            widget.setText("-")
        elif value != "Unknown":
            widget.setText(value)
        else:
            widget.setText("")

    def _set_type_combo(self, value):
        if value is False:
            self.detailsContent.comboBoxTangoType.setCurrentIndex(-1)
        else:
            self.detailsContent.comboBoxTangoType.setCurrentIndex(value - 1)

    def _set_year_spinbox(self, value):
        if value is False:
            self.detailsContent.spinBoxYear.setValue(-1)
        else:
            self.detailsContent.spinBoxYear.setValue(value)

    def getSameFieldInfos(self, indexes):
        sameFieldValue = {}
        for index in indexes:
            trackID = self.sourceProxyModel.data(index, Qt.DisplayRole)
            track = self._tangoList.tracks[trackID]
            sameFieldValue["artist"] = track.artist if "artist" not in sameFieldValue else sameFieldValue["artist"] if sameFieldValue["artist"] == track.artist else False
            sameFieldValue["album"] = track.album if "album" not in sameFieldValue else sameFieldValue["album"] if sameFieldValue["album"] == track.album else False
            sameFieldValue["type"] = track.type if "type" not in sameFieldValue else sameFieldValue["type"] if sameFieldValue["type"] == track.type else False
            sameFieldValue["year"] = track.year if "year" not in sameFieldValue else sameFieldValue["year"] if sameFieldValue["year"] == track.year else False
            sameFieldValue["title"] = track.title if "title" not in sameFieldValue else sameFieldValue["title"] if sameFieldValue["title"] == track.title else False
        return sameFieldValue

    def isSomethingChanged(self):
        return not (
            self.TrackBeforeChange.artist == self.detailsContent.lineEditArtist.text() and
            self.TrackBeforeChange.title == self.detailsContent.lineEditTitle.text() and
            self.TrackBeforeChange.year == self.detailsContent.spinBoxYear.value() and
            self.TrackBeforeChange.type == self.detailsContent.comboBoxTangoType.currentIndex() + 1 and
            self.TrackBeforeChange.album == self.detailsContent.lineEditAlbum.text()
        )

    def updateTrackSong(self):
        if not self.isSomethingChanged():
            return

        self.scanningDir = True
        indexes = self._dialog.milongaSource.selectionModel().selectedRows()
        for index in indexes:
            trackID = self.sourceProxyModel.data(index, Qt.DisplayRole)
            track = self._tangoList.tracks[trackID]
            self._update_track_fields(track)
            self._persist_track_changes(index, track)
        self.scanningDir = False

    def _update_track_fields(self, track):
        artist = self.detailsContent.lineEditArtist.text()
        title = self.detailsContent.lineEditTitle.text()
        album = self.detailsContent.lineEditAlbum.text()

        if artist != "-":
            track.artist = artist or "Unknown"
        if title != "-":
            track.title = title or "Unknown"
        if self.detailsContent.spinBoxYear.value() > 0:
            track.year = self.detailsContent.spinBoxYear.value()
        if album != "-":
            track.album = album or "Unknown"
        if self.detailsContent.comboBoxTangoType.currentIndex() > -1:
            track.type = self.detailsContent.comboBoxTangoType.currentIndex() + 1

    def _persist_track_changes(self, index, track):
        if self.normalize == 2:
            self._tangoList.normalizeTango(track.ID, self.TYPE)
        if self.writeTag == 2:
            track.writeTags(self.TYPE)
        for count, cdata in enumerate(track.list()):
            list_index = self.sourceProxyModel.index(index.row(), count)
            self.sourceProxyModel.setData(list_index, cdata, Qt.EditRole)
        self.djData.updateTrack(track)
        self.update_tango_infos(track)
