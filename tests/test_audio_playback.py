import os
import tempfile
import unittest
from types import SimpleNamespace

from PySide6.QtWidgets import QApplication

from ttvttm.audio_playback import AudioPlaybackMixin


class DummyPlayer:
    def __init__(self):
        self.source = None
        self.play_called = False

    def setSource(self, source):
        self.source = source

    def play(self):
        self.play_called = True


class DummyDialog:
    def __init__(self):
        self.playToolButton = SimpleNamespace(setIcon=lambda icon: None)
        self.timeLabel = SimpleNamespace(setText=lambda text: None)


class AudioPlaybackMixinTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    @classmethod
    def tearDownClass(cls):
        if cls.app is not None:
            cls.app.quit()
            cls.app.processEvents()
            cls.app = None

    def setUp(self):
        class Playback(AudioPlaybackMixin):
            pass

        self.playback = Playback()
        self.playback._showInfo = lambda msg: setattr(self.playback, "last_info", msg)
        self.playback._dialog = DummyDialog()
        self.playback.pauseIcon = object()
        self.playback._isMilongaPlaying = False
        self.playback.propWindow = SimpleNamespace(isVisible=lambda: False)
        self.playback._isPaused = False
        self.playback.ok_to_play_pause_stop = lambda: True
        self.playback.update_tango_infos = lambda track: None
        self.playback.seek = lambda seconds: setattr(self.playback, "seek_position", seconds)
        self.playback.player = DummyPlayer()
        self.playback.bar = SimpleNamespace(setRange=lambda *args, **kwargs: None, setValue=lambda *args, **kwargs: None)
        self.playback._dialog.songSlider = SimpleNamespace(isSliderDown=lambda: False, setValue=lambda value: None, maximum=lambda: 0, minimum=lambda: 0)
        self.playback.duration = 0
        self.playback.volumeSetToInitial = True
        self.playback._dialog.checkBoxLetCortinaUntilEnd = SimpleNamespace(isChecked=lambda: False, setCheckState=lambda state: None)

    def test_load_new_media_sets_source_for_existing_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        try:
            self.playback.curTango = SimpleNamespace(path=tmp_path)
            self.assertTrue(self.playback._load_new_media())
            self.assertIsNotNone(self.playback.mediaSource)
            self.assertEqual(self.playback.player.source.toLocalFile(), tmp_path)
            self.assertEqual(self.playback.player.source, self.playback.mediaSource)
        finally:
            os.remove(tmp_path)

    def test_load_new_media_returns_false_for_missing_file(self):
        self.playback.curTango = SimpleNamespace(path="/tmp/does-not-exist.mp3")
        self.assertFalse(self.playback._load_new_media())
        self.assertEqual(getattr(self.playback, "last_info", ""), "This file is not existing on disk, remove it")

    def test_play_media_calls_player_play_when_ready(self):
        self.playback.curTango = SimpleNamespace(path="/tmp/existing.mp3", tstart=0, type=1)
        self.playback._dialog.playToolButton = SimpleNamespace(setIcon=lambda icon: setattr(self.playback, "icon_set", icon))
        self.playback._dialog.timeLabel = SimpleNamespace(setText=lambda text: setattr(self.playback, "time_text", text))
        self.playback._play_media()
        self.assertTrue(self.playback.player.play_called)
        self.assertTrue(self.playback._isPlaying)


if __name__ == "__main__":
    unittest.main()
