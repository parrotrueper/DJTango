"""
Unit tests for search functionality in QML backend.

Tests verify that search and filtering work correctly.
"""

import tempfile
import pytest
from unittest.mock import patch

from ttvttm.qml_backend import QmlBackend


@pytest.fixture
def backend_with_tracks():
    """Create a backend with sample tracks for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.dict('os.environ', {"DJ_HOME_PATH": tmpdir}):
            backend = QmlBackend()
            # Add sample tracks to library
            test_tracks = [
                {"id": 1, "title": "La Cumparsita", "artist": "Gardel", "album": "Best of", "genre": "tango", "path": "/music/gardel/cumparsita.mp3"},
                {"id": 2, "title": "El Choclo", "artist": "Di Sarli", "album": "Golden", "genre": "tango", "path": "/music/disarli/choclo.mp3"},
                {"id": 3, "title": "Milonga del 900", "artist": "Biagi", "album": "Orchestra", "genre": "milonga", "path": "/music/biagi/milonga.mp3"},
                {"id": 4, "title": "Poema", "artist": "Gardel", "album": "Best of", "genre": "tango", "path": "/music/gardel/poema.mp3"},
                {"id": 5, "title": "Cortina", "artist": "Unknown", "album": "Unknown", "genre": "cortina", "path": "/music/cortina.mp3"},
            ]
            backend._libraryModel.setTracks(test_tracks)
            # Cache filter options and library tracks for search operations
            backend._cache_filter_options()
            yield backend


class TestSearchFunctionality:
    """Tests for the performSearch method"""
    
    def test_search_returns_matches_by_title(self, backend_with_tracks):
        """Test search finds tracks by title"""
        backend_with_tracks.performSearch("Cumparsita", "All artists", "All albums", "All genres", "Library")
        
        results = backend_with_tracks._libraryModel.asList()
        assert len(results) == 1
        assert results[0]["title"] == "La Cumparsita"
    
    def test_search_returns_matches_by_artist(self, backend_with_tracks):
        """Test search finds tracks by artist"""
        backend_with_tracks.performSearch("Gardel", "All artists", "All albums", "All genres", "Library")
        
        results = backend_with_tracks._libraryModel.asList()
        assert len(results) == 2
        assert all(track["artist"] == "Gardel" for track in results)
    
    def test_search_returns_matches_by_album(self, backend_with_tracks):
        """Test search finds tracks by album"""
        backend_with_tracks.performSearch("Best of", "All artists", "All albums", "All genres", "Library")
        
        results = backend_with_tracks._libraryModel.asList()
        assert len(results) == 2
        assert all(track["album"] == "Best of" for track in results)
    
    def test_search_returns_matches_by_genre(self, backend_with_tracks):
        """Test search finds tracks by genre"""
        backend_with_tracks.performSearch("tango", "All artists", "All albums", "All genres", "Library")
        
        results = backend_with_tracks._libraryModel.asList()
        assert len(results) == 3
        assert all(track["genre"] == "tango" for track in results)
    
    def test_search_returns_matches_by_path(self, backend_with_tracks):
        """Test search finds tracks by path"""
        backend_with_tracks.performSearch("disarli", "All artists", "All albums", "All genres", "Library")
        
        results = backend_with_tracks._libraryModel.asList()
        assert len(results) == 1
        assert "disarli" in results[0]["path"].lower()
    
    def test_search_case_insensitive(self, backend_with_tracks):
        """Test search is case insensitive"""
        backend_with_tracks.performSearch("GARDEL", "All artists", "All albums", "All genres", "Library")
        
        results = backend_with_tracks._libraryModel.asList()
        assert len(results) == 2
    
    def test_search_no_matches_returns_empty(self, backend_with_tracks):
        """Test search with no matches returns empty list"""
        backend_with_tracks.performSearch("NonExistent", "All artists", "All albums", "All genres", "Library")
        
        results = backend_with_tracks._libraryModel.asList()
        assert len(results) == 0
    
    def test_search_empty_string_returns_all(self, backend_with_tracks):
        """Test empty search string returns all tracks"""
        backend_with_tracks.performSearch("", "All artists", "All albums", "All genres", "Library")
        
        results = backend_with_tracks._libraryModel.asList()
        assert len(results) == 5
    
    def test_filter_by_artist_only(self, backend_with_tracks):
        """Test filtering by artist without text search"""
        backend_with_tracks.performSearch("", "Gardel", "All albums", "All genres", "Library")
        
        results = backend_with_tracks._libraryModel.asList()
        assert len(results) == 2
        assert all(track["artist"] == "Gardel" for track in results)
    
    def test_filter_by_album_only(self, backend_with_tracks):
        """Test filtering by album without text search"""
        backend_with_tracks.performSearch("", "All artists", "Best of", "All genres", "Library")
        
        results = backend_with_tracks._libraryModel.asList()
        assert len(results) == 2
        assert all(track["album"] == "Best of" for track in results)
    
    def test_filter_by_genre_only(self, backend_with_tracks):
        """Test filtering by genre without text search"""
        backend_with_tracks.performSearch("", "All artists", "All albums", "tango", "Library")
        
        results = backend_with_tracks._libraryModel.asList()
        assert len(results) == 3
        assert all(track["genre"] == "tango" for track in results)
    
    def test_filter_by_multiple_criteria(self, backend_with_tracks):
        """Test filtering by multiple criteria simultaneously"""
        backend_with_tracks.performSearch("", "Gardel", "Best of", "tango", "Library")
        
        results = backend_with_tracks._libraryModel.asList()
        assert len(results) == 2
        assert all(track["artist"] == "Gardel" for track in results)
        assert all(track["album"] == "Best of" for track in results)
        assert all(track["genre"] == "tango" for track in results)
    
    def test_search_with_filters_combines_criteria(self, backend_with_tracks):
        """Test that search text and filters are combined (AND logic)"""
        # Search for "a" (matches multiple) but filter to artist Gardel and genre tango
        backend_with_tracks.performSearch("a", "Gardel", "All albums", "tango", "Library")
        
        results = backend_with_tracks._libraryModel.asList()
        # Should match Gardel tracks with "a" in any field
        assert len(results) == 2
        assert all(track["artist"] == "Gardel" for track in results)
    
    def test_search_partial_match(self, backend_with_tracks):
        """Test that search works with partial matches"""
        backend_with_tracks.performSearch("Cump", "All artists", "All albums", "All genres", "Library")
        
        results = backend_with_tracks._libraryModel.asList()
        assert len(results) == 1
        assert "Cumparsita" in results[0]["title"]
    
    def test_search_emits_signal(self, backend_with_tracks):
        """Test that search emits libraryChanged signal"""
        with patch.object(backend_with_tracks, 'libraryChanged') as mock_signal:
            backend_with_tracks.performSearch("tango", "All artists", "All albums", "All genres", "Library")
            mock_signal.emit.assert_called_once()
    
    def test_search_playlist_scope(self, backend_with_tracks):
        """Test search works on playlist scope"""
        # Add some tracks to playlist
        backend_with_tracks._playlistModel.setTracks([
            {"id": 1, "title": "La Cumparsita", "artist": "Gardel", "album": "Best of", "genre": "tango", "path": "/music/gardel/cumparsita.mp3"},
            {"id": 2, "title": "Cortina", "artist": "Unknown", "album": "Unknown", "genre": "cortina", "path": "/music/cortina.mp3"},
        ])
        
        backend_with_tracks.performSearch("Gardel", "All artists", "All albums", "All genres", "Playlists")
        
        results = backend_with_tracks._playlistModel.asList()
        assert len(results) == 1
        assert results[0]["artist"] == "Gardel"
    
    def test_search_preserves_track_data_integrity(self, backend_with_tracks):
        """Test that search results preserve all track data"""
        backend_with_tracks.performSearch("Biagi", "All artists", "All albums", "All genres", "Library")
        
        results = backend_with_tracks._libraryModel.asList()
        assert len(results) == 1
        
        track = results[0]
        assert track["id"] == 3
        assert track["title"] == "Milonga del 900"
        assert track["artist"] == "Biagi"
        assert track["album"] == "Orchestra"
        assert track["genre"] == "milonga"
        assert track["path"] == "/music/biagi/milonga.mp3"
