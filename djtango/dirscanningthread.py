# -*- coding: utf-8 -*-

import logging
import time
from random import randint
from djtango import utils
from djtango.tangosong import TangoSong
from djtango.dirsong import dirSong
from djtango.data import djDataConnection
from djtango.qt_compat import QMutex, pyqtSignal, QObject, pyqtSlot
#from PyQt5.QtCore import pyqtSignal

logger = logging.getLogger(__name__)


class dirScan(QObject):
	scanned = pyqtSignal(list,list)
	def __init__(self, tangoList, djData, parent = None):
		super(dirScan, self).__init__(parent)
		logger.debug("dirScan worker thread initialized")
		self.tangoList = tangoList
		self.emitted = False
		self.running = True
		self.djData = djData

	def workOut(self):
		# logger.debug("running DirScanningThread")
		while self.running:
			# logger.debug("SCANNING !")
			if not self.emitted:
				newfiles = self.tangoList.checkNewFiles()
				if newfiles:
					# logger.debug("Nb of new tango: %s", len(newfiles))
					datas = []
					# firstID = 0
					tangos = []
					for path in newfiles:
						logger.debug("Processing new tango file: %s", path)
						insertedtango = TangoSong(path, 0, True)
						insertedID = self.djData.insertTango(insertedtango)
						# if firstID == 0:
						#	firstID = insertedID
						insertedtango.ID = insertedID
						# logger.debug("ID: %s", insertedID)
						tangos.append(insertedtango)
						data = insertedtango.list()
						datas.append(data)
					logger.debug("Inserted %s newly discovered tango entries into the database", len(datas))
					self.scanned.emit(datas, tangos)
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
	def updateTangoList(self, tangoList):
		self.tangoList = tangoList

	def stop(self):
		logger.debug("Stopping dirScan worker thread")
		self.running = False
	@pyqtSlot(bool)
	def setUpdatingStatus(self, status ):
		self.emitted = status

	@pyqtSlot(dirSong)
	def updateTangoList(self, tangoList):
		self.tangoList = tangoList

    


