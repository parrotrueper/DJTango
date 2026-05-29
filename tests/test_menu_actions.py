import os
import tempfile
import unittest
from unittest.mock import patch

from djtango.qt_compat import QApplication
from djtango.DJTango import AudioPlayerDialog


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

    def test_file_menu_contains_add_files_and_add_directory_and_calls_handlers(self):
        with tempfile.TemporaryDirectory() as tmp_home:
            env = {
                'HOME': tmp_home,
                'QT_QPA_PLATFORM': 'offscreen',
                'DJTANGO_DISABLE_DIR_SCAN': '1',
            }
            called = []

            def fake_open_files_dialog(self):
                called.append('files')

            def fake_open_file_dialog(self):
                called.append('directory')

            with patch.dict(os.environ, env), patch('djtango.DJTango.QMediaPlayer', new=DummyPlayer), patch.object(AudioPlayerDialog, 'open_files_dialog', new=fake_open_files_dialog), patch.object(AudioPlayerDialog, 'open_file_dialog', new=fake_open_file_dialog):
                dialog = AudioPlayerDialog()
                menu_actions = dialog._dialog.menuFile.actions()

                self.assertEqual(len(menu_actions), 2)
                self.assertEqual(menu_actions[0].text(), 'Add files')
                self.assertEqual(menu_actions[1].text(), 'Add directory')

                menu_actions[0].trigger()
                menu_actions[1].trigger()

                dialog.close()
                dialog.deleteLater()
                self.app.processEvents()

            self.assertEqual(called, ['files', 'directory'])

    def test_edit_menu_contains_expected_items_and_calls_handlers(self):
        env = {
            'QT_QPA_PLATFORM': 'offscreen',
            'DJTANGO_DISABLE_DIR_SCAN': '1',
        }
        called = []

        def fake_handelOpenPropWidow(self):
            called.append('details')

        def fake_load_bpm_from_id3_tag(self):
            called.append('load_bpm')

        def fake_handelBpmTappingAction(self):
            called.append('tap_bpm')

        with patch.dict(os.environ, env), patch('djtango.DJTango.QMediaPlayer', new=DummyPlayer), patch.object(AudioPlayerDialog, 'handelOpenPropWidow', new=fake_handelOpenPropWidow), patch.object(AudioPlayerDialog, '_load_bpm_from_id3_tag', new=fake_load_bpm_from_id3_tag), patch.object(AudioPlayerDialog, '_handelBpmTappingAction', new=fake_handelBpmTappingAction):
            dialog = AudioPlayerDialog()
            menu_actions = [action for action in dialog._dialog.menuEdition.actions() if not action.isSeparator()]

            self.assertEqual([action.text() for action in menu_actions], [
                'Preferences',
                'Track Appearance',
                'Edit selected song details',
                'Load BPM from ID3 tag',
                'Tap BPM manually',
            ])

            menu_actions[2].trigger()
            menu_actions[3].trigger()
            menu_actions[4].trigger()

            dialog.close()
            dialog.deleteLater()
            self.app.processEvents()

        self.assertEqual(called, ['details', 'load_bpm', 'tap_bpm'])

    def test_view_menu_contains_fullscreen_and_toggle_side_screen_and_calls_handlers(self):
        env = {
            'QT_QPA_PLATFORM': 'offscreen',
            'DJTANGO_DISABLE_DIR_SCAN': '1',
        }
        called = []

        def fake_handelFullScren(self):
            called.append('fullscreen')

        def fake_handelDisplaySideScreen(self):
            called.append('toggle_side_screen')

        with patch.dict(os.environ, env), patch('djtango.DJTango.QMediaPlayer', new=DummyPlayer), patch.object(AudioPlayerDialog, '_handelFullScren', new=fake_handelFullScren), patch.object(AudioPlayerDialog, '_handelDisplaySideScreen', new=fake_handelDisplaySideScreen):
            dialog = AudioPlayerDialog()
            menu_actions = dialog._dialog.menuDisplay.actions()

            self.assertEqual([action.text() for action in menu_actions], [
                'Fullscreen',
                'Toggle side screen',
            ])
            self.assertEqual(menu_actions[0].shortcut().toString(), 'F11')
            self.assertEqual(menu_actions[1].shortcut().toString(), 'Ctrl+F11')

            menu_actions[0].trigger()
            menu_actions[1].trigger()

            dialog.close()
            dialog.deleteLater()
            self.app.processEvents()

        self.assertEqual(called, ['fullscreen', 'toggle_side_screen'])
