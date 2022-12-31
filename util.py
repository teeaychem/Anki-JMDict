""" Utility functions.
"""

import json
from aqt import mw, gui_hooks
from aqt.utils import Qt, QDialog, QVBoxLayout, QLabel, QListWidget, QDialogButtonBox


def customChooseList(msg, choices, startrow=0):
    """ Copy of https://github.com/ankitects/anki/blob/main/
            qt/aqt/utils.py but with a cancel button added.

    """

    parent = mw.app.activeWindow()
    d = QDialog(parent)
    d.setWindowModality(Qt.WindowModal)
    l = QVBoxLayout()
    d.setLayout(l)
    t = QLabel(msg)
    l.addWidget(t)
    c = QListWidget()
    c.addItems(choices)
    c.setCurrentRow(startrow)
    l.addWidget(c)
    buts = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
    bb = QDialogButtonBox(buts)
    l.addWidget(bb)
    bb.accepted.connect(d.accept)
    bb.rejected.connect(d.reject)
    l.addWidget(bb)
    ret = d.exec_()  # 1 if Ok, 0 if Cancel or window closed
    if ret == 0:
        return None  # can't be Faluse b/c False == 0
    return c.currentRow()


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