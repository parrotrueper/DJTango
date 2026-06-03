import os

from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex, Property
from djtango.qt_compat import QObject, pyqtSignal, pyqtSlot
from djtango.data import djDataConnection
from djtango.tracksong import TrackSong


class TrackListModel(QAbstractListModel):
    TrackIdRole = Qt.UserRole + 1
    TitleRole = Qt.UserRole + 2
    ArtistRole = Qt.UserRole + 3
    AlbumRole = Qt.UserRole + 4
    GenreRole = Qt.UserRole + 5
    YearRole = Qt.UserRole + 6
    BpmRole = Qt.UserRole + 7
    DurationRole = Qt.UserRole + 8
    PathRole = Qt.UserRole + 9

    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent)
        self._tracks = []

    def roleNames(self):
        return {
            self.TrackIdRole: b'trackId',
            self.TitleRole: b'title',
            self.ArtistRole: b'artist',
            self.AlbumRole: b'album',
            self.GenreRole: b'genre',
            self.YearRole: b'year',
            self.BpmRole: b'bpm',
            self.DurationRole: b'duration',
            self.PathRole: b'path',
        }

    def rowCount(self, parent=QModelIndex()):
        return len(self._tracks)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() < 0 or index.row() >= len(self._tracks):
            return None

        track = self._tracks[index.row()]
        if role == self.TrackIdRole:
            return track.get('id', 0)
        if role == self.TitleRole:
            return track.get('title', '')
        if role == self.ArtistRole:
            return track.get('artist', '')
        if role == self.AlbumRole:
            return track.get('album', '')
        if role == self.GenreRole:
            return track.get('genre', '')
        if role == self.YearRole:
            return track.get('year', 0)
        if role == self.BpmRole:
            return track.get('bpm', 0)
        if role == self.DurationRole:
            return track.get('duration', 0)
        if role == self.PathRole:
            return track.get('path', '')
        return None

    def setTracks(self, tracks):
        self.beginResetModel()
        self._tracks = list(tracks)
        self.endResetModel()

    def addTrack(self, track):
        row = len(self._tracks)
        self.beginInsertRows(QModelIndex(), row, row)
        self._tracks.append(track)
        self.endInsertRows()

    def removeTrack(self, row):
        if row < 0 or row >= len(self._tracks):
            return False
        self.beginRemoveRows(QModelIndex(), row, row)
        del self._tracks[row]
        self.endRemoveRows()
        return True

    def clear(self):
        self.beginResetModel()
        self._tracks = []
        self.endResetModel()

    def asList(self):
        return list(self._tracks)


class QmlBackend(QObject):
    libraryChanged = pyqtSignal()
    playlistChanged = pyqtSignal()
    playbackStateChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.djhome = os.environ.get('DJ_HOME_PATH', os.path.join(os.path.expanduser('~'), '.djtango'))
        self.djData = djDataConnection(self.djhome)
        if not os.path.exists(self.djData.path):
            self.djData.createDatabase()

        self.track_type_names = self._load_track_type_names()
        self._libraryModel = TrackListModel(self)
        self._playlistModel = TrackListModel(self)
        self._isPlaying = False
        self._wipContext = "Library"
        self.loadLibrary()

    def _load_track_type_names(self):
        type_list = {}
        for key, value in self.djData.getTrackTypeList().items():
            if len(value) > 1:
                type_list[key] = value[1]
            else:
                type_list[key] = str(key)
        return type_list

    def _track_to_dict(self, track):
        genre = track.type
        if isinstance(track.type, int) and track.type in self.track_type_names:
            genre = self.track_type_names[track.type]
        return {
            'id': track.ID,
            'title': track.title or '',
            'artist': track.artist or '',
            'album': track.album or '',
            'genre': genre,
            'year': int(track.year or 0),
            'bpm': float(track.bpmHuman or track.bpmFromFile or 0),
            'duration': float(track.duration or 0),
            'path': track.path or '',
        }

    @Property(QObject, notify=libraryChanged)
    def libraryModel(self):
        return self._libraryModel

    @Property(QObject, notify=playlistChanged)
    def playlistModel(self):
        return self._playlistModel

    @pyqtSlot(result=bool)
    def loadLibrary(self):
        try:
            tracks = self.djData.getAllTracks()
        except Exception:
            self.djData.createDatabase()
            tracks = self.djData.getAllTracks()

        self.track_type_names = self._load_track_type_names()
        self._libraryModel.setTracks([self._track_to_dict(track) for track in tracks])
        self.libraryChanged.emit()
        return True

    @pyqtSlot(str, result=bool)
    def addTrack(self, path):
        if not os.path.isfile(path):
            return False

        track = TrackSong(path, 0, True)
        inserted_id = self.djData.insertTrack(track)
        if inserted_id:
            track.ID = inserted_id
            self._libraryModel.addTrack(self._track_to_dict(track))
            self.libraryChanged.emit()
            return True

        self.loadLibrary()
        return False

    @pyqtSlot(int, result=bool)
    def addTrackToPlaylist(self, track_id):
        for track in self._libraryModel.asList():
            if int(track.get('id', 0)) == int(track_id):
                self._playlistModel.addTrack(track)
                self.playlistChanged.emit()
                return True
        return False

    @pyqtSlot(int, result=bool)
    def removeTrackFromPlaylist(self, row):
        if self._playlistModel.removeTrack(row):
            self.playlistChanged.emit()
            return True
        return False

    @pyqtSlot(str, result=bool)
    def savePlaylist(self, name):
        if not name:
            return False
        track_ids = [int(track.get('id', 0)) for track in self._playlistModel.asList() if track.get('id')]
        if not track_ids:
            return False
        self.djData.saveMilonga(name, track_ids)
        return True

    @pyqtSlot(str, result=bool)
    def loadPlaylist(self, name):
        if not name:
            return False
        tracks = self.djData.getTrackFromMilonga(name)
        if not tracks:
            return False
        self._playlistModel.setTracks([self._track_to_dict(track) for track in tracks])
        self.playlistChanged.emit()
        return True

    @pyqtSlot(result=bool)
    def play(self):
        self._isPlaying = True
        self.playbackStateChanged.emit(True)
        return True

    @pyqtSlot(result=bool)
    def pause(self):
        if not self._isPlaying:
            return False
        self._isPlaying = False
        self.playbackStateChanged.emit(False)
        return True

    @pyqtSlot(result=bool)
    def togglePlayPause(self):
        self._isPlaying = not self._isPlaying
        self.playbackStateChanged.emit(self._isPlaying)
        return True

    @pyqtSlot(result='QVariantList')
    def getSavedPlaylists(self):
        return self.djData.getListOfMilongas()

    @pyqtSlot(result='QVariantList')
    def getWipContexts(self):
        return ["Library", "Library 2", "Last playlist"]

    @pyqtSlot(str, result=bool)
    def selectWipContext(self, context):
        if context not in self.getWipContexts():
            return False
        self._wipContext = context
        return True

    @pyqtSlot(result=str)
    def currentWipContext(self):
        return self._wipContext

    @pyqtSlot(result=str)
    def appTitle(self):
        return "DJTango"

    @pyqtSlot(result=str)
    def appVersion(self):
        return "0.1.0"

    @pyqtSlot(result=str)
    def liveOutputName(self):
        return "Default"

    @pyqtSlot(result=int)
    def liveVolume(self):
        return 100
