import importlib
import os

import pytest
from djtango.qt_compat import QApplication, QMainWindow


def test_qt_compat_loads_qapplication():
    assert callable(QApplication)
    assert callable(QMainWindow)


def test_gui_starts_in_offscreen_mode(monkeypatch):
    if not (importlib.util.find_spec('PySide6') or importlib.util.find_spec('PyQt5')):
        pytest.skip('Qt bindings not available')

    monkeypatch.setenv('QT_QPA_PLATFORM', 'offscreen')
    monkeypatch.setenv('DJTANGO_DISABLE_DIR_SCAN', '1')

    from djtango.DJTango import AudioPlayerDialog

    app = QApplication.instance() or QApplication([])
    dlg = AudioPlayerDialog()
    dlg.close()
    if hasattr(app, 'quit'):
        app.quit()


def test_library_selection_updates_side_display(monkeypatch):
    if not (importlib.util.find_spec('PySide6') or importlib.util.find_spec('PyQt5')):
        pytest.skip('Qt bindings not available')

    monkeypatch.setenv('QT_QPA_PLATFORM', 'offscreen')
    monkeypatch.setenv('DJTANGO_DISABLE_DIR_SCAN', '1')

    from djtango.DJTango import AudioPlayerDialog
    from djtango import tableModels
    from djtango.tangosong import TangoSong

    app = QApplication.instance() or QApplication([])
    dlg = AudioPlayerDialog()

    tango = TangoSong(path='dummy.mp3')
    tango.ID = 42
    tango.title = 'Selected Song'
    tango.artist = 'Artist Name'
    tango.album = 'Album Name'
    tango.type = 1
    tango.year = 1960

    dlg._tangoList.tangos = {42: tango}
    library_header = ['#', ' ', 'Title', 'Artist', 'Album', 'Genre', 'Year', 'BPM', 'Time']
    library_data = [tango.list()]
    dlg.sourceModel = tableModels.milongaSource(dlg, library_data, library_header, dlg.TYPE)
    dlg.sourceProxyModel = tableModels.sourceFilterProxyModel(dlg)
    dlg.sourceProxyModel.setSourceModel(dlg.sourceModel)
    dlg._dialog.milongaSource.setModel(dlg.sourceProxyModel)

    dlg._dialog.milongaSource.selectRow(0)
    dlg._handleLibrarySelectionChanged(None, None)

    assert dlg.curTango is tango
    assert dlg.sideContent.labelArtist.text() == 'Artist Name'
    assert dlg.sideContent.labelTitle.text() == 'Selected Song ( 1960 )'
    assert dlg.sideContent.labelType.text() == dlg.TYPE[1][1].upper()
    assert dlg._dialog.labelArtist.text() == 'Artist Name'
    assert dlg._dialog.labelAlbum.text() == 'Album Name'
    assert dlg._dialog.labelTitle.text() == 'Selected Song'
    assert dlg._dialog.labelTypeSong.text() == dlg.TYPE[1][1].upper()

    dlg.close()
    if hasattr(app, 'quit'):
        app.quit()
