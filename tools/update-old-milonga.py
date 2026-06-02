#!/usr/bin/python3
# -*- coding:Utf-8 -*-

from djtango.data import djDataConnection
from djtango.dirsong import dirSong
import string, os, sys


#print ('Number of arguments:', len(sys.argv), 'arguments.')
#print ('Argument List:', str(sys.argv))
if len(sys.argv) < 3:
	print ("USAGE: "+sys.argv[0]+ "source-database destination-database")


djhome = os.path.join(os.path.expanduser("~"), ".djtango")
djDataSource = djDataConnection(djhome, sys.argv[1])
djDataDest = djDataConnection(djhome, sys.argv[2])
print (len(djDataDest.getAllTracks()))

milongas = djDataSource.getListOfMilongas()
for milonga in milongas:
	tracks = djDataSource.getTrackFromMilonga(milonga)
	newtangolist = []
	for track in tracks:

		searchedTangos = djDataDest.searchTrack(track)
		#newtango = searchedTangos[0]
		if len(searchedTangos) > 0:
			#newtango = searchedTangos[0];
			newtangolist.append(searchedTangos[0].ID)
	print("I should insert in milonga "+milonga+" -> "+str(len(newtangolist))+" tracks")
	djDataDest.saveMilonga(milonga, newtangolist)

	

#trackList = dirSong('/home/hoonakker/media/track-propres-HQ', False)
#trackList.loadTangos(djData.getAllTracks())
#missed = trackList.getMissedFiles()
#missedFiles = trackList.getMissedFiles(True)


#for miss in missed:
#	print (miss)
#for file in missedFiles:
#	print("FILE NOT IN DB: "+file)

#if len(missed) == 0 and len(missedFiles) == 0:
#	print("No missing file")
#else:
#print("nb of file in the database without a real file: "+str(len(missed)))
#print("nb of file wich are not in the database: "+str(len(missedFiles)))
