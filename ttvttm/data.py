
import logging
import os
import sqlite3

from ttvttm import utils
from ttvttm.tracksong import TrackSong

logger = logging.getLogger(__name__)


class djDataConnection:
    def __init__(self, home, databaseName="ttvttm.db"):
        if not os.path.isdir(home):
            os.makedirs(home)

        self.path = os.path.join(home, databaseName)
        self.pathTangoDatabase = os.path.join(home, "el-recodo.db")
        self.typeList = {}

        if os.path.exists(self.path):
            self.ensureTreatedColumn()
            self.ensureTangoTypeColumns()
            self.ensureExcludedPathsTable()

    def getDataFromSql(self, sqlfile):
        ret = ""
        base_dir = os.path.dirname(__file__)
        if not os.path.isabs(sqlfile):
            normalized = sqlfile.lstrip("./\\")
            if normalized.startswith("ttvttm" + os.sep):
                normalized = normalized[len("ttvttm" + os.sep):]
            sqlfile = os.path.join(base_dir, normalized)

        with open(sqlfile) as file:
            for line in file:
                ret += line

        return ret

    def createDatabase(self):
        open(self.path, "w").close()
        open(self.pathTangoDatabase, "w").close()

        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()

        # create the table
        script = self.getDataFromSql("sql/databaseCreation.sql")
        logger.debug(script)
        cursor.executescript(script)

        # fill the default table
        script = self.getDataFromSql("sql/databaseFill.sql")
        logger.debug(script)
        cursor.executescript(script)

        conn.commit()
        conn.close()

        self.ensureTreatedColumn()

    def ensureTreatedColumn(self):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tangos'")
        result = cursor.fetchone()
        if result is None:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tracks'")
            result = cursor.fetchone()
            if result is None:
                conn.close()
                return
            table_name = "tracks"
        else:
            table_name = "tangos"

        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        if "treated" not in columns:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN treated INTEGER DEFAULT 0")
            conn.commit()
        conn.close()

    def ensureTangoTypeColumns(self):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tangoType'")
        result = cursor.fetchone()
        if result is None:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trackType'")
            result = cursor.fetchone()
            if result is None:
                conn.close()
                return
            table_name = "trackType"
        else:
            table_name = "tangoType"

        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        for column in ("fontR", "fontG", "fontB", "fontT"):
            if column not in columns:
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column} INTEGER DEFAULT NULL")
        conn.commit()
        conn.close()

    def ensureExcludedPathsTable(self):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='excludedPaths'")
        if cursor.fetchone() is None:
            cursor.execute("CREATE TABLE excludedPaths (path TEXT PRIMARY KEY)")
            conn.commit()
        conn.close()

    def getExcludedPaths(self):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute("SELECT path FROM excludedPaths")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

    def addExcludedPath(self, path):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO excludedPaths (path) VALUES (?)", (path,))
        conn.commit()
        conn.close()

    def deleteTracksByPath(self, path):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        normalized_path = os.path.normpath(path)
        if os.path.isdir(normalized_path):
            like_pattern = normalized_path.rstrip(os.sep) + os.sep + "%"
            cursor.execute("DELETE FROM tangos WHERE tangopath = ? OR tangopath LIKE ?", (normalized_path, like_pattern))
        else:
            cursor.execute("DELETE FROM tangos WHERE tangopath = ?", (normalized_path,))
        conn.commit()
        conn.close()

    def existTangoInTangoDatabase(self, track):
        conn = sqlite3.connect(self.pathTangoDatabase)
        sql = "SELECT * FROM tracks WHERE norm_artist = ? and norm_title = ?"
        cursor = conn.cursor()
        cursor.execute(sql, (utils.remove_accents(track.artist).lower(), utils.remove_accents(track.title).lower(),))
        rows = cursor.fetchall()
        conn.commit()
        conn.close()

        return rows

    def updateTitleArtistInTangoDatabase(self, ID, artist, title):
        conn = sqlite3.connect(self.pathTangoDatabase)
        cursor = conn.cursor()

        sql = """
		UPDATE tracks 
		SET norm_artist = ?, norm_title = ?
		WHERE ID = ? """
        cursor.execute(sql, (artist, title, ID))

        conn.commit()
        conn.close()

    def getAllTangInTangoDatabase(self):
        conn = sqlite3.connect(self.pathTangoDatabase)
        cursor = conn.cursor()

        sql = "SELECT ID, artist, title FROM tracks"
        cursor.execute(sql)
        rows = cursor.fetchall()

        conn.commit()
        conn.close()

        return rows

    def updatePath(self, ID, newpath):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()

        sql = """
		UPDATE tangos
		SET tangopath = ?
		WHERE ID = ? """
        cursor.execute(sql, (newpath, ID))

        conn.commit()
        conn.close()

    def searchTrack(self, track):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()

        sql = "SELECT * FROM tangos WHERE title = ? and artist = ? and album = ? and genre = ?"

        cursor.execute(sql, (track.title, track.artist, track.album, track.type))
        rows = cursor.fetchall()

        conn.commit()
        conn.close()

        trackList = []
        for row in rows:
            ctango = TrackSong(row[1], row[0])
            ctango.title = row[2]
            ctango.artist = row[3]
            ctango.album = row[4]
            ctango.type = row[5]
            if ctango.type == 0:
                ctango.type = 5
            ctango.year = row[6]
            ctango.bpmHuman = row[7]
            ctango.bpmFromFile = row[8]
            ctango.duration = row[9]
            ctango.singer = row[10]
            ctango.composer = row[11]
            ctango.author = row[12]
            ctango.tstart = row[13]
            ctango.tend = row[14]
            ctango.treated = row[15] if len(row) > 15 else 0

            trackList.append(ctango)

        return trackList

    def existTango(self, track):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()

        sql = "SELECT * FROM tangos WHERE tangopath = ?"

        cursor.execute(sql, (track.path,))
        rows = cursor.fetchall()

        conn.commit()
        conn.close()

        if len(rows) > 0:
            return True
        else:
            return False

    def insertTrack(self, track):
        # don't insert a track who already exist
        if self.existTango(track):
            return

        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()

            if not self.typeList:
                sql = "SELECT * FROM tangoType"
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    self.typeList[row[1]] = row[0]

        if str(track.type).lower() in self.typeList:
            track.type = self.typeList[str(track.type).lower()]
        else:
            track.type = self.typeList["unknown"]
        sql = "INSERT INTO tangos (tangopath, title, artist, album, genre, year, bpmHuman, bpmFromFile, duration, singer, composer, author, tstart, tend, treated) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        cursor.execute(sql, track.listDB())
        ret = cursor.lastrowid
        conn.commit()
        conn.close()
        return ret

    def getAllTracks(self):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        sql = "SELECT * from tangos"
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()

        trackList = []
        for row in rows:
            ctango = TrackSong(row[1], row[0])
            ctango.title = row[2]
            ctango.artist = row[3]
            ctango.album = row[4]
            ctango.type = row[5]
            if ctango.type == 0:
                ctango.type = 5
            ctango.year = row[6]
            ctango.bpmHuman = row[7]
            ctango.bpmFromFile = row[8]
            ctango.duration = row[9]
            ctango.singer = row[10]
            ctango.composer = row[11]
            ctango.author = row[12]
            ctango.tstart = row[13]
            ctango.tend = row[14]
            ctango.treated = row[15] if len(row) > 15 else 0
            if ctango.duration == 0 and os.path.isfile(ctango.path):
                ctango.extractAnyTag()

            trackList.append(ctango)
        return trackList

    def getTrackFromMilonga(self, name):
        ID = self.getMilongaID(name)
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        sql = "SELECT * FROM tangos, Milonga_Tango WHERE tangos.ID = Milonga_Tango.idTango AND Milonga_Tango.IdMilonga = ?"
        cursor.execute(sql, (ID,))
        rows = cursor.fetchall()
        conn.close()

        trackList = []
        for row in rows:
            ctango = TrackSong(row[1], row[0])
            ctango.title = row[2]
            ctango.artist = row[3]
            ctango.album = row[4]
            ctango.type = row[5]
            if ctango.type == 0:
                ctango.type = 5
            ctango.year = row[6]
            ctango.bpmHuman = row[7]
            ctango.bpmFromFile = row[8]
            ctango.duration = row[9]
            ctango.singer = row[10]
            ctango.composer = row[11]
            ctango.author = row[12]
            ctango.tstart = row[13]
            ctango.tend = row[14]
            ctango.treated = row[15] if len(row) > 15 else 0
            if ctango.duration == 0 and os.path.isfile(ctango.path):
                ctango.extractAnyTag()
            trackList.append(ctango)
        return trackList

    def getTrackFromListID(self, listID):
        if not listID:
            return []

        placeholders = ",".join(["?"] * len(listID))
        sql = f"SELECT * FROM tangos WHERE ID IN ({placeholders})"

        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute(sql, tuple(listID))
        rows = cursor.fetchall()
        conn.close()

        trackList = []
        for row in rows:
            ctango = TrackSong(row[1], row[0])
            ctango.title = row[2]
            ctango.artist = row[3]
            ctango.album = row[4]
            ctango.type = row[5]
            if ctango.type == 0:
                ctango.type = 5
            ctango.year = row[6]
            ctango.bpmHuman = row[7]
            ctango.bpmFromFile = row[8]
            ctango.duration = row[9]
            ctango.singer = row[10]
            ctango.composer = row[11]
            ctango.author = row[12]
            ctango.tstart = row[13]
            ctango.tend = row[14]
            ctango.treated = row[15] if len(row) > 15 else 0
            if ctango.duration == 0 and os.path.isfile(ctango.path):
                ctango.extractAnyTag()

            trackList.append(ctango)
        return trackList

    def getTrackTypeList(self):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        typeList = {}
        sql = "SELECT * FROM tangoType"
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            typeList[row[0]] = row
        return typeList

    def updateTrack(self, track):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()

        sql = """
		UPDATE tangos 
		SET title = ?,
		artist = ?,
		album = ?,
		genre = ?,
		year = ?,
		bpmHuman = ?,
		bpmFromFile = ?,
		duration = ?,
		tangopath = ?,
		tstart = ?,
		tend = ?,
		author=?,
		singer=?, 
		composer = ?,
		treated = ?
		WHERE ID = ? """
        cursor.execute(sql, track.listUpdateDB())

        conn.commit()
        conn.close()

    def deleteTango(self, ID):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()

        logger.debug("Deleting track ID %s", ID)
        sql = """
		DELETE FROM tangos
		WHERE ID = ? """
        cursor.execute(sql, [ID, ])

        conn.commit()
        conn.close()

    def updateBPM(self, track):
        logger.debug("Updating BPM in database: %s", track.bpmHuman)
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()

        sql = """
		UPDATE tangos 
		SET bpmHuman = ?
		WHERE ID = ? """
        cursor.execute(sql, (track.bpmHuman, track.ID))

        conn.commit()
        conn.close()

    def updateProperties(self, durationFadOut, fadeOutTime, writeTagBox, normalize, TYPE):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()

        sql = """UPDATE preferences 
		SET timeCortina = ?,
		timeFadOut = ?,
		writeID3tag = ?,
		normalize = ? """

        cursor.execute(sql, (fadeOutTime / 1000, durationFadOut / 1000, writeTagBox, normalize))

        conn.commit()
        conn.close()

        # TODO : add a finction that update the type
        self.updateType(TYPE)

    def updateSongPath(self, songPath):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()

        sql = """UPDATE preferences 
		SET baseDir = ?"""

        cursor.execute(sql, (songPath,))

        conn.commit()
        conn.close()

    def updateType(self, TYPE):

        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tangoType'")
        if cursor.fetchone() is not None:
            table_name = "tangoType"
        else:
            table_name = "trackType"

        cursor.execute(f"DELETE FROM {table_name}")

        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        has_font_columns = all(column in columns for column in ("fontR", "fontG", "fontB", "fontT"))

        if has_font_columns:
            sql = f"INSERT INTO {table_name} (ID, type, R, G, B, T, fontR, fontG, fontB, fontT) VALUES(?,?,?,?,?,?,?,?,?,?)"
        else:
            sql = f"INSERT INTO {table_name} (ID, type, R, G, B, T) VALUES(?,?,?,?,?,?)"

        for nb in TYPE:
            type_entry = TYPE[nb]
            if has_font_columns:
                if len(type_entry) < 10:
                    type_entry = type_entry + (None, None, None, None)
                cursor.execute(sql, type_entry[:10])
            else:
                cursor.execute(sql, type_entry[:6])
            conn.commit()

        conn.close()

    def setNewSongAvailable(self, value):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        val = 1 if value else 0

        sql = "UPDATE preferences SET newSongAvailable = ?"
        cursor.execute(sql, (val,))

        conn.commit()
        conn.close()

    def getPreferences(self):
        ret = {}
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()

        sql = "SELECT * FROM preferences"
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            ret["path"] = row[0]
            ret["cortinaDuration"] = row[1]
            ret["fadeOutTime"] = row[2]
            ret["writeTag"] = row[3]
            ret["normalize"] = row[4]

        return ret

    def getMilongaID(self, name):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()

        sql = "SELECT * FROM Milonga WHERE Name = ?"
        cursor.execute(sql, (name,))
        rows = cursor.fetchall()

        conn.commit()
        conn.close()

        if len(rows) > 0:
            return rows[0][0]
        else:
            return 0

    def getListOfMilongas(self):
        ret = []
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()

        sql = "SELECT * FROM Milonga"
        cursor.execute(sql)
        rows = cursor.fetchall()

        conn.commit()
        conn.close()

        for row in reversed(rows):
            ret.append(row[1])
        return ret

    def deleteMilonga(self, milongaID=0, name=""):

        if milongaID == 0 and name == "":
            return False

        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()

        if milongaID == 0 and not name == "":
            milongaID = self.getMilongaID(name)

        sql = "DELETE FROM Milonga WHERE ID = ?"
        cursor.execute(sql, (milongaID,))

        sql = "DELETE FROM Milonga_TANGO WHERE IdMilonga = ?"
        cursor.execute(sql, (milongaID,))

        conn.commit()
        conn.close()
        return True

    def saveMilonga(self, name, trackList):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        milongaID = self.getMilongaID(name)
        if milongaID > 0:
            self.deleteMilonga(milongaID)

        sql = "INSERT INTO Milonga (Name) VALUES(?)"
        cursor.execute(sql, (name,))

        ID = cursor.lastrowid

        count = 1
        for trackId in trackList:
            sql = "INSERT INTO Milonga_Tango (IdMilonga, IdTango, Ord) VALUES(?,?,?)"
            cursor.execute(sql, (ID, trackId, count))
            count += 1

        conn.commit()
        conn.close()
