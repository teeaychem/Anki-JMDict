"""
  Class for dictionary entry.
"""
import sqlite3
import re
from .senseC import *

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
		# Return a html string with sense info w/ HTML tags for formatting via CSS.
		# See end of loop for HTML for each distinct sense.

		HTMLSpanPrefix = "xyz"
		HTMLSenses = []

		for key in self.posSenseDict.keys():

			# Set for collecting info that applies to all senses.
			# Start with initial sense
			commonSenseInfo = set((self.posSenseDict[key][0]).info)
			# Now, take the intersection with all other senses
			for sense in self.posSenseDict[key]:
				commonSenseInfo = commonSenseInfo.intersection(set(sense.info))
      # This happens, and preference for less clutter
			commonSenseString = ", ".join([self.JInfo(inf) for inf in commonSenseInfo])

			sensesString = ""

			for sense in self.posSenseDict[key]:

				senseString = f'<span class="{HTMLSpanPrefix + "Sense"}">{", ".join(sense.gloss)}</span>'

				uniqueInfo = []
				for info in sense.info:
					if info not in commonSenseInfo:
						uniqueInfo.append(info)

				sensesInfoPreString = ", ".join([self.JInfo(inf) for inf in uniqueInfo])

				if sensesInfoPreString != "":
					sensesInfoPreString = f"({sensesInfoPreString})"
				senseInfoString = f' <span class="{HTMLSpanPrefix + "SenseInf"}">{sensesInfoPreString}</span>'

				# Each sense is written as item of ordered list
				sensesString += f"<li>{senseString}{senseInfoString}</li>"

			# Add HTML for particular sense
			HTMLSenses.append(f"""
				<span class "{HTMLSpanPrefix + "Sense"}">
				<span class="{HTMLSpanPrefix + "POS"}">{key}</span>
				<span class="{HTMLSpanPrefix + "POSCInf"}">{commonSenseString}</span>
				<br>
				<ol class="{HTMLSpanPrefix + "SenseList"}">
				{sensesString}
				</ol>
				</span>
			"""
			)

		HTML = "<br>".join(HTMLSenses)

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

		kanaList = cur.execute("SELECT text FROM Kana WHERE idseq='%s'" % self.entryID).fetchall()
		for i in range(0, len(kanaList)):
			self.kanaList.append(kanaList[i][0])


	def fillKanji(self, cur):
		kanjiList = cur.execute("SELECT text FROM Kanji WHERE idseq='%s'" % self.entryID).fetchall()
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
				newSuru = f"suru verb - included ({verbs})"
				posList = [newSuru if item == "suru verb - included" else item for item in posList]

		return posList


	def fillSenses(self, cur):

		senseIDs = cur.execute("SELECT ID FROM Sense WHERE idseq='%s'" % self.entryID).fetchall()
		senseList = []

		for senseID in senseIDs:

			senseText = [i[0] for i in cur.execute("SELECT text FROM SenseGloss WHERE sid='%s' AND lang='eng'" % senseID).fetchall()]
			posText = [i[0] for i in cur.execute("SELECT text FROM pos WHERE sid='%s'" % senseID).fetchall()]
			senseInfoText = [i[0] for i in cur.execute("SELECT text FROM SenseInfo WHERE sid='%s'" % senseID).fetchall()]

			pos = "・".join(self.collapseSV(posText))
			pos = re.sub(r'\n', '・', self.JPOS(pos))

			senseList = self.posSenseDict.get(pos, list())

			senseItem = Sense(self.entryID)

			senseItem.pos = pos
			senseItem.gloss = senseText
			senseItem.info = senseInfoText

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

		if self.JPOSs:

			part = re.sub(r'noun, used as a suffix', '名詞の接尾辞', part)
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
			part = re.sub(r'auxiliary verb', '補助動詞', part)
			part = re.sub(r'suru verb - included', 'サ変名詞', part)
			part = re.sub(r'Godan verb with \'(s|k|r|n|m|g|ts|b)*u\' ending', '五段動詞', part)
			part = re.sub(r'Godan verb with \'(s|k|r|n|m|g|ts|b)*u\' ending', '五段動詞', part)
			part = re.sub(r'Ichidan verb', '一段動詞', part)
			part = re.sub(r'pre-noun adjectival \(rentaishi\)', '連体詞', part)
			part = re.sub(r'pronoun', '代名詞', part)
			part = re.sub(r'interjection \(kandoushi\)', '感動詞', part)
			part = re.sub(r'auxiliary', '副詞', part)
			part = re.sub(r'noun or participle which takes the aux. verb suru', '~する', part)
			part = re.sub(r'noun', '名詞', part)
			part = re.sub(r'particle', '助詞', part)
			part = re.sub(r'suffix', '接尾語', part)
			part = re.sub(r'su verb - precursor to the modern suru', '', part)

		return part


	def JInfo(self, info):

		if self.JPOSs:

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


	def getEntryID(self):
		return str(self.entryID)