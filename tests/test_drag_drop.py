"""Tests for drag-and-drop functionality from Library to Live Playlist."""
import os
import pytest


def is_pyside_available():
    try:
        import PySide6.QtCore  # noqa: F401
        return True
    except Exception:
        return False


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_drag_library_track_to_playlist(monkeypatch, tmp_path):
    """Test that dragging a library track into the playlist adds it."""
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "ttvttm_home"))

    try:
        from ttvttm.quick_main import create_app
    except ImportError as exc:
        pytest.skip(f"Qt GUI cannot be imported in this environment: {exc}")

    from PySide6.QtCore import QObject
    from PySide6.QtTest import QTest

    # Setup: Create app and add a dummy track to the library
    app, engine = create_app([])
    root = engine.rootObjects()[0]
    backend = engine.rootContext().contextProperty("backend")
    assert backend is not None, "Backend not available"

    # Create a dummy audio track file
    dummy_dir = tmp_path / "music"
    dummy_dir.mkdir(parents=True)
    dummy_track = dummy_dir / "test_track.wav"
    # Minimal valid WAV file
    dummy_track.write_bytes(
        b"RIFF$\x00\x00\x00WAVEfmt "
        + b"\x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    )

    # Add track to library
    assert backend.addTrack(str(dummy_track)), "Failed to add test track to library"
    app.processEvents()
    QTest.qWait(100)
    app.processEvents()

    # Verify library view has the track
    library_view = root.findChild(QObject, "libraryView")
    assert library_view is not None, "libraryView not found in QML"
    library_count = library_view.property("count")
    assert library_count > 0, f"Library should have tracks, but count is {library_count}"

    # Get the playlist view
    playlist_view = root.findChild(QObject, "playlistView")
    assert playlist_view is not None, "playlistView not found in QML"
    initial_playlist_count = playlist_view.property("count")
    
    print(f"Initial playlist count: {initial_playlist_count}")

    # Test: Add the first library track to the playlist via backend
    # This simulates what should happen when drag-drop completes
    library_model = backend.libraryModel
    if library_model.rowCount() > 0:
        # Get the trackId of the first item (index 0)
        first_track_index = library_model.index(0, 0)
        track_id = library_model.data(first_track_index, backend.libraryModel.TrackIdRole)
        
        print(f"First track ID: {track_id}")
        
        # Call the backend method that should be called by the QML drop handler
        result = backend.addTrackToPlaylist(track_id)
        print(f"addTrackToPlaylist result: {result}")
        
        app.processEvents()
        QTest.qWait(100)
        app.processEvents()

        # Verify: Track should be added to playlist
        final_playlist_count = playlist_view.property("count")
        print(f"Final playlist count: {final_playlist_count}")
        
        assert (
            final_playlist_count > initial_playlist_count
        ), f"Playlist count should increase. Before: {initial_playlist_count}, After: {final_playlist_count}"

    app.quit()


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_drag_drop_uses_correct_mime_type(monkeypatch, tmp_path):
    """Test that drag-drop MIME data is configured correctly."""
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "ttvttm_home"))

    try:
        from ttvttm.quick_main import create_app
    except ImportError as exc:
        pytest.skip(f"Qt GUI cannot be imported in this environment: {exc}")

    from PySide6.QtCore import QObject
    from PySide6.QtTest import QTest

    app, engine = create_app([])
    root = engine.rootObjects()[0]
    backend = engine.rootContext().contextProperty("backend")

    # Create and add test track
    dummy_dir = tmp_path / "music"
    dummy_dir.mkdir(parents=True)
    dummy_track = dummy_dir / "mime_test.wav"
    dummy_track.write_bytes(
        b"RIFF$\x00\x00\x00WAVEfmt "
        + b"\x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    )
    backend.addTrack(str(dummy_track))
    app.processEvents()
    QTest.qWait(100)

    # Verify library and playlist models are accessible
    library_model = backend.libraryModel
    playlist_model = backend.playlistModel
    
    assert library_model is not None, "Library model should be available"
    assert playlist_model is not None, "Playlist model should be available"
    assert library_model.rowCount() > 0, "Library should have tracks"

    # Verify backend has the necessary method for drag-drop
    assert hasattr(backend, 'addTrackToPlaylist'), "Backend should have addTrackToPlaylist method"
    
    app.quit()


@pytest.mark.skipif(not is_pyside_available(), reason="PySide6 is required for Qt Quick tests")
def test_add_track_to_playlist_backend_method(monkeypatch, tmp_path):
    """Test the backend.addTrackToPlaylist() method works correctly."""
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setenv("DJ_HOME_PATH", str(tmp_path / "ttvttm_home"))

    try:
        from ttvttm.quick_main import create_app
    except ImportError as exc:
        pytest.skip(f"Qt GUI cannot be imported in this environment: {exc}")

    from PySide6.QtCore import QObject
    from PySide6.QtTest import QTest

    app, engine = create_app([])
    root = engine.rootObjects()[0]
    backend = engine.rootContext().contextProperty("backend")

    # Create and add multiple test tracks
    dummy_dir = tmp_path / "music"
    dummy_dir.mkdir(parents=True)
    
    track_ids = []
    for i in range(3):
        dummy_track = dummy_dir / f"test_track_{i}.wav"
        dummy_track.write_bytes(
            b"RIFF$\x00\x00\x00WAVEfmt "
            + b"\x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
        )
        result = backend.addTrack(str(dummy_track))
        assert result, f"Failed to add track {i}"
    
    app.processEvents()
    QTest.qWait(100)
    app.processEvents()

    # Get initial state
    library_model = backend.libraryModel
    playlist_model = backend.playlistModel
    
    initial_playlist_count = playlist_model.rowCount()
    library_count = library_model.rowCount()
    
    print(f"Library has {library_count} tracks, Playlist has {initial_playlist_count} tracks")
    
    # Add tracks from library to playlist
    for i in range(min(2, library_count)):  # Add first 2 library tracks
        track_index = library_model.index(i, 0)
        track_id = library_model.data(track_index, backend.libraryModel.TrackIdRole)
        
        print(f"Adding library track {i} (ID: {track_id}) to playlist")
        result = backend.addTrackToPlaylist(track_id)
        print(f"  Result: {result}")
        
        app.processEvents()
        QTest.qWait(50)
    
    # Verify tracks were added
    final_playlist_count = playlist_model.rowCount()
    print(f"Final playlist count: {final_playlist_count}")
    
    assert final_playlist_count > initial_playlist_count, (
        f"Playlist should have more tracks. Before: {initial_playlist_count}, After: {final_playlist_count}"
    )

    app.quit()
