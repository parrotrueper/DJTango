from pathlib import Path

from djtango import utils
from djtango.dirsong import dirSong
from djtango.tangosong import TangoSong


def test_remove_accents_and_odd_characters():
    assert utils.remove_accents('Éléphant') == 'Elephant'
    assert utils.remvoveSlash('a/b/c') == 'a-b-c'
    assert utils.removeOddCaracters('A:B.C') == 'ABC'


def test_title_fields_normalize_text():
    tango = TangoSong('/tmp/fake.mp3')
    tango.artist = 'carlos gardel'
    tango.title = 'el dia que me quieras'
    tango.album = 'gracias a la vida'
    tango.author = 'unknown'

    tango.titleFields()

    assert tango.artist == 'Carlos Gardel'
    assert tango.title == 'El Dia Que Me Quieras'
    assert tango.album == 'Gracias A La Vida'
    assert tango.author == 'Unknown'


class DummyAudio(dict):
    def __init__(self):
        super().__init__()
        self.saved = False

    def save(self):
        self.saved = True


def test_write_id3_tag_populates_audio_and_saves():
    tango = TangoSong('/tmp/fake.mp3')
    tango.title = 'Mi Tango'
    tango.artist = 'Astor Piazzolla'
    tango.album = 'Libertango'
    tango.type = 5
    tango.year = 1981
    tango.author = 'Piazzolla'
    tango.bpmHuman = 120
    tango.bpmFromFile = 110

    audio = DummyAudio()
    TYPE = {5: ('tango', 'Tango', 0, 0, 0, 255)}

    tango.writeID3Tag(audio, TYPE)

    assert audio.saved
    assert audio['title'] == 'Mi Tango'
    assert audio['artist'] == 'Astor Piazzolla'
    assert audio['album'] == 'Libertango'
    assert audio['genre'] == 'Tango'
    assert audio['date'] == '1981'
    assert audio['author'] == 'Piazzolla'
    assert audio['bpm'] == 120


def test_get_list_from_dir_only_returns_supported_extensions(tmp_path):
    (tmp_path / 'song1.mp3').write_text('dummy')
    (tmp_path / 'image.jpg').write_text('dummy')
    (tmp_path / 'song2.flac').write_text('dummy')

    scanner = dirSong(cpath=str(tmp_path))
    result = scanner.getListFromDir()

    assert len(result) == 2
    assert str(tmp_path / 'song1.mp3') in result
    assert str(tmp_path / 'song2.flac') in result
    assert str(tmp_path / 'image.jpg') not in result
    assert list(result.values()) == [1, 2]


def test_check_empty_dir_removes_unsupported_files(tmp_path):
    nested = tmp_path / 'nested'
    nested.mkdir()
    audio_file = nested / 'song.mp3'
    unsupported_file = nested / 'desktop.ini'
    audio_file.write_text('dummy')
    unsupported_file.write_text('dummy')

    scanner = dirSong(cpath=str(tmp_path))
    scanner.checkEmptyDir()

    assert audio_file.exists()
    assert not unsupported_file.exists()
    assert nested.exists()
