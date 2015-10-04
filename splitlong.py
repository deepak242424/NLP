__author__ = 'abhishek'
import re, collections

def words(text): return re.findall('[a-z]+', text.lower())

def splitlong(word, in_words):
    if word in in_words:
        return word
    legitchars = ['a','i']
    legitchars2 = ['a','e','i','o','u']
    splits = []
    nextsplit = []
    found1 = False
    for i in reversed(range(len(word) + 1)):
        splits.append([(word[:i], word[i:])])
        toreturn = []
#        if (i>1 and word[:i] in in_words) or (i==1 and word[:i] in legitchars):
        if word[:i] in in_words:
            toreturn.append(word[:i])
            nextsplit = [splitlong(word[i:], in_words)]
            for j in nextsplit:
               toreturn.append(j)

            if not (-1 in toreturn):
                found1 = True
                break
    if not found1:
        return -1
    else:
        return toreturn

def split2string(in_list):
    outsplit = ''
    for i in in_list:
        if not isinstance(i, list):
            outsplit += " " + i
        else:
            outsplit += split2string(i)
    return outsplit

def splitWord(word):
    in_words = words(file('word.list').read())
    out = splitlong('goodworkisrewarded', in_words)
    out = split2string(out)
    return out

print splitWord("beyotch")