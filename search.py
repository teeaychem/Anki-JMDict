import sqlite3
import re
from .util import containsKanji
from .classes.dicEntryC import *


def getEntryIDS(searchTerm, dicPath):
	# Search a string, return list of entryIDs
	dictionary = sqlite3.connect(dicPath)
	cur = dictionary.cursor()

	if containsKanji(searchTerm):
		entrySearch = cur.execute("SELECT idseq FROM Kanji WHERE text='%s'" % searchTerm)
	else:
		entrySearch = cur.execute("SELECT idseq FROM Kana WHERE text='%s'" % searchTerm)
	entryIDs = entrySearch.fetchall()
	# Get the actual id, rather than '(id,)'.
	# Things work fine without this apart from lookup by entryID
	return [id[0] for id in entryIDs]


def getKanjiKanaEntryIDS(kanji, kana, dicPath):
# Get entryIDs from kanji/kana.
# Assumed input is mainKanji and mainKana from card, so kanji arg may be kana hence test
	dictionary = sqlite3.connect(dicPath)
	cur = dictionary.cursor()

	if containsKanji(kanji):
		kanjiIDs = cur.execute("SELECT idseq FROM Kanji WHERE text='%s'" % kanji).fetchall()
		kanaIDs = cur.execute("SELECT idseq FROM Kana WHERE text='%s'" % kana).fetchall()
		common = [entryID for entryID in kanjiIDs if entryID in kanaIDs]
	else:
		common = cur.execute("SELECT idseq FROM Kana WHERE text='%s'" % kana).fetchall()

	return common


def makeDisplayEntriesList(dicEntryList):
# Make [entryID, displayString] list from entryIDs

	displayList = []

	for dicEntry in dicEntryList:

		mainKanji = dicEntry.getMainKanji()

		if mainKanji != None:
			displayString = mainKanji + f' ({", ".join(dicEntry.kanaList)})'
		else:
			displayString = f'{", ".join(dicEntry.kanaList)}'

		displayList.append(displayString)

	return displayList

