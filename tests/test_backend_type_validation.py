"""
Type validation tests for QML backend methods.

These tests ensure that all backend methods return the correct types,
preventing data type mismatches when consumed by QML.
"""

import os
import tempfile
import pytest
from unittest.mock import MagicMock, patch

from ttvttm.qml_backend import QmlBackend, TypeValidator


class TestTypeValidator:
    """Test the TypeValidator helper class"""
    
    def test_validate_bool_valid(self):
        """Test validation of valid boolean"""
        result = TypeValidator.validate_bool(True, "test_method")
        assert result is True
        
    def test_validate_bool_invalid(self):
        """Test validation of invalid boolean"""
        with pytest.raises(TypeError, match="expected bool"):
            TypeValidator.validate_bool(1, "test_method")
            
    def test_validate_int_valid(self):
        """Test validation of valid integer"""
        result = TypeValidator.validate_int(42, "test_method")
        assert result == 42
        
    def test_validate_int_rejects_bool(self):
        """Test that validate_int rejects boolean (which is technically an int in Python)"""
        with pytest.raises(TypeError, match="expected int"):
            TypeValidator.validate_int(True, "test_method")
            
    def test_validate_str_valid(self):
        """Test validation of valid string"""
        result = TypeValidator.validate_str("hello", "test_method")
        assert result == "hello"
        
    def test_validate_str_invalid(self):
        """Test validation of invalid string"""
        with pytest.raises(TypeError, match="expected str"):
            TypeValidator.validate_str(42, "test_method")
            
    def test_validate_string_list_valid(self):
        """Test validation of valid string list"""
        result = TypeValidator.validate_string_list(["a", "b", "c"], "test_method")
        assert result == ["a", "b", "c"]
        
    def test_validate_string_list_empty(self):
        """Test validation of empty list"""
        result = TypeValidator.validate_string_list([], "test_method")
        assert result == []
        
    def test_validate_string_list_not_list(self):
        """Test validation rejects non-list"""
        with pytest.raises(TypeError, match="expected list"):
            TypeValidator.validate_string_list("not a list", "test_method")
            
    def test_validate_string_list_contains_non_string(self):
        """Test validation rejects lists with non-string items"""
        with pytest.raises(TypeError, match="expected str"):
            TypeValidator.validate_string_list(["a", 42, "c"], "test_method")


class TestBackendReturnTypes:
    """Test that backend methods return correct types"""
    
    @pytest.fixture
    def backend(self):
        """Create a backend instance for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {"DJ_HOME_PATH": tmpdir}):
                backend = QmlBackend()
                yield backend
    
    def test_loadLibrary_returns_bool(self, backend):
        """Test loadLibrary returns boolean"""
        result = backend.loadLibrary()
        assert isinstance(result, bool)
        assert result is True
        
    def test_getLibraryArtists_returns_string_list(self, backend):
        """Test getLibraryArtists returns list of strings"""
        result = backend.getLibraryArtists()
        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)
        
    def test_getLibraryAlbums_returns_string_list(self, backend):
        """Test getLibraryAlbums returns list of strings"""
        result = backend.getLibraryAlbums()
        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)
        
    def test_getLibraryGenres_returns_string_list(self, backend):
        """Test getLibraryGenres returns list of strings"""
        result = backend.getLibraryGenres()
        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)
        
    def test_getWipContexts_returns_string_list(self, backend):
        """Test getWipContexts returns list of strings"""
        result = backend.getWipContexts()
        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)
        assert len(result) == 3
        assert "Library" in result
        
    def test_getSavedPlaylists_returns_string_list(self, backend):
        """Test getSavedPlaylists returns list of strings"""
        result = backend.getSavedPlaylists()
        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)
        
    def test_getM3u8Playlists_empty_dir_returns_string_list(self, backend):
        """Test getM3u8Playlists returns list of strings"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = backend.getM3u8Playlists(tmpdir)
            assert isinstance(result, list)
            assert all(isinstance(item, str) for item in result)
            
    def test_getM3u8Playlists_invalid_dir_returns_string_list(self, backend):
        """Test getM3u8Playlists handles invalid directory"""
        result = backend.getM3u8Playlists("/nonexistent/path")
        assert isinstance(result, list)
        assert result == []
        
    def test_getM3u8Playlists_empty_string_returns_string_list(self, backend):
        """Test getM3u8Playlists handles empty string"""
        result = backend.getM3u8Playlists("")
        assert isinstance(result, list)
        assert result == []
        
    def test_currentWipContext_returns_string(self, backend):
        """Test currentWipContext returns string"""
        result = backend.currentWipContext()
        assert isinstance(result, str)
        
    def test_appTitle_returns_string(self, backend):
        """Test appTitle returns string"""
        result = backend.appTitle()
        assert isinstance(result, str)
        assert result == "ttvttm"
        
    def test_appVersion_returns_string(self, backend):
        """Test appVersion returns string"""
        result = backend.appVersion()
        assert isinstance(result, str)
        
    def test_liveOutputName_returns_string(self, backend):
        """Test liveOutputName returns string"""
        result = backend.liveOutputName()
        assert isinstance(result, str)
        assert result == "Default"
        
    def test_liveVolume_returns_int(self, backend):
        """Test liveVolume returns int"""
        result = backend.liveVolume()
        assert isinstance(result, int)
        assert result == 100
        
    def test_playlistTotalDuration_returns_int(self, backend):
        """Test playlistTotalDuration returns int"""
        result = backend.playlistTotalDuration()
        assert isinstance(result, int)
        assert result >= 0
        
    def test_selectWipContext_returns_bool(self, backend):
        """Test selectWipContext returns boolean"""
        result = backend.selectWipContext("Library")
        assert isinstance(result, bool)
        assert result is True
        
    def test_selectWipContext_invalid_returns_bool(self, backend):
        """Test selectWipContext with invalid context returns boolean"""
        result = backend.selectWipContext("Invalid")
        assert isinstance(result, bool)
        assert result is False
        
    def test_setLiveSession_returns_bool(self, backend):
        """Test setLiveSession returns boolean"""
        result = backend.setLiveSession(True)
        assert isinstance(result, bool)
        assert result is True
        
    def test_savePlaylist_empty_name_returns_bool(self, backend):
        """Test savePlaylist returns boolean"""
        result = backend.savePlaylist("")
        assert isinstance(result, bool)
        
    def test_loadPlaylist_invalid_returns_bool(self, backend):
        """Test loadPlaylist returns boolean"""
        result = backend.loadPlaylist("nonexistent")
        assert isinstance(result, bool)
        assert result is False
        
    def test_addTrack_invalid_path_returns_bool(self, backend):
        """Test addTrack returns boolean"""
        result = backend.addTrack("/nonexistent/track.mp3")
        assert isinstance(result, bool)
        assert result is False


class TestConcatenationSafety:
    """Test that array concatenation works safely"""
    
    @pytest.fixture
    def backend(self):
        """Create a backend instance for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {"DJ_HOME_PATH": tmpdir}):
                backend = QmlBackend()
                yield backend
    
    def test_array_concatenation_artists(self, backend):
        """Test that array concatenation works for artists"""
        artists = backend.getLibraryArtists()
        # Should be able to concatenate without error
        result = ["All artists"] + artists
        assert isinstance(result, list)
        assert result[0] == "All artists"
        
    def test_concat_method_artists(self, backend):
        """Test that .concat() method works for artists"""
        artists = backend.getLibraryArtists()
        result = ["All artists"]
        result = result.__class__(result).extend(artists) or result + artists
        assert isinstance(result, list)
        
    def test_array_not_stringified(self, backend):
        """Verify array is not converted to string during concatenation"""
        genres = backend.getLibraryGenres()
        assert isinstance(genres, list), "genres must be a list"
        assert not isinstance(genres, str), "genres must NOT be a string"
        
        # After concatenation
        result = ["All genres"].extend(genres) or ["All genres"] + genres
        assert isinstance(result, list) or result is None, "concatenation must produce a list"


class TestDataTypeIntegrity:
    """Test data integrity through the backend"""
    
    @pytest.fixture
    def backend(self):
        """Create a backend instance for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {"DJ_HOME_PATH": tmpdir}):
                backend = QmlBackend()
                yield backend
    
    def test_no_string_in_list_results(self, backend):
        """Ensure list methods never return strings"""
        methods_returning_lists = [
            ("getLibraryArtists", backend.getLibraryArtists),
            ("getLibraryAlbums", backend.getLibraryAlbums),
            ("getLibraryGenres", backend.getLibraryGenres),
            ("getWipContexts", backend.getWipContexts),
            ("getSavedPlaylists", backend.getSavedPlaylists),
        ]
        
        for method_name, method in methods_returning_lists:
            result = method()
            assert isinstance(result, list), f"{method_name} returned non-list: {type(result)}"
            assert not isinstance(result, str), f"{method_name} returned a string instead of list"
    
    def test_list_items_are_strings(self, backend):
        """Ensure all items in lists are strings"""
        methods_returning_string_lists = [
            ("getLibraryArtists", backend.getLibraryArtists),
            ("getLibraryAlbums", backend.getLibraryAlbums),
            ("getLibraryGenres", backend.getLibraryGenres),
            ("getWipContexts", backend.getWipContexts),
        ]
        
        for method_name, method in methods_returning_string_lists:
            result = method()
            for i, item in enumerate(result):
                assert isinstance(item, str), \
                    f"{method_name}[{i}] is {type(item).__name__}, expected str: {repr(item)}"
