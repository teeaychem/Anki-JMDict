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

mainKanjiFN = ""
mainKanaFN = ""
POSFN = ""
glossFN = ""
altKanjiFN = ""
altKanaFN = ""
dictIDFN = ""

dicPath = None

configFile = "config.json"

def setDefaults(configFileVar):

    global mainKanjiFN, mainKanaFN, POSFN, glossFN, altKanjiFN, altKanaFN, dicPath

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


setDefaults(configFile)