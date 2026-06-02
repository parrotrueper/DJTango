#!/usr/bin/python3
# -*- coding:Utf-8 -*-

# If we detect that singer, author or composer are null, we put Unknown
#
from djtango.data import djDataConnection
import string, os


djhome = os.path.join(os.path.expanduser("~"), ".djtango")

djData = djDataConnection(djhome)

Tracks = djData.getAllTracks()
#start = 3880
start = 0

#print (Tracks)
for track in Tracks:
	if track.ID > start:
		if not track.singer:
			track.singer = 'Unknown'
		if not track.author:
			track.author = 'Unknown'
		if not track.composer:
			track.composer = 'Unknown'
		


		#print (track.title+" "+str(track.ID)+" -> "+string.capwords(track.title))
		print (track.listUpdateDB())
		djData.updateTrack(track)
	
