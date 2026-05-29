from djtango.qt_compat import QModelIndex, Qt
from djtango.tableModels import library, milongaSource, sourceFilterProxyModel


def test_library_column_count_empty_list():
    model = library(None, [], ['A'], {1: ('tango', 'Tango', 0, 0, 0, 255)})

    assert model.columnCount(None) == 0


def test_library_sort_order():
    model = library(None, [[3], [1], [2]], ['A'], {1: ('tango', 'Tango', 0, 0, 0, 255)})

    model.sort(0, Qt.AscendingOrder)
    assert model.mylist == [[1], [2], [3]]

    model.sort(0, Qt.DescendingOrder)
    assert model.mylist == [[3], [2], [1]]


def test_milonga_source_unknown_genre_returns_unknown():
    model = milongaSource(None, [[0, 0, 0, 0, 0, 999, 0, 0, 0]], ['A'] * 9,
                         {1: ('tango', 'Tango', 0, 0, 0, 255)})
    index = model.index(0, 5)

    assert model.data(index, Qt.DisplayRole) == 'Unknown'


def test_source_filter_proxy_model_filters_by_album_and_genre():
    source = library(None, [[0, 0, 0, 'Artist', 'My Album', 'Tango', 0, 0, 0]],
                     ['ID', 'Flag', 'Title', 'Artist', 'Album', 'Genre', 'Year', 'BPM', 'Duration'],
                     {5: ('tango', 'Tango', 0, 0, 0, 255), 'Tango': (5, 'Tango', 0, 0, 0, 255)})
    proxy = sourceFilterProxyModel(None)
    proxy.setSourceModel(source)
    proxy.setlFilterValues('', 'Tango', 'Tango', '.*')

    assert proxy.filterAcceptsRow(0, QModelIndex())
