#!/usr/bin/python3
# -*- coding:Utf-8 -*


from djtango.data import djDataConnection
import unicodedata, re, os
p = re.compile('(\s\(2\)| \(3\)| \(4\)| \(5\))')
djhome = os.path.join(os.path.expanduser("~"), ".djtango")

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def normalize(track):
	track = list(track)
	track[1] = remove_accents(track[1]).lower()
	track[2] = remove_accents(track[2]).lower()

	track[1] = p.sub('', track[1]) 
	track[2] = p.sub('', track[2]) 
	
	#djData.updateTitleArtistInTangoDatabase(track[0], track[1], track[2])

	print (str(track[0]) +" "+track[1]+" "+track[2])
	return(track)


data = djDataConnection(djhome)
tracks = data.getAllTangInTangoDatabase()

for track in tracks:
	track = normalize(track)
	data.updateTitleArtistInTangoDatabase(track[0], track[1], track[2])