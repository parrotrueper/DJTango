"""
Unit tests for search functionality.

Tests verify that search operations produce correct lists of matching tracks.
"""

import sqlite3
import tempfile
import pytest

from ttvttm.data import djDataConnection
from ttvttm.tracksong import TrackSong


@pytest.fixture
def test_db():
    """Create a test database with sample tracks"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = f"{tmpdir}/ttvttm.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tangos table with all required columns
        cursor.execute("""
            CREATE TABLE tangos (
                ID INTEGER PRIMARY KEY,
                tangopath TEXT,
                title TEXT,
                artist TEXT,
                album TEXT,
                genre INTEGER,
                year TEXT,
                bpmHuman INTEGER,
                bpmFromFile INTEGER,
                duration REAL,
                singer TEXT,
                composer TEXT,
                author TEXT,
                tstart REAL,
                tend REAL,
                treated INTEGER
            )
        """)
        
        # Insert test data
        test_tracks = [
            (1, "/path/to/track1.mp3", "La Cumparsita", "Gardel", "Best of", 1, "1924", 100, 100, 240.5, "Gardel", "Matos", "Contursi", 0, 240.5, 0),
            (2, "/path/to/track2.mp3", "El Choclo", "Di Sarli", "Golden", 1, "1926", 95, 95, 210.0, "Di Sarli", "Villoldo", "Villoldo", 0, 210.0, 0),
            (3, "/path/to/track3.mp3", "Poema", "Gardel", "Classic", 2, "1925", 110, 110, 180.0, "Gardel", "García", "Weill", 0, 180.0, 0),
            (4, "/path/to/track4.mp3", "Milonga del 900", "Biagi", "Golden", 3, "1940", 120, 120, 200.0, "Biagi", "Matos", "Contursi", 0, 200.0, 1),
            (5, "/path/to/track5.mp3", "La Cumparsita", "Di Sarli", "Orchestra", 1, "1928", 105, 105, 220.0, "Chorus", "Matos", "Contursi", 0, 220.0, 0),
        ]
        
        for track in test_tracks:
            cursor.execute("""
                INSERT INTO tangos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, track)
        
        conn.commit()
        conn.close()
        
        yield tmpdir


class TestSearchTrack:
    """Tests for track search functionality"""
    
    def test_search_exact_match_returns_matches(self, test_db):
        """Test that searching for an exact track returns matching results"""
        data = djDataConnection(test_db)
        
        # Search for "La Cumparsita" by Gardel from "Best of"
        search_track = TrackSong("/dummy/path.mp3", 0)
        search_track.title = "La Cumparsita"
        search_track.artist = "Gardel"
        search_track.album = "Best of"
        search_track.type = 1
        
        results = data.searchTrack(search_track)
        
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0].title == "La Cumparsita"
        assert results[0].artist == "Gardel"
        assert results[0].album == "Best of"
    
    def test_search_no_match_returns_empty_list(self, test_db):
        """Test that searching for non-existent track returns empty list"""
        data = djDataConnection(test_db)
        
        # Search for non-existent track
        search_track = TrackSong("/dummy/path.mp3", 0)
        search_track.title = "NonExistent"
        search_track.artist = "FakeArtist"
        search_track.album = "FakeAlbum"
        search_track.type = 1
        
        results = data.searchTrack(search_track)
        
        assert isinstance(results, list)
        assert len(results) == 0
    
    def test_search_requires_all_fields_match(self, test_db):
        """Test that search requires all fields (title, artist, album, genre) to match"""
        data = djDataConnection(test_db)
        
        # "La Cumparsita" exists by both Gardel and Di Sarli, but only Gardel is in "Best of"
        search_track = TrackSong("/dummy/path.mp3", 0)
        search_track.title = "La Cumparsita"
        search_track.artist = "Di Sarli"  # Wrong artist for Best of
        search_track.album = "Best of"    # This album has Gardel version
        search_track.type = 1
        
        results = data.searchTrack(search_track)
        
        assert isinstance(results, list)
        assert len(results) == 0
    
    def test_search_returns_tracksong_objects(self, test_db):
        """Test that search returns TrackSong objects with all fields populated"""
        data = djDataConnection(test_db)
        
        search_track = TrackSong("/dummy/path.mp3", 0)
        search_track.title = "El Choclo"
        search_track.artist = "Di Sarli"
        search_track.album = "Golden"
        search_track.type = 1
        
        results = data.searchTrack(search_track)
        
        assert len(results) == 1
        result = results[0]
        
        # Verify all fields are populated
        assert isinstance(result, TrackSong)
        assert result.title == "El Choclo"
        assert result.artist == "Di Sarli"
        assert result.album == "Golden"
        assert result.type == 1
        assert result.year == "1926"
        assert result.bpmHuman == 95
        assert result.bpmFromFile == 95
        assert result.duration == 210.0
        assert result.singer == "Di Sarli"
        assert result.composer == "Villoldo"
        assert result.author == "Villoldo"
        assert result.treated == 0
    
    def test_search_matches_genre_type_field(self, test_db):
        """Test that search correctly matches the genre/type field"""
        data = djDataConnection(test_db)
        
        # Search for Poema (type 2)
        search_track = TrackSong("/dummy/path.mp3", 0)
        search_track.title = "Poema"
        search_track.artist = "Gardel"
        search_track.album = "Classic"
        search_track.type = 2  # Genre type matters
        
        results = data.searchTrack(search_track)
        
        assert len(results) == 1
        assert results[0].type == 2
    
    def test_search_different_genre_no_match(self, test_db):
        """Test that searching with wrong genre type returns no results"""
        data = djDataConnection(test_db)
        
        search_track = TrackSong("/dummy/path.mp3", 0)
        search_track.title = "El Choclo"
        search_track.artist = "Di Sarli"
        search_track.album = "Golden"
        search_track.type = 2  # Wrong type (correct is 1)
        
        results = data.searchTrack(search_track)
        
        assert isinstance(results, list)
        assert len(results) == 0
    
    def test_search_returns_all_matching_tracks(self, test_db):
        """Test that search returns all tracks that match all criteria"""
        data = djDataConnection(test_db)
        
        # "La Cumparsita" exists in database in different albums/artists
        # Search for all "La Cumparsita" by Gardel in Best of (type 1)
        search_track = TrackSong("/dummy/path.mp3", 0)
        search_track.title = "La Cumparsita"
        search_track.artist = "Gardel"
        search_track.album = "Best of"
        search_track.type = 1
        
        results = data.searchTrack(search_track)
        
        # Should find exactly 1 match (Gardel version in Best of)
        assert len(results) == 1
        assert all(isinstance(r, TrackSong) for r in results)
        assert all(r.title == "La Cumparsita" for r in results)
        assert all(r.artist == "Gardel" for r in results)
        assert all(r.album == "Best of" for r in results)
    
    def test_search_preserves_all_track_properties(self, test_db):
        """Test that search results preserve all track properties from database"""
        data = djDataConnection(test_db)
        
        search_track = TrackSong("/dummy/path.mp3", 0)
        search_track.title = "Milonga del 900"
        search_track.artist = "Biagi"
        search_track.album = "Golden"
        search_track.type = 3
        
        results = data.searchTrack(search_track)
        
        assert len(results) == 1
        result = results[0]
        
        # Verify treated flag is preserved (this one was marked as treated)
        assert result.treated == 1
        assert result.duration == 200.0
        assert result.year == "1940"


class TestSearchEdgeCases:
    """Tests for edge cases in search functionality"""
    
    def test_search_empty_database(self):
        """Test search on empty database returns empty list"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/ttvttm.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create empty tangos table
            cursor.execute("""
                CREATE TABLE tangos (
                    ID INTEGER PRIMARY KEY,
                    tangopath TEXT,
                    title TEXT,
                    artist TEXT,
                    album TEXT,
                    genre INTEGER,
                    year TEXT,
                    bpmHuman INTEGER,
                    bpmFromFile INTEGER,
                    duration REAL,
                    singer TEXT,
                    composer TEXT,
                    author TEXT,
                    tstart REAL,
                    tend REAL,
                    treated INTEGER
                )
            """)
            conn.commit()
            conn.close()
            
            data = djDataConnection(tmpdir)
            
            search_track = TrackSong("/dummy/path.mp3", 0)
            search_track.title = "Anything"
            search_track.artist = "Anyone"
            search_track.album = "Album"
            search_track.type = 1
            
            results = data.searchTrack(search_track)
            
            assert isinstance(results, list)
            assert len(results) == 0
    
    def test_search_with_special_characters(self, test_db):
        """Test search handles tracks with special characters correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/ttvttm.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create table and add track with special characters
            cursor.execute("""
                CREATE TABLE tangos (
                    ID INTEGER PRIMARY KEY,
                    tangopath TEXT,
                    title TEXT,
                    artist TEXT,
                    album TEXT,
                    genre INTEGER,
                    year TEXT,
                    bpmHuman INTEGER,
                    bpmFromFile INTEGER,
                    duration REAL,
                    singer TEXT,
                    composer TEXT,
                    author TEXT,
                    tstart REAL,
                    tend REAL,
                    treated INTEGER
                )
            """)
            
            cursor.execute("""
                INSERT INTO tangos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (1, "/path.mp3", "El Café", "Artista's Band", "Album & More", 1, "1920", 100, 100, 200.0, "Singer", "Composer", "Author", 0, 200.0, 0))
            
            conn.commit()
            conn.close()
            
            data = djDataConnection(tmpdir)
            
            search_track = TrackSong("/dummy/path.mp3", 0)
            search_track.title = "El Café"
            search_track.artist = "Artista's Band"
            search_track.album = "Album & More"
            search_track.type = 1
            
            results = data.searchTrack(search_track)
            
            assert len(results) == 1
            assert results[0].title == "El Café"
