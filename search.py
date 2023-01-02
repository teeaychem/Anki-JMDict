from .util import customChooseList


def testKanji(term):
  # https://stackoverflow.com/questions/30069846/how-to-find-out-chinese-or-japanese-character-in-a-string-in-python
  # First hirigana, second katakana

  ranges = [{'from': ord(u'\u3040'), 'to': ord(u'\u309f')}, {"from": ord(u"\u30a0"), "to": ord(u"\u30ff")}]

  for char in term:
    if any([range["from"] <= ord(char) <= range["to"] for range in ranges]) == False:
      return True
  return False


def getResults(term, dicVar):

  results = []

  containsKanji = testKanji(term)

  for item in dicVar["words"]:

    if containsKanji == True:
      for kanji in item["kanji"]:
        if (kanji["text"] == term):
          results.append(item)
    else:
      for kana in item["kana"]:
        if (kana["text"] == term):
          results.append(item)

  return results


def displayChoices(resultList):

  choices = []

  for item in resultList:

    if (len(item["kanji"]) > 0) and (item["kanji"][0]["text"] != ""):
      choices.append("%s (%s)" % (item["kanji"][0]["text"], item["kana"][0]["text"]))
    else:
      choices.append(item["kana"][0]["text"])

  return customChooseList("Results", choices)

