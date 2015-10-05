__author__ = 'deepak'
import re
import cPickle
import math
import operator
import wordspellcheck
import csv
import globaldefs
import sys
<<<<<<< HEAD:src/phrasespellcheck.py
from collections import OrderedDict
=======

>>>>>>> 8d647dcf2d7d44155dbd3761bc3e195d254ad64c:phrasespellcheck.py
def words(text): return re.findall('[a-z]+', text.lower())

def get_neighbours(word_list, given_word, window):
    neighbours = []
    for count, wrd in enumerate(word_list):
        if wrd == given_word:
            neighbours += word_list[max(count-window,0):count] + word_list[count+1:min(count+window+1, len(word_list))]
    return neighbours

def get_neighbour_counts(window, corpus):
    count_dict = {}
    for count, wrd in enumerate(corpus):
        local_neighbours = corpus[max(count-window,0):count] + corpus[count+1:min(count+window+1, len(corpus))]
        if wrd not in count_dict:
            count_dict[wrd] = {}
        for neigh in local_neighbours:
            if neigh not in count_dict[wrd]:
                count_dict[wrd][neigh] = 0
            count_dict[wrd][neigh] += 1
        print 'GN'+ str(count)

    sum_count_dict = {}
    for iteration, wrd in enumerate(count_dict.keys()):
        sum_count_dict[wrd] = sum(count_dict[wrd].values())

    toreturn = (count_dict, sum_count_dict)
    return toreturn

def get_likelihood_dict(count_dict, sum_count_dict):
    dict_likeli = count_dict.copy()
    vocab_size = len(count_dict)
    for iteration, wrd in enumerate(count_dict.keys()):
        for neigh in count_dict[wrd]:
            dict_likeli[wrd][neigh] = (smooth_constant+count_dict[wrd][neigh])/float((sum_count_dict[wrd]+smooth_constant*vocab_size))
        print iteration
    return dict_likeli

def saveLikelihoodDict(window):
    wrd_list = words(open('brownuntagged.txt', 'r').read())
    (neighbours_dict,sum_count_dict) = get_neighbour_counts(window, wrd_list)
    likelihoods_dict = get_likelihood_dict(neighbours_dict, sum_count_dict)
    tostore = (likelihoods_dict, sum_count_dict)

    pickle_file = open(globaldefs.PATH_LIKELIHOOD_WSD, 'wb')
    cPickle.dump(tostore, pickle_file, protocol=cPickle.HIGHEST_PROTOCOL)
    pickle_file.close()

def loadLikelihoodDict():
    pickle_file = open(globaldefs.PATH_LIKELIHOOD_WSD, 'rb')
    (likelihood_dict,sum_count_dict) = cPickle.load(pickle_file)
    toreturn = (likelihood_dict,sum_count_dict)
    pickle_file.close()
    return toreturn

def getWordSuggestions(incorrect,numsuggestions=5):
    suggestions = wordspellcheck.getWordSuggestions(incorrect, numsuggestions,1)
    return suggestions

def getIncorrectWords(phrase):
    words_phrase = set(words(phrase))
    # print legit_words.intersection(words_phrase)
    incorrectword = words_phrase - globaldefs.legit_words.intersection(words_phrase)
    return incorrectword

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
    if in_list == -1:
        return -1
    outsplit = ''
    for i in in_list:
        if not isinstance(i, list):
            outsplit += " " + i
        else:
            outsplit += split2string(i)
    return outsplit

def splitWord(word):
<<<<<<< HEAD:src/phrasespellcheck.py
    in_words = words(file(globaldefs.DICTIONARY_PATH).read())
=======
    in_words = words(file('word.list').read())
>>>>>>> 8d647dcf2d7d44155dbd3761bc3e195d254ad64c:phrasespellcheck.py
    out_rev = split2string(splitlong(word, in_words,'rev'))
    out_fwd = split2string(splitlong(word, in_words,'fwd'))

    out_rev_bad=False
    out_fwd_bad=False

    if out_rev != -1:
        out_rev = out_rev.split()
    else:
        out_rev_bad = True
    if out_fwd != -1:
        out_fwd = out_fwd.split()
    else:
        out_fwd_bad = True

    p_out_rev = 0
    p_out_fwd = 0

    if not out_rev_bad:
        for out in out_rev:
            if out in globaldefs.prior_hashtable:
                p_out_rev += globaldefs.prior_hashtable[out]

    if not out_fwd_bad:
        for out in out_fwd:
            if out in globaldefs.prior_hashtable:
                p_out_fwd += globaldefs.prior_hashtable[out]

    if max(p_out_rev,p_out_fwd) == 0:
        return -1
    if p_out_rev > p_out_fwd:
        # return [[' '.join(out_rev),1],[' '.join(out_fwd),0]]
        return [' '.join(out_rev),1]
    else:
        # return [[' '.join(out_fwd),1],[' '.join(out_rev),0]]
        return [' '.join(out_fwd),1]

def getPhraseSuggestionsFromFile(filename):
    suggestionDict = OrderedDict()
    with open(filename) as f:
        for line in f:
<<<<<<< HEAD:src/phrasespellcheck.py
            try:
                (incorrectword, suggestions)=makePhraseChanges(line,True,True)
                suggestionDict[incorrectword]=suggestions
            except:
                print Exception
=======
            suggestionDict[line]=makePhraseChanges(line,True,True)
>>>>>>> 8d647dcf2d7d44155dbd3761bc3e195d254ad64c:phrasespellcheck.py
    f.close()
    return suggestionDict

def makePhraseChanges(phrase, bayesian=True,splitting=True):
<<<<<<< HEAD:src/phrasespellcheck.py
    suggestions =[]
    suggestions_split=[]
    suggestions_bayes=[]
    incorrectword = ''
    if splitting:
        splitDict = getSplitCorrectionsDict(phrase)
        if splitDict!=-1 and len(splitDict)>0:
            for key in splitDict:
                # correctedPhrase[correctedPhrase.index(key)] = splitDict[key]
                suggestions_split.append(splitDict[key][0])
                # suggestions_split.append(splitDict[key][1])
                incorrectword = key

            # return (incorrectword, suggestions)

    (incorrectword, suggestions_bayes) = getPhraseSuggestionsDict(phrase, 3-len(suggestions_split),incorrectword)
    temp_suggestion = []
    for count,suggestion in enumerate(suggestions_bayes):
        if count == 2:
            temp_suggestion = suggestion
            break
        suggestions.append(suggestion)

    if len(suggestions_split) > 0:
        suggestions.append([suggestions_split[0],0])
    else:
        suggestions.append(temp_suggestion)
    return (incorrectword,suggestions)
=======
    BayesianDict = getPhraseSuggestionsDict(phrase)
    if splitting:
        splitDict = getSplitCorrectionsDict(phrase)
        print BayesianDict, splitDict

        for key in splitDict:
            if key in BayesianDict:
                BayesianDict.pop(key)

    correctedPhrase = phrase.split()

    for key in BayesianDict:
        correctedword = BayesianDict[key][0][0]
        correctedPhrase[correctedPhrase.index(key)] = correctedword

    if splitting:
        for key in splitDict:
            correctedPhrase[correctedPhrase.index(key)] = splitDict[key]


    correctedPhrase = ' '.join(correctedPhrase)
    # print correctedPhrase
    return correctedPhrase
>>>>>>> 8d647dcf2d7d44155dbd3761bc3e195d254ad64c:phrasespellcheck.py

def getSplitCorrectionsDict(phrase):
    incorrectwords = list(getIncorrectWords(phrase))
    splitDict = {}
    for incorrectword in incorrectwords:
        splitout = splitWord(incorrectword)
        if splitout != -1 and len(splitout) != len(incorrectword):
            splitDict[incorrectword] = splitout
    return splitDict

def getPhraseSuggestionsDict(phrase,left,lookfor=''):
    suggestions_out = []
    incorrectword_out = ''
    numsuggestions = 5
    incorrectwords = list(getIncorrectWords(phrase))
    #Change this!
    if len(lookfor)>0:
        incorrectwords = [lookfor]
    suggestionScoreDict = {}    #Key: Word, Value: Dictionary (Key: Suggestion, Value = score)
    sortedsuggestionScoreDict = {}

    splitDict = {}

    if len(incorrectwords) == 0:
        incorrectwords = list(set(words(phrase)))
        numsuggestions = 3
    for incorrectword in incorrectwords:
        suggestions = getWordSuggestions(incorrectword, numsuggestions)
        suggestions_keys = [suggestion[0] for suggestion in suggestions]
        suggestionScoreDict[incorrectword] = dict.fromkeys(suggestions_keys)
#        output_likelihoods = dict.fromkeys(suggestions)
        for suggestion in suggestions:
            if suggestion[0] in likelihoods_dict:
                suggestionScoreDict[incorrectword][suggestion[0]] = math.log(suggestion[1])  #Change to prior, no?
#                print set(likelihoods_dict[suggestion].keys()).intersection(get_neighbours(words(phrase), incorrectword, window))
                for testnbr in get_neighbours(words(phrase), incorrectword, window):
                    if testnbr in likelihoods_dict[suggestion[0]]:
                        suggestionScoreDict[incorrectword][suggestion[0]] += math.log(likelihoods_dict[suggestion[0]][testnbr])
                    else:
                        suggestionScoreDict[incorrectword][suggestion[0]] += math.log(smooth_constant/float((sum_count_dict[suggestion[0]]+smooth_constant*vocab_size)))
            else:
                suggestionScoreDict[incorrectword][suggestion[0]] = -float("inf")

            sortedsuggestionScoreDict[incorrectword] = sorted(suggestionScoreDict[incorrectword].items(), key=operator.itemgetter(1), reverse=True)

<<<<<<< HEAD:src/phrasespellcheck.py
    for candidate in sortedsuggestionScoreDict:
        if sortedsuggestionScoreDict[candidate][0][0]!=candidate:
            for i in range(len(sortedsuggestionScoreDict[candidate])):
                if left > 0:
                    if candidate != sortedsuggestionScoreDict[candidate][i][0]:
                        incorrectword_out = candidate
                        suggestions_out.append([sortedsuggestionScoreDict[candidate][i][0],sortedsuggestionScoreDict[candidate][i][1]])
                        left -= 1
                else:
                    break

    return (incorrectword_out, suggestions_out)
    # return sortedsuggestionScoreDict

def writeDictToFile(suggestiondict,fout, maxnum):
    fo = open(fout,'w')
    for word in suggestiondict:
        towrite = word+'\t'
        for correction in suggestiondict[word]:
            towrite += correction[0] + '\t' + str(correction[1]) + '\t'
        fo.write(towrite + '\n')
=======
    print sortedsuggestionScoreDict
    return sortedsuggestionScoreDict

def writeDictToFile(suggestiondict, fin, fout, maxnum):
    fo = open(fout,'w')

    with open(fin, 'rb') as fi:
        reader = csv.reader(fi)
        for row in reader:
            input_word = row[0]
            towrite = input_word+'\t'+suggestiondict[input_word]
            # for count, word in enumerate(suggestiondict[input_word]):
            #     if count == maxnum:
            #         break
            #     towrite += word[0] + '\t' + str(word[1]) + '\t'
            print towrite
            fo.write(towrite + '\n')
    fi.close()
>>>>>>> 8d647dcf2d7d44155dbd3761bc3e195d254ad64c:phrasespellcheck.py
    fo.close()

window = 5
smooth_constant = 1e-5
vocab_size = len(globaldefs.legit_words)
print 'Loading context likelihoods'
(likelihoods_dict, sum_count_dict) = loadLikelihoodDict()
print 'Context likelihoods loaded!'
#------------------------------------------------------------


#----------------------Main------------------------------
# getPhraseSuggestionsFromFile('test2', )
if __name__ == "__main__":
<<<<<<< HEAD:src/phrasespellcheck.py
    if len(sys.argv) != 2:
        print "usage: python wordspellcheck.py <input_file>"
        sys.exit(1)

    fin = sys.argv[1]
    # fin = 'test2'
    suggestiondict = getPhraseSuggestionsFromFile(fin)  #Ordered dict
    writeDictToFile(suggestiondict, fin+'PSC', 3)
=======
    # if len(sys.argv) != 2:
    #     print "usage: python wordspellcheck.py <input_file>"
    #     sys.exit(1)
    #
    # fin = sys.argv[1]
    # # print getWordSuggestionsForFile(sys.argv[1])
    fin = 'test2'
    suggestiondict = getPhraseSuggestionsFromFile(fin)
    writeDictToFile(suggestiondict, fin, fin+'PSC', 3)
>>>>>>> 8d647dcf2d7d44155dbd3761bc3e195d254ad64c:phrasespellcheck.py
    print "Output written to " + fin+'PSC'
#------------------------------------------------------------
