import sqlite3
import re
from .util import containsKanji


class Sense:
  def __init__(self, entryID):
    self.entryID = entryID
    self.pos = ""
    self.gloss = []
    self.info = []


class dicEntry:
  def __init__(self, entryID, dictPath):
    self.entryID = entryID
    self.kanjiList = []
    self.kanaList = []
    self.POSList = []
    self.posSenseDict = {}
    self.altKanji = []
    self.altKana = []
    self.pitch = ""
    self.JPOSs = True
    self.dictPath = dictPath

    self.updateAllFields()


  def getSenseHTML(self):

    HTML = ""
    counter = 0
    for key in self.posSenseDict.keys():
      HTML += '<SPAN STYLE="opacity:0.75;">%s</SPAN> ' % key

      # Collect common info to display next to pos.
      for sense in self.posSenseDict[key]:

        commonInfo = set()
        for sensePart in sense.info:
          commonInfo.add(sensePart)

      # Display common info next to pos.
      if len(commonInfo) > 0:
        HTML  += '<SPAN STYLE="opacity:0.5;"> '
        for commonSensePart in commonInfo:
          if self.JPOSs:
            commonSensePart = self.JInfo(commonSensePart)
          HTML += commonSensePart + ", "
        HTML = HTML[:-2]
        HTML  += "</SPAN>"

      HTML += '<br><p style="margin-left: 25px;">'

      for sense in self.posSenseDict[key]:

        counter += 1
        HTML += str(counter) + ". "
        for glossPart in sense.gloss:
          HTML += glossPart + ", "
        HTML = HTML[:-2]

        # Display any non-common info next to gloss.
        if len(sense.info) > 0:
          specificInfoString = ""
          for sensePart in sense.info:
            if sensePart not in commonInfo:
              specificInfoString += sensePart + ", "
          if specificInfoString != "":
            HTML += ' ( <SPAN STYLE="opacity:0.75;"><i>' + specificInfoString[:-2] + '</i></SPAN>)'
        HTML += "<br>"

      HTML = HTML[:-4] + "</p>"

    return HTML

  def getPOSHTML(self):

    return "・".join(self.POSList)

  def getAltKanjiHTML(self):

    return "・".join(self.kanjiList[1:])

  def getAltKanaHTML(self):

    return "・".join(self.kanaList[1:])


  def updateAllFields(self):

    cur = sqlite3.connect(self.dictPath).cursor()

    self.fillSenses(cur)
    self.fillKanji(cur)
    self.fillKana(cur)
    self.fillPOS(cur)


  def fillKana(self, cur):

    kanaList = cur.execute("SELECT elem FROM reading WHERE entry='%s'" % self.entryID).fetchall()
    for i in range(0, len(kanaList)):
      self.kanaList.append(kanaList[i][0])

  def fillKanji(self, cur):
    kanjiList = cur.execute("SELECT elem, chars FROM kanji WHERE entry='%s'" % self.entryID).fetchall()
    for i in range(0, len(kanjiList)):
      self.kanjiList.append(kanjiList[i][0])


  def collapseSV(self, posList):
    # If suru and tv/it in posList, then return list with suru (tv/iv) instead

    if "suru verb - included" in posList:
      verbs = ""
      if "transitive verb" in posList:
        verbs += "transitive verb, "
        posList.remove("transitive verb")
      if "intransitive verb" in posList:
        verbs += "intransitive verb, "
        posList.remove("intransitive verb")
      verbs = verbs[:-2]
      if verbs != "":
        newSuru = "suru verb - included (%s)" % verbs
        posList = [newSuru if item == "suru verb - included" else item for item in posList]

    return posList

  def fillSenses(self, cur):

    senseList = cur.execute("SELECT * FROM sense WHERE entry='%s' AND lang='eng'" % self.entryID)
    for entry, pos, lang, gloss, info, xref in senseList:

      pos = "・".join(self.collapseSV(pos.split('\n')))

      if self.JPOSs:
        pos = self.JPOS(pos)

      pos = re.sub(r'\n', '・', pos)

      senseList = self.posSenseDict.get(pos, list())

      senseItem = Sense(entry)

      senseItem.pos = pos
      senseItem.gloss = gloss.split("\n")  # re.sub(r'\n', ', ', gloss)
      if len(info) > 0:
        senseItem.info = info.split("\n")

      senseList.append(senseItem)

      self.posSenseDict[pos] = senseList

  def fillPOS(self, cur):

    if self.posSenseDict == {}:
      self.fillSenses(cur)
    posSet = set()
    for key in self.posSenseDict.keys():
      for subkey in key.split('・'):
        posSet.add(subkey)
    self.POSList = list(posSet)


  def JPOS(self, part):

    part = re.sub(r'adverb taking the \'to\' particle', '〜と 副詞', part)
    part = re.sub(r'adjectival nouns or quasi-adjectives \(keiyodoshi\)', '形容動詞', part)
    part = re.sub(r'adjective \(keiyoushi\)', '形容詞', part)
    part = re.sub(r'expressions \(phrases, clauses, etc.\)', '言い回し', part)
    part = re.sub(r'adverb \(fukushi\)', '副詞', part)
    part = re.sub(r'intransitive verb', '動詞', part)
    part = re.sub(r'transitive verb', '他動詞', part)
    part = re.sub(r'noun \(common\) \(futsuumeishi\)', '普通名詞', part)
    part = re.sub(r'nouns which may take the genitive case particle \'no\'', '〜の 形容詞', part)
    part = re.sub(r"taru' adjective", '〜たる 形容詞', part)
    part = re.sub(r'particle', '助詞', part)
    part = re.sub(r'suffix', '接尾語', part)
    part = re.sub(r'auxiliary verb', '補助動詞', part)
    part = re.sub(r'suru verb - included', 'サ変名詞', part)
    part = re.sub(r'Godan verb with \'(s|k|r|n|m|g|ts|b)*u\' ending', '五段動詞', part)
    part = re.sub(r'Godan verb with \'(s|k|r|n|m|g|ts|b)*u\' ending', '五段動詞', part)
    part = re.sub(r'Ichidan verb with \'(s|k|r|n|m|g|ts|b)*u\' ending', '一段動詞', part)
    part = re.sub(r'pre-noun adjectival \(rentaishi\)', '連体詞', part)
    part = re.sub(r'pronoun', '代名詞', part)
    part = re.sub(r'interjection \(kandoushi\)', '感動詞', part)
    part = re.sub(r'auxiliary', '副詞', part)
    part = re.sub(r'noun or participle which takes the aux. verb suru', '~する', part)

    return part

  def JInfo(self, info):

    info = re.sub(r'word usually written using kana alone', '仮名', info)
    info = re.sub(r'abbreviation', '略語', info)
    info = re.sub(r'idiomatic expression', '慣用表現', info)
    info = re.sub(r'obsolete term', '古臭い', info)
    info = re.sub(r'colloquialism', '俗語', info)
    info = re.sub(r'onomatopoeic or mimetic word', '擬音語 / 擬態語', info)
    info = re.sub(r'archaism', '古語', info)
    info = re.sub(r'honorific or respectful \(sonkeigo\) language', '尊敬語', info)
    info = re.sub(r'polite \(teineigo\) language', '丁寧語', info)
    info = re.sub(r'yojijukugo', '四字熟語', info)
    info = re.sub(r'derogatory', '蔑称', info)

    return info



  def getMainKanji(self):
    if len(self.kanjiList) > 0:
      return self.kanjiList[0]
    else:
      return None

  def getMainKana(self):
    return self.kanaList[0]


class idKanjiKanaClass:
  # def __init__(self, entryID, mainKanji, mainKana, POS, gloss, altKanji, altKana, pitch):
  def __init__(self, entryID, kanjiList = [], kanaList = []):
    self.entryID = entryID
    self.kanji = kanjiList
    self.kana = kanaList





def getEntryIDS(searchTerm, dicPath):
  # Search a string, return list of entryIDs
  dictionary = sqlite3.connect(dicPath)
  cur = dictionary.cursor()


  if containsKanji(searchTerm):
    entrySearch = cur.execute("SELECT entry FROM kanji WHERE elem='%s'" % searchTerm)
  else:
    entrySearch = cur.execute("SELECT entry FROM reading WHERE elem='%s'" % searchTerm)
  entryIDs = entrySearch.fetchall()
  return entryIDs



def makeIDKanjiKanaList(entryIDList):
  returnList = []
  for entryID in entryIDList:
    instance = idKanjiKanaClass(entryID, getKanji(entryID), getKana(entryID))
    returnList.append(instance)
  return returnList


def makeDisplayEntriesList(dicEntryList):
  # Make [entryID, displayString] list from entryIDs

  displayList = []

  for dicEntry in dicEntryList:

    displayString = ""

    mainKanji = dicEntry.getMainKanji()
    mainKana = dicEntry.getMainKana()

    if mainKanji != None:
      displayString += mainKanji + " ("
    for kana in dicEntry.kanaList:
      displayString += kana + ", "
    displayString = displayString[:-2]
    if mainKanji != None:
      displayString += ")"

    displayList.append(displayString)

  return displayList


# def getFieldVal():

#   posDict = dict()
#   # posList = cur.execute("SELECT pos FROM sense WHERE lang='eng'")
#   posList = cur.execute("SELECT info FROM sense WHERE lang='eng'")
#   for pos in posList:
#     poses = pos[0].split('\n')
#     for posi in poses:
#       posDict[posi] = posDict.get(posi, 0) + 1

#   for key in posDict.keys():
#     if posDict[key] > 20:
#       print(key + ": " + str(posDict[key]))


# def testing():

#   searchTerm = "する"

#   entryIDs = getEntryIDS(searchTerm)

#   nlist = [dicEntry(entryID) for entryID in entryIDs]

#   # print(nlist)

#   # print(makeDisplayEntriesList(nlist))
#   # nlist[0].print()

# testing()
# getFieldVal()