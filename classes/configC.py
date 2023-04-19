"""
	Class to pass around config options.
"""

from pathlib import Path
import json

class Config:

	def __init__(self):
		self.mainKanjiFN = ""
		self.mainKanaFN = ""
		self.POSFN = ""
		self.glossFN = ""
		self.altKanjiFN = ""
		self.altKanaFN = ""
		self.entryIDFN = ""
		self.dicPath = ""

	def setByJSON(self, configName):

		mainPath = Path(__file__).parent.parent.absolute()
		configPath = mainPath.joinpath(configName)
		configRaw = open(configPath, encoding='utf-8')
		configJSON = json.load(configRaw)

		ankiFields = configJSON['ankiFields']

		if ankiFields['mainKanji']:
			self.mainKanjiFN = ankiFields['mainKanji']
		if ankiFields['mainKana']:
			self.mainKanaFN = ankiFields['mainKana']
		if ankiFields['partOfSpeech']:
			self.POSFN = ankiFields['partOfSpeech']
		if ankiFields['gloss']:
			self.glossFN = ankiFields['gloss']
		if ankiFields['altKanji']:
			self.altKanjiFN = ankiFields['altKanji']
		if ankiFields['altKana']:
			self.altKanaFN = ankiFields['altKana']
		if ankiFields['id']:
			self.entryIDFN = ankiFields['id']

		self.dicPath = mainPath.joinpath(configJSON['dictionary'])