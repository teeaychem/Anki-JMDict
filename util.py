""" Utility functions.
"""

def containsKanji(term):
  # https://stackoverflow.com/questions/30069846/how-to-find-out-chinese-or-japanese-character-in-a-string-in-python
  # First hirigana, second katakana
  ranges = [{'from': ord(u'\u3040'), 'to': ord(u'\u309f')}, {"from": ord(u"\u30a0"), "to": ord(u"\u30ff")}]

  for char in term:
    if any([range["from"] <= ord(char) <= range["to"] for range in ranges]) == False:
      return True
  return False