import sqlite3
from pathlib import Path

from djtango.data import djDataConnection


def test_djdata_connection_ensure_treated_column(tmp_path):
    db_path = tmp_path / 'djtango.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE tangos (ID INTEGER PRIMARY KEY, tangopath TEXT)')
    conn.commit()
    conn.close()

    data = djDataConnection(str(tmp_path))
    conn = sqlite3.connect(data.path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(tangos)")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()

    assert 'treated' in columns


def test_get_tango_from_list_id_empty_returns_empty(tmp_path):
    db_path = tmp_path / 'djtango.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE tangos (ID INTEGER PRIMARY KEY, tangopath TEXT)')
    conn.commit()
    conn.close()

    data = djDataConnection(str(tmp_path))

    assert data.getTangoFromListID([]) == []


def test_set_new_song_available_updates_preferences(tmp_path):
    conn = sqlite3.connect(tmp_path / 'djtango.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE preferences (baseDir TEXT, timeCortina INTEGER, timeFadOut INTEGER, writeID3Tag INTEGER, normalize INTEGER, newSongAvailable INTEGER)')
    cursor.execute('INSERT INTO preferences VALUES (?, ?, ?, ?, ?, ?)', ('none', 46, 6, 0, 0, 0))
    conn.commit()
    conn.close()

    data = djDataConnection(str(tmp_path))
    data.setNewSongAvailable(True)

    conn = sqlite3.connect(data.path)
    cursor = conn.cursor()
    cursor.execute('SELECT newSongAvailable FROM preferences')
    value = cursor.fetchone()[0]
    conn.close()

    assert value == 1
