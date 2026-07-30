#!/usr/bin/python3
# -*- coding:Utf-8 -*-
import os
import signal
import sys

if getattr(sys, "frozen", False):
    ROOT = getattr(sys, "_MEIPASS", os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
else:
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import logging
import os
import sys
import threading
import time

import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
from PySide6.QtCore import QObject, Qt, QTimer
from PySide6.QtCore import Signal as pyqtSignal
from PySide6.QtCore import Slot as pyqtSlot
from PySide6.QtGui import QIcon
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QProgressDialog,
    QStyleFactory,
)

from ttvttm.ask_delete_dialog import AskDeleteDialogMixin
from ttvttm.audio_playback import AudioPlaybackMixin
from ttvttm.connections import ConnectionsMixin
from ttvttm.data import djDataConnection
from ttvttm.dirsong import dirSong
from ttvttm.dummy_progress import DummyProgressDialog
from ttvttm.gui_helpers import InfoThreading
from ttvttm.info_display import InfoDisplayMixin
from ttvttm.info_milonga_window import InfoMilongaWindowMixin
from ttvttm.info_window import InfoWindowMixin
from ttvttm.library_manager import LibraryManagerMixin
from ttvttm.library_scanner import LibraryScannerMixin
from ttvttm.menu_actions import MenuActionsMixin
from ttvttm.milonga_manager import MilongaManagerMixin
from ttvttm.milonga_name_dialog import MilongaNameDialogMixin
from ttvttm.milonga_select_dialog import MilongaSelectDialogMixin
from ttvttm.preferences import PreferencesMixin
from ttvttm.preferences_helpers import PreferencesHelperMixin
from ttvttm.progress_bar import ProgressBarMixin
from ttvttm.selection_handlers import SelectionHandlerMixin
from ttvttm.shortcuts import ShortcutsMixin
from ttvttm.side_display import SideDisplayMixin
from ttvttm.side_display_window import SideDisplayWindowMixin
from ttvttm.tap_dialog import TapDialogMixin
from ttvttm.track_customization import TrackCustomizationMixin
from ttvttm.track_details_dialog import TrackDetailsDialogMixin
from ttvttm.track_properties import TrackPropertiesMixin
from ttvttm.ui_setup import UISetupMixin
from ttvttm.ui_theme import (
    dialog_style,
    load_app_theme,
    progress_dialog_style,
)
from ttvttm.visibility_controls import VisibilityControlsMixin


def _qt_sigint_handler(signum, frame):
    app = QApplication.instance()
    if app is not None:
        app.closeAllWindows()
        app.quit()
    timer = threading.Timer(3.0, lambda: os._exit(0))
    timer.daemon = True
    timer.start()

LOG_DIR = os.path.join(os.path.expanduser("~"), ".ttvttm")
try:
    os.makedirs(LOG_DIR, exist_ok=True)
except Exception:
    pass

LOG_FILE = os.path.join(LOG_DIR, "ttvttm.log")
logger = logging.getLogger("ttvttm")
if not logger.handlers:
    handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
logger.debug("Logger initialized at %s", LOG_FILE)

QString = getattr(QtCore, "QString", None)
if QString is not None:
    _fromUtf8 = QString.fromUtf8
else:
    def _fromUtf8(s):
        return s


class AudioPlayerDialog(AudioPlaybackMixin, SelectionHandlerMixin, LibraryManagerMixin, LibraryScannerMixin, MilongaManagerMixin, SideDisplayMixin, SideDisplayWindowMixin, InfoDisplayMixin, InfoWindowMixin, InfoMilongaWindowMixin, TapDialogMixin, TrackDetailsDialogMixin, MilongaSelectDialogMixin, MilongaNameDialogMixin, AskDeleteDialogMixin, UISetupMixin, ConnectionsMixin, ShortcutsMixin, VisibilityControlsMixin, TrackCustomizationMixin, TrackPropertiesMixin, ProgressBarMixin, MenuActionsMixin, PreferencesMixin, PreferencesHelperMixin, QMainWindow, QObject):
    trackListUpdated = pyqtSignal(dirSong)
    workingOnNewfileStatus = pyqtSignal(bool)

    def __init__(self):
        QMainWindow.__init__(self)
        self._set_window_icon()
        self._initialize_state()
        self._setup_progress_bar()
        self._ensure_database()
        self.TYPE = self.djData.getTrackTypeList()
        self._configure_audio_preferences()
        self._create_application_palette()
        self._show_first_time_dialog_if_needed()
        self._initialize_tango_list()

        self.curTango = None
        self._setup_library_scanner()

        # necessary methods to create a user interface
        self._createUI()

        # Connect slots with signals.
        self._connect()

        # Create the shortcuts
        self._createShorcuts()

        # launch the worker thread only when directory scanning is enabled
        self._start_library_scanner()

        # Show the Audio player when not running headless.
        if not self.disableDirScan:
            self.show()
        else:
            print("Headless mode: main window not shown")

    def _set_window_icon(self):
        icon_path = os.path.join(ROOT, "gui", "img", "djt.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def _initialize_state(self):
        self.bpm = 0
        self.tapTable = []
        self.info_thread = InfoThreading()
        self.mediaSource = None
        self.djhome = os.environ.get("DJ_HOME_PATH", os.path.join(os.path.expanduser("~"), ".ttvttm"))
        print("DJ_HOME_PATH: " + self.djhome)
        self.addedEffects = {}
        self.effectsDict = {}
        self.curTango = None
        self.curLibraryRow = 0
        self.djData = djDataConnection(self.djhome)
        self.disableDirScan = os.environ.get("TTVTTM_DISABLE_DIR_SCAN", "0") == "1" or os.environ.get("QT_QPA_PLATFORM") == "offscreen"
        self.curTangoEditingIndexes = []
        self.curTangoEditing = 0  # an index for the current track edited in properties window
        self.volumeSetToInitial = True
        self.infoMilongaSentence = ""
        self._isPlaying = False
        self._isPaused = False
        self._isMilongaPlaying = False
        self._startMilongaTimeStamp = 0
        self._curMilongaLine = 0
        self._isClicked = False  # to be sure to do nothing on changing state if it's clicked
        self._currentIndex = 0
        self._filePath = ""
        self._dialog = None
        self.player = QMediaPlayer()
        self.firstTime = False

    def _ensure_database(self):
        if not os.path.exists(self.djData.path):
            print("it's the first time, will create the database")
            self.djData.createDatabase()
            self.firstTime = True

    def _configure_audio_preferences(self):
        prop = self.djData.getPreferences()
        self.audioPath = prop["path"]
        self.durationFadOut = prop["fadoutTime"] * 1000  # in ms
        self.FadOutTime = prop["cortinaDuration"] * 1000  # in ms, to get form the database
        self.writeTag = prop["writeTag"]
        self.normalize = prop["normalize"]
        self.stepFadOut = self.durationFadOut / (self.player.notifyInterval() if hasattr(self.player, "notifyInterval") else 100)
        self.duration = 0

    def _create_application_palette(self):
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(160, 52, 77, 150))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(160, 52, 77, 150))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(160, 52, 77, 150))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(160, 52, 77, 150))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)

    def _show_first_time_dialog_if_needed(self):
        if not self.firstTime:
            return

        if self.disableDirScan:
            print("Skipping first-time user dialog in offscreen/CI mode")
            return

        introDialog = QMessageBox()
        introDialog.setStyleSheet(dialog_style())
        introDialog.setWindowTitle("First time user ?")
        introDialog.setText(
            "Looks like this is the first time  using ttvttm. \nSelect the directory for your music library.")
        introDialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        introDialog.setDefaultButton(QMessageBox.Ok)
        if introDialog.exec() == QMessageBox.Ok:
            self.audioPath = QFileDialog.getExistingDirectory(
                self,
                "Open Library directory",
                os.path.expanduser("~"),
                QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
            )
            self.djData.updateSongPath(self.audioPath)
            time.sleep(0.3)
        else:
            sys.exit(0)

    def _initialize_tango_list(self):
        progressBar = self._build_progress_dialog()
        self._tangoList = dirSong(self.audioPath, self.firstTime, progressBar, self.djData)
        progressBar.reset()
        if not self.firstTime:
            self._tangoList.loadTangos(self.djData.getAllTracks())

    def _build_progress_dialog(self):
        if self.disableDirScan:
            return self._build_dummy_progress_dialog()

        progressBar = QProgressDialog("Scanning dir and analyzing the tracks...", "Abort", 0, 100, self)
        progressBar.setWindowTitle("Importing tracks into the database and setting tags")
        progressBar.setWindowModality(Qt.WindowModal)
        progressBar.setStyleSheet(progress_dialog_style())
        progressBar.reset()
        return progressBar

    def _build_dummy_progress_dialog(self):
        return DummyProgressDialog()

    def closeEvent(self, evt):
        """
        Overrides QMainWindow.closeEvent.
        """
        self.player.stop()
        self.infoWindow.close()
        self.prefWindow.close()
        self.sideWindow.close()
        self._stop_library_scanner()
        if hasattr(self, "info_thread") and self.info_thread is not None:
            self.info_thread.exiting = True
            try:
                self.info_thread.wait(1000)
            except Exception:
                pass
        QMainWindow.closeEvent(self, evt)

    @pyqtSlot(list, list)
    def done(self, datas, tracks):

        self.workingOnNewfileStatus.emit(True)
        # datas = newfiles[0]
        # tracks = newfiles[1]
        for track in tracks:
            self._tangoList.addTango(track)  # add a Track with only the path
        self.sourceModel.addNewData(datas)  # update the table
        self._showInfo(str(len(tracks)) + " track has been added")
        self.workingOnNewfileStatus.emit(False)


# ----------------------------------
# Run the Audio Player !
# ----------------------------------

def _ensure_desktop_file():
    desktop_dir = os.path.expanduser("~/.local/share/applications")
    try:
        os.makedirs(desktop_dir, exist_ok=True)
    except OSError:
        return

    desktop_file = os.path.join(desktop_dir, "ttvttm.desktop")
    exec_path = os.path.join(ROOT, ".venv", "bin", "python")
    if not os.path.exists(exec_path):
        exec_path = sys.executable or exec_path
    app_path = os.path.join(ROOT, "bin", "ttvttm.py")
    icon_path = os.path.join(ROOT, "gui", "img", "djt.ico")
    desktop_contents = f"""[Desktop Entry]
Type=Application
Name=ttvttm
Comment=ttvttm music playlist and milonga app
Exec={exec_path} {app_path}
Path={ROOT}
Icon={icon_path}
Terminal=false
Categories=Audio;Music;Qt;
StartupWMClass=ttvttm
X-GNOME-WMClass=ttvttm
"""
    try:
        with open(desktop_file, "w", encoding="utf-8") as handle:
            handle.write(desktop_contents)
    except OSError:
        pass


def main(argv=None):
    if argv is None:
        argv = sys.argv
    _ensure_desktop_file()
    print("Starting ttvttm...", flush=True)
    signal.signal(signal.SIGINT, _qt_sigint_handler)
    app = QApplication(argv)
    signal.signal(signal.SIGINT, _qt_sigint_handler)
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(1000)
    app.setApplicationName("ttvttm")
    app.setApplicationDisplayName("")
    app.setOrganizationName("ttvttm")
    app.setDesktopFileName("ttvttm.desktop")
    try:
        icon_path = os.path.join(ROOT, "gui", "img", "djt.ico")
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
        native_style = app.style().objectName()
        app.setStyle(QStyleFactory.create(native_style))
        app.setPalette(app.style().standardPalette())
        load_app_theme(app)
    except Exception as err:
        logger.warning("Could not apply native OS style: %s", err)
    musicPlayer = AudioPlayerDialog()
    app.aboutToQuit.connect(musicPlayer.close)
    signal.signal(signal.SIGINT, lambda signum, frame: _qt_sigint_handler(signum, frame))
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(1000)
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())
