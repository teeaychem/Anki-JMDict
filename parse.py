import re

def parsePOS(dicEntry):

    partVal = ""
    sense = dicEntry["sense"]
    for j in range(len(sense)):
        partSet = set()
        nonVerbPOSList = []
        verbPOSList = []
        parts = sense[j]["partOfSpeech"]
        suruVerb = False
        for k in range(len(parts)):
            partTerm = sense[j]["partOfSpeech"][k]

            if partTerm not in partSet:
                partSet.add(partTerm)

                if re.fullmatch(r'n|adj-na|adj-i|exp|adv|adv-to', partTerm):
                    nonVerbPOSList.append(partTerm)
                elif re.fullmatch(r'vi|vt', partTerm):
                    verbPOSList.append(partTerm)
                elif re.fullmatch(r'vs', partTerm):
                    suruVerb = True

        for pos in nonVerbPOSList:
                partVal += pos + "・"

        if suruVerb == True:
            partVal += "する: ("
        for pos in verbPOSList:
            partVal += pos + "・"
        if suruVerb == True:
            partVal = partVal[:-1] + ")・"

        if len(partSet) != 0:
            partVal = partVal[:-1]
            partVal += " 〜 "
    partVal = partVal[:-3]

    partVal = re.sub(r'vi', '動詞', partVal)
    partVal = re.sub(r'vt', '他動詞', partVal)
    partVal = re.sub(r'n', '名詞', partVal)
    partVal = re.sub(r'adj-na', '形容動詞', partVal)
    partVal = re.sub(r'adj-i', '形容詞', partVal)
    partVal = re.sub(r'exp', '言い回し', partVal)
    partVal = re.sub(r'adv', '副詞', partVal)
    partVal = re.sub(r'adv-to', '〜と 副詞', partVal)

    return partVal


def parseMainKanji(dicEntry):

    rVal = ""

    if len(dicEntry["kanji"]) > 0:
        rVal = dicEntry["kanji"][0]["text"]

    return rVal


def parseMainKana(dicEntry):
    return dicEntry["kana"][0]["text"]


def parseAltKanji(dicEntry):

    rVal = ""

    if len(dicEntry["kanji"]) > 1:
        for j in range(1, len(dicEntry["kanji"])):
            rVal += dicEntry["kanji"][j]["text"] + "・"
        rVal = rVal[:-1]

    return rVal

def parseAltKana(dicEntry):

    rVal = ""

    if len(dicEntry["kana"]) > 1:
        for j in range(1, len(dicEntry["kana"])):
            rVal += dicEntry["kana"][j]["text"] + "・"
        rVal = rVal[:-1]

    return rVal


def parseGloss(dicEntry):

    entries = dicEntry["sense"]

    rVal = ""
    counter = 1

    for j in range(0,len(entries)):
        rVal += str(j + 1) + ". "
        for glossString in dicEntry["sense"][j]["gloss"]:
            rVal += glossString["text"] + ", "
        rVal = rVal[:-2]
        if len(dicEntry["sense"][j]["field"]) > 0:
            rVal += ' (<i>'
            for field in dicEntry["sense"][j]["field"]:
                rVal += field + ', '
            rVal = rVal[:-2] + '</i>)'
        rVal += "<br>"
    rVal = rVal[:-4]

    return rVal

def parseID(dicEntry):

    return dicEntry["id"]



