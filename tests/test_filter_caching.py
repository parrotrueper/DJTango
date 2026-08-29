"""
Test to verify that filter options are preserved during search operations.

This ensures dropdowns show all options even when search results are empty.
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
            backend._cache_filter_options()
            yield backend


class TestFilterOptionsCaching:
    """Tests to verify filter options are cached and preserved during searches"""
    
    def test_filter_options_cached_after_library_load(self, backend_with_tracks):
        """Test that filter options are cached when library loads"""
        # Check that caches are populated
        assert len(backend_with_tracks._cached_artists) > 0
        assert len(backend_with_tracks._cached_albums) > 0
        assert len(backend_with_tracks._cached_genres) > 0
    
    def test_getLibraryArtists_returns_cached_values(self, backend_with_tracks):
        """Test that getLibraryArtists returns cached values"""
        artists = backend_with_tracks.getLibraryArtists()
        
        # Should return all 4 unique artists
        assert isinstance(artists, list)
        assert "Gardel" in artists
        assert "Di Sarli" in artists
        assert "Biagi" in artists
        assert "Unknown" in artists
        assert len(artists) == 4
    
    def test_getLibraryAlbums_returns_cached_values(self, backend_with_tracks):
        """Test that getLibraryAlbums returns cached values"""
        albums = backend_with_tracks.getLibraryAlbums()
        
        # Should return all 4 unique albums (including "Unknown")
        assert isinstance(albums, list)
        assert "Best of" in albums
        assert "Golden" in albums
        assert "Orchestra" in albums
        assert "Unknown" in albums
        assert len(albums) == 4
    
    def test_getLibraryGenres_returns_cached_values(self, backend_with_tracks):
        """Test that getLibraryGenres returns cached values"""
        genres = backend_with_tracks.getLibraryGenres()
        
        # Should return all 3 unique genres
        assert isinstance(genres, list)
        assert "tango" in genres
        assert "milonga" in genres
        assert "cortina" in genres
        assert len(genres) == 3
    
    def test_filter_options_preserved_after_empty_search(self, backend_with_tracks):
        """Test that filter options remain available even after search returns no results"""
        # Perform a search that yields no results
        backend_with_tracks.performSearch("NonExistentTrack", "All artists", "All albums", "All genres", "Library")
        
        # Verify library is empty
        results = backend_with_tracks._libraryModel.asList()
        assert len(results) == 0
        
        # But filter options should still be available
        artists = backend_with_tracks.getLibraryArtists()
        albums = backend_with_tracks.getLibraryAlbums()
        genres = backend_with_tracks.getLibraryGenres()
        
        assert len(artists) == 4
        assert "Gardel" in artists
        assert len(albums) == 4
        assert "Best of" in albums
        assert len(genres) == 3
        assert "tango" in genres
    
    def test_can_select_different_filter_after_no_results(self, backend_with_tracks):
        """Test that user can select different filter options after getting no results"""
        # First search returns no results
        backend_with_tracks.performSearch("NonExistent", "All artists", "All albums", "All genres", "Library")
        assert len(backend_with_tracks._libraryModel.asList()) == 0
        
        # Second search with different filter should work
        backend_with_tracks.performSearch("", "Gardel", "All albums", "All genres", "Library")
        results = backend_with_tracks._libraryModel.asList()
        
        # Should find Gardel's tracks
        assert len(results) == 2
        assert all(track["artist"] == "Gardel" for track in results)
    
    def test_filter_options_show_all_artists_despite_filtered_results(self, backend_with_tracks):
        """Test that artist dropdown shows all artists even when library is filtered to one artist"""
        # Filter library to show only Di Sarli
        backend_with_tracks.performSearch("", "Di Sarli", "All albums", "All genres", "Library")
        
        # Library should only show Di Sarli's tracks
        library_results = backend_with_tracks._libraryModel.asList()
        assert len(library_results) == 1
        assert library_results[0]["artist"] == "Di Sarli"
        
        # But artist filter dropdown should still show all artists
        all_artists = backend_with_tracks.getLibraryArtists()
        assert len(all_artists) == 4
        assert "Gardel" in all_artists
        assert "Biagi" in all_artists
        assert "Unknown" in all_artists
    
    def test_sequential_filter_changes_work(self, backend_with_tracks):
        """Test that multiple sequential filter changes work correctly"""
        # Start with no filter
        backend_with_tracks.performSearch("", "All artists", "All albums", "All genres", "Library")
        assert len(backend_with_tracks._libraryModel.asList()) == 5
        
        # Filter to Gardel (2 results)
        backend_with_tracks.performSearch("", "Gardel", "All albums", "All genres", "Library")
        assert len(backend_with_tracks._libraryModel.asList()) == 2
        
        # Filter to Di Sarli (1 result)
        backend_with_tracks.performSearch("", "Di Sarli", "All albums", "All genres", "Library")
        assert len(backend_with_tracks._libraryModel.asList()) == 1
        
        # Filter to Biagi (1 result)
        backend_with_tracks.performSearch("", "Biagi", "All albums", "All genres", "Library")
        assert len(backend_with_tracks._libraryModel.asList()) == 1
        
        # But artists dropdown always shows all 4
        assert len(backend_with_tracks.getLibraryArtists()) == 4
    
    def test_albums_filter_preserved_despite_search_results(self, backend_with_tracks):
        """Test that all albums remain available in dropdown during searches"""
        # Search for something specific
        backend_with_tracks.performSearch("Cortina", "All artists", "All albums", "All genres", "Library")
        
        # Only 1 result (the Cortina track)
        assert len(backend_with_tracks._libraryModel.asList()) == 1
        
        # But all albums should still be available
        albums = backend_with_tracks.getLibraryAlbums()
        assert len(albums) == 4
        assert "Best of" in albums
        assert "Golden" in albums
        assert "Orchestra" in albums
        assert "Unknown" in albums
    
    def test_genres_filter_preserved_despite_search_results(self, backend_with_tracks):
        """Test that all genres remain available in dropdown during searches"""
        # Search for a tango artist
        backend_with_tracks.performSearch("", "Di Sarli", "All albums", "All genres", "Library")
        
        # Only tango results
        results = backend_with_tracks._libraryModel.asList()
        assert len(results) == 1
        assert all(track["genre"] == "tango" for track in results)
        
        # But all genres should still be available
        genres = backend_with_tracks.getLibraryGenres()
        assert len(genres) == 3
        assert "tango" in genres
        assert "milonga" in genres
        assert "cortina" in genres
