import sqlite3

from ttvttm.data import djDataConnection
from ttvttm.tracksong import TrackSong


def test_djdata_connection_ensure_treated_column(tmp_path):
    db_path = tmp_path / "ttvttm.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE tangos (ID INTEGER PRIMARY KEY, tangopath TEXT)")
    conn.commit()
    conn.close()

    data = djDataConnection(str(tmp_path))
    conn = sqlite3.connect(data.path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(tangos)")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()

    assert "treated" in columns


def test_get_tango_from_list_id_empty_returns_empty(tmp_path):
    db_path = tmp_path / "ttvttm.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE tangos (ID INTEGER PRIMARY KEY, tangopath TEXT)")
    conn.commit()
    conn.close()

    data = djDataConnection(str(tmp_path))

    assert data.getTrackFromListID([]) == []


def test_set_new_song_available_updates_preferences(tmp_path):
    conn = sqlite3.connect(tmp_path / "ttvttm.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE preferences (baseDir TEXT, timeCortina INTEGER, timeFadOut INTEGER, writeID3Tag INTEGER, normalize INTEGER, newSongAvailable INTEGER)")
    cursor.execute("INSERT INTO preferences VALUES (?, ?, ?, ?, ?, ?)", ("none", 46, 6, 0, 0, 0))
    conn.commit()
    conn.close()

    data = djDataConnection(str(tmp_path))
    data.setNewSongAvailable(True)

    conn = sqlite3.connect(data.path)
    cursor = conn.cursor()
    cursor.execute("SELECT newSongAvailable FROM preferences")
    value = cursor.fetchone()[0]
    conn.close()

    assert value == 1


def test_insert_tango_stores_duration(tmp_path):
    data = djDataConnection(str(tmp_path))
    data.createDatabase()

    track = TrackSong(str(tmp_path / "song.mp3"), 0, False)
    track.duration = 123.456
    inserted_id = data.insertTrack(track)

    conn = sqlite3.connect(data.path)
    cursor = conn.cursor()
    cursor.execute("SELECT duration FROM tangos WHERE ID = ?", (inserted_id,))
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert float(row[0]) == 123.456
