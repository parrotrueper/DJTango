import os
import tempfile
import unittest
from unittest.mock import patch

from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QApplication, QDialog, QTableView, QWidget

from ttvttm.gui_helpers import TrackAppearanceDialog
from ttvttm.menu_actions import LibraryContentsDialog
from ttvttm.TTVTTM import AudioPlayerDialog


class DummySignal:
    def connect(self, *args, **kwargs):
        pass


class DummyPlayer:
    def __init__(self):
        self.durationChanged = DummySignal()
        self.positionChanged = DummySignal()
        self.playbackStateChanged = DummySignal()
        self.stateChanged = DummySignal()

    def notifyInterval(self):
        return 100

    def playbackState(self):
        return 0

    def state(self):
        return 0

    def stop(self):
        pass

    def setVolume(self, volume):
        pass

    def setPosition(self, position):
        pass


class FileMenuActionsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    @classmethod
    def tearDownClass(cls):
        if cls.app is not None:
            cls.app.quit()
            cls.app.processEvents()
            cls.app = None

    def test_file_menu_contains_library_submenu_and_calls_handlers(self):
        with tempfile.TemporaryDirectory() as tmp_home:
            env = {
                "HOME": tmp_home,
                "QT_QPA_PLATFORM": "offscreen",
                "TTVTTM_DISABLE_DIR_SCAN": "1",
            }
            called = []

            def fake_open_files_dialog(self):
                called.append("files")

            def fake_open_file_dialog(self):
                called.append("directory")

            with patch.dict(os.environ, env), patch("ttvttm.TTVTTM.QMediaPlayer", new=DummyPlayer), patch.object(AudioPlayerDialog, "open_files_dialog", new=fake_open_files_dialog), patch.object(AudioPlayerDialog, "open_file_dialog", new=fake_open_file_dialog):
                dialog = AudioPlayerDialog()
                menu_actions = dialog._dialog.menuFile.actions()

                self.assertEqual(len(menu_actions), 1)
                self.assertEqual(menu_actions[0].text(), "Library")

                library_menu = menu_actions[0].menu()
                library_actions = library_menu.actions()
                self.assertEqual([action.text() for action in library_actions], ["Add files", "Add directory", "Library contents..."])

                library_actions[0].trigger()
                library_actions[1].trigger()

                dialog.close()
                dialog.deleteLater()
                self.app.processEvents()

            self.assertEqual(called, ["files", "directory"])

    def test_library_contents_action_opens_the_dialog(self):
        with tempfile.TemporaryDirectory() as tmp_home:
            env = {
                "HOME": tmp_home,
                "QT_QPA_PLATFORM": "offscreen",
                "TTVTTM_DISABLE_DIR_SCAN": "1",
            }
            called = []

            def fake_open_library_contents_dialog(self):
                called.append("library_contents")

            with patch.dict(os.environ, env), patch("ttvttm.TTVTTM.QMediaPlayer", new=DummyPlayer), patch.object(AudioPlayerDialog, "open_library_contents_dialog", new=fake_open_library_contents_dialog):
                dialog = AudioPlayerDialog()
                library_menu = dialog._dialog.menuFile.actions()[0].menu()
                library_contents_action = [action for action in library_menu.actions() if action.text() == "Library contents..."][0]
                library_contents_action.trigger()
                dialog.close()
                dialog.deleteLater()
                self.app.processEvents()

            self.assertEqual(called, ["library_contents"])

    def test_library_contents_dialog_uses_default_library_list_style(self):
        dialog = LibraryContentsDialog(None, os.getcwd())
        stylesheet = dialog.tree.styleSheet()
        self.assertIn("background: rgb(42, 42, 42);", stylesheet)
        self.assertIn("alternate-background-color: rgb(34, 34, 48);", stylesheet)
        self.assertIn("color: #d3d3d3;", stylesheet)
        self.assertIn("selection-background-color: rgb(64, 64, 64);", stylesheet)
        dialog.close()

    def test_exclude_library_path_removes_track_and_persists_exclusion(self):
        with tempfile.TemporaryDirectory() as tmp_home, tempfile.TemporaryDirectory() as library_dir:
            env = {
                "HOME": tmp_home,
                "QT_QPA_PLATFORM": "offscreen",
                "TTVTTM_DISABLE_DIR_SCAN": "1",
                "DJ_HOME_PATH": tmp_home,
            }
            track_path = os.path.join(library_dir, "song.mp3")
            open(track_path, "a").close()

            with patch.dict(os.environ, env), patch("ttvttm.TTVTTM.QMediaPlayer", new=DummyPlayer):
                dialog = AudioPlayerDialog()
                dialog._tangoList.songpath = library_dir

                from ttvttm.tracksong import TrackSong
                track = TrackSong(track_path, 0, False)
                track.type = "unknown"
                dialog.djData.insertTrack(track)
                dialog._tangoList.loadTangos(dialog.djData.getAllTracks())
                dialog.sourceModel.changeData([t.list() for t in dialog._tangoList.tracks.values()])

                self.assertIn(track_path, dialog._tangoList.listFiles)
                self.assertEqual(dialog.djData.getAllTracks()[0].path, track_path)

                dialog.exclude_library_path(track_path)

                self.assertNotIn(track_path, dialog._tangoList.listFiles)
                self.assertEqual(dialog.djData.getExcludedPaths(), [os.path.abspath(track_path)])
                self.assertEqual(dialog.djData.getAllTracks(), [])

                dialog.close()
                dialog.deleteLater()
                self.app.processEvents()

    def test_edit_menu_contains_expected_items_and_calls_handlers(self):
        env = {
            "QT_QPA_PLATFORM": "offscreen",
            "TTVTTM_DISABLE_DIR_SCAN": "1",
        }
        called = []

        def fake_handelOpenPropWidow(self):
            called.append("details")

        def fake_load_bpm_from_id3_tag(self):
            called.append("load_bpm")

        def fake_handelBpmTappingAction(self):
            called.append("tap_bpm")

        with patch.dict(os.environ, env), patch("ttvttm.TTVTTM.QMediaPlayer", new=DummyPlayer), patch.object(AudioPlayerDialog, "handelOpenPropWidow", new=fake_handelOpenPropWidow), patch.object(AudioPlayerDialog, "_load_bpm_from_id3_tag", new=fake_load_bpm_from_id3_tag), patch.object(AudioPlayerDialog, "_handelBpmTappingAction", new=fake_handelBpmTappingAction):
            dialog = AudioPlayerDialog()
            menu_actions = [action for action in dialog._dialog.menuEdition.actions() if not action.isSeparator()]

            self.assertEqual([action.text() for action in menu_actions], [
                "Preferences",
                "Track Appearance",
                "Edit selected track details",
                "Load BPM from ID3 tag",
                "Tap BPM manually",
            ])

            menu_actions[2].trigger()
            menu_actions[3].trigger()
            menu_actions[4].trigger()

            dialog.close()
            dialog.deleteLater()
            self.app.processEvents()

        self.assertEqual(called, ["details", "load_bpm", "tap_bpm"])

    def test_track_appearance_menu_updates_type_and_calls_color_font_handlers(self):
        with tempfile.TemporaryDirectory() as tmp_home:
            env = {
                "HOME": tmp_home,
                "QT_QPA_PLATFORM": "offscreen",
                "TTVTTM_DISABLE_DIR_SCAN": "1",
                "DJ_HOME_PATH": tmp_home,
            }
            called = []

            def fake_show_info(self, msg):
                called.append(msg)

            def fake_update_side_screen(self):
                called.append("side_screen")

            def fake_exec(self):
                self._selectTangoChange(0)
                self.colorDialog.setCurrentColor(QColor(10, 20, 30, 255))
                self._selectTangoColor()
                self.colorDialog.setCurrentColor(QColor(255, 255, 255, 255))
                self._selectTangoFontColor()
                return QDialog.Accepted

            with patch.dict(os.environ, env), patch("ttvttm.TTVTTM.QMediaPlayer", new=DummyPlayer), patch.object(AudioPlayerDialog, "_showInfo", new=fake_show_info), patch.object(AudioPlayerDialog, "_updateSideScreen", new=fake_update_side_screen), patch.object(TrackAppearanceDialog, "exec", new=fake_exec):
                dialog = AudioPlayerDialog()
                track_appearance_action = [action for action in dialog._dialog.menuEdition.actions() if action.text() == "Track Appearance"][0]
                track_appearance_action.trigger()
                dialog.close()
                dialog.deleteLater()
                self.app.processEvents()

            self.assertIn("Track appearance saved", called)
            self.assertIn("side_screen", called)

    def test_track_appearance_dialog_apply_button_commits_changes_without_closing(self):
        parent = QWidget()
        parent.TYPE = {1: ("track", "Track", 42, 42, 42, 255)}
        parent.djData = unittest.mock.Mock()
        parent._showInfo = unittest.mock.Mock()
        parent._updateSideScreen = unittest.mock.Mock()

        dialog = TrackAppearanceDialog(parent.TYPE, parent=parent)
        self.assertTrue(hasattr(dialog, "applyButton"))
        self.assertEqual(dialog.applyButton.text(), "Apply")

        dialog.typesList.setCurrentRow(0)
        dialog.colorDialog.setCurrentColor(QColor(10, 20, 30, 255))
        dialog._selectTangoColor()
        dialog.colorDialog.setCurrentColor(QColor(255, 255, 255, 255))
        dialog._selectTangoFontColor()
        dialog._applyTypeChanges()

        self.assertEqual(parent.TYPE[1][2:6], (10, 20, 30, 255))
        parent.djData.updateType.assert_called_once_with(parent.TYPE)
        parent._showInfo.assert_called_once_with("Track appearance applied")
        parent._updateSideScreen.assert_called_once()

    def test_track_appearance_dialog_choose_font_button_updates_preview_font(self):
        parent = QWidget()
        dialog = TrackAppearanceDialog({1: ("track", "Track", 42, 42, 42, 255)}, parent=parent)
        self.assertTrue(hasattr(dialog, "selectFontButton"))
        self.assertEqual(dialog.selectFontButton.text(), "Choose font")

        original_font = dialog.previewLabel.font()

        class DummyFontDialog:
            def __init__(self, parent=None):
                self.parent = parent
                self._current_font = None
                self.title = ""

            def setCurrentFont(self, font):
                self._current_font = font

            def setWindowTitle(self, title):
                self.title = title

            def exec(self):
                return QDialog.Accepted

            def selectedFont(self):
                return QFont("Arial", 16)

        with patch("ttvttm.gui_helpers.QFontDialog", new=DummyFontDialog):
            dialog._openFontDialog()

        self.assertEqual(dialog._currentFont.family(), "Arial")
        self.assertEqual(dialog._currentFont.pointSize(), 16)
        self.assertNotEqual(dialog.previewLabel.font().family(), original_font.family())
        self.assertEqual(dialog.previewLabel.font().pointSize(), 16)

    def test_track_appearance_apply_updates_library_table_font(self):
        parent = QWidget()
        parent.TYPE = {1: ("track", "Track", 42, 42, 42, 255)}
        parent.djData = unittest.mock.Mock()
        parent._showInfo = unittest.mock.Mock()
        parent._updateSideScreen = unittest.mock.Mock()
        parent._dialog = type("Dialog", (), {})()
        parent._dialog.milongaSource = QTableView(parent)
        parent._dialog.milongaDest = QTableView(parent)

        dialog = TrackAppearanceDialog(parent.TYPE, parent=parent)
        dialog._currentTrackColor = QColor(42, 42, 42, 255)
        dialog._currentFont = QFont("Arial", 18)
        dialog._applyTrackButtonPreview()
        dialog._applyTypeChanges()

        self.assertEqual(parent._dialog.milongaSource.font().family(), "Arial")
        self.assertEqual(parent._dialog.milongaSource.font().pointSize(), 18)
        self.assertEqual(parent.trackAppearanceFont.family(), "Arial")

    def test_view_menu_contains_fullscreen_and_toggle_side_screen_and_calls_handlers(self):
        env = {
            "QT_QPA_PLATFORM": "offscreen",
            "TTVTTM_DISABLE_DIR_SCAN": "1",
        }
        called = []

        def fake_handelFullScren(self):
            called.append("fullscreen")

        def fake_handelDisplaySideScreen(self):
            called.append("toggle_side_screen")

        with patch.dict(os.environ, env), patch("ttvttm.TTVTTM.QMediaPlayer", new=DummyPlayer), patch.object(AudioPlayerDialog, "_handelFullScren", new=fake_handelFullScren), patch.object(AudioPlayerDialog, "_handelDisplaySideScreen", new=fake_handelDisplaySideScreen):
            dialog = AudioPlayerDialog()
            menu_actions = dialog._dialog.menuDisplay.actions()

            self.assertEqual([action.text() for action in menu_actions], [
                "Fullscreen",
                "Toggle side screen",
            ])
            self.assertEqual(menu_actions[0].shortcut().toString(), "F11")
            self.assertEqual(menu_actions[1].shortcut().toString(), "Ctrl+F11")

            menu_actions[0].trigger()
            menu_actions[1].trigger()

            dialog.close()
            dialog.deleteLater()
            self.app.processEvents()

        self.assertEqual(called, ["fullscreen", "toggle_side_screen"])
