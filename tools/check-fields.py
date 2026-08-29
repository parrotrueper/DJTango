#!/usr/bin/python3
# -*- coding:Utf-8 -*

import os

from ttvttm.data import djDataConnection

#listOfTango = []
djHome = os.path.join(os.path.expanduser("~"), ".ttvttm")
djData = djDataConnection(djHome)
TYPE = djData.getTrackTypeList()


def getFormatedNb(nb):
	if (nb<1000):
		nb = " "+str(nb)
	elif (nb<100):
		nb = "  "+str(nb)
	elif (nb<10):
		nb = "   "+str(nb)
	else:
		nb = str(nb)

	return nb

def getTypeFromName(name):
	ret = 5
	for i in range (1, len(TYPE)):
		#print(name+" is equal to "+TYPE[i][1].upper())
		if TYPE[i][1].upper() == name:
			ret = i
	return ret


#trackInDB = djData.getAllTangInTangoDatabase()

listOfTango = djData.getAllTracks()
noMatching = 0
matched = 0
multiChoice = 0
noMatched = []


for track in listOfTango:
	#print (track.list())
	rows = djData.existTangoInTangoDatabase(track)#if exist in el-recodo database
	#print(rows)
	if len(rows) == 0: #If we can't find this track in el-recodo database
		#print(track.listUpdateDB())
		noMatching+=1
		noMatched.append(track)
	elif len(rows) == 1: #if only one track is corresponding to el-recodo database (better case)
		matched+=1
		row = list(rows[0])
		#print(row)
		if track.year < 10 or track.year>1990:
		#if track.year >=0:
			for i in range (0, len(row)):
			#print(row[i])
				if(row[i] == "?" or row[i] == "" or row[i] == " "):
					row[i] = "Unnkown"
			
			#print(track.listUpdateDB())
			#print ("will update date, composer, singer")
			#print("row: ")
			#print(rows[0])
			track.year = row[7]
			track.singer = row[10]
			track.composer = row[11]
			track.author = row[12]
			#print ("track modifié : "+str(track.listUpdateDB()))
			#print()
			djData.updateTrack(track)
		if track.type == 5:
			track.type = getTypeFromName(row[6])
			#print(row[6]+" -> "+str(getTypeFromName(row[6])))

			djData.updateTrack(track)


	else: #if we have more than one track
		#print (track.title+" | "+track.artist)
		#print(rows)
		#for row in rows:
		#	print (row)
		#print ("multiple choice, we will to have to treat this correctly");
		multiChoice+=1

		#for row in rows:
		#	print("\t - "+str(row[7]))

count = 0
fichier = open("./tobecorrected.csv", "w")
for track in noMatched:
	tList = track.list()
	#if tList[5] <4 and not (tList[3].lower() == 'miguel calo'):
	
	if tList[5] <4 :
		count+=1
		print(track.listUpdateDB())
		#print ('{0:10}  {1:30}  {2:30}  {3:2}'.format(str(tList[0]), tList[2].lower(), tList[3].lower(), tList[5]))
		fichier.write("%s;%s;%s\n" % (str(tList[0]),tList[2].lower(),tList[3].lower()))
	
fichier.close()

print("\n-------------------------------")


altCor = noMatching-count
total = altCor+count+matched+multiChoice

altCor = getFormatedNb(altCor)
total = getFormatedNb(total)
multiChoice = getFormatedNb(multiChoice)

print("#alt. cort.:\t"+altCor)
print("#noMatch:\t"+str(count))
print("#Corrected:\t"+str(matched))
print("#MultiChoice:\t"+multiChoice)
print("----------------------------------")
print("TOTAL: \t\t"+total)

#print ("\n"+str(noMatching-count)+" alternatif or cortina "+ str(count)+" noMaching and "+str(matched)+" matched on "+str(noMatching+matched))

