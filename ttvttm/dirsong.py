
import logging
import os
from shutil import move

from ttvttm import utils
from ttvttm.tracksong import TrackSong

logger = logging.getLogger(__name__)

class dirSong:
	def __init__(self, cpath = "", fill=False, progressBar = None, djData = None):
		self.songpath = os.path.abspath(cpath) if cpath else ""
		self.listFiles ={}
		self.tracks ={}
		self.progress = progressBar
		self.djData = djData
		self.excluded_paths = set()
		if self.djData is not None and hasattr(self.djData, "getExcludedPaths"):
			for path in self.djData.getExcludedPaths():
				self.excluded_paths.add(os.path.abspath(path))
		if fill:
			self.fillListOfFile()
	def _path_is_excluded(self, path):
		normalized = os.path.abspath(path)
		for excluded in self.excluded_paths:
			if normalized == excluded or normalized.startswith(excluded + os.sep):
				return True
		return False

	def _accepted_files(self):
		for root, _dirs, files in os.walk(self.songpath):
			if self._path_is_excluded(root):
				continue
			for filename in files:
				path = os.path.join(root, filename)
				if self._path_is_excluded(path):
					continue
				_, ext = os.path.splitext(filename)
				if ext.lower() in utils.acceptedFileExt:
					yield path

	def fillListOfFile(self):
		total = len(self.getListFromDir())
		count = 0
		if self.progress is not None:
			self.progress.setMaximum(total)
			self.progress.setMinimum(0)
			self.progress.forceShow()
		abort = False
		for path in self._accepted_files():
			count += 1
			if self.progress is not None:
				self.progress.setValue(count)
			self.listFiles[path] = count
			tmpTango = TrackSong(path, count, True)
			head, tail = os.path.split(tmpTango.path)
			if self.progress is not None:
				self.progress.setLabelText("Importing Tracks, please be patient...\n" + str(count) + "/" + str(total) + "\n" + tail)
			self.tracks[count] = tmpTango
			self.djData.insertTrack(tmpTango)
			if self.progress is not None and self.progress.wasCanceled():
				abort = True
				break
		if abort:
			logger.debug("Import aborted by user; database remains unchanged")

	def getListFromDir(self):
		accepted = 0
		ret = {}
		for path in self._accepted_files():
			accepted += 1
			ret[path] = accepted
		return ret

	def loadTangos(self, tracks):
		#check if the track is not arleady existing and do someting with it
		#countExistingPath = {}
		for t in tracks:
			self.tracks[t.ID] = t
			if t.path in self.listFiles:
				logger.debug("Duplicate track path detected: %s", t.path)
			self.listFiles[t.path] = t.ID

	def excludePath(self, path):
		normalized = os.path.abspath(path)
		if normalized not in self.excluded_paths:
			self.excluded_paths.add(normalized)
		for track_id in list(self.tracks.keys()):
			track = self.tracks[track_id]
			if self._path_is_excluded(track.path):
				self.removeTango(track_id)
		for file_path in list(self.listFiles.keys()):
			if self._path_is_excluded(file_path):
				del self.listFiles[file_path]

	def addTango(self, t):
		#check if the track is not arleady existing and do someting with it
		self.tracks[t.ID] = t
		self.listFiles[t.path] = t.ID

	def removeTango(self, ID):
		t = self.tracks[ID]
		del self.tracks[ID]
		del self.listFiles[t.path]

	def checkNewFiles(self):
		ret = []
		newfiles = self.getListFromDir()
		if not len(self.tracks) == len(newfiles):
			for key in newfiles.keys():
				if key not in self.listFiles:
					ret.append(key)
		return ret

	def getMissedFiles(self, realfiles = False):
		ret=[]
		if realfiles:
			files = self.getListFromDir()
			for file in files:
				if file in self.listFiles:
					pass
				else:
					ret.append(file)
		else:
			for i in self.tracks:
				track = self.tracks[i]
				if not os.path.isfile(track.path):
					ret.append(track.path)
				

		
		return ret

# this function will take a track and verify if the naming correspond to the norm and if the folders are corrects.
# if not, it will normalize it
# root is the root folder where track are stored
	def normalizeTango(self, Tid, TYPE):
		track = self.tracks[Tid]
		filename, file_extension = os.path.splitext(track.path)
		name = str(track.year)+"-"+utils.removeOddCaracters(track.title)+"-"+utils.remove_accents(track.artist).upper()+"-"+utils.remove_accents(track.album).upper()+"-"+TYPE[track.type][1].upper()+file_extension

		name = utils.remvoveSlash(name) #be sure that no more slash are in the filename

		if track.type == 4:
			rep = os.path.join(self.songpath, "CORTINA")
		elif track.type < 4:
			rep = os.path.join(self.songpath, "TANGO", utils.remove_accents(track.artist).upper())
		elif track.type >5 :
			rep = os.path.join(self.songpath, "ALTERNATIF", utils.remove_accents(track.artist).upper())
		else:
			rep = os.path.join(self.songpath, "UNKNOWN")

		if not os.path.isdir(rep):
			os.makedirs(rep)

		if track.title == "Unknown" and track.artist == "Unknown":
			logger.debug("Normalization skipped because track metadata is unknown for file: %s", track.path)
		else:
			count = 2 
			while os.path.isfile(os.path.join(rep, name)):
				name = str(track.year)+"-"+utils.removeOddCaracters(track.title)+"_"+str(count)+"-"+utils.remove_accents(track.artist).upper()+"-"+utils.remove_accents(track.album).upper()+"-"+TYPE[track.type][1].upper()+file_extension
				name = utils.remvoveSlash(name) #be sure that no more slash are in the filename
				count+=1
			if track.path in self.listFiles: 
				del(self.listFiles[track.path])
			else: 
				logger.debug("Normalization path not found in listFiles: %s", track.path)

			new_path = os.path.join(rep, name)
			move(track.path, new_path)

			logger.debug("Normalized track ID %s path to %s", Tid, new_path)
			self.tracks[Tid].path = new_path
			self.tracks[Tid].titleFields()
			self.listFiles[new_path] = track.ID


	#will remove the empty dir
	def checkEmptyDir(self):
		for root, _dirs, files in os.walk(self.songpath):
			for file in files:
				filename, file_extension = os.path.splitext(file)
				if file_extension.lower() not in utils.acceptedFileExt:
					os.remove(os.path.join(root, file))
			try:
				os.rmdir(root)
			except OSError:
				pass

