#!/usr/bin/python3
# -*- coding:Utf-8 -*-
import os
import sys
import pdb

if getattr(sys, "frozen", False):
    ROOT = getattr(sys, "_MEIPASS", os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
else:
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from djtango.tangosong import TangoSong
from djtango.dirsong import dirSong
from djtango.data import djDataConnection
from djtango import tableModels
from djtango import utils

from djtango.qt_compat import QMainWindow
from djtango.qt_compat import QProgressDialog
from djtango.qt_compat import QApplication
from djtango.qt_compat import QDesktopWidget
from djtango.qt_compat import QThread
from djtango.qt_compat import QObject
from djtango.qt_compat import pyqtSignal
from djtango.qt_compat import pyqtSlot
from djtango.qt_compat import QFileDialog
from djtango.qt_compat import QIcon
from djtango.qt_compat import QAction
from djtango.qt_compat import QMessageBox
from djtango.qt_compat import QStyleFactory
from djtango.qt_compat import QAbstractTableModel
from djtango.qt_compat import QAbstractItemView
from djtango.qt_compat import QFont
from djtango.qt_compat import QFontMetrics
from djtango.qt_compat import QPalette
from djtango.qt_compat import QSortFilterProxyModel
from djtango.ui_utils import (
    tango_type_key_from_row,
    apply_tango_type_color,
    get_contrast_color,
    get_type_font_color,
    set_type_font_color,
)
from djtango.gui_helpers import TrackAppearanceDialog, InfoThreading, MyTimer
from djtango.audio_playback import AudioPlaybackMixin
from djtango.selection_handlers import SelectionHandlerMixin
from djtango.library_manager import LibraryManagerMixin
from djtango.library_scanner import LibraryScannerMixin
from djtango.milonga_manager import MilongaManagerMixin
from djtango.side_display import SideDisplayMixin
from djtango.side_display_window import SideDisplayWindowMixin
from djtango.info_display import InfoDisplayMixin
from djtango.info_window import InfoWindowMixin
from djtango.info_milonga_window import InfoMilongaWindowMixin
from djtango.tap_dialog import TapDialogMixin
from djtango.track_details_dialog import TrackDetailsDialogMixin
from djtango.milonga_select_dialog import MilongaSelectDialogMixin
from djtango.milonga_name_dialog import MilongaNameDialogMixin
from djtango.ask_delete_dialog import AskDeleteDialogMixin
from djtango.track_customization import TrackCustomizationMixin
from djtango.track_properties import TrackPropertiesMixin
from djtango.menu_actions import MenuActionsMixin
from djtango.preferences import PreferencesMixin
from djtango.preferences_helpers import PreferencesHelperMixin
from djtango.progress_bar import ProgressBarMixin
from djtango.ui_setup import UISetupMixin
from djtango.shortcuts import ShortcutsMixin
from djtango.connections import ConnectionsMixin
from djtango.visibility_controls import VisibilityControlsMixin
from djtango.ui_theme import (
    load_app_theme,
    dialog_style,
    progress_dialog_style,
    qss_color,
    track_preview_style,
    button_style,
    side_display_frame_style,
    side_display_label_style,
)
from mutagen.mp3 import MP3

from djtango.qt_compat import QMediaPlayer, QMediaContent, Qt, QtCore, QtGui, QCursor

import logging
import os, sys, time, threading, operator, re, audioread, platform

LOG_DIR = os.path.join(os.path.expanduser("~"), ".djtango")
try:
    os.makedirs(LOG_DIR, exist_ok=True)
except Exception:
    pass

LOG_FILE = os.path.join(LOG_DIR, "djtango.log")
logger = logging.getLogger("djtango")
if not logger.handlers:
    handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
logger.debug("Logger initialized at %s", LOG_FILE)

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class AudioPlayerDialog(AudioPlaybackMixin, SelectionHandlerMixin, LibraryManagerMixin, LibraryScannerMixin, MilongaManagerMixin, SideDisplayMixin, SideDisplayWindowMixin, InfoDisplayMixin, InfoWindowMixin, InfoMilongaWindowMixin, TapDialogMixin, TrackDetailsDialogMixin, MilongaSelectDialogMixin, MilongaNameDialogMixin, AskDeleteDialogMixin, UISetupMixin, ConnectionsMixin, ShortcutsMixin, VisibilityControlsMixin, TrackCustomizationMixin, TrackPropertiesMixin, ProgressBarMixin, MenuActionsMixin, PreferencesMixin, PreferencesHelperMixin, QMainWindow, QObject):
    tangoListUpdated = pyqtSignal(dirSong)
    workingOnNewfileStatus = pyqtSignal(bool)

    def __init__(self):
        QMainWindow.__init__(self)
        icon_path = os.path.join(ROOT, "gui", "img", "djt.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.bpm = 0

        self.tapTable = []
        self.info_thread = InfoThreading()

        self.mediaSource = None

        self.djhome = os.path.join(os.path.expanduser("~"), ".djtango")
        print('DJ_HOME_PATH: ' + self.djhome)

        self.addedEffects = {}
        self.effectsDict = {}
        self.curTango = None
        self.curLibraryRow = 0
        self.djData = djDataConnection(self.djhome)
        self.disableDirScan = os.environ.get('DJTANGO_DISABLE_DIR_SCAN', '0') == '1' or os.environ.get('QT_QPA_PLATFORM') == 'offscreen'

        self.curTangoEditingIndexes = []
        self.curTangoEditing = 0  # a index telling wich is the current tango idited in properties window
        self.volumeSetToInitial = True

        self.infoMilongaSentence = ''

        # print(mime_types)

        self._isPlaying = False
        self._isPaused = False
        self._isMilongaPlaying = False
        self._startMilongaTimeStamp = 0
        self._curMilongaLine = 0
        self._isClicked = False  # to be sure to do nothing on changing state if it's clicked
        self._currentIndex = 0

        # Initialize some other variables.
        self._filePath = ''
        self._dialog = None

        # self.mediaObj = phonon.Phonon.MediaObject(self)
        self.player = QMediaPlayer()
        # self.mediaObj.setTickInterval(250)
        # self.audioSink = Phonon.AudioOutput(Phonon.MusicCategory, self)
        # self.audioSink.setVolume(1)
        # self.audioPath = Phonon.createPath(self.mediaObj, self.audioSink)
        self.firstTime = False

        self._setup_progress_bar()

        if not os.path.exists(self.djData.path):
            print("it's the first time, will create the database")
            self.djData.createDatabase()
            self.firstTime = True
            # self._tangoList.fillListOfFile()

        # print (self._tangoList.tangos[1].type)
        self.TYPE = self.djData.getTangoTypeList()

        # Tt = TANGO = 1, VALS = 2, MILONGA = 3, CORTINA = 4, UNKNOWN=5
        # print (self.TYPE[1])
        prop = self.djData.getPreferences()

        self.audioPath = prop['path']
        self.durationFadOut = prop['fadoutTime'] * 1000  # in ms
        self.FadOutTime = prop['cortinaDuration'] * 1000  # in ms, to get form the database
        self.writeTag = prop['writeTag']
        self.normalize = prop['normalize']
        self.stepFadOut = self.durationFadOut / (self.player.notifyInterval() if hasattr(self.player, 'notifyInterval') else 100)
        self.duration = 0

        # print("AUDIO PATH IN INITIALIZING DATA : "+self.audioPath)

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

        if self.firstTime:
            if self.disableDirScan:
                print('Skipping first-time user dialog in offscreen/CI mode')
            else:
                introDialog = QMessageBox()
                # introDialog.setPalette(palette)
                introDialog.setStyleSheet(dialog_style())
                introDialog.setWindowTitle("First time user ?")
                # introDialog = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel);
                introDialog.setText(
                    "Hi, I'm DJ-Tango and it appear that is the first time you use me. \nPlease select the directory where all your Tango are stored.");
                introDialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel);
                # introDialog.setModal(True)
                introDialog.setDefaultButton(QMessageBox.Ok);
                # introDialog.button(QMessageBox.Cancel).setDefault(False)
                # for button in introDialog.StandardButtons():
                #    button.setFocusPolicy(setFocusPolicy(QtCore.Qt.NoFocus))
                # introDialog.
                # res = introDialog.exec()
                # print (res)
                if introDialog.exec() == QMessageBox.Ok:
                    self.audioPath = QFileDialog.getExistingDirectory(self, "Open Tango directory", os.path.expanduser('~'),
                                                                      QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks);
                    self.djData.updateSongPath(self.audioPath)
                    time.sleep(0.3)
                else:
                    sys.exit(0)

        class DummyProgressDialog:
            def setWindowTitle(self, *args, **kwargs):
                pass

            def setWindowModality(self, *args, **kwargs):
                pass

            def setStyleSheet(self, *args, **kwargs):
                pass

            def reset(self, *args, **kwargs):
                pass

            def setMaximum(self, *args, **kwargs):
                pass

            def setMinimum(self, *args, **kwargs):
                pass

            def setValue(self, *args, **kwargs):
                pass

            def setLabelText(self, *args, **kwargs):
                pass

            def forceShow(self, *args, **kwargs):
                pass

            def wasCanceled(self, *args, **kwargs):
                return False

        if self.disableDirScan:
            progressBar = DummyProgressDialog()
        else:
            progressBar = QProgressDialog("Scanning dir and analyzing the songs...", "Abort", 0, 100, self)
            progressBar.setWindowTitle("Inporting Tangos in the database and set tags")
            progressBar.setWindowModality(Qt.WindowModal);
            progressBar.setStyleSheet(progress_dialog_style())
            progressBar.reset()

        self._tangoList = dirSong(self.audioPath, self.firstTime, progressBar, self.djData)
        progressBar.reset()
        # self.firstTime = False
        if not self.firstTime:
            self._tangoList.loadTangos(self.djData.getAllTangos())

        self.curTango = None
        self._setup_library_scanner()

        # j'ai modifié
        # Create self._dialog instance and call
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
            print('Headless mode: main window not shown')


    def closeEvent(self, evt):
        """
        Overrides QMainWindow.closeEvent.
        """
        self.player.stop()
        self.infoWindow.close()
        self.prefWindow.close()
        self.sideWindow.close()
        self._stop_library_scanner()
        QMainWindow.closeEvent(self, evt)

    @pyqtSlot(list, list)
    def done(self, datas, tangos):

        # print ("IN DONE")
        # print (len(datas))
        self.workingOnNewfileStatus.emit(True)
        # datas = newfiles[0]
        # tangos = newfiles[1]
        for tango in tangos:
            self._tangoList.addTango(tango)  # add a Tango with only the path
        self.sourceModel.addNewData(datas)  # update the table
        self._showInfo(str(len(tangos)) + " song has been added")
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

    desktop_file = os.path.join(desktop_dir, "djtango.desktop")
    exec_path = os.path.join(ROOT, ".venv", "bin", "python")
    if not os.path.exists(exec_path):
        exec_path = sys.executable or exec_path
    app_path = os.path.join(ROOT, "bin", "DJTango.py")
    icon_path = os.path.join(ROOT, "gui", "img", "djt.ico")
    desktop_contents = f"""[Desktop Entry]
Type=Application
Name=DJTango
Comment=DJTango music playlist and milonga app
Exec={exec_path} {app_path}
Path={ROOT}
Icon={icon_path}
Terminal=false
Categories=Audio;Music;Qt;
StartupWMClass=djtango
X-GNOME-WMClass=djtango
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
    print("Starting DJTango...")
    app = QApplication(argv)
    app.setApplicationName("DJTango")
    app.setApplicationDisplayName("")
    app.setOrganizationName("djtango")
    app.setDesktopFileName("djtango.desktop")
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
    return app.exec()

if __name__ == '__main__':
    raise SystemExit(main())
