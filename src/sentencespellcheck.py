import nltk
from nltk.corpus import state_union
from nltk.tokenize import PunktSentenceTokenizer
import cPickle
from nltk.tag import pos_tag, map_tag
import math
import operator
import wordspellcheck
import csv
import globaldefs
import re, sys
from collections import OrderedDict

#-----------<<Starting>>--Sentence Spell Checker--------------------
def save_custom_tokenizer():
    train_text = file('../data/brownuntagged.txt').read()
    custom_sent_tokenizer= PunktSentenceTokenizer(train_text)
    pickle_file = open('custom_tokenizer.save', 'wb')
    cPickle.dump(custom_sent_tokenizer,pickle_file, protocol=cPickle.HIGHEST_PROTOCOL)
    pickle_file.close()

def load_custom_tokenizer():
    pickle_file = open('../data/custom_tokenizer.save', 'rb')
    custom_sent_tokenizer = cPickle.load(pickle_file)
    pickle_file.close()
    return custom_sent_tokenizer

def save_brown_tagged(window_pos, leftORright):
    # leftORright will tell whether to look on left or right of the word to generate
    # POS tag.
    train_text = file('../data/brownuntagged.txt').readlines()
    tagged_corpra_list = []
    corpra_dict = {}
    word_list = []
    for count, line in enumerate(train_text):
        text = nltk.word_tokenize(line)
        posTagged = pos_tag(text)
        simplifiedTags = [(word, map_tag('en-ptb', 'universal', tag)) for word, tag in posTagged]
        tagged_corpra_list += simplifiedTags
        word_list += text
        print count
    if leftORright == 'left' :
        for count, (word, tag) in enumerate(tagged_corpra_list[window_pos:]):
            if word not in corpra_dict:
                corpra_dict[word] = {}
            joined_tag = ''
            for i in range(window_pos):
                joined_tag += tagged_corpra_list[count+i][1]
            if joined_tag not in corpra_dict[word]:
                corpra_dict[word][joined_tag] = 0
            corpra_dict[word][joined_tag] += 1

    if leftORright == 'right':
         for count, (word, tag) in enumerate(tagged_corpra_list[:-window_pos]):
            if word not in corpra_dict:
                corpra_dict[word] = {}
            joined_tag = ''
            for i in range(window_pos):
                joined_tag += tagged_corpra_list[count+i+1][1]
            if joined_tag not in corpra_dict[word]:
                corpra_dict[word][joined_tag] = 0
            corpra_dict[word][joined_tag] += 1

    if leftORright == 'both':
         for count, (word, tag) in enumerate(tagged_corpra_list[window_pos:-window_pos]):
            if word not in corpra_dict:
                corpra_dict[word] = {}
            joined_tag = ''
            for i in range(window_pos):
                joined_tag += tagged_corpra_list[count+i][1]
            temp_count = count+window_pos+1
            for i in range(window_pos):
                joined_tag += tagged_corpra_list[temp_count+i][1]
            if joined_tag not in corpra_dict[word]:
                corpra_dict[word][joined_tag] = 0
            corpra_dict[word][joined_tag] += 1

    pickle_file = open('../data/brown_tagged_win' + str(window_pos) + '_' + leftORright + '.save', 'wb')
    cPickle.dump(corpra_dict, pickle_file, protocol=cPickle.HIGHEST_PROTOCOL)
    pickle_file.close()

def load_brown_tagged():
    pickle_file = open('../data/brown_tagged_win' + str(window_pos) + '_' + leftORright + '.save', 'rb')
    tagged_corprus = cPickle.load(pickle_file)
    pickle_file.close()
    return tagged_corprus

def get_tagged_label_for_incorrect_word(simplifiedTags, given_word, window_pos):
    joined_tag = ''
    if leftORright == 'left':
        for count, (word, tag) in enumerate(simplifiedTags):
            if word == given_word:
                for i in range(window_pos):
                    joined_tag += simplifiedTags[count-window_pos+i][1]

    if leftORright == 'right':
        for count, (word, tag) in enumerate(simplifiedTags[:-window_pos]):
            if word == given_word:
                for i in range(window_pos):
                    joined_tag += simplifiedTags[count+i+1][1]

    if leftORright == 'both':
        for count, (word, tag) in enumerate(simplifiedTags[:-window_pos]):
            if word == given_word:
                for i in range(window_pos):
                    joined_tag += simplifiedTags[count-window_pos+i][1]
                for i in range(window_pos):
                    joined_tag += simplifiedTags[count+i+1][1]

    return joined_tag

def get_POS_suggestions(filename, tagged_corpus):
    f = open(filename, 'r')
    sentences_read = f.readlines()
    sentences_read = map(lambda x: x.strip(),sentences_read)
    sugg_dict_toreturn = OrderedDict()
    correct_word = ''

    for sentence in sentences_read:
        try:
            tokens = nltk.word_tokenize(sentence)
            posTagged = pos_tag(tokens)
            simplifiedTags = [(word, map_tag('en-ptb', 'universal', tag)) for word, tag in posTagged]
            output_likelihoods = {}
            sum_count_dict = {}
            for iteration, wrd in enumerate(tagged_corpus.keys()):
                sum_count_dict[wrd] = sum(tagged_corpus[wrd].values())

            incorrectwords = getIncorrectWords(sentence)
            #print incorrectwords
            for incorrectword in incorrectwords:
                #---------from Abhishek's---------------
                temp_suggestions = getWordSuggestions(incorrectword,numsuggestions=5)
                suggestions = [z[0] for z in temp_suggestions]
                output_likelihoods = dict.fromkeys(suggestions)
                for key in output_likelihoods.keys():
                    output_likelihoods[key] = 1e-300
                #print suggestions
                label = get_tagged_label_for_incorrect_word(simplifiedTags, incorrectword, window_pos)
                #print label
                for suggestion in suggestions:
                    if suggestion in tagged_corpus:
                        output_likelihoods[suggestion] = 0
                        if label in tagged_corpus[suggestion]:
                            #print math.log(tagged_corpus[suggestion][label])
                            #print suggestion, tagged_corpus[suggestion][label]
                            output_likelihoods[suggestion] += math.log((smooth_constant+tagged_corpus[suggestion][label])/float((sum_count_dict[wrd]+smooth_constant*vocab_size_pos)))
                        else:
                            #print math.log(smooth_constant/float((sum_count_dict[suggestion]+smooth_constant*vocab_size_pos)))
                            output_likelihoods[suggestion] += math.log(smooth_constant/float((sum_count_dict[suggestion]+smooth_constant*vocab_size_pos)))
                sorted_out_likelihoods = sorted(output_likelihoods.items(), key=operator.itemgetter(1), reverse=True)
                #print sorted_out_likelihoods
                #print sorted_out_likelihoods
                correct_word = [sorted_out_likelihoods[0], sorted_out_likelihoods[1], sorted_out_likelihoods[2]]
                sugg_dict_toreturn[incorrectword] = correct_word
        except:
            pass
    f.close()
    return sugg_dict_toreturn

# def getPOSSuggestionsFromFile(filename):
#     suggestionDict = {}
#     with open(filename) as f:
#         for line in f:
#             get_POS_suggestions(line)
#     f.close()
#     suggestions[]
#     return suggestionDict

#-----------<<Ending>>--Sentence Spell Checker--------------------

#-----------<<Starting>>--Phrase Spell Checker--------------------
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
    wrd_list = words(open('../data/brownuntagged.txt', 'r').read())
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
    in_words = words(file(globaldefs.DICTIONARY_PATH).read())
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
            try:
                (incorrectword, suggestions)=makePhraseChanges(line,True,True)
                suggestionDict[incorrectword]=suggestions
            except:
                pass
    f.close()
    return suggestionDict


def makePhraseChanges(phrase, bayesian=True,splitting=True):
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

def getSplitCorrectionsDict(phrase):
    incorrectwords = list(getIncorrectWords(phrase))
    splitDict = {}
    for incorrectword in incorrectwords:
        splitout = splitWord(incorrectword)
        if splitout != -1 and len(splitout) != len(incorrectword):
            splitDict[incorrectword] = splitout
    return splitDict

def getPhraseSuggestionsDict(phrase, left,lookfor=''):
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
    fo.close()

def get_final_suggestions_for_sentence(filename):
    pos_suggestions =  get_POS_suggestions('test2', tagged_corpus)
    #saveLikelihoodDict(5)
    phrase_suggestions = getPhraseSuggestionsFromFile('test2')

    final_suggestions = OrderedDict()

    for key in pos_suggestions.keys():
        final_suggestions[key] = [pos_suggestions[key][0]]+[pos_suggestions[key][1]]
        if key in phrase_suggestions:
            if phrase_suggestions[key][0][0] != pos_suggestions[key][0][0] and phrase_suggestions[key][0][0] != pos_suggestions[key][1][0]:
                final_suggestions[key].append(phrase_suggestions[key][0])
            else:
                final_suggestions[key].append(pos_suggestions[key][2])
        else:
            final_suggestions[key].append(pos_suggestions[key][2])

    for key in phrase_suggestions.keys():
        if key not in final_suggestions:
            final_suggestions[key] = phrase_suggestions[key]

    return final_suggestions


   # if len(sys.argv) != 2:
    #     print "usage: python wordspellcheck.py <input_file>"
    #     sys.exit(1)

#-----------<<Ending>>--Phrase Spell Checker--------------------


#--------------------------------Globals----------------------------
#-------------------------------------------------------------------
window_pos = 1
vocab_size_pos = 12 ** window_pos
smooth_constant = 1e-5
leftORright = 'left'
#-------------------------------------------------------------------
window = 5
smooth_constant = 1e-5
vocab_size = len(globaldefs.legit_words)
print 'Loading context likelihoods'
(likelihoods_dict, sum_count_dict) = loadLikelihoodDict()
print 'Context likelihoods loaded!'
tagged_corpus = load_brown_tagged()
#-------------------------------------------------------------------
#-------------------------------------------------------------------


#----------------------------------Main-----------------------------

if len(sys.argv) != 2:
    print "usage: python wordspellcheck.py <input_file>"
    sys.exit(1)
fin = sys.argv[1]
final_suggestions = get_final_suggestions_for_sentence(fin)  #Ordered dict
writeDictToFile(final_suggestions, fin+'SSC', 3)
print "Output written to " + fin+'SSC'

# fin = 'test2'
# final_suggestions = get_final_suggestions_for_sentence(fin)
# writeDictToFile(final_suggestions, fin+'SSC', 3)

# sentence = 'The roers police now shift to they east'
# print getIncorrectWords(sentence)