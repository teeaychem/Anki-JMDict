"""
    Anki plugin to get JMdict info.

    Assumes a database from https://github.com/obfusk/jiten formatted for v1.1.0
"""

import json
import os
import re
import sqlite3
from aqt import mw, gui_hooks
from aqt.utils import showInfo, chooseList, getText
from aqt.qt import *
from anki.storage import Collection
from .util import *
from .search import *
from .databaseUtil import *

import time

mainKanjiFN = ""
mainKanaFN = ""
POSFN = ""
glossFN = ""
altKanjiFN = ""
altKanaFN = ""
entryIDFN = ""

dicPath = None

configFile = "config.json"

def setDefaults(configFileVar):

    global mainKanjiFN, mainKanaFN, POSFN, glossFN, altKanjiFN, altKanaFN, dicPath, entryIDFN

    mainPath = os.path.dirname(__file__)
    configRaw = open(os.path.join(mainPath, configFileVar), encoding='utf-8')
    configJSON = json.load(configRaw)

    ankiFields = configJSON['ankiFields']

    if ankiFields['mainKanji']:
        mainKanjiFN = ankiFields['mainKanji']
    if ankiFields['mainKana']:
        mainKanaFN = ankiFields['mainKana']
    if ankiFields['partOfSpeech']:
        POSFN = ankiFields['partOfSpeech']
    if ankiFields['gloss']:
        glossFN = ankiFields['gloss']
    if ankiFields['altKanji']:
        altKanjiFN = ankiFields['altKanji']
    if ankiFields['altKana']:
        altKanaFN = ankiFields['altKana']
    if ankiFields['id']:
        entryIDFN = ankiFields['id']

    dicPath = os.path.join(mainPath, configJSON['dictionary'])


def lookup(editor):

    term, term_succeeded = getText('Enter a word. (Example: 探検)')
    if not term_succeeded:
        return

    results = getResults(term, dicPath)
    choice = None

    if len(results) == 0:
        showInfo(("No results found"))
    elif len(results) == 1:
        choice = 0
    elif len(results) > 1:
        choice = displayChoices(results)

    if choice != None:

        entry = results[choice]

        data = [
            (fld, editor.mw.col.media.escapeImages(val))
            for fld, val in editor.note.items()
        ]

    fillAllFields(editor, entry, data)


def fillAllFields(editor, entry, data):

    if len(entry.kanjiList) > 0:
            mainKanji = entry.kanjiList[0]
    else:
        mainKanji = entry.kanaList[0]
    updateField(editor, data, mainKanjiFN, mainKanji)

    updateField(editor, data, mainKanaFN, entry.kanaList[0])
    updateField(editor, data, POSFN, entry.getPOSHTML())
    updateField(editor, data, glossFN, entry.getSenseHTML())
    updateField(editor, data, altKanjiFN, entry.getAltKanjiHTML())
    updateField(editor, data, altKanaFN, entry.getAltKanaHTML())
    updateField(editor, data, entryIDFN, entry.getEntryID())

def fillAllFieldsByKanjiKana(editor):

    data = [
            (fld, editor.mw.col.media.escapeImages(val))
            for fld, val in editor.note.items()
        ]

    kanjiText = ""
    kanaText = ""

    for i in range(len(data)):
        if data[i][0] == mainKanjiFN:
            kanjiText = data[i][1]
        if data[i][0] == mainKanaFN:
            kanaText = data[i][1]

    results = getKanjiKanaEntryIDS(kanjiText, kanaText, dicPath)

    if len(results) == 1:
        entry = dicEntry(results[0], dicPath)
        fillAllFields(editor, entry, data)


def fillEntryIDByKanjiKana(editor):

    data = [
            (fld, editor.mw.col.media.escapeImages(val))
            for fld, val in editor.note.items()
        ]

    kanjiText = ""
    kanaText = ""

    for i in range(len(data)):
        if data[i][0] == mainKanjiFN:
            kanjiText = data[i][1]
        if data[i][0] == mainKanaFN:
            kanaText = data[i][1]

    results = getKanjiKanaEntryIDS(kanjiText, kanaText, dicPath)

    if len(results) == 1:
        entry = dicEntry(results[0], dicPath)
        updateField(editor, data, entryIDFN, entry.getEntryID())


def fillAllFieldsbyEntryID(editor):

    eID = ""

    data = [
            (fld, editor.mw.col.media.escapeImages(val))
            for fld, val in editor.note.items()
        ]

    for i in range(len(data)):
        if data[i][0] == entryIDFN:
            eID = data[i][1]

    if eID != "":

        entry = dicEntry(eID, dicPath)
        fillAllFields(editor, entry, data)

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



def addEntryIDByMainKanjiKana():

    deckID = select_deck_id('Which deck would you like to add IDs to?')
    if deckID == None:
        return
    note_type_ids = getNoteTypes(deckID)
    # TODO add new note ids
    noteTypeID = note_type_ids[0]
    noteIDs = getNoteIDs(deckID, noteTypeID)
    for noteID in noteIDs:
        updateNote_entryID_KanjiKana(noteID)


def updateEntryies_entryID():

    deckID = select_deck_id('Which deck would you like to add IDs to?')
    if deckID == None:
        return
    note_type_ids = getNoteTypes(deckID)
    # TODO add new note ids
    noteTypeID = note_type_ids[0]
    noteIDs = getNoteIDs(deckID, noteTypeID)
    for noteID in noteIDs:
        updateNote_all_entryID(noteID)



def getNoteIDs(deckID, noteTypeID):

    noteIDs = []
    for row in mw.col.db.execute(
        'SELECT id FROM notes WHERE mid = ? AND id IN (SELECT nid FROM'
        ' cards WHERE did = ?) ORDER BY id', noteTypeID, deckID):
        nid = row[0]
        noteIDs.append(nid)
    return noteIDs


def getNoteTypes(deckID):

    noteTypes = []

    for row in mw.col.db.execute(
        'SELECT distinct mid FROM notes WHERE id IN (SELECT nid FROM'
        ' cards WHERE did = ?) ORDER BY id', deckID):
        mid = row[0]
        noteTypes.append(mid)

    return noteTypes


def updateNote_entryID_KanjiKana(noteID):

    # All fields are bundled
    row = mw.col.db.first(
            'SELECT flds FROM notes WHERE id = ?', noteID
            )
    flds_str = row[0]
    # \x1f to separate bundled fields
    fields = flds_str.split('\x1f')

    # Figure out mainKanji
    mainKanji_idx = mw.col.db.first('SELECT ord FROM fields WHERE name = ? AND ntid IN (SELECT mid FROM notes WHERE id = ?)', mainKanjiFN, noteID)[0]
    # Figure out mainKana
    mainKana_idx = mw.col.db.first('SELECT ord FROM fields WHERE name = ? AND ntid IN (SELECT mid FROM notes WHERE id = ?)', mainKanaFN, noteID)[0]
    # Figure out the index of the entryID field
    eID_idx = mw.col.db.first('SELECT ord FROM fields WHERE name = ? AND ntid IN (SELECT mid FROM notes WHERE id = ?)', entryIDFN , noteID)[0]

    mainKanji_str = fields[mainKanji_idx]
    mainKana_str = fields[mainKana_idx]

    entryIDs = getKanjiKanaEntryIDS(mainKanji_str, mainKana_str, dicPath)
    if len(entryIDs) == 1:

        fields[eID_idx] = str(entryIDs[0][0])

        newFieldsStr = '\x1f'.join(fields)
        mod_time = int(time.time())
        mw.col.db.execute(
            'UPDATE notes SET usn = ?, mod = ?, flds = ? WHERE id = ?',
            -1, mod_time, newFieldsStr, noteID
            )


def updateNote_all_entryID(noteID):

    # All fields are bundled
    row = mw.col.db.first(
            'SELECT flds FROM notes WHERE id = ?', noteID
            )
    flds_str = row[0]
    # \x1f to separate bundled fields
    fields = flds_str.split('\x1f')

    # Figure out the index of the entryID field
    eID_idx = mw.col.db.first('SELECT ord FROM fields WHERE name = ? AND ntid IN (SELECT mid FROM notes WHERE id = ?)', entryIDFN , noteID)[0]

    entryID = fields[eID_idx]

    if entryID != "":

        entry = dicEntry(entryID, dicPath)

        # Figure out mainKanji
        mainKanji_idx = mw.col.db.first('SELECT ord FROM fields WHERE name = ? AND ntid IN (SELECT mid FROM notes WHERE id = ?)', mainKanjiFN, noteID)[0]
        # Etc.
        mainKana_idx = mw.col.db.first('SELECT ord FROM fields WHERE name = ? AND ntid IN (SELECT mid FROM notes WHERE id = ?)', mainKanaFN, noteID)[0]
        POS_idx = mw.col.db.first('SELECT ord FROM fields WHERE name = ? AND ntid IN (SELECT mid FROM notes WHERE id = ?)', POSFN, noteID)[0]
        gloss_idx = mw.col.db.first('SELECT ord FROM fields WHERE name = ? AND ntid IN (SELECT mid FROM notes WHERE id = ?)', glossFN, noteID)[0]
        altKanjiFN_idx = mw.col.db.first('SELECT ord FROM fields WHERE name = ? AND ntid IN (SELECT mid FROM notes WHERE id = ?)', altKanjiFN, noteID)[0]
        altKanaFN_idx = mw.col.db.first('SELECT ord FROM fields WHERE name = ? AND ntid IN (SELECT mid FROM notes WHERE id = ?)', altKanaFN, noteID)[0]


        if len(entry.kanjiList) > 0:
            fields[mainKanji_idx] = entry.kanjiList[0]
        else:
            fields[mainKanji_idx] = entry.kanaList[0]

        fields[mainKana_idx] = entry.kanaList[0]
        fields[POS_idx] = entry.getPOSHTML()
        fields[gloss_idx] = entry.getSenseHTML()
        fields[altKanjiFN_idx] = entry.getAltKanjiHTML()
        fields[altKanaFN_idx] = entry.getAltKanaHTML()

        newFieldsStr = '\x1f'.join(fields)
        mod_time = int(time.time())
        mw.col.db.execute(
            'UPDATE notes SET usn = ?, mod = ?, flds = ? WHERE id = ?',
            -1, mod_time, newFieldsStr, noteID
            )



# add editor button
gui_hooks.editor_did_init_buttons.append(addJMdictButton)

sJDI_menu = QMenu('Simple JDI', mw)

sJDI_menu_test = sJDI_menu.addAction('Add EntryIDs to notes by main kanji and kana')
sJDI_menu_test.triggered.connect(addEntryIDByMainKanjiKana)

sJDI_menu_test = sJDI_menu.addAction('Redo notes by entryID')
sJDI_menu_test.triggered.connect(updateEntryies_entryID)




mw.form.menuTools.addMenu(sJDI_menu)



setDefaults(configFile)