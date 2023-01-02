# Assumes a database from https://github.com/obfusk/jiten formatted for v1.1.0

import sqlite3

mainDict = sqlite3.connect("jmdict.sqlite3")
cur = mainDict.cursor()

class dicEntry:
  # def __init__(self, entryID, mainKanji, mainKana, POS, gloss, altKanji, altKana, pitch):
  def __init__(self, entryID):
    self.entryID = entryID
    self.mainKanji = ""
    self.mainKana = ""
    self.POS = ""
    self.gloss = []
    self.altKanji = []
    self.altKana = []
    self.pitch = ""

def containsKanji(term):
  # https://stackoverflow.com/questions/30069846/how-to-find-out-chinese-or-japanese-character-in-a-string-in-python
  # First hirigana, second katakana
  ranges = [{'from': ord(u'\u3040'), 'to': ord(u'\u309f')}, {"from": ord(u"\u30a0"), "to": ord(u"\u30ff")}]

  for char in term:
    if any([range["from"] <= ord(char) <= range["to"] for range in ranges]) == False:
      return True
  return False


def getEntryIDS(searchTerm):
  # Search a string, return list of entryIDs
  if containsKanji(searchTerm):
    entrySearch = cur.execute("SELECT entry FROM kanji WHERE elem='%s'" % searchTerm)
  else:
    entrySearch = cur.execute("SELECT entry FROM reading WHERE elem='%s'" % searchTerm)
  entryIDs = entrySearch.fetchall()
  return entryIDs


def makeIDKanjiKanaList(entryIDList):
  returnList = []
  for entryID in entryIDList:
    returnList.append([entryID, getKanji(entryID), getKana(entryID)])
  return returnList


def getKanji(entryID):
  kanjiList = cur.execute("SELECT elem FROM kanji WHERE entry='%s'" % entryID).fetchall()
  return kanjiList


def getKana(entryID):
  kanaList = cur.execute("SELECT elem FROM reading WHERE entry='%s'" % entryID).fetchall()
  return kanaList


def getPOS(entryID):
  posList = cur.execute("SELECT pos FROM sense WHERE entry='%s' AND lang='eng'" % entryID).fetchall()
  return posList


def getGloss(entryID):
  glossList = cur.execute("SELECT gloss FROM sense WHERE entry='%s' AND lang='eng'" % entryID).fetchall()
  return glossList


def uniqueItems(inList):
  # Return list of unique POS
  itemSet = set()
  outList = []
  for item in inList:
    for subitem in item:
      if subitem not in itemSet:
        itemSet.add(subitem)
        outList.append(subitem)

  # As cleanEntryList expects list of lists, wrap outList as a list
  return [outList]


def cleanEntryList(inList):
  outList = []
  for item in inList:
    outList.append(item[0].split('\n'))
  return outList


def buildEntryIF(entryID):
  entry = dicEntry(entryID)

  # kanji
  kanjiList = getKanji(entryID)

  if len(kanjiList) > 0:
    entry.mainKanji = kanjiList[0][0]
  if len(kanjiList) > 1:
    for i in range(1, len(kanjiList)):
      entry.altKanji.append(kanjiList[i][0])

  # kana
  kanaList = getKana(entryID)

  entry.mainKana = kanaList[0][0]
  if len(kanaList) > 1:
    for i in range(1, len(kanaList)):
      entry.altKana.append(kanaList[i][0])

  entry.POS = cleanEntryList(uniqueItems(getPOS(entryID)))
  entry.gloss = cleanEntryList(getGloss(entryID))

  return entry


searchTerm = "致命"

def testing(entryID):

  entry = buildEntryIF(entryID)

  print(entry.entryID)
  print(entry.mainKanji)
  print(entry.altKanji)
  print(entry.mainKana)
  print(entry.altKana)
  print(entry.POS)
  print(entry.gloss)

entryIDs = getEntryIDS(searchTerm)

# print(makeIDKanjiKanaList(entryIDs))

for ent in entryIDs:
  testing(ent)
