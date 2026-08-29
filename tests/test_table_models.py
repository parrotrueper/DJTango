from types import SimpleNamespace

import pytest
from PySide6.QtCore import (
    QByteArray,
    QDataStream,
    QIODevice,
    QMimeData,
    QModelIndex,
    Qt,
)

from ttvttm.milonga_manager import MilongaManagerMixin
from ttvttm.tableModels import (
    library,
    milongaSource,
    normalize_type_key,
    sourceFilterProxyModel,
)
from ttvttm.tracksong import TrackSong


def test_library_column_count_empty_list():
    model = library(None, [], ["A"], {1: ("track", "Track", 0, 0, 0, 255)})

    assert model.columnCount(None) == 0


def test_library_sort_order():
    model = library(None, [[3], [1], [2]], ["A"], {1: ("track", "Track", 0, 0, 0, 255)})

    model.sort(0, Qt.AscendingOrder)
    assert model.mylist == [[1], [2], [3]]

    model.sort(0, Qt.DescendingOrder)
    assert model.mylist == [[3], [2], [1]]


def test_milonga_source_unknown_genre_returns_unknown():
    model = milongaSource(None, [[0, 0, 0, 0, 0, 999, 0, 0, 0]], ["A"] * 9,
                         {1: ("track", "Track", 0, 0, 0, 255)})
    index = model.index(0, 5)

    assert model.data(index, Qt.DisplayRole) == "Unknown"


def test_milonga_source_recognizes_string_type_name_for_genre():
    model = milongaSource(None, [[1, 0, "Title", "Artist", "Album", "Track", 1960, 120.0, 123456]],
                         ["#", " ", "Title", "Artist", "Album", "Genre", "Year", "BPM", "Time"],
                         {1: ("track", "Track", 0, 0, 0, 255)})
    index = model.index(0, 5)

    assert model.data(index, Qt.DisplayRole) == "Track"


@pytest.mark.parametrize("type_value", [1, "1", "Track", "track", "TRACK"])
def test_milonga_source_genre_column_uses_type_mapping_for_numeric_and_text_keys(type_value):
    model = milongaSource(None, [[1, 0, "Title", "Artist", "Album", type_value, 1960, 120.0, 123456]],
                         ["#", " ", "Title", "Artist", "Album", "Genre", "Year", "BPM", "Time"],
                         {1: ("track", "Track", 0, 0, 0, 255)})
    index = model.index(0, 5)

    assert model.data(index, Qt.DisplayRole) == "Track"


def test_milonga_source_genre_column_displays_track_genre_label():
    row = [1, 0, "Title", "Artist", "Album", 3, 1960, 120.0, 123456]
    model = milongaSource(None, [row],
                         ["#", " ", "Title", "Artist", "Album", "Genre", "Year", "BPM", "Time"],
                         {3: ("tango", "Vals", 10, 20, 30, 255)})
    index = model.index(0, 5)

    assert model.data(index, Qt.DisplayRole) == "Vals"


def test_normalize_type_key_resolves_numeric_and_text_type_names():
    TYPE = {1: ("track", "Track", 0, 0, 0, 255)}

    assert normalize_type_key(1, TYPE) == 1
    assert normalize_type_key("1", TYPE) == 1
    assert normalize_type_key("Track", TYPE) == 1
    assert normalize_type_key("track", TYPE) == 1
    assert normalize_type_key("TRACK", TYPE) == 1


def test_source_filter_proxy_model_filters_by_album_and_genre():
    source = library(None, [[0, 0, 0, "Artist", "My Album", "Track", 0, 0, 0]],
                     ["ID", "Flag", "Title", "Artist", "Album", "Genre", "Year", "BPM", "Duration"],
                     {5: ("track", "Track", 0, 0, 0, 255), "Track": (5, "Track", 0, 0, 0, 255)})
    proxy = sourceFilterProxyModel(None)
    proxy.setSourceModel(source)
    proxy.setlFilterValues("", "Track", "Track", ".*")

    assert proxy.filterAcceptsRow(0, QModelIndex())


def test_milonga_dest_drop_converts_string_genre_to_type_id():
    TYPE = {
        1: ("track", "Track", 0, 0, 0, 255),
        5: ("unknown", "Unknown", 42, 42, 42, 255),
    }
    from ttvttm.tableModels import milongaDest

    model = milongaDest(None, [], ["#", " ", "Title", "Artist", "Album", "Genre", "Year", "BPM", "Time"], TYPE)
    mime = QMimeData()
    encoded = QByteArray()
    stream = QDataStream(encoded, QIODevice.WriteOnly)
    values = [1, 0, "Title", "Artist", "Album", "Track", 1960, 120.0, 123456]
    for column, value in enumerate(values):
        stream.writeInt32(0)
        stream.writeInt32(column)
        stream.writeInt32(1)
        stream.writeInt32(int(Qt.DisplayRole))
        stream.writeQVariant(value)
    mime.setData("application/x-qabstractitemmodeldatalist", encoded)

    assert model.dropMimeData(mime, Qt.CopyAction, -1, -1, QModelIndex())
    assert model.mylist[0][5] == 1


def test_update_milonga_infos_handles_string_type_values():
    class DummyManager(MilongaManagerMixin):
        pass

    manager = DummyManager()
    manager.TYPE = {
        1: ("track", "Track", 0, 0, 0, 255),
        4: ("cortina", "Cortina", 0, 0, 0, 255),
        5: ("unknown", "Unknown", 42, 42, 42, 255),
    }
    manager.FadeOutTime = 1000
    manager._startMilongaTimeStamp = 0
    manager._dialog = SimpleNamespace(labelSizeDuration=SimpleNamespace(setText=lambda text: setattr(manager, "info_text", text)))
    manager.djData = SimpleNamespace(getTrackFromListID=lambda ids: [TrackSong("/tmp/song.mp3", 1)])
    track = manager.djData.getTrackFromListID([1])[0]
    track.type = "Track"
    track.duration = 1000
    manager.getIDListFromMilonga = lambda: [1]

    manager.updateMilongaInfos()

    assert "1 track(s)" in manager.info_text


def test_milonga_source_time_column_displays_total_play_time_in_seconds():
    duration_seconds = 123.456
    model = milongaSource(None, [[0, 0, "Title", "Artist", "Album", 1, 1960, 120.0, duration_seconds]],
                         ["#", " ", "Title", "Artist", "Album", "Genre", "Year", "BPM", "Time"],
                         {1: ("track", "Track", 0, 0, 0, 255)})
    index = model.index(0, 8)

    assert model.data(index, Qt.DisplayRole) == "02:03"


def test_milonga_source_time_column_displays_total_play_time():
    duration_ms = 123456
    model = milongaSource(None, [[0, 0, "Title", "Artist", "Album", 1, 1960, 120.0, duration_ms]],
                         ["#", " ", "Title", "Artist", "Album", "Genre", "Year", "BPM", "Time"],
                         {1: ("track", "Track", 0, 0, 0, 255)})
    index = model.index(0, 8)

    assert model.data(index, Qt.DisplayRole) == "02:03"


def test_milonga_source_all_library_columns_display_correctly():
    row = [1, 0, "Song Title", "Artist Name", "Album Name", 1, 1960, 120.0, 123456]
    model = milongaSource(None, [row],
                         ["#", " ", "Title", "Artist", "Album", "Genre", "Year", "BPM", "Time"],
                         {1: ("track", "Track", 0, 0, 0, 255)})

    assert model.data(model.index(0, 0), Qt.DisplayRole) == 1
    assert model.data(model.index(0, 1), Qt.DisplayRole) == ""
    assert model.data(model.index(0, 2), Qt.DisplayRole) == "Song Title"
    assert model.data(model.index(0, 3), Qt.DisplayRole) == "Artist Name"
    assert model.data(model.index(0, 4), Qt.DisplayRole) == "Album Name"
    assert model.data(model.index(0, 5), Qt.DisplayRole) == "Track"
    assert model.data(model.index(0, 6), Qt.DisplayRole) == 1960
    assert model.data(model.index(0, 7), Qt.DisplayRole) == "120.00"
    assert model.data(model.index(0, 8), Qt.DisplayRole) == "02:03"


def test_milonga_source_flag_column_shows_prompt_when_flag_is_set():
    row = [1, 1, "Song Title", "Artist Name", "Album Name", 1, 1960, 120.0, 123456]
    model = milongaSource(None, [row],
                         ["#", " ", "Title", "Artist", "Album", "Genre", "Year", "BPM", "Time"],
                         {1: ("track", "Track", 0, 0, 0, 255)})

    assert model.data(model.index(0, 1), Qt.DisplayRole) == ">>>"
