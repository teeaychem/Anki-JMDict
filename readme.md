A basic Anki extension to easily create cards from JMDict entries.

Set up a note type with a handful of named fields (see below).
Download a 'jamdict.db' file and copy it to the 

Press "" or click the icon and then type in a word using kanji/kana.

If there is a unique JMDict entry, the fileds are automatically filled with the correspond information.
If multiple entries are found, a window opens for you to choose the right entry.


This extension relies on a pre-compiled jamdict database used by Jamdict.
You can find a link to the database here: https://jamdict.readthedocs.io/en/latest/install.html#download-database-file-manually
The 'jamdict.db' file is assumed to be in the same folder as '__init__.py'.

The extension assumes your Anki note type has some specifically named fields.
Specifically:

"mainKanji", to display the default kanji entry.
"mainKana", to display the default kana entry. (If there is no kanji entry, the main kana entry is also copied to "mainKanji")
"partOfSpeech", to display the part of speach
"gloss", the gloss for the entry
"altKanji", alternative kanji
"altKana", alternative kana
"entryId", the JMDict unquie ID.

No field is required.
For example, if you only have a "mainKanji" field, 

If you'd prefer to use different names, update the "config.json" file.

