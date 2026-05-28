# -*- coding: utf-8 -*-
# TODO ajouter les liseur et ecrivain de tag pour tous les type de fichiers traités.
# TODO - ajouter compositeur (et pas seulement auteur)
# TODO - ajouter l'extraction du bpm pour chaque chanson (l'affichier éventuellement)

import logging
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
import os
import string
from djtango import utils

logger = logging.getLogger(__name__)


class TangoSong:
	def __init__(self, path, ID=0, extractTag = False):
		self.ID = ID
		self.path=path
		self.type=5
		self.artist='Unknown'
		self.title='Unknown'
		self.album='Unknown'
		self.year=0
		self.author = 'Unknown'
		self.duration = 0
		self.bpmHuman = 0
		self.bpmFromFile = 0
		self.tstart = 0
		self.tend = 0
		self.composer = 'Unknown'
		self.author = 'Unknown'
		self.singer = 'Unknown'
		self.treated = 0
		#print (EasyID3.valid_keys.keys())
		#self.list = []
		
		#TODO, replace this by a function that extract tag according to the file type (mp3, flac, aiff, wave  etc)
		if extractTag:
			self.extractAnyTag()
		#if extractTag:
			#self.extractID3Tag()

	def titleFields(self):
		self.artist = self.artist.title()
		self.title = self.title.title()
		self.album = self.album.title()
		if self.author:
			self.author = self.author.title()
		else:
			self.author = 'Unknown'.title()
		#self.author = self.author.title()	

	def extractAnyTag(self):
		name, ext = os.path.splitext(self.path)
		if not os.path.isfile(self.path):
			logger.debug("Missing audio file: %s", self.path)
			return

		ext = ext.lower()
		if ext not in utils.acceptedFileExt:
			logger.debug("Unsupported audio file extension: %s", ext)
			return

		if ext == '.mp3':
			self.extractID3Tag()
		elif ext == '.flac':
			try:
				audio = FLAC(self.path)
				self.extractTags(audio)
			except Exception as err:
				logger.debug("Unable to read FLAC metadata for %s: %s", self.path, err)
		else:
			logger.debug("No tag extraction handler for accepted extension: %s", ext)

	def extractTags(self, audio):
		try:
			self.duration = audio.info.length
			self.title = string.capwords(audio["title"][0])
			self.artist = audio["artist"][0]
			self.album = audio["album"][0]
			self.type = audio["genre"][0] #TODO: map genre values to the database tango types
			self.year = int(audio["date"][0])
			self.author = audio["author"][0]
			self.bpmFromFile = audio["bpm"][0].replace(',','.')
		except Exception as err:
			logger.debug("Failed to extract FLAC metadata from %s: %s", self.path, err)

	def extractID3Tag(self):
		audio = None
		try:
			audio = MP3(self.path, ID3=EasyID3)
			self.duration = audio.info.length
			self.title = string.capwords(audio["title"][0])
			self.artist = audio["artist"][0]
			self.album = audio["album"][0]
			self.type = audio["genre"][0]
			self.year = int(audio["date"][0])
			self.author = audio["author"][0]
			self.bpmFromFile = audio['bpm'][0].replace(',','.')
		except Exception as err:
			logger.debug("Failed to extract ID3 metadata from %s: %s", self.path, err)

	def listDB(self):
		#print (self.type)
		return [self.path, self.title, self.artist, self.album, self.type, int(self.year) ]

	def list(self):
		bpm = 0
		if self.bpmHuman > 0:
			bpm = self.bpmHuman
		else:
			bpm = self.bpmFromFile
		return [self.ID, 0, self.title, self.artist, self.album, self.type, self.year, bpm, self.duration ]

	def sourceList(self):
		return [self.ID, self.title, self.artist, self.album, self.type]

	def listUpdateDB(self):
		return [self.title, self.artist, self.album, self.type, int(self.year), self.bpmHuman, self.bpmFromFile, self.duration, self.path, self.tstart, self.tend,self.author, self.singer, self.composer, self.treated, self.ID ]

	def	listUpdateDBTxt(self):
		return [self.title, self.artist, self.album, str(self.type), str(self.year), str(self.bpmHuman), str(self.bpmFromFile), str(self.duration), self.path, str(self.tstart), str(self.tend), self.author, self.singer, self.composer, str(self.treated), str(self.ID) ]


	def writeTags(self, TYPE):
		name, ext = os.path.splitext(self.path)
		if ext.lower() in utils.acceptedFileExt:
			if ext.lower() == '.mp3':
				try:
					audio = MP3(self.path, ID3=EasyID3)
					self.writeAnyTags(audio, TYPE)
				except Exception:
					logger.debug("Unable to write MP3 tags for %s", self.path)
			elif ext.lower() == '.flac':
				try:
					audio = FLAC(self.path)
					self.writeAnyTags(audio, TYPE)
				except Exception as err:
					logger.debug("Unable to write FLAC tags for %s: %s", self.path, err)
			else:
				logger.debug("Unsupported file type for tag writing: %s", ext)
				pass
		else:
			logger.debug("Tag write skipped for unsupported file extension %s in %s", ext, self.path)

	def writeAnyTags(self, audio, TYPE):
		"""Write generic audio tags for MP3 and FLAC audio objects."""
		try:
			audio['title'] = u"" + self.title
			audio['artist'] = [u"" + self.artist, u"" + self.singer]
			audio['album'] = u"" + self.album
			audio['genre'] = u"" + str(TYPE[self.type][1].title())
			audio['date'] = u"" + str(self.year)
			audio['author'] = u"" + self.author
			audio['composer'] = u"" + self.composer
			audio['length'] = u"" + str(self.duration)
			# audio['INVOLVEDPEOPLE'] = u"Singer:" + self.singer
			if self.bpmHuman > 0:
				audio['bpm'] = str(self.bpmHuman)
			else:
				audio['bpm'] = str(self.bpmFromFile)
			audio.save()
		except Exception as err:
			logger.debug("Unable to save audio tags for %s: %s", self.path, err)

	def writeID3Tag(self, audio, TYPE):
		# Writing ID3 tags for MP3 audio files
		try:
			audio['title'] = self.title
			audio['artist'] = self.artist
			audio['album'] = self.album
			audio['genre'] = str(TYPE[self.type][1].title())
			audio['date'] = str(self.year)
			audio['author'] = self.author
			if self.bpmHuman > 0:
				audio['bpm'] = self.bpmHuman
			else:
				audio['bpm'] = self.bpmFromFile
			audio.save()
		except Exception as err:
			logger.debug("Unable to write ID3 tags for %s: %s", self.path, err)
def toString(self):
		return " Path: "+str(self.path)+"\n Title: "+str(self.title)+"\n Album: "+str(self.album)+"\n Artist: "+str(self.artist)+"\n Author: "+str(self.author)+"\n Type: "+str(self.type)+"\n Année: "+str(self.year)+"\n bpmHuman: "+str(self.bpmHuman)+"\n bpmFromFile: "+str(self.bpmFromFile)+"\n Duration: "+str(self.duration)
