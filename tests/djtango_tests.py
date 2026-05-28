#!/usr/bin/python3
# -*- coding:Utf-8 -*-

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from djtango.qt_compat import QColor, QModelIndex, Qt
from bin.DJTango import apply_tango_type_color, get_contrast_color, tango_type_key_from_row
from djtango import utils
from djtango.dirsong import dirSong
from djtango.tangosong import TangoSong
from djtango.tableModels import library, milongaSource, sourceFilterProxyModel


class DummyColor:
    def __init__(self, r, g, b, a):
        self._r = r
        self._g = g
        self._b = b
        self._a = a

    def red(self):
        return self._r

    def green(self):
        return self._g

    def blue(self):
        return self._b

    def alpha(self):
        return self._a


class TangoDialogHelpersTest(unittest.TestCase):
    def test_tango_type_key_from_row_valid(self):
        self.assertEqual(tango_type_key_from_row(0), 1)
        self.assertEqual(tango_type_key_from_row(2), 3)

    def test_tango_type_key_from_row_no_selection(self):
        with self.assertRaises(ValueError):
            tango_type_key_from_row(-1)

    def test_apply_tango_type_color_updates_type(self):
        TYPE = {1: ('unknown', 'Unknown', 1, 2, 3, 255)}
        new_color = DummyColor(100, 150, 200, 180)
        result = apply_tango_type_color(TYPE, 0, new_color)
        self.assertEqual(result, (TYPE[1][0], TYPE[1][1], 100, 150, 200, 180))
        self.assertEqual(TYPE[1], result)

    def test_apply_tango_type_color_invalid_row(self):
        TYPE = {1: ('unknown', 'Unknown', 1, 2, 3, 255)}
        new_color = DummyColor(100, 150, 200, 180)
        with self.assertRaises(KeyError):
            apply_tango_type_color(TYPE, 1, new_color)

    def test_table_model_foreground_role_uses_saved_font_color(self):
        TYPE = {
            3: ('milonga', 'Milonga', 10, 20, 30, 40, 1, 2, 3, 255)
        }
        model = milongaSource(None, [[None, None, None, None, None, 3]], ['c0', 'c1', 'c2', 'c3', 'c4', 'c5'], TYPE)
        index = model.createIndex(0, 0)
        color = model.data(index, Qt.ForegroundRole)

        self.assertIsNotNone(color)
        self.assertEqual(color.red(), 1)
        self.assertEqual(color.green(), 2)
        self.assertEqual(color.blue(), 3)
        self.assertEqual(color.alpha(), 255)

    def test_get_contrast_color_dark_background(self):
        color = QColor(10, 10, 10)
        self.assertEqual(get_contrast_color(color).name(), QColor(255, 255, 255).name())

    def test_get_contrast_color_light_background(self):
        color = QColor(250, 250, 250)
        self.assertEqual(get_contrast_color(color).name(), QColor(0, 0, 0).name())


class TangoSongAndDirSongTest(unittest.TestCase):
    def test_remove_accents_and_odd_characters(self):
        self.assertEqual(utils.remove_accents('Éléphant'), 'Elephant')
        self.assertEqual(utils.remvoveSlash('a/b/c'), 'a-b-c')
        self.assertEqual(utils.removeOddCaracters('A:B.C'), 'ABC')

    def test_title_fields_normalize_text(self):
        tango = TangoSong('/tmp/fake.mp3')
        tango.artist = 'carlos gardel'
        tango.title = 'el dia que me quieras'
        tango.album = 'gracias a la vida'
        tango.author = 'unknown'
        tango.titleFields()
        self.assertEqual(tango.artist, 'Carlos Gardel')
        self.assertEqual(tango.title, 'El Dia Que Me Quieras')
        self.assertEqual(tango.album, 'Gracias A La Vida')
        self.assertEqual(tango.author, 'Unknown')

    def test_write_id3_tag_populates_audio_and_saves(self):
        tango = TangoSong('/tmp/fake.mp3')
        tango.title = 'Mi Tango'
        tango.artist = 'Astor Piazzolla'
        tango.album = 'Libertango'
        tango.type = 5
        tango.year = 1981
        tango.author = 'Piazzolla'
        tango.bpmHuman = 120
        tango.bpmFromFile = 110

        class DummyAudio(dict):
            def __init__(self):
                super().__init__()
                self.saved = False

            def save(self):
                self.saved = True

        audio = DummyAudio()
        TYPE = {5: ('tango', 'Tango', 0, 0, 0, 255)}
        tango.writeID3Tag(audio, TYPE)

        self.assertTrue(audio.saved)
        self.assertEqual(audio['title'], 'Mi Tango')
        self.assertEqual(audio['artist'], 'Astor Piazzolla')
        self.assertEqual(audio['album'], 'Libertango')
        self.assertEqual(audio['genre'], 'Tango')
        self.assertEqual(audio['date'], '1981')
        self.assertEqual(audio['author'], 'Piazzolla')
        self.assertEqual(audio['bpm'], 120)

    def test_getListFromDir_only_returns_supported_extensions(self):
        import tempfile
        import pathlib

        with tempfile.TemporaryDirectory() as tmpdir:
            pathlib.Path(tmpdir, 'song1.mp3').write_text('dummy')
            pathlib.Path(tmpdir, 'image.jpg').write_text('dummy')
            pathlib.Path(tmpdir, 'song2.flac').write_text('dummy')

            scanner = dirSong(cpath=tmpdir)
            result = scanner.getListFromDir()

            self.assertEqual(len(result), 2)
            self.assertIn(str(pathlib.Path(tmpdir, 'song1.mp3')), result)
            self.assertIn(str(pathlib.Path(tmpdir, 'song2.flac')), result)
            self.assertNotIn(str(pathlib.Path(tmpdir, 'image.jpg')), result)
            self.assertEqual(list(result.values()), [1, 2])

    def test_checkEmptyDir_removes_unsupported_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            nested = Path(tmpdir) / 'nested'
            nested.mkdir()
            audio_file = nested / 'song.mp3'
            unsupported_file = nested / 'desktop.ini'
            audio_file.write_text('dummy')
            unsupported_file.write_text('dummy')

            scanner = dirSong(cpath=tmpdir)
            scanner.checkEmptyDir()

            self.assertTrue(audio_file.exists())
            self.assertFalse(unsupported_file.exists())
            self.assertTrue(nested.exists())


class AdditionalProjectTests(unittest.TestCase):
    def test_djDataConnection_ensure_treated_column(self):
        from djtango.data import djDataConnection

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / 'djtango.db'
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('CREATE TABLE tangos (ID INTEGER PRIMARY KEY, tangopath TEXT)')
            conn.commit()
            conn.close()

            data = djDataConnection(tmpdir)
            conn = sqlite3.connect(data.path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(tangos)")
            columns = [row[1] for row in cursor.fetchall()]
            conn.close()
            self.assertIn('treated', columns)

    def test_dirSong_normalizeTango_updates_listFiles_key(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / 'song.mp3'
            source.write_text('dummy')

            tango = TangoSong(str(source), 1)
            tango.title = 'Mi Tango'
            tango.artist = 'Astor Piazzolla'
            tango.album = 'Libertango'
            tango.year = 1981
            tango.type = 5
            song_dir = dirSong(cpath=str(root))
            song_dir.tangos[1] = tango
            song_dir.listFiles[str(source)] = 1

            song_dir.normalizeTango(1, {5: ('tango', 'Tango', 0, 0, 0, 255), 1: ('unknown', 'Unknown', 0, 0, 0, 255)})
            new_path = song_dir.tangos[1].path

            self.assertNotEqual(new_path, str(source))
            self.assertTrue(Path(new_path).exists())
            self.assertIn(new_path, song_dir.listFiles)
            self.assertNotIn(str(source), song_dir.listFiles)

    def test_TangoSong_extractAnyTag_missing_file_does_not_raise(self):
        tango = TangoSong('/tmp/does_not_exist.mp3', 1, extractTag=False)
        tango.extractAnyTag()
        self.assertEqual(tango.title, 'Unknown')
        self.assertEqual(tango.artist, 'Unknown')

    def test_getTangoFromListID_empty_returns_empty(self):
        from djtango.data import djDataConnection

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / 'djtango.db'
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('CREATE TABLE tangos (ID INTEGER PRIMARY KEY, tangopath TEXT)')
            conn.commit()
            conn.close()

            data = djDataConnection(tmpdir)
            self.assertEqual(data.getTangoFromListID([]), [])

    def test_setNewSongAvailable_updates_preferences(self):
        from djtango.data import djDataConnection

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / 'djtango.db'
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('CREATE TABLE preferences (baseDir TEXT, timeCortina INTEGER, timeFadOut INTEGER, writeID3Tag INTEGER, normalize INTEGER, newSongAvailable INTEGER)')
            cursor.execute('INSERT INTO preferences VALUES (?, ?, ?, ?, ?, ?)', ('none', 46, 6, 0, 0, 0))
            conn.commit()
            conn.close()

            data = djDataConnection(tmpdir)
            data.setNewSongAvailable(True)
            conn = sqlite3.connect(data.path)
            cursor = conn.cursor()
            cursor.execute('SELECT newSongAvailable FROM preferences')
            value = cursor.fetchone()[0]
            conn.close()
            self.assertEqual(value, 1)

    def test_qt_compat_loads_qapplication(self):
        from djtango.qt_compat import QApplication, QMainWindow

        self.assertTrue(callable(QApplication))
        self.assertTrue(callable(QMainWindow))

    def test_gui_starts_in_offscreen_mode(self):
        import importlib.util
        import os

        if not (importlib.util.find_spec('PySide6') or importlib.util.find_spec('PyQt5')):
            self.skipTest('Qt bindings not available')

        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
        os.environ.setdefault('DJTANGO_DISABLE_DIR_SCAN', '1')
        from djtango.qt_compat import QApplication
        from bin.DJTango import AudioPlayerDialog

        app = QApplication([])
        dlg = AudioPlayerDialog()
        dlg.close()
        if hasattr(app, 'quit'):
            app.quit()

    def test_insertTango_does_not_duplicate_existing_tango(self):
        from djtango.data import djDataConnection

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / 'djtango.db'
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('CREATE TABLE tangos (ID INTEGER PRIMARY KEY, tangopath TEXT, title TEXT, artist TEXT, album TEXT, genre INTEGER, year INTEGER DEFAULT 0, bpmHuman REAL DEFAULT 0, bpmFromFile REAL DEFAULT 0, duration INTEGER DEFAULT 0, singer TEXT DEFAULT "Unknown", composer TEXT DEFAULT "Unknown", author TEXT DEFAULT "Unknown", tstart INTEGER DEFAULT 0, tend INTEGER DEFAULT 0, treated INTEGER DEFAULT 0)')
            cursor.execute('CREATE TABLE tangoType (ID INTEGER PRIMARY KEY ASC, type TEXT, R INTEGER, G INTEGER, B INTEGER, T INTEGER)')
            cursor.execute('CREATE TABLE preferences (baseDir TEXT DEFAULT "none", timeCortina INTEGER DEFAULT 46, timeFadOut INTEGER DEFAULT 6, writeID3Tag INTEGER DEFAULT 0, normalize INTEGER DEFAULT 0, newSongAvailable INTEGER DEFAULT 0)')
            cursor.execute('INSERT INTO tangoType VALUES (?, ?, ?, ?, ?, ?)', (1, 'unknown', 0, 0, 0, 255))
            cursor.execute('INSERT INTO tangoType VALUES (?, ?, ?, ?, ?, ?)', (5, 'Tango', 0, 0, 0, 255))
            cursor.execute('INSERT INTO tangos (ID, tangopath, title, artist, album, genre, year) VALUES (?, ?, ?, ?, ?, ?, ?)', (1, '/tmp/song.mp3', 'Song', 'Artist', 'Album', 5, 1980))
            conn.commit()
            conn.close()

            data = djDataConnection(tmpdir)
            tango = TangoSong('/tmp/song.mp3', 1)
            tango.title = 'Song'
            tango.artist = 'Artist'
            tango.album = 'Album'
            tango.type = 5
            data.insertTango(tango)

            conn = sqlite3.connect(data.path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM tangos')
            self.assertEqual(cursor.fetchone()[0], 1)
            conn.close()

    def test_library_columnCount_empty_list(self):
        model = library(None, [], ['A'], {1: ('tango', 'Tango', 0, 0, 0, 255)})
        self.assertEqual(model.columnCount(None), 0)

    def test_library_sort_order(self):
        model = library(None, [[3], [1], [2]], ['A'], {1: ('tango', 'Tango', 0, 0, 0, 255)})
        model.sort(0, Qt.AscendingOrder)
        self.assertEqual(model.mylist, [[1], [2], [3]])
        model.sort(0, Qt.DescendingOrder)
        self.assertEqual(model.mylist, [[3], [2], [1]])

    def test_milongaSource_unknown_genre_returns_unknown(self):
        model = milongaSource(None, [[0, 0, 0, 0, 0, 999, 0, 0, 0]], ['A'] * 9, {1: ('tango', 'Tango', 0, 0, 0, 255)})
        index = model.index(0, 5)
        self.assertEqual(model.data(index, Qt.DisplayRole), 'Unknown')

    def test_sourceFilterProxyModel_filters_by_album_and_genre(self):
        source = library(None, [[0, 0, 0, 'Artist', 'My Album', 'Tango', 0, 0, 0]],
                         ['ID', 'Flag', 'Title', 'Artist', 'Album', 'Genre', 'Year', 'BPM', 'Duration'],
                         {5: ('tango', 'Tango', 0, 0, 0, 255), 'Tango': (5, 'Tango', 0, 0, 0, 255)})
        proxy = sourceFilterProxyModel(None)
        proxy.setSourceModel(source)
        proxy.setlFilterValues('', 'Tango', 'Tango', '.*')
        self.assertTrue(proxy.filterAcceptsRow(0, QModelIndex()))


if __name__ == '__main__':
    unittest.main()
