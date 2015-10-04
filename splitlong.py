__author__ = 'abhishek'
import re, collections
import globaldefs
def words(text): return re.findall('[a-z]+', text.lower())

def splitlong(word, in_words,direction='rev'):
    if word in in_words:
        return word
    legitchars = ['a','i']
    legitchars2 = ['a','e','i','o','u']
    splits = []
    nextsplit = []
    found1 = False
    if direction == 'rev':
        irange = reversed(range(len(word) + 1))
    else:
        irange = range(len(word) + 1)
    for i in irange:
        splits.append([(word[:i], word[i:])])
        toreturn = []
#        if (i>1 and word[:i] in in_words) or (i==1 and word[:i] in legitchars):
        if word[:i] in in_words:
            toreturn.append(word[:i])
            nextsplit = [splitlong(word[i:], in_words,direction)]
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
    out_rev = splitlong(word, in_words,'rev')
    out_fwd = splitlong(word, in_words,'fwd')

    print out_rev,out_fwd

    if out_rev != -1:
        out_rev = split2string(out_rev).split()
    else:
        out_rev = []

    if out_fwd != -1:
        out_fwd = split2string(out_fwd).split()
    else:
        out_fwd= []

    p_out_rev = 0
    p_out_fwd = 0

    for out in out_rev:
        if out in globaldefs.prior_hashtable:
            p_out_rev += globaldefs.prior_hashtable[out]

    for out in out_fwd:
        if out in globaldefs.prior_hashtable:
            p_out_fwd += globaldefs.prior_hashtable[out]

    if p_out_fwd == 0 and p_out_rev == 0:
        return -1

    if p_out_rev > p_out_fwd:
        return ' '.join(out_rev)
    else:
        return ' '.join(out_fwd)

print splitWord('howdoyousay')
