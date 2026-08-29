#!/usr/bin/python3
# -*- coding:Utf-8 -*-

import os
import string

from ttvttm.data import djDataConnection

djHome = os.path.join(os.path.expanduser("~"), ".ttvttm")

djData = djDataConnection(djHome)

Tracks = djData.getAllTracks()
#start = 3880
start = 3400

#print (Tracks)
for track in Tracks:
	if track.ID > start:
		track.title = string.capwords(track.title)
		track.artist = string.capwords(track.artist)

		#print (track.title+" "+str(track.ID)+" -> "+string.capwords(track.title))
		print (track.title)
		djData.updateTrack(track)
	
