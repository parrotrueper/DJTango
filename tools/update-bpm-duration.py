#!/usr/bin/python3
# -*- coding:Utf-8 -*-


import os

from pydub import AudioSegment

from ttvttm.data import djDataConnection

#import gi

djHome = os.path.join(os.path.expanduser("~"), ".ttvttm")
djData = djDataConnection(djHome)
trackList = djData.getAllTracks()

TYPE=djData.getTrackTypeList()
count = 0
countNU = 0
tagedFileNB =0
lenght = len(trackList)
for track in trackList:
	count+=1
	print(str(track.ID)+" - "+track.path)
	
	if not os.path.isfile(track.path):
		djData.deleteTango(track.ID)
	else :
	
		countNU+=1
		ext = os.path.splitext(track.path)[1][1:]

		try:
			song = AudioSegment.from_file(track.path, ext.lower())

			track.duration=len(song)
			#print(track.duration)
			djData.updateTrack(track)
		except Exception as err:
			print(err)
			pass

	#if count>200: sys.exit(0)
print("number of remaning file not tagged: "+str(countNU-tagedFileNB))



