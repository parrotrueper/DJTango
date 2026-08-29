import glob
import os

from PySide6.QtCore import (
    Property,
    QAbstractListModel,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    Qt,
    QUrl,
)
from PySide6.QtCore import Signal as pyqtSignal
from PySide6.QtCore import Slot as pyqtSlot
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer

from ttvttm.data import djDataConnection
from ttvttm.tracksong import TrackSong

QT_USER_ROLE = getattr(Qt, "UserRole", 256)

class TrackListModel(QAbstractListModel):
    TrackIdRole = QT_USER_ROLE + 1
    TitleRole = QT_USER_ROLE + 2
    ArtistRole = QT_USER_ROLE + 3
    AlbumRole = QT_USER_ROLE + 4
    GenreRole = QT_USER_ROLE + 5
    YearRole = QT_USER_ROLE + 6
    BpmRole = QT_USER_ROLE + 7
    DurationRole = QT_USER_ROLE + 8
    PathRole = QT_USER_ROLE + 9

    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent)
        self._tracks = []

    def roleNames(self):
        return {
            self.TrackIdRole: b"trackId",
            self.TitleRole: b"title",
            self.ArtistRole: b"artist",
            self.AlbumRole: b"album",
            self.GenreRole: b"genre",
            self.YearRole: b"year",
            self.BpmRole: b"bpm",
            self.DurationRole: b"duration",
            self.PathRole: b"path",
        }

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex | None = None):
        if parent is not None and parent.isValid():
            return 0
        return len(self._tracks)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() < 0 or index.row() >= len(self._tracks):
            return None

        track = self._tracks[index.row()]
        role_map = {
            self.TrackIdRole: ("id", 0),
            self.TitleRole: ("title", ""),
            self.ArtistRole: ("artist", ""),
            self.AlbumRole: ("album", ""),
            self.GenreRole: ("genre", ""),
            self.YearRole: ("year", 0),
            self.BpmRole: ("bpm", 0),
            self.DurationRole: ("duration", 0),
            self.PathRole: ("path", ""),
        }
        key, default = role_map.get(role, (None, None))
        if key is None:
            return None
        return track.get(key, default)

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
    playbackPositionChanged = pyqtSignal()
    playbackDurationChanged = pyqtSignal()

    @Property(int, notify=playbackPositionChanged)
    def playbackPosition(self):
        return self._playbackPosition

    @Property(int, notify=playbackDurationChanged)
    def playbackDuration(self):
        return self._playbackDuration

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.djHome = os.environ.get("DJ_HOME_PATH", os.path.join(os.path.expanduser("~"), ".ttvttm"))
        self.djData = djDataConnection(self.djHome)
        if not os.path.exists(self.djData.path):
            self.djData.createDatabase()

        self.track_type_names = self._load_track_type_names()
        self._libraryModel = TrackListModel(self)
        self._playlistModel = TrackListModel(self)
        self._player = None
        self._audio_output = None
        self._currentTrackId = -1
        self._isPlaying = False
        self._isLiveSession = False
        self._playbackPosition = 0
        self._playbackDuration = 0
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
            "id": track.ID,
            "title": track.title or "",
            "artist": track.artist or "",
            "album": track.album or "",
            "genre": genre,
            "year": int(track.year or 0),
            "bpm": float(track.bpmHuman or track.bpmFromFile or 0),
            "duration": float(track.duration or 0),
            "path": track.path or "",
        }

    def _ensure_player(self):
        if self._player is not None:
            return True
        try:
            self._player = QMediaPlayer()
            self._audio_output = QAudioOutput()
            self._player.setAudioOutput(self._audio_output)
            try:
                self._player.positionChanged.connect(self._on_position_changed)
                self._player.durationChanged.connect(self._on_duration_changed)
            except Exception:
                pass
            print(f"QmlBackend initialized QMediaPlayer={type(self._player)} play_attr={hasattr(self._player,'play')} pause_attr={hasattr(self._player,'pause')} setSource_attr={hasattr(self._player,'setSource')} setAudioOutput_attr={hasattr(self._player,'setAudioOutput')}")
            return True
        except Exception as exc:
            print(f"QmlBackend _ensure_player failed: {exc}")
            self._player = None
            self._audio_output = None
            return False

    def _on_position_changed(self, position):
        try:
            self._playbackPosition = int(position)
        except Exception:
            self._playbackPosition = 0
        self.playbackPositionChanged.emit()

    def _on_duration_changed(self, duration):
        try:
            self._playbackDuration = int(duration)
        except Exception:
            self._playbackDuration = 0
        self.playbackDurationChanged.emit()

    @Property(QObject, notify=libraryChanged)
    def libraryModel(self):
        return self._libraryModel

    @Property(QObject, notify=playlistChanged)
    def playlistModel(self):
        return self._playlistModel

    def _load_media(self, path):
        if not path or not os.path.isfile(path):
            print(f"_load_media failed, invalid path: {path}")
            return False
        if not self._ensure_player():
            return False
        abs_path = os.path.abspath(path)
        print(f"_load_media loading path: {abs_path}")
        try:
            self._player.setSource(QUrl.fromLocalFile(abs_path))
            self._playbackPosition = 0
            self._playbackDuration = 0
            self.playbackPositionChanged.emit()
            self.playbackDurationChanged.emit()
        except Exception as exc:
            print(f"_load_media setSource exception: {exc}")
            return False
        return True

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
        try:
            library_ids = [int(track.get("id", 0)) for track in self._libraryModel.asList()]
            print(f"addTrackToPlaylist called track_id={track_id}, library_ids={library_ids[:10]}, playlist_count_before={self._playlistModel.rowCount()}")
            for track in self._libraryModel.asList():
                if int(track.get("id", 0)) == int(track_id):
                    self._playlistModel.addTrack(track)
                    self.playlistChanged.emit()
                    print(f"added track_id={track_id} to playlist, playlist_count_after={self._playlistModel.rowCount()}")
                    return True
            print(f"track_id={track_id} not found in library")
        except Exception as exc:
            print(f"addTrackToPlaylist exception track_id={track_id}: {exc}")
        return False

    @pyqtSlot(int, result=bool)
    def playPlaylistTrack(self, track_id):
        if track_id is None or track_id < 0:
            print(f"playPlaylistTrack invalid track_id={track_id}")
            return False
        for track in self._playlistModel.asList():
            if int(track.get("id", 0)) == int(track_id):
                path = track.get("path", "")
                print(f"playPlaylistTrack requested track_id={track_id} path={path}")
                if not self._load_media(path):
                    print(f"playPlaylistTrack failed to load media for track_id={track_id} path={path}")
                    return False
                if not hasattr(self._player, "play"):
                    print("QMediaPlayer playback support is unavailable")
                    return False
                try:
                    self._player.play()
                except Exception as exc:
                    print(f"QMediaPlayer.play() exception: {exc}")
                    return False
                self._currentTrackId = int(track_id)
                self._isPlaying = True
                self.playbackStateChanged.emit(True)
                return True
        print(f"playPlaylistTrack track_id={track_id} not found in playlist")
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
        track_ids = [int(track.get("id", 0)) for track in self._playlistModel.asList() if track.get("id")]
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
        if self._currentTrackId < 0 or not self._ensure_player():
            return False
        try:
            self._player.play()
        except Exception as exc:
            print(f"play exception: {exc}")
            return False
        self._isPlaying = True
        self.playbackStateChanged.emit(True)
        return True

    @pyqtSlot(result=bool)
    def pause(self):
        if not self._isPlaying or not self._ensure_player():
            return False
        try:
            self._player.pause()
        except Exception as exc:
            print(f"pause exception: {exc}")
            return False
        self._isPlaying = False
        self.playbackStateChanged.emit(False)
        return True

    @pyqtSlot(result=bool)
    def togglePlayPause(self):
        if self._isPlaying:
            return self.pause()

        if self._currentTrackId < 0 and self._playlistModel.rowCount() > 0:
            first_track = self._playlistModel.asList()[0]
            first_id = int(first_track.get("id", -1))
            if first_id >= 0:
                return self.playPlaylistTrack(first_id)

        return self.play()

    @pyqtSlot(result=bool)
    def previousTrack(self):
        if self._currentTrackId < 0:
            return False
        ids = [int(track.get("id", -1)) for track in self._playlistModel.asList()]
        try:
            index = ids.index(self._currentTrackId)
        except ValueError:
            return False
        if index <= 0:
            return False
        return self.playPlaylistTrack(ids[index - 1])

    @pyqtSlot(result=bool)
    def nextTrack(self):
        if self._currentTrackId < 0:
            return False
        ids = [int(track.get("id", -1)) for track in self._playlistModel.asList()]
        try:
            index = ids.index(self._currentTrackId)
        except ValueError:
            return False
        if index >= len(ids) - 1:
            return False
        return self.playPlaylistTrack(ids[index + 1])

    @pyqtSlot(int, result=bool)
    def seek(self, position_ms):
        if self._player is None or not self._ensure_player():
            return False
        if not hasattr(self._player, "setPosition"):
            return False
        try:
            self._player.setPosition(int(position_ms))
            self._playbackPosition = int(position_ms)
            self.playbackPositionChanged.emit()
            return True
        except Exception as exc:
            print(f"seek exception: {exc}")
            return False

    @pyqtSlot(result="QVariantList")
    def getSavedPlaylists(self):
        return self.djData.getListOfMilongas()

    @pyqtSlot(str, result="QVariantList")
    def getM3u8Playlists(self, playlist_directory):
        if not playlist_directory:
            return []
        try:
            if not os.path.isdir(playlist_directory):
                return []
            pattern = os.path.join(playlist_directory, "*.m3u8")
            playlist_files = [os.path.basename(path) for path in glob.glob(pattern)]
            return sorted(playlist_files)
        except Exception:
            return []

    @pyqtSlot(result="QVariantList")
    def getLibraryArtists(self):
        artists = {track.get("artist", "").strip() or "Unknown" for track in self._libraryModel.asList()}
        return [artist for artist in sorted(artists) if artist is not None]

    @pyqtSlot(result="QVariantList")
    def getLibraryAlbums(self):
        albums = {track.get("album", "").strip() or "Unknown" for track in self._libraryModel.asList()}
        return [album for album in sorted(albums) if album is not None]

    @pyqtSlot(result="QVariantList")
    def getLibraryGenres(self):
        genres = {track.get("genre", "").strip() or "Unknown" for track in self._libraryModel.asList()}
        return [genre for genre in sorted(genres) if genre is not None]

    @pyqtSlot(result="QVariantList")
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

    @pyqtSlot(bool, result=bool)
    def setLiveSession(self, enabled):
        self._isLiveSession = bool(enabled)
        return True

    @pyqtSlot(result=int)
    def playlistTotalDuration(self):
        total = 0
        for track in self._playlistModel.asList():
            try:
                total += int(round(float(track.get("duration", 0))))
            except Exception:
                continue
        return total

    @pyqtSlot(result=str)
    def appTitle(self):
        return "ttvttm"

    @pyqtSlot(result=str)
    def appVersion(self):
        return "0.1.0"

    @pyqtSlot(result=str)
    def liveOutputName(self):
        return "Default"

    @pyqtSlot(result=int)
    def liveVolume(self):
        return 100
