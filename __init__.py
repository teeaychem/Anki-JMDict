"""
    Anki plugin to get JMdict info.

    Assumes a database from https://github.com/obfusk/jiten formatted for v1.1.0
"""

import json
import os
from aqt import mw, gui_hooks
from aqt.utils import showInfo, getText
from aqt.qt import *
from anki.storage import Collection

from .search import *
from .ankiInteraction import *
from .classes.configC import *



configFile = "config.json"

mainConfig = Config()
mainConfig.setByJSON(configFile)


def getResults(searchTerm, config):
	# Return list of dicEntries which match searchTerm.
	# Config specifies db to use

	results = []
	entryIDs = getEntryIDS(searchTerm, config.dicPath)
	results = [dicEntry(entryID, config.dicPath) for entryID in entryIDs]

	return results


def lookup(editor):

	term, term_succeeded = getText('Enter a word. (Example: 探検)')
	if not term_succeeded:
		return

	results = getResults(term, mainConfig)
	choice = None

	if len(results) == 0:
		showInfo(("No results found"))
	elif len(results) == 1:
		choice = 0
	elif len(results) > 1:
		choice = displayChoices(results)

	if choice != None:
		entry = results[choice]
		data = [(fld, editor.mw.col.media.escapeImages(val)) for fld, val in editor.note.items()]
		fillAllFields(editor, entry, data, mainConfig)


def fillAllFields(editor, entry, data, config):

	if len(entry.kanjiList) > 0:
		mainKanji = entry.kanjiList[0]
	else:
		mainKanji = entry.kanaList[0]
	updateField(editor, data, config.mainKanjiFN, mainKanji)

	updateField(editor, data, config.mainKanaFN, entry.kanaList[0])
	updateField(editor, data, config.POSFN, entry.getPOSHTML())
	updateField(editor, data, config.glossFN, entry.getSenseHTML())
	updateField(editor, data, config.altKanjiFN, entry.getAltKanjiHTML())
	updateField(editor, data, config.altKanaFN, entry.getAltKanaHTML())
	updateField(editor, data, config.entryIDFN, entry.getEntryID())


# def fillAllFieldsByKanjiKana(editor):

#     data = [
#             (fld, editor.mw.col.media.escapeImages(val))
#             for fld, val in editor.note.items()
#         ]

#     kanjiText = ""
#     kanaText = ""

#     for i in range(len(data)):
#         if data[i][0] == mainKanjiFN:
#             kanjiText = data[i][1]
#         if data[i][0] == mainKanaFN:
#             kanaText = data[i][1]

#     results = getKanjiKanaEntryIDS(kanjiText, kanaText, dicPath)

#     if len(results) == 1:
#         entry = dicEntry(results[0], dicPath)
#         fillAllFields(editor, entry, data)


# def fillEntryIDByKanjiKana(editor):

#     data = [
#             (fld, editor.mw.col.media.escapeImages(val))
#             for fld, val in editor.note.items()
#         ]

#     kanjiText = ""
#     kanaText = ""

#     for i in range(len(data)):
#         if data[i][0] == mainKanjiFN:
#             kanjiText = data[i][1]
#         if data[i][0] == mainKanaFN:
#             kanaText = data[i][1]

#     results = getKanjiKanaEntryIDS(kanjiText, kanaText, dicPath)

#     if len(results) == 1:
#         entry = dicEntry(results[0], dicPath)
#         updateField(editor, data, entryIDFN, entry.getEntryID())


# def fillAllFieldsbyEntryID(editor):

#     eID = ""

#     data = [
#             (fld, editor.mw.col.media.escapeImages(val))
#             for fld, val in editor.note.items()
#         ]

#     for i in range(len(data)):
#         if data[i][0] == entryIDFN:
#             eID = data[i][1]

#     if eID != "":

#         entry = dicEntry(eID, dicPath)
#         fillAllFields(editor, entry, data)



def addEntryIDByMainKanjiKana():

	deckID = select_deck_id('Which deck would you like to add IDs to?')
	if deckID == None:
		return
	note_type_ids = getNoteTypes(deckID)
	# TODO add new note ids
	noteTypeID = note_type_ids[0]
	noteIDs = getNoteIDs(deckID, noteTypeID)
	for noteID in noteIDs:
		updateNote_entryID_KanjiKana(noteID, mainConfig)


def updateEntryies_entryID():

	deckID = select_deck_id('Which deck would you update by entryID?')
	if deckID == None:
		return
	note_type_ids = getNoteTypes(deckID)
	# TODO add new note ids
	noteTypeID = note_type_ids[0]
	noteIDs = getNoteIDs(deckID, noteTypeID)
	for noteID in noteIDs:
		updateNote_all_entryID(noteID, mainConfig)


def addJMdictButton(buttons, editor):
    # environment
	collection_path = mw.col.path
	plugin_dir_name = __name__

	user_dir_path = os.path.split(collection_path)[0]
	anki_dir_path = os.path.split(user_dir_path)[0]
	plugin_dir_path = os.path.join(anki_dir_path, 'addons21', plugin_dir_name)
	icon_path = os.path.join(plugin_dir_path, 'icon.png')

	btn = editor.addButton(icon=icon_path,
												 cmd='foo',
												 func=lookup,
												 tip='search JMdict　(⌘J)',
												 keys=QKeySequence('Ctrl+J')
	 )
	buttons.append(btn)


# add editor button
gui_hooks.editor_did_init_buttons.append(addJMdictButton)

sJDI_menu = QMenu('Simple JDI', mw)

sJDI_menu_test = sJDI_menu.addAction('Add EntryIDs to notes by main kanji and kana')
sJDI_menu_test.triggered.connect(addEntryIDByMainKanjiKana)

sJDI_menu_test = sJDI_menu.addAction('Redo notes by entryID')
sJDI_menu_test.triggered.connect(updateEntryies_entryID)

mw.form.menuTools.addMenu(sJDI_menu)