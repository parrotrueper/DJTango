import os
import re

import pytest


@pytest.fixture(autouse=True)
def qt_offscreen(monkeypatch):
    """Ensure Qt uses the offscreen platform for headless test environments."""
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")


def is_pyside_available():
    try:
        import PySide6.QtCore  # noqa: F401
        return True
    except Exception:
        return False


def test_quick_main_qml_file_exists():
    from ttvttm.quick_main import QML_FILE

    assert os.path.isfile(QML_FILE), f"Expected QML file to exist at {QML_FILE}"


def test_qml_ids_do_not_start_with_uppercase():
    from ttvttm.quick_main import QML_FILE

    with open(QML_FILE, encoding="utf-8") as qml_file:
        for line_number, line in enumerate(qml_file, start=1):
            if "id:" in line:
                stripped = line.strip()
                if stripped.startswith("id:"):
                    _, value = stripped.split("id:", 1)
                    value = value.strip().split()[0]
                    assert not value[0].isupper(), (
                        f"QML id values must not start with uppercase letters: {value} "
                        f"(found in {QML_FILE}:{line_number})"
                    )


def test_qml_ids_are_unique():
    from ttvttm.quick_main import QML_FILE

    ids = []
    with open(QML_FILE, encoding="utf-8") as qml_file:
        for line_number, line in enumerate(qml_file, start=1):
            match = re.match(r"^\s*id\s*:\s*([A-Za-z_]\w*)\b", line)
            if match:
                ids.append((match.group(1), line_number))

    seen = {}
    duplicates = []
    for value, line_number in ids:
        if value in seen:
            duplicates.append((value, seen[value], line_number))
        else:
            seen[value] = line_number

    assert not duplicates, (
        "Found duplicate QML ids in Main.qml: "
        + ", ".join(f"{name} at lines {first} and {second}" for name, first, second in duplicates)
    )


def test_qml_component_ids_are_not_instantiated_as_types():
    from ttvttm.quick_main import QML_FILE

    with open(QML_FILE, encoding="utf-8") as qml_file:
        lines = qml_file.readlines()

    component_ids = set()
    inside_component = False
    for line in lines:
        if re.match(r"^\s*Component\s*{", line):
            inside_component = True
            continue
        if inside_component:
            id_match = re.match(r"^\s*id\s*:\s*([A-Za-z_]\w*)", line)
            if id_match:
                component_ids.add(id_match.group(1))
                inside_component = False
                continue
            if re.match(r"^\s*}", line):
                inside_component = False

    bad_usages = []
    for line_number, line in enumerate(lines, start=1):
        type_match = re.match(r"^\s*([A-Za-z_]\w*)\s*{", line)
        if type_match:
            type_name = type_match.group(1)
            if type_name in component_ids:
                bad_usages.append((line_number, type_name))

    assert not bad_usages, (
        "Found QML component ids instantiated as types, which is invalid: "
        + ", ".join(f"{name} at line {line}" for line, name in bad_usages)
    )


def test_qml_button_content_properties_are_qualified():
    from ttvttm.quick_main import QML_FILE

    with open(QML_FILE, encoding="utf-8") as qml_file:
        lines = qml_file.readlines()

    violations = []
    for line_number, line in enumerate(lines, start=1):
        if re.search(r"^\s*text\s*:\s*label\b", line):
            violations.append((line_number, line.strip()))
        if re.search(r"^\s*source\s*:\s*iconSource\b", line):
            violations.append((line_number, line.strip()))

    assert not violations, (
        "Found unqualified Button content property usage in Main.qml: "
        + ", ".join(f"line {linenum}: {code}" for linenum, code in violations)
    )


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_qml_backend_importable():
    """Catch startup issues caused by bad imports in the QML backend."""
    try:
        from ttvttm.qml_backend import QmlBackend  # noqa: F401
    except ImportError as exc:
        pytest.fail(f"Unable to import QML backend: {exc}")


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_qml_backend_playback_toggle(monkeypatch, tmp_path):
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "ttvttm_home"))

    from PySide6.QtWidgets import QApplication

    from ttvttm.qml_backend import QmlBackend

    app = QApplication.instance() or QApplication([])

    backend = QmlBackend()
    assert not backend._isPlaying

    dummy_dir = tmp_path / "music"
    dummy_dir.mkdir()
    dummy_track = dummy_dir / "track.wav"
    dummy_track.write_bytes(b"RIFF$\x00\x00\x00WAVEfmt " + b"\x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")

    assert backend.addTrack(str(dummy_track))
    track_id = backend.libraryModel.asList()[0]["id"]
    assert backend.addTrackToPlaylist(track_id)

    assert backend.togglePlayPause()
    assert backend._isPlaying

    assert backend.togglePlayPause()
    assert not backend._isPlaying

    app.quit()


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_qml_backend_app_metadata(monkeypatch, tmp_path):
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "ttvttm_home"))

    from ttvttm.qml_backend import QmlBackend

    backend = QmlBackend()
    assert backend.appTitle() == "ttvttm"
    assert backend.appVersion() == "0.1.0"
    assert backend.liveOutputName() == "Default"
    assert backend.liveVolume() == 100


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_qml_backend_playlist_total_duration(monkeypatch, tmp_path):
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "ttvttm_home"))

    from ttvttm.qml_backend import QmlBackend

    backend = QmlBackend()
    backend._playlistModel.setTracks([
        {"duration": 120},
        {"duration": 182.6},
        {"duration": "33"},
    ])

    assert backend.playlistModel.rowCount() == 3
    assert backend.playlistTotalDuration() == 120 + 183 + 33


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_qml_backend_set_live_session(monkeypatch, tmp_path):
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "ttvttm_home"))

    from ttvttm.qml_backend import QmlBackend

    backend = QmlBackend()
    assert not backend._isLiveSession
    assert backend.setLiveSession(True)
    assert backend._isLiveSession is True
    assert backend.setLiveSession(False)
    assert backend._isLiveSession is False


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_live_session_button_exists_in_qml(monkeypatch, tmp_path):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "ttvttm_home"))

    try:
        from ttvttm.quick_main import create_app
    except ImportError as exc:
        pytest.skip(f"Qt GUI cannot be imported in this environment: {exc}")

    from PySide6.QtCore import QObject

    app, engine = create_app([])
    root = engine.rootObjects()[0]
    live_button = root.findChild(QObject, "liveSessionButton")
    assert live_button is not None
    assert root.property("isLiveSession") is False
    app.quit()


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_playlist_save_controls_exist_in_qml(monkeypatch, tmp_path):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "ttvttm_home"))

    try:
        from ttvttm.quick_main import create_app
    except ImportError as exc:
        pytest.skip(f"Qt GUI cannot be imported in this environment: {exc}")

    from PySide6.QtCore import QObject

    app, engine = create_app([])
    root = engine.rootObjects()[0]

    save_name_field = root.findChild(QObject, "saveNameField")
    save_button = root.findChild(QObject, "playlistSaveButton")
    playlist_selector = root.findChild(QObject, "playlistSelector")
    load_button = root.findChild(QObject, "playlistLoadButton")
    refresh_button = root.findChild(QObject, "playlistRefreshButton")

    assert save_name_field is not None
    assert save_button is not None
    assert playlist_selector is not None
    assert load_button is not None
    assert refresh_button is not None

    assert save_button.property("enabled") is False
    assert playlist_selector.property("currentIndex") == -1

    app.quit()


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_playback_controls_and_slider_exist_in_qml(monkeypatch, tmp_path):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "ttvttm_home"))

    try:
        from ttvttm.quick_main import create_app
    except ImportError as exc:
        pytest.skip(f"Qt GUI cannot be imported in this environment: {exc}")

    from PySide6.QtCore import QObject

    app, engine = create_app([])
    root = engine.rootObjects()[0]

    progress_bar = root.findChild(QObject, "playbackProgressBar")
    prev_button = root.findChild(QObject, "prevButton")
    next_button = root.findChild(QObject, "nextButton")
    live_button = root.findChild(QObject, "liveSessionButton")

    assert progress_bar is not None
    assert prev_button is not None
    assert next_button is not None
    assert live_button is not None

    app.quit()


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_qml_playback_time_labels_update(monkeypatch, tmp_path):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "ttvttm_home"))

    try:
        from ttvttm.quick_main import create_app
    except ImportError as exc:
        pytest.skip(f"Qt GUI cannot be imported in this environment: {exc}")

    from PySide6.QtCore import QObject

    app, engine = create_app([])
    root = engine.rootObjects()[0]
    backend = engine.rootContext().contextProperty("backend")
    assert backend is not None

    elapsed_label = root.findChild(QObject, "playbackTimeElapsed")
    duration_label = root.findChild(QObject, "playbackTimeDuration")
    assert elapsed_label is not None
    assert duration_label is not None

    backend._playbackPosition = 65
    backend._playbackDuration = 245
    backend.playbackPositionChanged.emit()
    backend.playbackDurationChanged.emit()
    app.processEvents()

    assert elapsed_label.property("text") == "1:05"
    assert duration_label.property("text") == "4:05"

    app.quit()


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_qml_playlist_save_and_load_workflow(monkeypatch, tmp_path):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "ttvttm_home"))

    try:
        from ttvttm.quick_main import create_app
    except ImportError as exc:
        pytest.skip(f"Qt GUI cannot be imported in this environment: {exc}")

    from PySide6.QtCore import QObject

    app, engine = create_app([])
    root = engine.rootObjects()[0]
    backend = engine.rootContext().contextProperty("backend")
    assert backend is not None

    save_name_field = root.findChild(QObject, "saveNameField")
    save_button = root.findChild(QObject, "playlistSaveButton")
    playlist_selector = root.findChild(QObject, "playlistSelector")
    load_button = root.findChild(QObject, "playlistLoadButton")

    assert save_name_field is not None
    assert save_button is not None
    assert playlist_selector is not None
    assert load_button is not None

    dummy_dir = tmp_path / "music"
    dummy_dir.mkdir()
    dummy_track = dummy_dir / "track.wav"
    dummy_track.write_bytes(
        b"RIFF$\x00\x00\x00WAVEfmt "
        + b"\x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    )

    assert backend.addTrack(str(dummy_track))
    track_id = backend.libraryModel.asList()[0]["id"]
    assert backend.addTrackToPlaylist(track_id)
    assert backend.playlistModel.rowCount() == 1

    assert save_button.property("enabled") is False
    save_name_field.setProperty("text", "test-playlist")
    app.processEvents()
    assert save_button.property("enabled") is True

    save_button.clicked.emit()
    app.processEvents()

    assert playlist_selector.property("currentIndex") == 0
    assert load_button.property("enabled") is True

    assert backend.removeTrackFromPlaylist(0)
    assert backend.playlistModel.rowCount() == 0

    playlist_selector.setProperty("currentIndex", 0)
    app.processEvents()
    assert playlist_selector.property("currentText") == "test-playlist"

    load_button.clicked.emit()
    app.processEvents()
    assert backend.playlistModel.rowCount() == 1

    app.quit()


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_qml_backend_wip_contexts(monkeypatch, tmp_path):
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "ttvttm_home"))

    from ttvttm.qml_backend import QmlBackend

    backend = QmlBackend()
    contexts = backend.getWipContexts()
    assert contexts == ["Library", "Library 2", "Last playlist"]
    assert backend.currentWipContext() == "Library"
    assert backend.selectWipContext("Library 2")
    assert backend.currentWipContext() == "Library 2"
    assert not backend.selectWipContext("Invalid")


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_qml_backend_playlist_actions(monkeypatch, tmp_path):
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "ttvttm_home"))

    from ttvttm.qml_backend import QmlBackend

    # Ensure the backend uses a fresh temporary database location.
    backend = QmlBackend()
    assert backend.libraryModel.rowCount() == 0

    dummy_dir = tmp_path / "music"
    dummy_dir.mkdir()
    dummy_track = dummy_dir / "track.wav"
    dummy_track.write_text("")

    assert backend.addTrack(str(dummy_track))
    assert backend.libraryModel.rowCount() == 1

    track_id = backend.libraryModel.asList()[0]["id"]
    assert backend.addTrackToPlaylist(track_id)
    assert backend.playlistModel.rowCount() == 1

    assert backend.removeTrackFromPlaylist(0)
    assert backend.playlistModel.rowCount() == 0


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_qml_backend_playlist_playback(monkeypatch, tmp_path):
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "ttvttm_home"))

    import ttvttm.qml_backend as qml_backend

    class DummyAudioOutput:
        def __init__(self, *args, **kwargs):
            pass

    class DummyMediaPlayer:
        def __init__(self, *args, **kwargs):
            self.source = None
            self.audio_output = None
            self.play_called = False
            self.pause_called = False

        def setAudioOutput(self, output):
            self.audio_output = output

        def setSource(self, source):
            self.source = source

        def play(self):
            self.play_called = True

        def pause(self):
            self.pause_called = True

    monkeypatch.setattr(qml_backend, "QMediaPlayer", DummyMediaPlayer)
    monkeypatch.setattr(qml_backend, "QAudioOutput", DummyAudioOutput)

    backend = qml_backend.QmlBackend()

    dummy_dir = tmp_path / "music"
    dummy_dir.mkdir()
    dummy_track = dummy_dir / "track.wav"
    dummy_track.write_bytes(b"RIFF$\x00\x00\x00WAVEfmt " + b"\x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")

    assert backend.addTrack(str(dummy_track))
    assert backend.libraryModel.rowCount() == 1

    track_id = backend.libraryModel.asList()[0]["id"]
    assert backend.addTrackToPlaylist(track_id)
    assert backend.playlistModel.rowCount() == 1

    assert backend.playPlaylistTrack(track_id)
    assert backend._player.play_called is True
    assert backend._player.source is not None
    assert backend._player.source.toLocalFile() == str(dummy_track)


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_qml_backend_save_and_load_playlist(monkeypatch, tmp_path):
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "ttvttm_home"))

    from ttvttm.qml_backend import QmlBackend

    backend = QmlBackend()
    dummy_dir = tmp_path / "music"
    dummy_dir.mkdir()
    dummy_track = dummy_dir / "track.wav"
    dummy_track.write_text("")

    assert backend.addTrack(str(dummy_track))
    track_id = backend.libraryModel.asList()[0]["id"]
    assert backend.addTrackToPlaylist(track_id)
    assert backend.savePlaylist("test-playlist")

    assert backend.playlistModel.rowCount() == 1
    assert backend.removeTrackFromPlaylist(0)
    assert backend.playlistModel.rowCount() == 0

    assert backend.loadPlaylist("test-playlist")
    assert backend.playlistModel.rowCount() == 1


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_qml_backend_m3u8_playlist_scan(monkeypatch, tmp_path):
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "ttvttm_home"))

    from ttvttm.qml_backend import QmlBackend

    backend = QmlBackend()
    playlist_dir = tmp_path / "playlists"
    playlist_dir.mkdir()
    (playlist_dir / "a.m3u8").write_text("#EXTM3U\n")
    (playlist_dir / "b.m3u8").write_text("#EXTM3U\n")
    (playlist_dir / "ignore.txt").write_text("hello")

    results = backend.getM3u8Playlists(str(playlist_dir))
    assert results == ["a.m3u8", "b.m3u8"]


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_quick_main_qml_file_loads_without_errors(monkeypatch, tmp_path):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    import subprocess
    import sys

    script = r"""
import os
import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine
from ttvttm.qml_backend import QmlBackend

app = QGuiApplication([])
engine = QQmlApplicationEngine()
engine.rootContext().setContextProperty('backend', QmlBackend())
qml_file = os.path.abspath(os.path.join(os.getcwd(), 'ttvttm', 'qml', 'Main.qml'))
engine.load(QUrl.fromLocalFile(qml_file))
assert engine.rootObjects(), 'QML root objects should load'
"""

    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "offscreen"
    result = subprocess.run([sys.executable, "-c", script], env=env, capture_output=True, text=True)
    assert result.returncode == 0, f"QML file failed to load: {result.stdout}\n{result.stderr}"


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_quick_main_loads_qml(monkeypatch, tmp_path):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "ttvttm_home"))

    try:
        from ttvttm.quick_main import create_app
    except ImportError as exc:
        pytest.skip(f"Qt GUI cannot be imported in this environment: {exc}")

    app, engine = create_app([])
    assert engine.rootObjects(), "QML root objects should load"

    root = engine.rootObjects()[0]
    assert root.property("title") == "ttvttm"

    backend = engine.rootContext().contextProperty("backend")
    assert backend is not None
    assert hasattr(backend, "loadLibrary")
    assert backend.libraryModel.rowCount() >= 0
    assert root.property("wipContext") in backend.getWipContexts()
    assert backend.currentWipContext() == root.property("wipContext")

    app.quit()


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_quick_main_app_launches_without_errors(monkeypatch, tmp_path):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "ttvttm_home"))

    try:
        from ttvttm.quick_main import create_app
    except ImportError as exc:
        pytest.skip(f"Qt GUI cannot be imported in this environment: {exc}")

    app, engine = create_app([])
    assert engine.rootObjects(), "App should create root objects on launch"
    assert app is not None
    app.quit()

@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_library_add_button_click(monkeypatch, tmp_path):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "ttvttm_home"))

    import os

    from PySide6.QtCore import QUrl
    from PySide6.QtQml import QQmlApplicationEngine
    from PySide6.QtQuick import QQuickItem
    from PySide6.QtWidgets import QApplication

    from ttvttm.qml_backend import QmlBackend

    app = QApplication.instance() or QApplication([])
    engine = QQmlApplicationEngine()
    backend = QmlBackend()
    engine.rootContext().setContextProperty("backend", backend)
    qml_file = os.path.abspath(os.path.join(os.getcwd(), "ttvttm", "qml", "Main.qml"))
    engine.load(QUrl.fromLocalFile(qml_file))
    assert engine.rootObjects(), "QML root objects should load"

    root = engine.rootObjects()[0]
    library_view = root.findChild(QQuickItem, "libraryView")
    assert library_view is not None
    assert library_view.property("count") == 0

    dummy_dir = tmp_path / "music"
    dummy_dir.mkdir()
    dummy_track = dummy_dir / "track.wav"
    dummy_track.write_text("")
    assert backend.addTrack(str(dummy_track))
    assert backend.libraryModel.rowCount() == 1

    app.processEvents()
    assert library_view.property("count") == 1

    library_view.setProperty("currentIndex", 0)
    app.processEvents()

    content_item = library_view.property("contentItem")
    assert content_item is not None

    def find_named_item(item, name):
        if item.objectName() == name or item.property("name") == name:
            return item
        if hasattr(item, "childItems"):
            for child in item.childItems():
                found = find_named_item(child, name)
                if found:
                    return found
        return None

    add_button = find_named_item(content_item, "libraryAddButton")
    assert add_button is not None
    add_button.click()
    app.processEvents()

    assert backend.playlistModel.rowCount() == 1
    app.quit()
