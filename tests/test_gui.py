import importlib

import pytest
from PySide6.QtWidgets import QApplication, QMainWindow


def test_qt_compat_loads_qapplication():
    assert callable(QApplication)
    assert callable(QMainWindow)


def test_gui_starts_in_offscreen_mode(monkeypatch):
    if not (importlib.util.find_spec("PySide6") or importlib.util.find_spec("PyQt5")):
        pytest.skip("Qt bindings not available")

    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setenv("TTVTTM_DISABLE_DIR_SCAN", "1")

    from ttvttm.TTVTTM import AudioPlayerDialog

    app = QApplication.instance() or QApplication([])
    dlg = AudioPlayerDialog()
    dlg.close()
    if hasattr(app, "quit"):
        app.quit()


def test_library_selection_updates_side_display(monkeypatch):
    if not (importlib.util.find_spec("PySide6") or importlib.util.find_spec("PyQt5")):
        pytest.skip("Qt bindings not available")

    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setenv("TTVTTM_DISABLE_DIR_SCAN", "1")

    from ttvttm import tableModels
    from ttvttm.tracksong import TrackSong
    from ttvttm.TTVTTM import AudioPlayerDialog

    app = QApplication.instance() or QApplication([])
    dlg = AudioPlayerDialog()

    track = TrackSong(path="dummy.mp3")
    track.ID = 42
    track.title = "Selected Song"
    track.artist = "Artist Name"
    track.album = "Album Name"
    track.type = 1
    track.year = 1960

    dlg._tangoList.tracks = {42: track}
    library_header = ["#", " ", "Title", "Artist", "Album", "Genre", "Year", "BPM", "Time"]
    library_data = [track.list()]
    dlg.sourceModel = tableModels.milongaSource(dlg, library_data, library_header, dlg.TYPE)
    dlg.sourceProxyModel = tableModels.sourceFilterProxyModel(dlg)
    dlg.sourceProxyModel.setSourceModel(dlg.sourceModel)
    dlg._dialog.milongaSource.setModel(dlg.sourceProxyModel)

    dlg._dialog.milongaSource.selectRow(0)
    dlg._handleLibrarySelectionChanged(None, None)

    assert dlg.curTango is track
    assert dlg.sideContent.labelArtist.text() == "Artist Name"
    assert dlg.sideContent.labelTitle.text() == "Selected Song ( 1960 )"
    assert dlg.sideContent.labelType.text() == dlg.TYPE[1][1].upper()
    assert dlg._dialog.labelArtist.text() == "Artist Name"
    assert dlg._dialog.labelAlbum.text() == "Album Name"
    assert dlg._dialog.labelTitle.text() == "Selected Song"
    assert dlg._dialog.labelTypeSong.text() == dlg.TYPE[1][1].upper()

    dlg.close()
    if hasattr(app, "quit"):
        app.quit()


def test_library_selection_shows_metadata_above_library(monkeypatch):
    if not (importlib.util.find_spec("PySide6") or importlib.util.find_spec("PyQt5")):
        pytest.skip("Qt bindings not available")

    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setenv("TTVTTM_DISABLE_DIR_SCAN", "1")

    from ttvttm import tableModels
    from ttvttm.tracksong import TrackSong
    from ttvttm.TTVTTM import AudioPlayerDialog

    app = QApplication.instance() or QApplication([])
    dlg = AudioPlayerDialog()

    track = TrackSong(path="dummy.mp3")
    track.ID = 24
    track.title = "Library Track"
    track.artist = "Library Artist"
    track.album = "Library Album"
    track.type = 2
    track.year = 1984

    dlg._tangoList.tracks = {24: track}
    library_header = ["#", " ", "Title", "Artist", "Album", "Genre", "Year", "BPM", "Time"]
    library_data = [track.list()]
    dlg.sourceModel = tableModels.milongaSource(dlg, library_data, library_header, dlg.TYPE)
    dlg.sourceProxyModel = tableModels.sourceFilterProxyModel(dlg)
    dlg.sourceProxyModel.setSourceModel(dlg.sourceModel)
    dlg._dialog.milongaSource.setModel(dlg.sourceProxyModel)

    dlg._dialog.milongaSource.selectRow(0)
    dlg._handleLibrarySelectionChanged(None, None)

    assert dlg._dialog.labelTitle.text() == "Library Track"
    assert dlg._dialog.labelArtist.text() == "Library Artist"
    assert dlg._dialog.labelAlbum.text() == "Library Album"
    assert dlg._dialog.labelTypeSong.text() == dlg.TYPE[2][1].upper()

    dlg.close()
    if hasattr(app, "quit"):
        app.quit()


def test_library_selection_with_non_numeric_type_does_not_crash(monkeypatch):
    if not (importlib.util.find_spec("PySide6") or importlib.util.find_spec("PyQt5")):
        pytest.skip("Qt bindings not available")

    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setenv("TTVTTM_DISABLE_DIR_SCAN", "1")

    from ttvttm import tableModels
    from ttvttm.tracksong import TrackSong
    from ttvttm.TTVTTM import AudioPlayerDialog

    app = QApplication.instance() or QApplication([])
    dlg = AudioPlayerDialog()

    track = TrackSong(path="dummy.mp3")
    track.ID = 99
    track.title = "Latina Groove"
    track.artist = "Latina Artist"
    track.album = "Latina Album"
    track.type = "Latina"
    track.year = 2000

    dlg._tangoList.tracks = {99: track}
    library_header = ["#", " ", "Title", "Artist", "Album", "Genre", "Year", "BPM", "Time"]
    library_data = [track.list()]
    dlg.sourceModel = tableModels.milongaSource(dlg, library_data, library_header, dlg.TYPE)
    dlg.sourceProxyModel = tableModels.sourceFilterProxyModel(dlg)
    dlg.sourceProxyModel.setSourceModel(dlg.sourceModel)
    dlg._dialog.milongaSource.setModel(dlg.sourceProxyModel)

    dlg._dialog.milongaSource.selectRow(0)
    dlg._handleLibrarySelectionChanged(None, None)

    assert dlg.sideContent.labelType.text() == dlg.TYPE[5][1].upper()
    assert dlg.sideContent.labelTitle.text() == "Latina Groove ( 2000 )"
    assert dlg.sideContent.labelArtist.text() == "Latina Artist"

    dlg.close()
    if hasattr(app, "quit"):
        app.quit()


def test_library_selection_calls_update_handlers(monkeypatch):
    if not (importlib.util.find_spec("PySide6") or importlib.util.find_spec("PyQt5")):
        pytest.skip("Qt bindings not available")

    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setenv("TTVTTM_DISABLE_DIR_SCAN", "1")

    from ttvttm import tableModels
    from ttvttm.tracksong import TrackSong
    from ttvttm.TTVTTM import AudioPlayerDialog

    update_calls = []

    def spy_update_selected_library_row(self):
        update_calls.append("selected")

    monkeypatch.setattr(AudioPlayerDialog, "_updateSelectedLibraryRow", spy_update_selected_library_row)

    app = QApplication.instance() or QApplication([])
    dlg = AudioPlayerDialog()

    track = TrackSong(path="dummy.mp3")
    track.ID = 24
    track.title = "Library Track"
    track.artist = "Library Artist"
    track.album = "Library Album"
    track.type = 2
    track.year = 1984

    dlg._tangoList.tracks = {24: track}
    library_header = ["#", " ", "Title", "Artist", "Album", "Genre", "Year", "BPM", "Time"]
    library_data = [track.list()]
    dlg.sourceModel = tableModels.milongaSource(dlg, library_data, library_header, dlg.TYPE)
    dlg.sourceProxyModel = tableModels.sourceFilterProxyModel(dlg)
    dlg.sourceProxyModel.setSourceModel(dlg.sourceModel)
    dlg._dialog.milongaSource.setModel(dlg.sourceProxyModel)

    index = dlg.sourceModel.index(0, 0)
    dlg._dialog.milongaSource.clicked.emit(index)
    app.processEvents()

    assert update_calls == ["selected"]

    dlg.close()
    if hasattr(app, "quit"):
        app.quit()
