__author__ = 'deepak'
import re
import cPickle
import math
import operator

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

def getWordSuggestions(incorrect):
    suggestions = ['giant', 'ant', 'meant', 'stunt']
    return suggestions

def getVocabSet():
    f = open('word.list')
    out = set(words(f.read()))
    f.close()
    return out

def getIncorrectWords(phrase):
    words_phrase = set(words(phrase))
    legit_words = getVocabSet()
    print legit_words.intersection(words_phrase)
    incorrectword = words_phrase - legit_words.intersection(words_phrase)
    return incorrectword

#----------------------Main------------------------------
window = 5
smooth_constant = 1e-5
phrase = "a geant leap for mankind"
#saveLikelihoodDict(5)
(likelihoods_dict, sum_count_dict) = loadLikelihoodDict()
incorrectwords = getIncorrectWords(phrase)
vocab_size = len(getVocabSet())

#Change this!
suggestions = getWordSuggestions(incorrectwords)
output_likelihoods = dict.fromkeys(suggestions)

for incorrectword in incorrectwords:
    for suggestion in suggestions:
        if suggestion in likelihoods_dict:
            output_likelihoods[suggestion] = 0
            print set(likelihoods_dict[suggestion].keys()).intersection(get_neighbours(words(phrase), incorrectword, window))
            for testnbr in get_neighbours(words(phrase), incorrectword, window):

                if testnbr in likelihoods_dict[suggestion]:
                    print math.log(likelihoods_dict[suggestion][testnbr])
                    output_likelihoods[suggestion] += math.log(likelihoods_dict[suggestion][testnbr])
                else:
                    print math.log(smooth_constant/float((sum_count_dict[suggestion]+smooth_constant*vocab_size)))
                    output_likelihoods[suggestion] += math.log(smooth_constant/float((sum_count_dict[suggestion]+smooth_constant*vocab_size)))
    sorted_x = sorted(output_likelihoods.items(), key=operator.itemgetter(1), reverse=True)
    print sorted_x
