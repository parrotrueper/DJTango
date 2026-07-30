import os

import PySide6.QtCore as QtCore
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFileDialog,
    QFileSystemModel,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTreeView,
    QVBoxLayout,
)

from ttvttm.tracksong import TrackSong


class LibraryContentsDialog(QDialog):
    def __init__(self, parent, root_path):
        super().__init__(parent)
        self.root_path = os.path.abspath(root_path)
        self.setWindowTitle("Library contents")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Library root: {self.root_path}"))

        self.model = QFileSystemModel(self)
        self.model.setRootPath(self.root_path)
        self.model.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot)

        self.tree = QTreeView(self)
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.root_path))
        self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tree.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tree.setAlternatingRowColors(True)
        self.tree.setStyleSheet(
            "QTreeView {"
            "background: rgb(42, 42, 42);"
            "alternate-background-color: rgb(34, 34, 48);"
            "color: #d3d3d3;"
            "selection-background-color: rgb(64, 64, 64);"
            "selection-color: white;"
            "border: none;"
            "}"
            "QHeaderView::section {"
            "background: rgb(42, 42, 42);"
            "color: white;"
            "border: 1px solid rgb(32, 32, 32);"
            "}"
        )
        self.tree.header().setStretchLastSection(True)
        layout.addWidget(self.tree)

        button_layout = QHBoxLayout()
        self.exclude_button = QPushButton("Exclude selected")
        self.close_button = QPushButton("Close")
        button_layout.addWidget(self.exclude_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.exclude_button.clicked.connect(self._exclude_selected)
        self.close_button.clicked.connect(self.accept)

    def _exclude_selected(self):
        indexes = self.tree.selectionModel().selectedIndexes()
        if not indexes:
            QMessageBox.information(self, "No selection", "Select a file or directory to exclude from the library.")
            return

        path = self.model.filePath(indexes[0])
        if not os.path.commonpath([self.root_path, path]) == self.root_path and self.root_path != path:
            QMessageBox.warning(self, "Invalid selection", "The selected item is not inside the library root.")
            return

        self.parent().exclude_library_path(path)
        self.status_label.setText(f"Excluded: {path}")
        self.tree.selectionModel().clearSelection()


class MenuActionsMixin:
    def open_file_dialog(self):
        dir_name = QFileDialog.getExistingDirectory(
            self,
            "Open Directory",
            os.path.expanduser("~"),
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
                self.djData.insertTrack(TrackSong(path, 0, True))
            self._tangoList.loadTangos(self.djData.getAllTracks())

            data = [track.list() for track in self._tangoList.tracks.values()]
            self.sourceModel.changeData(data)
            self._showInfo(str(len(new_files)) + " track has been added")

        self.scanningDir = False

    def open_files_dialog(self):
        filenames, _ = QFileDialog.getOpenFileNames(
            self,
            "Add files",
            os.path.expanduser("~"),
            "Audio files (*.mp3 *.flac *.ogg *.wav *.m4a);;All files (*)",
        )
        if not filenames:
            return

        self.scanningDir = True
        for path in filenames:
            self.djData.insertTrack(TrackSong(path, 0, True))

        self._tangoList.loadTangos(self.djData.getAllTracks())
        data = [track.list() for track in self._tangoList.tracks.values()]
        self.sourceModel.changeData(data)
        self._showInfo(str(len(filenames)) + " track(s) have been added")
        self.scanningDir = False

    def open_library_contents_dialog(self):
        if not getattr(self._tangoList, "songpath", None):
            QMessageBox.information(self, "Library contents", "Library path is not configured.")
            return

        dialog = LibraryContentsDialog(self, self._tangoList.songpath)
        dialog.exec()

    def exclude_library_path(self, path):
        normalized_path = os.path.abspath(path)
        self._tangoList.excludePath(normalized_path)
        self.djData.addExcludedPath(normalized_path)
        self.djData.deleteTracksByPath(normalized_path)
        self._tangoList.loadTangos(self.djData.getAllTracks())
        data = [track.list() for track in self._tangoList.tracks.values()]
        self.sourceModel.changeData(data)
        self._showInfo("Excluded path from library: " + normalized_path)
