import os
import re
import time

from djtango import utils
from djtango.qt_compat import QMenu, QModelIndex, Qt


class LibraryManagerMixin:
    def deleteTangos(self, removeFile=False):
        indexes = self._dialog.milongaSource.selectionModel().selectedRows()
        for index in indexes:
            curTangoID = self.sourceProxyModel.data(index, Qt.DisplayRole)
            self.djData.deleteTango(curTangoID)
            if removeFile and os.path.isfile(self._tangoList.tangos[curTangoID].path):
                os.remove(self._tangoList.tangos[curTangoID].path)
            if curTangoID in self._tangoList.tangos.keys():
                self._tangoList.removeTango(curTangoID)
                self.tangoListUpdated.emit(self._tangoList)

        data = [self._tangoList.tangos[key].list() for key in self._tangoList.tangos.keys()]
        self.sourceModel.changeData(data)
        self._dialog.labelsongNB_source.setText(str(self.sourceProxyModel.rowCount(QModelIndex())) + " song(s)")

    def _handelBpmTappingAction(self):
        indexes = self._dialog.milongaSource.selectionModel().selectedRows()
        self.curTangoEditing = self.sourceProxyModel.data(indexes[0], Qt.DisplayRole)
        self.curLibraryRow = indexes[0].row()
        self._isClicked = True
        self.curTango = self._tangoList.tangos[self.curTangoEditing]
        self._load_new_media()
        self._play_media()
        self.tapTable = []
        self.tapContent.lcdNumber.display(0.0)
        self.bpm = 0
        self.initialiszeBmpInfo()
        self.tapWindow.show()

    def _load_bpm_from_id3_tag(self):
        indexes = self._dialog.milongaSource.selectionModel().selectedRows()
        if not indexes:
            return

        tangoID = self.sourceProxyModel.data(indexes[0], Qt.DisplayRole)
        self.curTangoEditing = tangoID
        self.curLibraryRow = indexes[0].row()
        self.curTango = self._tangoList.tangos[tangoID]
        self.curTango.extractAnyTag()

        bpm = self.curTango.bpmFromFile
        if bpm:
            try:
                self.curTango.bpmHuman = float(bpm)
            except (TypeError, ValueError):
                self.curTango.bpmHuman = bpm
            self.updateTangoBPM()
            self._showInfo('BPM loaded from ID3 tag')
        else:
            self._showInfo('No BPM found in ID3 tag')

    def _handelBpmTapping(self):
        self.tapTable.append(time.time())
        self.delta = []
        self.bpmtrack = []
        if len(self.tapTable) > 1:
            for i in range(1, len(self.tapTable)):
                self.delta.append(self.tapTable[i] - self.tapTable[i - 1])
                self.bpmtrack.append(60 / (sum(self.delta) / len(self.delta)))
            mean = sum(self.delta) / len(self.delta)
            self.bpm = 60 / mean
            if len(self.bpmtrack) > 4:
                temp = [self.bpmtrack[i] for i in range(len(self.bpmtrack) - 1, len(self.bpmtrack) - 6, -1)]
                if max(temp) - min(temp) < 0.3 and self.bmpState != 2:
                    self.tapContent.labelDone.setText("DONE")
                    self.tapContent.labelDone.setStyleSheet("color: rgb(70,169,73)")
                    self.bmpState = 2
                elif max(temp) - min(temp) < 0.8 and max(temp) - min(temp) > 0.5 and self.bmpState == 0:
                    self.tapContent.labelDone.setText("CONTINUE")
                    self.tapContent.labelDone.setStyleSheet("color: rgb(215,0,8)")
                    self.bmpState = 1
                elif max(temp) - min(temp) < 0.5 and self.bmpState != 2:
                    self.tapContent.labelDone.setText("ALMOST")
                    self.tapContent.labelDone.setStyleSheet("color: rgb(240,169,73)")
            self.curTango.bpmHuman = self.bpm
            self.tapContent.lcdNumber.display(self.bpm)

    def initialiszeBmpInfo(self):
        self.bmpState = 0
        self.tapContent.labelDone.setText("DONE")
        self.tapContent.labelDone.setStyleSheet("color: rgb(42,42,42)")
        if self.curTango.bpmHuman == 0 and self.curTango.bpmFromFile == 0:
            self.tapContent.labelTypeBmp.setText("Not set")
            self.tapContent.labelTypeBmp.setStyleSheet("color: rgb(215,0,8)")
        elif self.curTango.bpmHuman == 0 and self.curTango.bpmFromFile > 0:
            self.tapContent.labelTypeBmp.setText("Set by computer")
            self.tapContent.labelTypeBmp.setStyleSheet("color: rgb(240,169,73)")
        else:
            self.tapContent.labelTypeBmp.setText("Set by human")
            self.tapContent.labelTypeBmp.setStyleSheet("color: rgb(70,169,73)")

    def _handelValidatebpm(self):
        self.updateTangoBPM()
        self.tapWindow.close()

    def _handelCancelbpm(self):
        self.tapWindow.close()

    def _handelTapingNext(self):
        self.updateTangoBPM()
        self.tapTable = []
        self.delta = []
        self.tapContent.lcdNumber.display(0.0)
        self.bpm = 0
        if self.curLibraryRow + 1 < self.sourceProxyModel.rowCount(QModelIndex()):
            self.curLibraryRow += 1
            index = self.sourceProxyModel.index(self.curLibraryRow, 0)
            self.curTangoEditing = self.sourceProxyModel.data(index, Qt.DisplayRole)
            self._dialog.milongaSource.selectRow(self.curLibraryRow)
            self._isClicked = True
            self.curTango = self._tangoList.tangos[self.curTangoEditing]
            self._load_new_media()
            self._play_media()
            self.initialiszeBmpInfo()

    def _handelTapingPrevious(self):
        self.updateTangoBPM()
        self.tapTable = []
        self.delta = []
        self.tapContent.lcdNumber.display(0.0)
        self.bpm = 0
        if self.curLibraryRow - 1 >= 0:
            self.curLibraryRow -= 1
            index = self.sourceProxyModel.index(self.curLibraryRow, 0)
            self.curTangoEditing = self.sourceProxyModel.data(index, Qt.DisplayRole)
            self._dialog.milongaSource.selectRow(self.curLibraryRow)
            self._isClicked = True
            self.curTango = self._tangoList.tangos[self.curTangoEditing]
            self._load_new_media()
            self._play_media()
            self.initialiszeBmpInfo()

    def updateTangoBPM(self):
        indexes = self._dialog.milongaSource.selectionModel().selectedRows()
        tangoID = self.sourceProxyModel.data(indexes[0], Qt.DisplayRole)
        data = self._tangoList.tangos[tangoID].list()
        for count, cdata in enumerate(data):
            index = self.sourceProxyModel.index(indexes[0].row(), count)
            self.sourceProxyModel.setData(index, cdata, Qt.EditRole)
        self.djData.updateBPM(self._tangoList.tangos[tangoID])

    def popupLibrary(self, pos):
        menu = QMenu()
        detailsAction = menu.addAction("Details")
        audacityAction = menu.addAction("Open with audacity")
        deleteAction = menu.addAction("Delete selected")
        deleteAction2 = menu.addAction("Remove selected (without deleting file")
        writeTagAction = menu.addAction("Write the tags")
        mp3infos = menu.addAction("Show mp3 infos")
        tapbpm = menu.addAction("Set the bpm by taping the tempo of the song")
        updateTangoDurations = menu.addAction("update the Tango duration")
        action = menu.exec(self._dialog.milongaSource.viewport().mapToGlobal(pos))
        if action == detailsAction:
            self.handelOpenPropWidow()
        elif action == deleteAction:
            self.deleteTangos(True)
        elif action == deleteAction2:
            self.deleteTangos()
        elif action == audacityAction:
            indexes = self._dialog.milongaSource.selectionModel().selectedRows()
            self.curTangoEditing = self.sourceProxyModel.data(indexes[0], Qt.DisplayRole)
            os.system("audacity \"" + str(self._tangoList.tangos[self.curTangoEditing].path) + "\" &")
        elif action == writeTagAction:
            indexes = self._dialog.milongaSource.selectionModel().selectedRows()
            for index in indexes:
                curTangoID = self.sourceProxyModel.data(index, Qt.DisplayRole)
                self._tangoList.tangos[curTangoID].writeTags(self.TYPE)
        elif action == mp3infos:
            indexes = self._dialog.milongaSource.selectionModel().selectedRows()
            self.curTangoEditing = self.sourceProxyModel.data(indexes[0], Qt.DisplayRole)
            os.system("mp3info2 \"" + str(self._tangoList.tangos[self.curTangoEditing].path) + "\" &")
        elif action == tapbpm:
            self._handelBpmTappingAction()
        elif action == updateTangoDurations:
            self.update_duration()

    def get_list_of_artist(self, album, genre):
        artists = {}
        for key in self._tangoList.tangos.keys():
            if not album == '' and not self._tangoList.tangos[key].album.lower() == album.lower():
                continue
            if self._tangoList.tangos[key].artist not in artists:
                artists[self._tangoList.tangos[key].artist] = 1
            else:
                artists[self._tangoList.tangos[key].artist] += 1
        return artists

    def get_list_of_album(self, artist, genre):
        albums = {}
        for key in self._tangoList.tangos.keys():
            if self._tangoList.tangos[key].album not in albums:
                albums[self._tangoList.tangos[key].album] = 1
            else:
                albums[self._tangoList.tangos[key].album] += 1
        return albums

    def set_list_of_type(self):
        self._dialog.comboBoxGenre.clear()
        self._dialog.comboBoxGenre.insertItem(0, '-select type-')
        for i in range(1, len(self.TYPE) + 1):
            self._dialog.comboBoxGenre.insertItem(i, self.TYPE[i][1].title())

    def set_list_of_artist(self, album='', genre=''):
        artists = self.get_list_of_artist(album, genre)
        self._dialog.comboBoxArtist.clear()
        self._dialog.comboBoxArtist.insertItem(0, '-select Artist-')
        for count, key in enumerate(sorted(artists.keys()), start=1):
            self._dialog.comboBoxArtist.insertItem(count, key + " (" + str(artists[key]) + ")")

    def setListOfAlbum(self, artist='', genre=''):
        album = self.get_list_of_album(artist, genre)
        self._dialog.comboBoxAlbum.clear()
        self._dialog.comboBoxAlbum.insertItem(0, '-select Album-')
        for count, key in enumerate(sorted(album.keys()), start=1):
            self._dialog.comboBoxAlbum.insertItem(count, key + " (" + str(album[key]) + ")")

    def _handel_filter_change(self):
        reg = re.compile(r'(.+)\s\(\d+\)')
        artist = self._dialog.comboBoxArtist.currentText()
        album = self._dialog.comboBoxAlbum.currentText()
        genre = self._dialog.comboBoxGenre.currentText()
        linefilter = self._dialog.lineEditFilter.text()

        res = reg.search(artist)
        if res:
            artist = res.group(1)
        elif self._dialog.comboBoxArtist.currentIndex() == 0:
            artist = '.*'
        res = reg.search(album)
        if res:
            album = res.group(1)
        elif self._dialog.comboBoxAlbum.currentIndex() == 0:
            album = '.*'

        if self._dialog.comboBoxGenre.currentIndex() == 0:
            genre = '.*'

        if linefilter == '':
            linefilter = '.*'

        self.sourceProxyModel.setlFilterValues(artist, album, genre, linefilter)
        self._dialog.labelsongNB_source.setText(str(self.sourceProxyModel.rowCount(QModelIndex())) + " song(s)")

    def _clear_filter(self):
        index_artist = self._dialog.comboBoxArtist.currentIndex()
        index_album = self._dialog.comboBoxAlbum.currentIndex()
        index_genre = self._dialog.comboBoxGenre.currentIndex()
        filter_val = self._dialog.lineEditFilter.text()
        manual_update = False

        if index_album == 0 and index_artist == 0 and index_genre == 0 and filter_val != '':
            manual_update = True

        self._dialog.comboBoxArtist.setCurrentIndex(0)
        self._dialog.comboBoxAlbum.setCurrentIndex(0)
        self._dialog.comboBoxGenre.setCurrentIndex(0)
        self._dialog.lineEditFilter.clear()

        if manual_update:
            self._handel_filter_change()

        self._dialog.labelsongNB_source.setText(str(self.sourceProxyModel.rowCount(QModelIndex())) + " song(s)")
