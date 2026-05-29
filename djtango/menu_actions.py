import os

from djtango.qt_compat import QFileDialog, QModelIndex
from djtango.tangosong import TangoSong


class MenuActionsMixin:
    def open_file_dialog(self):
        dir_name = QFileDialog.getExistingDirectory(
            self,
            "Open Directory",
            os.path.expanduser('~'),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )
        if not dir_name:
            return

        self.prefContent.lineEditSongDir.setText(dir_name)
        self._tangoList.songpath = dir_name
        self.scanningDir = True
        new_files = self._tangoList.checkNewFiles()
        if new_files:
            for path in new_files:
                self.djData.insertTango(TangoSong(path, 0, True))
            self._tangoList.loadTangos(self.djData.getAllTangos())

            data = [tango.list() for tango in self._tangoList.tangos.values()]
            self.sourceModel.changeData(data)
            self._showInfo(str(len(new_files)) + " song has been added")

        self.scanningDir = False

    def open_files_dialog(self):
        filenames, _ = QFileDialog.getOpenFileNames(
            self,
            "Add files",
            os.path.expanduser('~'),
            "Audio files (*.mp3 *.flac *.ogg *.wav *.m4a);;All files (*)",
        )
        if not filenames:
            return

        self.scanningDir = True
        for path in filenames:
            self.djData.insertTango(TangoSong(path, 0, True))

        self._tangoList.loadTangos(self.djData.getAllTangos())
        data = [tango.list() for tango in self._tangoList.tangos.values()]
        self.sourceModel.changeData(data)
        self._showInfo(str(len(filenames)) + " song(s) have been added")
        self.scanningDir = False
