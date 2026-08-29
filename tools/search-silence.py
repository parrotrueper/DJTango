#!/usr/bin/python3
# -*- coding:Utf-8 -*


# use pydub to detect the silences at the begining and the end of a song
# and save the real begining and end of each song in the database
import os

import pydub
from pydub import AudioSegment, silence

from ttvttm.data import djDataConnection


#p = re.compile('(\s\(2\)| \(3\)| \(4\)| \(5\))')
def backspace(n):
    # print((b'\x08').decode(), end='')     # use \x08 char to go back
    #clear()

    toPrint = ""
    for i in range(0,n):
    	toPrint+=" "
    print(toPrint, end="\r") 

def clear():

    os.system( "clear" )
    print()


djHome = os.path.join(os.path.expanduser("~"), ".ttvttm")

data = djDataConnection(djHome)
tracks = data.getAllTracks()
sizeBackSpace = 1000

startworkat = 5562
trackCount = 0
cont = 1
size = 3
#count = 0
for track in tracks:
	trackCount+=1
	#count+=1
	#sys.stdout.flush()

	#printing infos
	backspace(sizeBackSpace)
	percent = trackCount*100/len(tracks)
	start = "   ["+"%.0f" % percent+"% "
	for i in range(0,cont):
		start+="."
	for i in range(0,size-cont):
		start+=" "
	start+="] - "
	cont+=1
	if cont >size: cont = 1
	toPrint = start+str(track.ID) + " - "+track.path 
	print(toPrint, end="\r", flush=True) 
	sizeBackSpace = len (toPrint)


	file_extension = os.path.splitext(track.path)[1][1:]
	if track.ID >= startworkat:
		try:
			song = AudioSegment.from_file(track.path, file_extension.lower())
			silences = silence.detect_silence_start_end(song, 500, -56)
			if (len(silences) > 1):
				starttime = silences[0][1]
				stoptime = silences[len(silences)-1][0]
				track.tstart = starttime
				track.tend = stoptime
			elif len(silences) == 1:
				if (silences[0][0] == 0):
					track.tstart = silences[0][1]
					track.tend = len(song)
				elif silences[0][0] > len(song)*3/4:
					track.tstart = 0
					track.tend = silences[0][0]
			elif len(silences) == 0:
				track.tstart = 0
				track.tend = len(song)
			else:
				track.tstart = 0
				track.tend = 0
		
			track.duration = len(song)

			data.updateTrack(track)
		except FileNotFoundError:
			print (start+"We can not find the file of "+str(track.ID))
			backspace(sizeBackSpace)
			print(toPrint)
		except KeyboardInterrupt:
			backspace(sizeBackSpace)
			print(toPrint)
			print(start+"KeyboardInterrupt")
			exit(0)
		except pydub.exceptions.CouldntDecodeError:
			clear()
			backspace(sizeBackSpace)
			print(toPrint)
			print(start+"Can't Decode "+str(track.ID)+" "+track.path)
			
			pass
