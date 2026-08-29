#!/usr/bin/python3
# -*- coding:Utf-8 -*

import os
import re
import sys
import time
import unicodedata
import urllib

import bs4
from bs4 import BeautifulSoup
from colors import *

from ttvttm.data import djDataConnection

#listOfTango = []
djHome = os.path.join(os.path.expanduser("~"), ".ttvttm")
djData = djDataConnection(djHome)
TYPE = djData.getTrackTypeList()

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def getFormatedNb(nb):
	if (nb<1000 and nb>99):
		nb = " "+str(nb)
	elif (nb<100 and nb>9):
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

def getNumeFromType(val):
	return TYPE[val][1].upper()
	#for i in range (1, len(TYPE)):
	#	print(TYPE[i]);

def getProgress(progress, size, total, track):
	factor = progress/total
	endRange = round(size*factor)
	#print (factor)
	start = "   ["
	for i in range(0,endRange):
		start+="#"
	for i in range(0,size-endRange):
		start+="_"
	start+="]"
	start+=" - "+track.title+" - "+track.artist+" ("+str(track.year)+")"
	start+="                                                                  "
	sys.stdout.write(BLUE)
	print(start, end="\r", flush=True)
	sys.stdout.write(RESET)
	if factor == 1: print()


def getStatistics(tracks):
	
	print("counting ...")
	altCor = 0
	noMatching = 0
	matched = 0
	multiChoice = 0
	count = 0
	cnt = 0
	size = 25
	total = len(tracks)
	for track in tracks:
		cnt+=1
		getProgress(cnt, size, total, track)
		if track.type == 4 or track.type>5:
			altCor+=1
		else:
			if track.treated == 1:
				matched+=1
			else:
				rows = djData.existTangoInTangoDatabase(track)#if exist in el-recodo database
				if len(rows) == 0: #If we can't find this track in el-recodo database
					noMatching+=1
				elif len(rows) == 1 :
					matched+=1
				elif track.year < 10 or track.year>1990:
					multiChoice+=1
				else:
					matched+=1


	print("counting DONE")
	return [noMatching, matched, multiChoice, altCor]

def printResum(values):
	(noMatching, matched, multiChoice, altCor) = values
	print("\n-------------------------------")


	#altCor = noMatching-count
	total = altCor+noMatching+matched+multiChoice

	#altCor = getFormatedNb(altCor)
	#total = getFormatedNb(total)
	#multiChoice = getFormatedNb(multiChoice)

	print("# alt. cort.:\t"+getFormatedNb(altCor))
	print("# noMatch:\t"+getFormatedNb(noMatching))
	print("# matched:\t"+getFormatedNb(matched))
	print("# MultiChoice:\t"+getFormatedNb(multiChoice))
	print("\n-------------------------------")
	sys.stdout.write(GREEN)
	print("TOTAL: \t\t"+getFormatedNb(total))
	sys.stdout.write(RESET)


def getChoiceSelection(e):
	val = ""
	while True:
		try:
			val = input(e+": ")       
			if val =="quit": 
				val = -1
				break
			else:
				val = int(val)				

		except ValueError:
			print('You have to choos an interger or "quit" to quit the app')
			continue
		else: break 
	return val

def getLink():
	return input("Copy paste the link: ")

def askForNewField(track):
	print("will change some fields")
	acceptedFields = ["year","artist","title","singer","type","composer","author","album"]
	#print(vars(track))
	for field in acceptedFields:
		if field == "type":
			value = input(field+ " ["+str(getNumeFromType(getattr(track, field)))+"]: ")
		else:
			value = input(field+ " ["+str(getattr(track, field))+"]: ")
		if value != "":
			if field == "type": value = getTypeFromName(value)
			#print (value)
			setattr(track, field, value)

	#for key in vars(track):
	#	if key in acceptedFields:
	#		#print (key+ ' ['+str(getattr(track, key))+']: ')
	#		value = input(key+ ' ['+str(getattr(track, key))+']: ')
	#		if value != '':
	#			#print (value)
	#			setattr(track, key, value)
	return track

def playAndSearchTango(track):
	cmdvlc = 'vlc -q "'+track.path+'" &'
	cmdFirefox = ('firefox "https://www.el-recodo.com/music?T='+track.title+"&G=&O="+track.artist+'&C=&Dmin=&Dmax=&Cr=&Ar=&L=&lang=fr" &')
	cmdTangoDjAt = ('firefox "https://www.track-dj.at/database/index.htm?titlesearch='+track.title+"&albumsearch=&yearsearch=&orquestrasearch="+track.artist+'&advsearch=Search"')
	os.system("killall vlc")
	os.system("wmctrl -a firefox")
	os.system("wmctrl -a nightly")
	time.sleep(0.5)
	os.system("xdotool key Alt+2")
	time.sleep(0.5)
	os.system("xdotool key Ctrl+w")
	time.sleep(0.5)
	os.system("xdotool key Ctrl+w")
	time.sleep(0.5)
	os.system(cmdFirefox)
	os.system(cmdTangoDjAt)

	
	os.system(cmdvlc)

def getSongsFromPageFromTangoDj(page, url):
	soup = BeautifulSoup(page, "lxml")
	#print (soup)
	table = soup. find("table",{"id":"searchresult"})
	mytrs = table.findAll("tr")
	#print (mytrs)
	songs =[]

	for tr in mytrs:
		tds = tr.findAll("td")
		if (len(tds) > 5):
			song = []
			if (len(tds[7].next.split("-"))>1):
				song.append(tds[7].next.split("-")[0])#year
				song.append(tds[7].next.split("-")[1])#month
				song.append(tds[7].next.split("-")[2])#day
			else:
				song.append(0)#year
				song.append(0)#month
				song.append(0)#day

			song.append(tds[6].a.next.split("con")[0])#orchestra
			
			song.append("")
			song.append(tds[4].a.next)#title,
			song.append("")

			if len(tds[6].a.next.split("con"))>1: #singer
				song.append(tds[6].a.next.split("con")[1])
			else:
				song.append("None")
			
			genre = "Unnkown"
			if tds[5].next.find("Track")>-1:
				genre = "Track"
			if tds[5].next.find("Milonga")>-1:
				genre = "Milonga"
			if tds[5].next.find("Nuevo")>-1:
				genre = "Track Nuevo"
			if tds[5].next.find("Vals")>-1:
				genre = "Vals"

			song.append(genre)#genre
			song.append(tds[13].next)
			song.append(tds[14].next)
			song.append(tds[11].a.next)
			songs.append(song)

	return songs



def getSongsFromPageFromElRecodo(page, url):
	soup = BeautifulSoup(page, "lxml")
	myul = soup.find("ul", {"class": "pagination"})
	#print()
	#print(url)
	pageNb = 0
	songs =[]
	if myul != None:
		mylis = myul.findAll("li")
		if "ENREGISTREMENTS" in mylis[len(mylis)-2].a.next : 
			pageNb = 1
		else:
			#print (mylis[len(mylis)-2].a)
			pageNb = int(mylis[len(mylis)-2].a.next)

		#print('pageNB: '+str(pageNb))
		curPage = 1
		while curPage <= pageNb:
			#print("reading page " +str(curPage))
			mytrs = soup.findAll("tr", {"class": "small"})
			for tr in mytrs:
				song = []
				tds = tr.findAll("td")
				#print(str(tds[4].a.next)+' | '+str(tds[5].next))
				song = [
				tds[1].a.next,
				int(tds[1].a.span.next.split("-")[1]),#month
				int(tds[1].a.span.next.split("-")[2]),#day
				tds[2].a.next,
				remove_accents(tds[2].a.next).lower(),
				tds[3].a.next,
				remove_accents(tds[3].a.next).lower(),
				tds[4].a.next,
				tds[5].next+tds[5].span.next,
				tds[6].a.next]

				if isinstance(tds[4].a.next, bs4.element.Tag):
					song[7] =""
				if not isinstance(tds[7].a.next, bs4.element.Tag):
					song.append(tds[7].a.next)
				else:
 					song.append("?")
				
				for i, curVal in enumerate(song):
					if isinstance(curVal, bs4.element.Tag):
						song[i] = ""
				#print(song)
				song.append("")

				songs.append(song)

			curPage+=1
			url = orchestra = re.sub(r"P=\d+","P="+str(curPage), url)
			#print(url)
			fp = urllib.request.urlopen(url)
			soup = BeautifulSoup(fp.read(), "lxml")
	#else:
		#print("Pas d'enregistrement pour "+url)
	#exit(0);
	return songs

def updateTrack2(track, song):
	if song is not None:
		track.year = song[0]
		track.artist = song[3]
		track.title = song[5]
		track.singer = song[7]
		#track.type = getTypeFromName(song[8])
		track.composer = song[9]
		track.author = song[10]
		#print(song[11])
		if track.album == "Unnkown":
			track.album = song[11]
		track.treated = 1
		#print(track.listUpdateDB())
		djData.updateTrack(track)
		os.system("clear")

def updateTrack(track, row):
	if track.treated == 0:
		for i in range (0, len(row)):
			if(row[i] == "?" or row[i] == "" or row[i] == " "):
				row[i] = "Unnkown"
			track.year = row[7]
			track.singer = row[10]
			track.composer = row[11]
			track.author = row[12]
			track.treated = 1
			#djData.updateTrack(track)
			if track.type == 5:
				track.type = getTypeFromName(row[6])

			djData.updateTrack(track)

def verifyFromLink(track, shouldAskCorrection, toprint):
	title = remove_accents(track.title.replace(" ", "+"))
	#print (title)
	artist = remove_accents(track.artist.replace(" ", "+"))
	#print (artist)
	#exit(0)
	linkElRecodo = "https://www.el-recodo.com/music?T="+title+"&G=&O="+artist+"&C=&Dmin=&Dmax=&Cr=&Ar=&L=&lang=fr"
	linkTangoDjAt = "https://www.track-dj.at/database/index.htm?titlesearch="+title+"&albumsearch=&yearsearch=&orquestrasearch="+artist+"&advsearch=Search"
	#print (linkElRecodo)
	#print (linkTangoDjAt)
	songElRecodo = []
	songTangoDjAt = []
	try:
		fp = urllib.request.urlopen(linkElRecodo)
		songElRecodo = getSongsFromPageFromElRecodo(fp.read(), linkElRecodo)
		fp = urllib.request.urlopen(linkTangoDjAt)
		songTangoDjAt = getSongsFromPageFromTangoDj(fp.read(),linkTangoDjAt)
	except urllib.error.HTTPError:
		print(linkElRecodo)
		print(linkTangoDjAt)
		#pass
		pass
	except UnicodeEncodeError:
		pass
	if len(songElRecodo)>0 or len(songTangoDjAt)>0 and (len(songElRecodo) !=1 and len(songTangoDjAt) !=1):
		#os.system('clear')
		sys.stdout.write(RED)
		print(toprint)
		sys.stdout.write(RESET)
		#print(len(songElRecodo))
		#print(len(songTangoDjAt))


	if (len(songElRecodo) == 1):
		updateTrack2(track, songElRecodo[0])
	elif (len(songTangoDjAt) == 1):
		updateTrack2(track, songTangoDjAt[0])
	elif len(songElRecodo) > 1 and shouldAskCorrection:
		playAndSearchTango(track)
		print(track.listUpdateDB())
		for i in range (0, len(songElRecodo)):
			print(str(i+1)+" - "+str(songElRecodo[i] ))
		val = int(input("Which one is the one: "))
		song = songElRecodo[val-1]
		updateTrack2(track, song)
	elif len(songTangoDjAt) > 1 and shouldAskCorrection:
		playAndSearchTango(track)
		print(track.listUpdateDB())
		#print('we are in songTangoDjAt loop')
		#print('size of songTangoDjAt: '+str(len(songTangoDjAt)))
		for i in range (0, len(songTangoDjAt)):
			print(str(i+1)+" - "+str(songTangoDjAt[i] ))
		val = int(input("Which one is the one: "))
		song = songTangoDjAt[val-1]
		updateTrack2(track, song)


	#print(len(songTangoDjAt))
	#exit(0)


	ret = False
	if len(songElRecodo)>0 or len(songTangoDjAt)>0:
		ret = True 
	return ret

#**********************************************
# MAIN
#**********************************************

#exit(0)
#print(sys.argv)
ARGV = sys.argv
#print(ARGV)
if ARGV[1] == "true":
	shouldAskCorrection = True
else:
	shouldAskCorrection = False

#print (shouldAskCorrection)
listOfTango = djData.getAllTracks()
noMatching = 0
matched = 0
multiChoice = 0
treatedMultiChoice = 0
treatedUnique = 0
altCort =0
totcount = 0
noMatched = []
stats = [0,0,0,0,0]

os.system("clear") #initialize the screen
if shouldAskCorrection:
	stats = getStatistics(listOfTango)
	printResum(stats)

#printResum()
print("analyzing")
cnt = 0
size = 25
for track in listOfTango:
	#print (track.list())
	cnt+=1
	getProgress(cnt, size, len(listOfTango), track)
	
	#if cnt > 4: cnt = 0
	toprint = "\n"+"treated: "+str(treatedUnique)+" , remaining: "+str(stats[0]-noMatching-treatedUnique)
	if track.list()[5]<4 and track.treated == 0 and verifyFromLink(track, shouldAskCorrection, toprint):
		treatedUnique+=1
		matched+=1
	elif track.list()[5]<4 and track.treated == 0 :
		totcount+=1
		rows = djData.existTangoInTangoDatabase(track)#if exist in el-recodo database
		#print(rows)
		if len(rows) == 0: #If we can't find this track in el-recodo database

			#print('will clear')
			
			if track.treated ==0 and shouldAskCorrection :
				print()
				sys.stdout.write(RED)
				print(toprint)
				sys.stdout.write(RESET)
			
			
				print(track.listUpdateDB())
				playAndSearchTango(track)			
				print()
				print (str(0)+" - Pass to the next, but will continue to show it")
				print (str(1)+" - Pass to the next, but will consider it as treated")
				print (str(2)+" - Correct the field")
				print (str(3)+" - Give me the link on el-recodo where I can find the infos")

				print()
				time.sleep(2)
				val = getChoiceSelection("select an action")
				if val == -1:
					os.system("killall vlc")
					exit(0)
				elif val == 0:
					print("do nothing")
					noMatching+=1
				elif val == 1:
					track.treated = 1
					treatedUnique+=1
					djData.updateTrack(track)
				elif val == 2:
					track = askForNewField(track)
					print(track.listUpdateDB())
					treatedUnique+=1
					track.treated = 1
					djData.updateTrack(track)
				elif val == 3:
					link = getLink()
					fp = urllib.request.urlopen(link)
					songs = []
					if (link.find("el-recodo")>-1):
						#print('I will get the data from el-recodo')
						songs = getSongsFromPageFromElRecodo(fp.read(), link)
					elif (link.find("track-dj.at")>-1):
						#print('I will get the data from track-dj')
						songs = getSongsFromPageFromTangoDj(fp.read(), link)

					#print(songs)
					#exit(0)
					
					
					#print(songs)
					if (len(songs) == 1):
						song = songs[0]
					elif (len(songs)>1):
						for i in range (0, len(songs)):
							print(str(i+1)+" - "+str(songs[i] ))
						val = int(input("Which one is the one: "))
						song = songs[val-1]

					updateTrack2(track, song)
					print("will clear")
					os.system( "clear" )
				#noMatched.append(track)

			else:
				noMatching+=1
		elif len(rows) == 1: #if only one track is corresponding to el-recodo database (better case)
			matched+=1
			row = list(rows[0])
			updateTrack(track, row)


		elif track.treated == 0 and track.year<10: #if we have more than one track
			if shouldAskCorrection:
				sys.stdout.write(RED)
				print("\n"+"treated: "+str(treatedMultiChoice)+" , remaining: "+str(stats[2]-treatedMultiChoice))
				sys.stdout.write(RESET)
				count = 0
				print (str(count)+" - IT'S AN OTHER VERSION GOT TO THE NEXT ONE (YEAR WILL BE SET TO 11)")
				print("      ...............    ")
				for row in rows:
					count+=1
					print (str(count)+" - "+str(row))
				print("      ...............    ")
				print (str(22)+" - Change some fields")
				print (str(23)+" - Wrong annotation to be corrected later (will add TO_BE_CORRECTED to title and artist)")
				#print ("multiple choice, we will to have to treat this correctly");
			
				playAndSearchTango(track)		
				print()
				time.sleep(5)
				val = getChoiceSelection("Which one correspond ?")

				if val == -1:
					shouldAskCorrection = False
				elif val >0 and val < 22:
					row = list(rows[val-1])
					print(row)
					#exit(0)
					for i in range (0, len(row)):
						if(row[i] == "?" or row[i] == "" or row[i] == " "):
							#print(row[i])
							row[i] = "Unnkown"
						track.year = row[7]
						track.singer = row[10]
						track.composer = row[11]
						track.author = row[12]
					if track.type == 5:
						track.type = getTypeFromName(row[6])
					djData.updateTrack(track)
				elif val == 22:
					track = askForNewField(track)
					print(track.listUpdateDB())
					djData.updateTrack(track)
				elif val ==23:
					track.treated = 1
					track.artist = track.artist+"_TO_BE_CORRECTED"
					track.title = track.title+"_TO_BE_CORRECTED"
					#print(track.listUpdateDB())
					djData.updateTrack(track)
					#exit(0)
				else:
					track.treated = 1 # in this case, we will not ask for this track, until the value is <10 again
					djData.updateTrack(track)
				treatedMultiChoice+=1
				multiChoice-=1
				matched+=1

			if shouldAskCorrection:
				os.system( "clear" )

			multiChoice+=1
		else: #more than one choice, but these tracks are matched
			#print (track.listUpdateDB())
			track.treated = 1
			djData.updateTrack(track)
			matched+=1
	elif track.type==4 or track.type>5:
		altCort+=1
	elif track.treated >0:
		matched+=1
	




		#for row in rows:
		#	print("\t - "+str(row[7]))

#count = 0
#fichier = open("./tobecorrected.csv", "w")
#for track in noMatched:
#	tList = track.list()
	#if tList[5] <4 and not (tList[3].lower() == 'miguel calo'):
	
#	if tList[5] <4 :
#		count+=1
		#row  = track.listUpdateDB()
		#print(track.listUpdateDB())
		#cmdFirefox = ('firefox "https://www.el-recodo.com/music?T='+row[0]+'&G=&O='+row[1]+'&C=&Dmin=&Dmax=&Cr=&Ar=&L=&lang=fr" &')
		#print (cmdFirefox)
		#print ('{0:10}  {1:30}  {2:30}  {3:2}'.format(str(tList[0]), tList[2].lower(), tList[3].lower(), tList[5]))
		#fichier.write("%s;%s;%s\n" % (str(tList[0]),tList[2].lower(),tList[3].lower()))
	
#fichier.close()

printResum([noMatching, matched, multiChoice, altCort])

