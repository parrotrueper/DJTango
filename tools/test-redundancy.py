#!/usr/bin/python3
# -*- coding:Utf-8 -*-

import os

from ttvttm.data import djDataConnection
from ttvttm.dirsong import dirSong

djhome = os.path.join(os.path.expanduser("~"), ".ttvttm")
djData = djDataConnection(djhome)

trackList = dirSong("/home/hoonakker/media/track-propres-HQ", False)
trackList.loadTangos(djData.getAllTracks())
fileOnHD = trackList.getListFromDir()
tracks ={}
for ID in trackList.tracks:
	#print (trackList.tracks[ID].path)
	tracks[trackList.tracks[ID].path] = ID

tmp = {}
for file in fileOnHD:
	if file in tracks and file in tmp:
		tmp[file]+=1
		print (tmp[file])
	else:
		tmp[file] = 1
		#print (tmp[file])

isredundancy  = False
for file in tmp:
	if tmp[file]>1:
		isredundancy = True
	#else:
	#	print(file+" "+str(tmp[file]))
		

if isredundancy:
	print("this file appear twice: "+file)
else:
	print ("No redundancy")


