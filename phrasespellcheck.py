__author__ = 'deepak'
import re
import cPickle
import math
import operator
import wordspellcheck
import csv
import globaldefs

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

    pickle_file = open('likelihoods_WSD.save', 'wb')
    cPickle.dump(tostore, pickle_file, protocol=cPickle.HIGHEST_PROTOCOL)
    pickle_file.close()

def loadLikelihoodDict():
    pickle_file = open('likelihoods_WSD.save', 'rb')
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
    outsplit = ''
    for i in in_list:
        if not isinstance(i, list):
            outsplit += " " + i
        else:
            outsplit += split2string(i)
    return outsplit

def splitWord(word):
    in_words = words(file('word.list').read())
    out_rev = split2string(splitlong(word, in_words,'rev')).split()
    out_fwd = split2string(splitlong(word, in_words,'fwd')).split()

    p_out_rev = 0
    p_out_fwd = 0

    for out in out_rev:
        if out in globaldefs.prior_hashtable:
            p_out_rev += globaldefs.prior_hashtable[out]

    for out in out_fwd:
        if out in globaldefs.prior_hashtable:
            p_out_fwd += globaldefs.prior_hashtable[out]

    if p_out_rev > p_out_fwd:
        return ' '.join(out_rev)
    else:
        return ' '.join(out_fwd)

def getPhraseSuggestionsFromFile(filename):
    suggestionDict = {}
    with open(filename) as f:
        for line in f:
            makePhraseChanges(line,True,True)
    f.close()
    return suggestionDict

def makePhraseChanges(phrase, bayesian=True,splitting=True):
    BayesianDict = getPhraseSuggestionsDict(phrase)

    if splitting:
        splitDict = getSplitCorrectionsDict(phrase)

        for key in splitDict:
            if key in BayesianDict:
                BayesianDict.pop(key)

    correctedPhrase = phrase.split()

    for key in BayesianDict:
        correctedword = BayesianDict[key][0][0]
        correctedPhrase[correctedPhrase.index(key)] = correctedword

    if splitting:
        if key in splitDict:
            correctedPhrase[correctedPhrase.index(key)] = splitDict[key]

    correctedPhrase = ' '.join(correctedPhrase)
    # print correctedPhrase
    return correctedPhrase

def getSplitCorrectionsDict(phrase):
    incorrectwords = list(getIncorrectWords(phrase))
    splitDict = {}
    for incorrectword in incorrectwords:
        splitout = splitWord(incorrectword)
        print splitout
        if splitout != -1 and len(splitout) != len(incorrectword):
            splitDict[incorrectword] = splitout

    return splitDict

def getPhraseSuggestionsDict(phrase):
    allwrongflag = 0
    numsuggestions = 5
    incorrectwords = list(getIncorrectWords(phrase))
    #Change this!
    suggestionScoreDict = {}    #Key: Word, Value: Dictionary (Key: Suggestion, Value = score)
    sortedsuggestionScoreDict = {}

    splitDict = {}

    if len(incorrectwords) == 0:
        incorrectwords = list(set(phrase.split()))
        numsuggestions = 3
        allwrongflag = 1
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

    # print sortedsuggestionScoreDict
    return sortedsuggestionScoreDict


#----------------Global variables----------------------------
# DICTIONARY_PATH = 'word.list'
# alphabet = 'abcdefghijklmnopqrstuvwxyz~'
# prior_hashtable = wordspellcheck.loadPriorHashTable()
# prior_hashtable_keys = set(prior_hashtable.keys())
# (rev_mat,ins_mat,del_mat,sub_mat) = wordspellcheck.getConfusionMatrices()
# bigrammat = wordspellcheck.getBigramMatrix()
# # (in_bigrams, in_trigrams, inverted_idx_dic) = wordspellcheck.loadgrams()

window = 5
smooth_constant = 1e-5
vocab_size = len(globaldefs.legit_words)
print 'Loading context likelihoods'
(likelihoods_dict, sum_count_dict) = loadLikelihoodDict()
print 'Context likelihoods loaded!'
#------------------------------------------------------------


#----------------------Main------------------------------
#saveLikelihoodDict(5)
getPhraseSuggestionsFromFile('test2')
