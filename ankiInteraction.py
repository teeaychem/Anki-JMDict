"""
Interaction with anki
"""


import time
import sqlite3
import json
from aqt.utils import chooseList
from aqt import mw, gui_hooks

from .databaseUtil import *


def updateField(editor, data, fieldID, newVal):

    for i in range(len(data)):
        if data[i][0] == fieldID:

            data[i] = (
                        data[i][0],       # leave field name as is
                        newVal            # update field value
                    )
            js = 'setFields(%s); setFonts(%s); focusField(%s); setNoteId(%s)' % (
                json.dumps(data),
                json.dumps(editor.fonts()),
                json.dumps(editor.web.editor.currentField),
                json.dumps(editor.note.id)
            )
            js = gui_hooks.editor_will_load_note(js, editor.note, editor)
            editor.web.eval(js)


def select_deck_id(msg):
    decks = []
    for row in mw.col.db.execute('SELECT id, name FROM decks'):
        deckID = row[0]
        deckName = row[1]
        decks.append((deckID, deckName))
    choices = [deck[1] for deck in decks]
    choice = chooseList(msg, choices)
    return decks[choice][0]


def displayChoices(resultList):

  choices = makeDisplayEntriesList(resultList)

  return chooseList("Results", choices)


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


def updateNote_entryID_KanjiKana(noteID, config):

    # All fields are bundled
    row = mw.col.db.first(
            'SELECT flds FROM notes WHERE id = ?', noteID
            )
    flds_str = row[0]
    # \x1f to separate bundled fields
    fields = flds_str.split('\x1f')

    # Figure out mainKanji
    mainKanji_idx = mw.col.db.first('SELECT ord FROM fields WHERE name = ? AND ntid IN (SELECT mid FROM notes WHERE id = ?)', config.mainKanjiFN, noteID)[0]
    # Figure out mainKana
    mainKana_idx = mw.col.db.first('SELECT ord FROM fields WHERE name = ? AND ntid IN (SELECT mid FROM notes WHERE id = ?)', config.mainKanaFN, noteID)[0]
    # Figure out the index of the entryID field
    eID_idx = mw.col.db.first('SELECT ord FROM fields WHERE name = ? AND ntid IN (SELECT mid FROM notes WHERE id = ?)', config.entryIDFN , noteID)[0]

    mainKanji_str = fields[mainKanji_idx]
    mainKana_str = fields[mainKana_idx]

    entryIDs = getKanjiKanaEntryIDS(mainKanji_str, mainKana_str, config.dicPath)
    if len(entryIDs) == 1:

        fields[eID_idx] = str(entryIDs[0][0])

        newFieldsStr = '\x1f'.join(fields)
        mod_time = int(time.time())
        mw.col.db.execute(
            'UPDATE notes SET usn = ?, mod = ?, flds = ? WHERE id = ?',
            -1, mod_time, newFieldsStr, noteID
            )


def updateNote_all_entryID(noteID, config):

    # All fields are bundled
    row = mw.col.db.first(
            'SELECT flds FROM notes WHERE id = ?', noteID
            )
    flds_str = row[0]
    # \x1f to separate bundled fields
    fields = flds_str.split('\x1f')

    # Figure out the index of the entryID field
    eID_idx = mw.col.db.first('SELECT ord FROM fields WHERE name = ? AND ntid IN (SELECT mid FROM notes WHERE id = ?)', config.entryIDFN , noteID)[0]

    entryID = fields[eID_idx]

    if entryID != "":

        entry = dicEntry(entryID, config.dicPath)

        # Figure out mainKanji
        mainKanji_idx = mw.col.db.first('SELECT ord FROM fields WHERE name = ? AND ntid IN (SELECT mid FROM notes WHERE id = ?)', config.mainKanjiFN, noteID)[0]
        # Etc.
        mainKana_idx = mw.col.db.first('SELECT ord FROM fields WHERE name = ? AND ntid IN (SELECT mid FROM notes WHERE id = ?)', config.mainKanaFN, noteID)[0]
        POS_idx = mw.col.db.first('SELECT ord FROM fields WHERE name = ? AND ntid IN (SELECT mid FROM notes WHERE id = ?)', config.POSFN, noteID)[0]
        gloss_idx = mw.col.db.first('SELECT ord FROM fields WHERE name = ? AND ntid IN (SELECT mid FROM notes WHERE id = ?)', config.glossFN, noteID)[0]
        altKanjiFN_idx = mw.col.db.first('SELECT ord FROM fields WHERE name = ? AND ntid IN (SELECT mid FROM notes WHERE id = ?)', config.altKanjiFN, noteID)[0]
        altKanaFN_idx = mw.col.db.first('SELECT ord FROM fields WHERE name = ? AND ntid IN (SELECT mid FROM notes WHERE id = ?)', config.altKanaFN, noteID)[0]


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