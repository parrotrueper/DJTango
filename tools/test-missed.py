#!/usr/bin/python3
# -*- coding:Utf-8 -*-

import os

from ttvttm.data import djDataConnection
from ttvttm.dirsong import dirSong

djHome = os.path.join(os.path.expanduser("~"), ".ttvttm")
djData = djDataConnection(djHome)

trackList = dirSong("/home/hoonakker/media/track-propres-HQ", False)
trackList.loadTangos(djData.getAllTracks())
missed = trackList.getMissedFiles()
missedFiles = trackList.getMissedFiles(True)


for miss in missed:
	print (miss)
for file in missedFiles:
	print("FILE NOT IN DB: "+file)

#if len(missed) == 0 and len(missedFiles) == 0:
#	print("No missing file")
#else:
print("nb of file in the database without a real file: "+str(len(missed)))
print("nb of file wich are not in the database: "+str(len(missedFiles)))
