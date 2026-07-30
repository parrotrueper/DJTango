import os
import platform
import time

import audioread
from PySide6 import QtCore
from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QCursor
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtWidgets import QApplication

from ttvttm import utils


class AudioPlaybackMixin:
    def playSelectedSource(self):
        self._libraryClicked()

    def _libraryClicked(self):
        if self._isMilongaPlaying:
            self._showInfo("You can't play a track if the Milonga is playing. Stop the Milonga first")
            return
        if self.propWindow.isVisible():
            return
        self._isClicked = True
        indexes = self._dialog.milongaSource.selectionModel().selectedRows()

        if len(indexes) == 1:
            self._currentIndex = self.sourceProxyModel.data(indexes[0], Qt.DisplayRole)
            self.curLibraryRow = indexes[0].row()
            self.curTango = self._tangoList.tracks[self._currentIndex]
            self.updatePlayingCursor()
            self._load_new_media()
            self._play_media()
            self._updateSideScreen()

    def _destLibraryClicked(self):
        if self._isMilongaPlaying:
            self._showInfo("You can't play a track if the Milonga is playing. Stop the Milonga first")
            return
        if self.propWindow.isVisible():
            return

        self._isClicked = True
        indexes = self._dialog.milongaDest.selectionModel().selectedRows()

        if len(indexes) == 1:
            self._currentIndex = self.destModel.data(indexes[0], Qt.DisplayRole)
            self.curLibraryRow = indexes[0].row()
            self.curTango = self._tangoList.tracks[self._currentIndex]
            self._load_new_media()
            self._play_media()

    def update_duration(self):
        sys_name = platform.system()
        if sys_name == "Linux":
            for key in self._tangoList.tracks:
                tmpTango = self._tangoList.tracks[key]
                audio = audioread.audio_open(tmpTango.path)
                tmpTango.duration = audio.duration * 1000
                self.djData.updateTrack(tmpTango)
        elif sys_name == "Windows":
            self._showInfo("You can not run this command on Windows :-(")

    def _load_new_media(self):
        if not os.path.isfile(self.curTango.path):
            self._showInfo("This file is not existing on disk, remove it")
            return False
        source = QtCore.QUrl.fromLocalFile(QtCore.QFileInfo(self.curTango.path).absoluteFilePath())
        self.mediaSource = source
        self.player.setSource(source)
        return True

    def _play_media(self):
        if not self.ok_to_play_pause_stop():
            return

        if self.curTango is None:
            self._showInfo("No track selected")
            return

        self._dialog.playToolButton.setIcon(self.pauseIcon)
        self.update_tango_infos(self.curTango)
        self._isPlaying = True

        if not self.curTango.tstart == 0:
            self.seek(self.curTango.tstart / 1000)

        if self._isMilongaPlaying:
            time.sleep(1.5)
        try:
            self.player.play()
        except Exception as err:
            print(err)

    def _resolve_type_id(self, type_value):
        if type_value in self.TYPE:
            return type_value
        if isinstance(type_value, str):
            lookup = type_value.strip().lower()
            for key, value in self.TYPE.items():
                if str(value[1]).lower() == lookup:
                    return key
            try:
                numeric = int(type_value)
                if numeric in self.TYPE:
                    return numeric
            except (TypeError, ValueError):
                pass
        try:
            numeric = int(type_value)
            if numeric in self.TYPE:
                return numeric
        except (TypeError, ValueError):
            pass
        return 5

    def update_tango_infos(self, track):
        if self.curTango is not None and self.curTango.ID == track.ID:
            self.curTango = track
            type_id = self._resolve_type_id(track.type)
            self._dialog.labelTypeSong.setText(self.TYPE[type_id][1].upper())
            self._dialog.labelArtist.setText(track.artist)
            self._dialog.labelAlbum.setText(track.album)
            self._dialog.labelTitle.setText(track.title)

    def stop_media(self):
        if not self.ok_to_play_pause_stop():
            return
        self.clearPlayingCursor()

        if self._isMilongaPlaying:
            self._isMilongaPlaying = False

        self._isPlaying = False
        self._dialog.playToolButton.setIcon(self.playIcon)
        self._dialog.timeLabel.setText("00:00 / 00:00")
        self.player.stop()

    def pause_media(self):
        self._isPlaying = False
        if not self.ok_to_play_pause_stop():
            return
        self.player.pause()
        self._dialog.playToolButton.setIcon(self.playIcon)

    def ok_to_play_pause_stop(self):
        ok_to_proceed = True
        if self.mediaSource is None:
            err = "No track selected"
            self._dialog.playToolButton.setIcon(self.playIcon)
            self._showInfo(err)
            ok_to_proceed = False
        return ok_to_proceed

    def _handelPlayPause(self):
        if self._isPlaying:
            self.pause_media()
            self._isPaused = True
        else:
            if self.destModel.rowCount(QModelIndex()) > 0 and not self._isPaused:
                self._handelMilongaLaunch()
            else:
                if self.ok_to_play_pause_stop():
                    self._play_media()
            self._isPaused = False

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

    def _handel_state_changed(self):
        current_state = self.player.playbackState() if hasattr(self.player, "playbackState") else self.player.state()
        if current_state == QMediaPlayer.PlayingState:
            self._isClicked = False
        elif current_state == QMediaPlayer.StoppedState:
            if not self._isClicked and self._isPlaying:
                if self._isMilongaPlaying:
                    if self._dialog.checkBoxLetCortinaUntilEnd.isChecked():
                        self._dialog.checkBoxLetCortinaUntilEnd.setCheckState(Qt.Unchecked)
                    self.play_next_milonga_song()
                else:
                    self.playNextLibrarySong()

    def durationChanged(self, duration):
        self.bar.setRange(0, duration)
        duration /= 1000
        self.duration = duration
        self._dialog.songSlider.setMaximum(duration)
        if (not self.curTango.duration == duration * 1000) and (duration > 0):
            self.curTango.duration = duration * 1000
            if self._isMilongaPlaying:
                indexes = self._dialog.milongaDest.selectionModel().selectedRows()
                trackID = self.sourceProxyModel.data(indexes[0], Qt.DisplayRole)
            else:
                indexes = self._dialog.milongaSource.selectionModel().selectedRows()
                trackID = self.sourceProxyModel.data(indexes[0], Qt.DisplayRole)
                data = self._tangoList.tracks[trackID].list()
                count = 0
                for cdata in data:
                    index = self.sourceProxyModel.index(indexes[0].row(), count)
                    self.sourceProxyModel.setData(index, cdata, Qt.EditRole)
                    count += 1
            self.djData.updateTrack(self.curTango)

    def position_changed(self, progress):
        slider_progress = progress / 1000
        if not self._dialog.songSlider.isSliderDown():
            self._dialog.songSlider.setValue(slider_progress)
            self._dialog.timeLabel.setText(
                str(utils.msecToms(progress)) + " / " + str(utils.msecToms(self.duration * 1000)))

        if not self.curTango.type == 4 or not self.volumeSetToInitial or self._dialog.checkBoxLetCortinaUntilEnd.isChecked():
            self.player.setVolume(100)
            self.volumeSetToInitial = True
            self.bar.setValue(self.duration * 1000 - progress)
            if progress >= self.curTango.tend:
                self.player.stop()
        elif self.curTango.type == 4 and not self._dialog.checkBoxLetCortinaUntilEnd.isChecked():
            self.bar.setRange(0, self.FadOutTime)
            self.bar.setValue(self.FadOutTime - progress)
            if (self.FadOutTime - self.durationFadOut) <= progress:
                if self.player.volume() > 1:
                    self.player.setVolume(self.player.volume() - 100 / self.stepFadOut)
                if self.player.volume() <= 1 and progress >= self.FadOutTime:
                    self.volumeSetToInitial = False
                    self.player.stop()
                    self.player.setVolume(100)

    def seek(self, seconds):
        self.player.setPosition(seconds * 1000)

    def sliderValueChanged(self, newpos):
        btns = QApplication.mouseButtons()
        localMousePos = self._dialog.songSlider.mapFromGlobal(QCursor.pos())
        clickOnSlider = btns == Qt.LeftButton and (
                localMousePos.x() >= 0 and localMousePos.y() >= 0 and localMousePos.x() < self._dialog.songSlider.size().width() and localMousePos.y() < self._dialog.songSlider.size().height())
        if clickOnSlider:
            posRatio = localMousePos.x() / self._dialog.songSlider.size().width()
            slideRange = self._dialog.songSlider.maximum() - self._dialog.songSlider.minimum()
            sliderPosUnderMouse = self._dialog.songSlider.minimum() + slideRange * posRatio
            if not sliderPosUnderMouse == newpos:
                self._dialog.songSlider.setValue(sliderPosUnderMouse)
                self.seek(sliderPosUnderMouse)

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
            self._showInfo("The playlist set is finished")

    def playNextLibrarySong(self):
        rowIndex = self.curLibraryRow + 1
        if rowIndex <= self.sourceProxyModel.rowCount(QModelIndex()):
            self.curLibraryRow += 1
            rowIndex = self.curLibraryRow + 1
        index = self.sourceProxyModel.index(self.curLibraryRow, 0)
        self._currentIndex = self.sourceProxyModel.data(index, Qt.DisplayRole)
        self._dialog.milongaSource.selectRow(self.curLibraryRow)
        self.updatePlayingCursor()
        time.sleep(0.1)

        if rowIndex <= self.sourceProxyModel.rowCount(QModelIndex()):
            self.curTango = self._tangoList.tracks[self._currentIndex]
            self._load_new_media()
            self._play_media()
            self._updateSideScreen()
        else:
            self._showInfo("We have reach the end of the list we stop here")

    def updatePlayingCursor(self):
        self.clearPlayingCursor()
        if self._isMilongaPlaying:
            index = self.destModel.index(self.curLibraryRow, 1)
            self.destModel.setData(index, 1, Qt.EditRole)
        else:
            index = self.sourceProxyModel.index(self.curLibraryRow, 1)
            self.sourceProxyModel.setData(index, 1, Qt.EditRole)

    def clearPlayingCursor(self):
        if not self._isMilongaPlaying:
            for row in range(0, self.sourceProxyModel.rowCount(QModelIndex())):
                index = self.sourceProxyModel.index(row, 1)
                self.sourceProxyModel.setData(index, 0, Qt.EditRole)
        else:
            for row in range(0, self.destModel.rowCount(QModelIndex())):
                index = self.destModel.index(row, 1)
                self.destModel.setData(index, 0, Qt.EditRole)
