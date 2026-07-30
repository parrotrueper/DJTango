# -*- coding:Utf-8 -*-
import unicodedata

acceptedFileExt={".mp3", ".flac", ".wav", ".aiff", ".ogg"}


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def remvoveSlash(input_str):
	output = input_str.replace("/", "-")
	return output

def removeOddCaracters(input_str):
    output = remvoveSlash(input_str)
    output = output.replace(":", "")
    output = output.replace(".", "")
    return output

def msecToms(msec):
    if type(msec) is not float and type(msec) is not int:
        return msec  # we assume that the value is already a string set to the right value
    m, s = (0, 0)
    if msec >= 0:
        sec = int(msec / 1000)
        q, s = divmod(sec, 60)
        h, m = divmod(q, 60)
    return f"{m:02d}:{s:02d}"

def msecTohms(msec):
    if type(msec) is not float and type(msec) is not int:
        msec = 0
    h, m, s = (0, 0, 0)
    if msec >= 0:
        sec = int(msec / 1000)
        q, s = divmod(sec, 60)
        h, m = divmod(q, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def msecToHouMin(msec):
    if type(msec) is not float and type(msec) is not int:
        msec = 0
    h, m = (0, 0)
    if msec >= 0:
        sec = int(msec / 1000)
        q, s = divmod(sec, 60)
        h, m = divmod(q, 60)
    return f"{h:d} h {m:02d} min"


