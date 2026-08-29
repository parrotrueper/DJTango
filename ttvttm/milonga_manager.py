import time

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import QMenu

from ttvttm import utils
from ttvttm.tableModels import normalize_type_key


class MilongaManagerMixin:
    def popupMilonga(self, pos):
        menu = QMenu()
        deleteAction = menu.addAction("Delete")
        action = menu.exec(self._dialog.milongaDest.viewport().mapToGlobal(pos))
        if action == deleteAction:
            self.deleteTangoInMilonga()

    def deleteTangoInMilonga(self):
        indexes = self._dialog.milongaDest.selectionModel().selectedRows()
        for index in indexes:
            if index.isValid():
                self.destModel.removeRows(index.row(), 1, QModelIndex())

    def _save_milonga(self):
        if self.destModel.rowCount(QModelIndex()) == 0:
            self._showInfo("The Milonga list is empty, can't save anything")
            return

        if self._dialog.labelMilongaName.text() == "- No Milonga -":
            self.milongaNameWindow.exec()
            if self.milongaNameWindow.result() == 1:
                self.currentMilongaName = self.milongaNameContent.lineEditName.text()
                self._dialog.labelMilongaName.setText(self.currentMilongaName)
            else:
                return

        self.djData.saveMilonga(self.currentMilongaName, self.getIDListFromMilonga())
        self._showInfo('The milonga "' + str(self.currentMilongaName) + '" has been saved')

    def _save_milonga_as(self):
        if self.destModel.rowCount(QModelIndex()) == 0:
            self._showInfo("The Milonga list is empty, can't save anything")
            return

        self.milongaNameContent.lineEditName.setText(self.currentMilongaName)
        self.milongaNameWindow.exec()
        if self.milongaNameWindow.result() == 1:
            self.currentMilongaName = self.milongaNameContent.lineEditName.text()
            self._dialog.labelMilongaName.setText(self.currentMilongaName)
        else:
            return

        self.djData.saveMilonga(self.currentMilongaName, self.getIDListFromMilonga())
        self._showInfo('The milonga "' + str(self.currentMilongaName) + '" has been saved')

    def _delete_milonga(self):
        if self._isMilongaPlaying:
            self._showInfo("You can not do this while a milonga is playing")
            return

        if self._dialog.labelMilongaName.text() == "- No Milonga -":
            return

        self.milongaAskDelete.exec()
        if self.milongaAskDelete.result() == 1:
            if self.djData.deleteMilonga(0, self.currentMilongaName):
                self.destModel.removeRows(0, self.destModel.rowCount(QModelIndex()), QModelIndex())
                self._dialog.labelMilongaName.setText("- No Milonga -")
                self._showInfo(self.currentMilongaName + " has been deleted")
            else:
                self._showInfo("something went wrong, " + self.currentMilongaName + " has not been deleted")
        else:
            self._showInfo("You abort the deletion")

    def _load_milonga(self):
        if self._isMilongaPlaying:
            self._showInfo("You can not do this while a milonga is playing")
            return

        self.selectMilongaListContent.listWidgetMilongas.clear()
        self.selectMilongaListContent.listWidgetMilongas.addItems(self.djData.getListOfMilongas())
        self.selectMilongaListWindow.exec()

        if self.selectMilongaListWindow.result() == 0:
            return
        self.currentMilongaName = self.selectMilongaListContent.listWidgetMilongas.currentItem().data(Qt.DisplayRole)
        tango_list = self.djData.getTrackFromMilonga(self.currentMilongaName)

        data = [track.list() for track in tango_list]

        self._dialog.labelMilongaName.setText(self.currentMilongaName)
        self.destModel.changeData(data)
        self.updateMilongaInfos(tango_list)

    def _normalize_track_type(self, track_type):
        type_key = normalize_type_key(track_type, self.TYPE)
        if type_key in self.TYPE:
            return type_key
        try:
            type_key = int(track_type)
        except (TypeError, ValueError):
            type_key = 5
        if type_key not in self.TYPE:
            type_key = 5
        return type_key

    def updateMilongaInfos(self, trackList=None):
        trackIdList = self.getIDListFromMilonga()
        trackList = self.djData.getTrackFromListID(trackIdList)
        songnum = 0
        classique = 0
        totalDuration = 0
        totalDurWithCort = 0
        typeCount = {}
        for track in trackList:
            type_key = self._normalize_track_type(track.type)
            typeCount[type_key] = typeCount.get(type_key, 0) + track.duration
            if type_key < 4:
                classique += track.duration
            if type_key != 4:
                totalDuration += float(track.duration)
                totalDurWithCort += float(track.duration)
                songnum += 1
            else:
                totalDuration += self.FadeOutTime

        if totalDurWithCort > 0:
            self.infoMilongaSentence = (
                f"Classique \t{classique * 100 / totalDurWithCort:.0f}% \nAlternatif \t{(1 - classique / totalDurWithCort) * 100:.0f}%"
                + "\n\n---------------------------------------\n\n"
            )
            for key in typeCount:
                if key != 4:
                    self.infoMilongaSentence += (
                        f"{self.TYPE[key][1].title():15}  \t{typeCount[key] * 100 / totalDurWithCort:.0f}%"
                        + "\n"
                    )

        end = time.strftime("%H:%M", time.localtime(self._startMilongaTimeStamp + totalDuration / 1000))
        text = (
            str(songnum)
            + " track(s)    |    duration : "
            + str(utils.msecToHouMin(totalDuration))
            + "    |    Milonga will end at "
            + end
        )
        self._dialog.labelSizeDuration.setText(text)

    def getIDListFromMilonga(self):
        trackIdList = []
        for i in range(0, self.destModel.rowCount(QModelIndex())):
            index = self.destModel.index(i, 0)
            trackID = self.destModel.data(index, Qt.DisplayRole)
            trackIdList.append(trackID)
        return trackIdList

    def _clearMilonga(self):
        if self._isMilongaPlaying:
            self._showInfo("You can not do this while a milonga is playing")
            return

        self._dialog.labelMilongaName.setText("- No Milonga -")
        self.destModel.removeRows(0, self.destModel.rowCount(QModelIndex()), QModelIndex())

    def _doubleClickedMilongaSelect(self):
        self.selectMilongaListWindow.done(1)

    def _handelMilongaLaunch(self):
        self.curLibraryRow = 0
        index = self.destModel.index(self.curLibraryRow, 0)
        self._currentIndex = self.destModel.data(index, Qt.DisplayRole)
        self.curTango = self._tangoList.tracks[self._currentIndex]
        self._isMilongaPlaying = True
        self._updateSideScreen()
        self._startMilongaTimeStamp = time.time()
        self._isClicked = True
        self._dialog.milongaDest.selectRow(self.curLibraryRow)
        index = self.destModel.index(self.curLibraryRow, 1)
        self.destModel.setData(index, 1, Qt.EditRole)
        self.updateMilongaInfos()
        self._load_new_media()
        self._play_media()

    def play_next_milonga_song(self):
        rowIndex = self.curLibraryRow + 1
        if rowIndex <= self.destModel.rowCount(QModelIndex()):
            self.curLibraryRow += 1
            rowIndex = self.curLibraryRow + 1
        index = self.destModel.index(self.curLibraryRow, 0)
        self._currentIndex = self.destModel.data(index, Qt.DisplayRole)
        self._dialog.milongaDest.selectRow(self.curLibraryRow)
        self.updatePlayingCursor()

        if rowIndex <= self.destModel.rowCount(QModelIndex()):
            self.curTango = self._tangoList.tracks[self._currentIndex]
            if self.curTango.type == 4:
                time.sleep(0.5)
            if self.sideWindow.isFullScreen() and rowIndex == self.destModel.rowCount(QModelIndex()):
                self._updateSideScreen(True)
            elif self.sideWindow.isFullScreen():
                self._updateSideScreen()
            if self._load_new_media():
                self._play_media()
            else:
                self.play_next_milonga_song()
        else:
            self._showInfo("The milonga is finished")

    def getNbSongInCurTanda(self):
        count = self.curLibraryRow
        index = self.destModel.index(count, 5)
        currentType = self.destModel.data(index, Qt.DisplayRole)
        num = 0
        while currentType == self.destModel.data(index, Qt.DisplayRole) and count + 1 <= self.destModel.rowCount(QModelIndex()):
            num += 1
            count += 1
            index = self.destModel.index(count, 5)
        count = self.curLibraryRow - 1
        index = self.destModel.index(count, 5)
        while currentType == self.destModel.data(index, Qt.DisplayRole) and count + 1 < self.destModel.rowCount(QModelIndex()) and index.row() > -1:
            num += 1
            count -= 1
            index = self.destModel.index(count, 5)
        return num

    def getNextTanda(self):
        ret = {}
        ret["nbintanda"] = self.getNbSongInCurTanda()
        count = self.curLibraryRow
        numSong = 0
        index = self.destModel.index(count, 5)
        currentType = self.destModel.data(index, Qt.DisplayRole)
        while currentType == self.destModel.data(index, Qt.DisplayRole) and count + 1 <= self.destModel.rowCount(QModelIndex()):
            numSong += 1
            count += 1
            index = self.destModel.index(count, 5)
        if numSong == 1:
            ret["num"] = 1
        else:
            ret["num"] = numSong
        if self.destModel.data(index, Qt.DisplayRole) == "Cortina":
            index = self.destModel.index(count + 1, 5)
            ret["type"] = self.destModel.data(index, Qt.DisplayRole).upper()
        elif count + 1 >= self.destModel.rowCount(QModelIndex()):
            ret["type"] = "last"
        else:
            ret["type"] = self.destModel.data(index, Qt.DisplayRole).upper()
        return ret
