# -*- coding: utf-8 -*-

import logging
import time
from random import randint
from djtango import utils
from djtango.tracksong import TrackSong
from djtango.dirsong import dirSong
from djtango.data import djDataConnection
from djtango.qt_compat import QMutex, pyqtSignal, QObject, pyqtSlot

logger = logging.getLogger(__name__)


class dirScan(QObject):
	scanned = pyqtSignal(list,list)
	def __init__(self, trackList, djData, parent = None):
		super(dirScan, self).__init__(parent)
		logger.debug("dirScan worker thread initialized")
		self.trackList = trackList
		self.emitted = False
		self.running = True
		self.djData = djData

	def workOut(self):
		# logger.debug("running DirScanningThread")
		while self.running:
			# logger.debug("SCANNING !")
			if not self.emitted:
				newfiles = self.trackList.checkNewFiles()
				if newfiles:
					logger.debug("Nb of new track: %s", len(newfiles))
					datas = []
					# firstID = 0
					tracks = []
					for path in newfiles:
						logger.debug("Processing new track file: %s", path)
						insertedtango = TrackSong(path, 0, True)
						insertedID = self.djData.insertTrack(insertedtango)
						insertedtango.ID = insertedID
						tracks.append(insertedtango)
						data = insertedtango.list()
						datas.append(data)
					logger.debug("Inserted %s newly discovered track entries into the database", len(datas))
					self.scanned.emit(datas, tracks)
			else:
				logger.debug("dirScan worker skipped this iteration because a scan is already active")

			for _ in range(100):
				if not self.running:
					break
				time.sleep(0.1)

	@pyqtSlot(bool)
	def setUpdatingStatus(self, status ):
		self.emitted = status

	@pyqtSlot(dirSong)
	def updateTangoList(self, trackList):
		self.trackList = trackList

	def stop(self):
		logger.debug("Stopping dirScan worker thread")
		self.running = False

