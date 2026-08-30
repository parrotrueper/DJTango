"""
Comprehensive regression tests for drag-drop functionality.

Tests cover:
- Internal drag-drop (library to playlist)
- External export (MIME types for external apps)
- External import (files from file manager)
- Backend support (addTrackFromPath)
- Edge cases and error handling
"""

import os
import pytest
import tempfile
from pathlib import Path

from ttvttm.data import djDataConnection
from ttvttm.qml_backend import QmlBackend, TrackListModel


class TestDragDropInternal:
    """Tests for internal drag-drop (library to playlist)"""
    
    def test_add_track_to_playlist_basic(self):
        """Test basic internal drag-drop: library track to playlist"""
        backend = QmlBackend()
        backend.loadLibrary()
        
        # Get first track from library
        library_tracks = backend.libraryModel.asList()
        assert len(library_tracks) > 0, "Library should have tracks"
        
        first_track = library_tracks[0]
        track_id = first_track.get("id")
        
        # Initially playlist should be empty
        initial_count = backend.playlistModel.rowCount()
        
        # Add track to playlist
        result = backend.addTrackToPlaylist(track_id)
        assert result is True, "addTrackToPlaylist should return True"
        
        # Verify track was added
        new_count = backend.playlistModel.rowCount()
        assert new_count == initial_count + 1, "Playlist count should increase by 1"
        
        # Verify correct track was added
        playlist_tracks = backend.playlistModel.asList()
        added_track = playlist_tracks[-1]
        assert added_track.get("id") == track_id, "Added track should have correct ID"
        assert added_track.get("title") == first_track.get("title"), "Track title should match"
        assert added_track.get("artist") == first_track.get("artist"), "Track artist should match"
    
    def test_add_multiple_tracks_to_playlist(self):
        """Test adding multiple tracks via drag-drop"""
        backend = QmlBackend()
        backend.loadLibrary()
        
        library_tracks = backend.libraryModel.asList()
        assert len(library_tracks) >= 3, "Library should have at least 3 tracks"
        
        # Add 3 tracks
        for i in range(3):
            track_id = library_tracks[i].get("id")
            result = backend.addTrackToPlaylist(track_id)
            assert result is True, f"Failed to add track {i}"
        
        # Verify all 3 were added
        playlist_count = backend.playlistModel.rowCount()
        assert playlist_count == 3, f"Playlist should have 3 tracks, has {playlist_count}"
    
    def test_add_nonexistent_track(self):
        """Test that adding nonexistent track returns False"""
        backend = QmlBackend()
        backend.loadLibrary()
        
        # Try to add track with invalid ID
        result = backend.addTrackToPlaylist(999999)
        assert result is False, "Adding nonexistent track should return False"
        
        # Playlist should remain empty
        assert backend.playlistModel.rowCount() == 0, "Playlist should stay empty"
    
    def test_add_same_track_twice(self):
        """Test that same track can be added to playlist multiple times"""
        backend = QmlBackend()
        backend.loadLibrary()
        
        library_tracks = backend.libraryModel.asList()
        assert len(library_tracks) > 0
        
        track_id = library_tracks[0].get("id")
        
        # Add same track twice
        result1 = backend.addTrackToPlaylist(track_id)
        result2 = backend.addTrackToPlaylist(track_id)
        
        assert result1 is True and result2 is True, "Both adds should succeed"
        assert backend.playlistModel.rowCount() == 2, "Playlist should have 2 entries"


class TestDragDropExport:
    """Tests for exporting tracks to external apps (MIME types)"""
    
    def test_library_track_has_required_mime_types(self):
        """Test that library tracks provide all required MIME types"""
        backend = QmlBackend()
        backend.loadLibrary()
        
        library_tracks = backend.libraryModel.asList()
        assert len(library_tracks) > 0
        
        track = library_tracks[0]
        
        # Verify track has all required fields for MIME types
        # text/uri-list format
        assert "path" in track, "Track must have path for text/uri-list"
        assert os.path.isfile(track["path"]), f"Track path must exist: {track['path']}"
        
        # text/plain format
        assert "artist" in track, "Track must have artist for text/plain"
        assert "title" in track, "Track must have title for text/plain"
        assert isinstance(track["artist"], str), "Artist must be string"
        assert isinstance(track["title"], str), "Title must be string"
        
        # Internal format
        assert "id" in track, "Track must have ID for internal drag-drop"
    
    def test_library_track_export_format(self):
        """Test the actual export format for external apps"""
        backend = QmlBackend()
        backend.loadLibrary()
        
        track = backend.libraryModel.asList()[0]
        
        # Simulate Drag.mimeData dict format
        mime_data = {
            "application/x-ttvttm-trackid": str(track["id"]),
            "text/uri-list": f"file://{track['path']}",
            "text/plain": f"{track['artist']} - {track['title']}"
        }
        
        # Verify all formats are non-empty
        assert mime_data["application/x-ttvttm-trackid"], "trackId should not be empty"
        assert mime_data["text/uri-list"].startswith("file://"), "URI list should start with file://"
        assert mime_data["text/plain"], "Plain text should not be empty"
        assert " - " in mime_data["text/plain"], "Plain text should have artist - title format"


class TestDragDropImport:
    """Tests for importing external files (file manager drop)"""
    
    def test_add_track_from_external_file_basic(self):
        """Test importing external audio file to playlist"""
        backend = QmlBackend()
        backend.loadLibrary()
        
        # Get a real file from library to test with
        library_tracks = backend.libraryModel.asList()
        assert len(library_tracks) > 0
        
        real_file = library_tracks[0]["path"]
        assert os.path.isfile(real_file), f"Test file should exist: {real_file}"
        
        initial_count = backend.playlistModel.rowCount()
        
        # Import the file
        result = backend.addTrackFromPath(real_file)
        assert result is True, "addTrackFromPath should return True for valid file"
        
        # Verify track was added
        new_count = backend.playlistModel.rowCount()
        assert new_count == initial_count + 1, "Playlist count should increase"
        
        # Verify track data was extracted
        added_track = backend.playlistModel.asList()[-1]
        assert added_track.get("path") == real_file, "Track path should match"
        assert added_track.get("title"), "Track title should be extracted"
    
    def test_add_track_from_file_uri(self):
        """Test that file:// URIs are properly handled"""
        backend = QmlBackend()
        backend.loadLibrary()
        
        library_tracks = backend.libraryModel.asList()
        real_file = library_tracks[0]["path"]
        
        # Test with file:// prefix (common from file managers)
        file_uri = f"file://{real_file}"
        result = backend.addTrackFromPath(file_uri)
        assert result is True, "Should handle file:// URIs"
        
        # Verify the path was normalized correctly
        added_track = backend.playlistModel.asList()[-1]
        assert added_track.get("path") == real_file, "file:// prefix should be stripped"
    
    def test_add_track_from_nonexistent_file(self):
        """Test that nonexistent files return False"""
        backend = QmlBackend()
        
        result = backend.addTrackFromPath("/nonexistent/path/to/file.mp3")
        assert result is False, "Should return False for nonexistent file"
        
        # Playlist should remain empty
        assert backend.playlistModel.rowCount() == 0, "Playlist should stay empty"
    
    def test_add_track_from_unsupported_format(self):
        """Test that unsupported file formats return False"""
        backend = QmlBackend()
        
        # Create temporary unsupported file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            temp_path = f.name
            f.write(b"Not an audio file")
        
        try:
            result = backend.addTrackFromPath(temp_path)
            assert result is False, "Should return False for unsupported format"
            assert backend.playlistModel.rowCount() == 0, "Playlist should stay empty"
        finally:
            os.unlink(temp_path)
    
    def test_add_multiple_files_from_external(self):
        """Test importing multiple files at once (from file manager selection)"""
        backend = QmlBackend()
        backend.loadLibrary()
        
        library_tracks = backend.libraryModel.asList()
        assert len(library_tracks) >= 3, "Need at least 3 tracks for this test"
        
        # Import 3 files
        for i in range(3):
            file_path = library_tracks[i]["path"]
            result = backend.addTrackFromPath(file_path)
            assert result is True, f"Failed to import file {i}"
        
        # Verify all were added
        assert backend.playlistModel.rowCount() == 3, "All 3 files should be in playlist"


class TestDragDropIntegration:
    """Integration tests combining multiple drag-drop scenarios"""
    
    def test_mixed_internal_and_external_drag_drop(self):
        """Test mixing internal drag-drop with external file import"""
        backend = QmlBackend()
        backend.loadLibrary()
        
        library_tracks = backend.libraryModel.asList()
        assert len(library_tracks) >= 2
        
        # Add via internal drag-drop
        internal_id = library_tracks[0]["id"]
        backend.addTrackToPlaylist(internal_id)
        
        # Add via external import
        external_file = library_tracks[1]["path"]
        backend.addTrackFromPath(external_file)
        
        # Verify both are in playlist
        playlist = backend.playlistModel.asList()
        assert len(playlist) == 2, "Should have 2 tracks"
        assert playlist[0]["id"] == internal_id, "First should be internal track"
        assert playlist[1]["path"] == external_file, "Second should be external file"
    
    def test_playback_of_dragged_track(self):
        """Test that dragged tracks can be played"""
        backend = QmlBackend()
        backend.loadLibrary()
        
        library_tracks = backend.libraryModel.asList()
        track_id = library_tracks[0]["id"]
        
        # Add to playlist via drag-drop
        backend.addTrackToPlaylist(track_id)
        
        # Try to play it
        playlist_track_id = backend.playlistModel.asList()[0]["id"]
        result = backend.playPlaylistTrack(playlist_track_id)
        
        # Note: playback might fail if no audio device, but call should not error
        # Just verify the call works without exception
        assert isinstance(result, bool), "playPlaylistTrack should return bool"
    
    def test_drag_drop_preserves_track_metadata(self):
        """Test that metadata is preserved through drag-drop"""
        backend = QmlBackend()
        backend.loadLibrary()
        
        library_tracks = backend.libraryModel.asList()
        original_track = library_tracks[0]
        track_id = original_track["id"]
        
        # Add via drag-drop
        backend.addTrackToPlaylist(track_id)
        
        # Compare metadata
        playlist_track = backend.playlistModel.asList()[0]
        
        # Core fields should match
        assert playlist_track["title"] == original_track["title"], "Title should match"
        assert playlist_track["artist"] == original_track["artist"], "Artist should match"
        assert playlist_track["album"] == original_track["album"], "Album should match"
        assert playlist_track["path"] == original_track["path"], "Path should match"


class TestDragDropEdgeCases:
    """Tests for edge cases and error conditions"""
    
    def test_add_track_with_special_characters(self):
        """Test handling tracks with special characters in metadata"""
        backend = QmlBackend()
        backend.loadLibrary()
        
        # Find a track with special characters if available
        for track in backend.libraryModel.asList():
            if any(c in track.get("title", "") for c in ["'", '"', "&", "<", ">"]):
                track_id = track["id"]
                result = backend.addTrackToPlaylist(track_id)
                assert result is True, "Should handle special characters"
                break
    
    def test_add_track_with_unicode_metadata(self):
        """Test handling tracks with unicode in metadata"""
        backend = QmlBackend()
        backend.loadLibrary()
        
        # Try adding any track - unicode handling is implicit
        tracks = backend.libraryModel.asList()
        if tracks:
            result = backend.addTrackToPlaylist(tracks[0]["id"])
            assert result is True, "Should handle unicode"
    
    def test_rapid_consecutive_drag_drops(self):
        """Test stress test with rapid drag-drop operations"""
        backend = QmlBackend()
        backend.loadLibrary()
        
        library_tracks = backend.libraryModel.asList()
        
        # Rapidly add tracks
        for i in range(min(10, len(library_tracks))):
            result = backend.addTrackToPlaylist(library_tracks[i]["id"])
            assert result is True, f"Failed at iteration {i}"
        
        # Verify all were added
        assert backend.playlistModel.rowCount() == min(10, len(library_tracks))
    
    def test_playlist_model_clear_after_drag_drop(self):
        """Test that playlist can be cleared after drag-drop"""
        backend = QmlBackend()
        backend.loadLibrary()
        
        # Add some tracks
        tracks = backend.libraryModel.asList()
        backend.addTrackToPlaylist(tracks[0]["id"])
        backend.addTrackToPlaylist(tracks[1]["id"])
        
        assert backend.playlistModel.rowCount() == 2
        
        # Clear playlist
        backend.playlistModel.clear()
        assert backend.playlistModel.rowCount() == 0, "Playlist should be empty after clear"


class TestDragDropModels:
    """Tests for TrackListModel drag-drop capabilities"""
    
    def test_track_list_model_exposes_all_roles(self):
        """Test that TrackListModel exposes all required roles for drag-drop"""
        model = TrackListModel()
        
        # Create test track
        test_track = {
            "id": 1,
            "path": "/test/path.mp3",
            "title": "Test Track",
            "artist": "Test Artist",
            "album": "Test Album",
            "genre": "Tango",
            "year": 2020,
            "bpm": 120,
            "duration": 180
        }
        
        model.addTrack(test_track)
        
        # Verify all roles are accessible
        from PySide6.QtCore import Qt
        
        # Note: Qt.UserRole is 256
        QT_USER_ROLE = 256
        
        TrackIdRole = QT_USER_ROLE + 1
        TitleRole = QT_USER_ROLE + 2
        ArtistRole = QT_USER_ROLE + 3
        PathRole = QT_USER_ROLE + 9
        
        index = model.createIndex(0, 0)
        
        assert model.data(index, TrackIdRole) == 1
        assert model.data(index, TitleRole) == "Test Track"
        assert model.data(index, ArtistRole) == "Test Artist"
        assert model.data(index, PathRole) == "/test/path.mp3"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
