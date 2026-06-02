import os
import re

import pytest


def is_pyside_available():
    try:
        import PySide6.QtCore  # noqa: F401
        return True
    except Exception:
        return False


def test_quick_main_qml_file_exists():
    from djtango.quick_main import QML_FILE

    assert os.path.isfile(QML_FILE), f"Expected QML file to exist at {QML_FILE}"


def test_qml_ids_do_not_start_with_uppercase():
    from djtango.quick_main import QML_FILE

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
    from djtango.quick_main import QML_FILE

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
    from djtango.quick_main import QML_FILE

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
    from djtango.quick_main import QML_FILE

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
        from djtango.qml_backend import QmlBackend  # noqa: F401
    except ImportError as exc:
        pytest.fail(f"Unable to import QML backend: {exc}")


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_qml_backend_playback_toggle(monkeypatch, tmp_path):
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "djtango_home"))

    from djtango.qml_backend import QmlBackend

    backend = QmlBackend()
    assert not backend._isPlaying

    assert backend.togglePlayPause()
    assert backend._isPlaying

    assert backend.togglePlayPause()
    assert not backend._isPlaying


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_qml_backend_app_metadata(monkeypatch, tmp_path):
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "djtango_home"))

    from djtango.qml_backend import QmlBackend

    backend = QmlBackend()
    assert backend.appTitle() == "DJTango"
    assert backend.appVersion() == "0.1.0"
    assert backend.liveOutputName() == "Default"
    assert backend.liveVolume() == 100


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_qml_backend_wip_contexts(monkeypatch, tmp_path):
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "djtango_home"))

    from djtango.qml_backend import QmlBackend

    backend = QmlBackend()
    contexts = backend.getWipContexts()
    assert contexts == ["Library", "Library 2", "Last playlist"]
    assert backend.currentWipContext() == "Library"
    assert backend.selectWipContext("Library 2")
    assert backend.currentWipContext() == "Library 2"
    assert not backend.selectWipContext("Invalid")


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_qml_backend_playlist_actions(monkeypatch, tmp_path):
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "djtango_home"))

    from djtango.qml_backend import QmlBackend

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
def test_qml_backend_save_and_load_playlist(monkeypatch, tmp_path):
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "djtango_home"))

    from djtango.qml_backend import QmlBackend

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
def test_quick_main_qml_file_loads_without_errors(monkeypatch, tmp_path):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    import subprocess
    import sys

    script = r'''
import os
import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine
from djtango.qml_backend import QmlBackend

app = QGuiApplication([])
engine = QQmlApplicationEngine()
engine.rootContext().setContextProperty('backend', QmlBackend())
qml_file = os.path.abspath(os.path.join(os.getcwd(), 'djtango', 'qml', 'Main.qml'))
engine.load(QUrl.fromLocalFile(qml_file))
assert engine.rootObjects(), 'QML root objects should load'
'''

    env = os.environ.copy()
    env['QT_QPA_PLATFORM'] = 'offscreen'
    result = subprocess.run([sys.executable, '-c', script], env=env, capture_output=True, text=True)
    assert result.returncode == 0, f"QML file failed to load: {result.stdout}\n{result.stderr}"


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_quick_main_loads_qml(monkeypatch, tmp_path):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "djtango_home"))

    try:
        from djtango.quick_main import create_app
    except ImportError as exc:
        pytest.skip(f"Qt GUI cannot be imported in this environment: {exc}")

    app, engine = create_app([])
    assert engine.rootObjects(), "QML root objects should load"

    root = engine.rootObjects()[0]
    assert root.property("title") == "DJTango"

    theme = root.property("theme")
    assert theme is not None
    assert theme.property("primary") == "#a0344d"
    assert theme.property("background") == "#161616"

    backend = engine.rootContext().contextProperty("backend")
    assert backend is not None
    assert hasattr(backend, "loadLibrary")
    assert backend.libraryModel.rowCount() >= 0

    app.quit()


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_quick_main_app_launches_without_errors(monkeypatch, tmp_path):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "djtango_home"))

    try:
        from djtango.quick_main import create_app
    except ImportError as exc:
        pytest.skip(f"Qt GUI cannot be imported in this environment: {exc}")

    app, engine = create_app([])
    assert engine.rootObjects(), "App should create root objects on launch"
    assert app is not None
    app.quit()
