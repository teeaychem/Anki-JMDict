"""
  Class to collect info relating to sense of a word.
"""

class Sense:
  def __init__(self, entryID):
    self.entryID = entryID
    self.pos = ""
    self.gloss = []
    self.info = []
