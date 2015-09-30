__author__ = 'abhishek'
#This script takes a file name containing 1 incorrect word per line as input, and prints the output in the specified output file

import re, collections
import sys
import csv
from heapq import nlargest
from operator import itemgetter
import cPickle

def words(text): return re.findall('[a-z]+', text.lower())

def edit_distance_1(text):
    #Returns all words at edit distance 1 from the input word,"text"
    s = [(text[:i], text[i:]) for i in range(len(text) + 1)]
    deletion    = [a + b[1:] for a, b in s if b]
    transposition = [a + b[1] + b[0] + b[2:] for a, b in s if len(b)>1]
    replacement   = [a + c + b[1:] for a, b in s for c in alphabet if b]
    insertion   = [a + c + b     for a, b in s for c in alphabet]
    return set(deletion + transposition + replacement + insertion)

def edit_distance_2(text):
    #Returns all words at edit distance 2 from the input word,"text"
    return set(e2 for e1 in edit_distance_1(text) for e2 in edit_distance_2(e1) if e2 in prior_hashtable)

def get_bigrams(wrd):
    #Gives bigrams in a word
    bigrams = []
    for i in range(len(wrd)-1):
        bigrams.append(wrd[i:i+2])
    return bigrams

def get_trigrams(wrd):
    #Gives bigrams in a word
    trigrams = []
    for i in range(len(wrd)-2):
        trigrams.append(wrd[i:i+3])
    return trigrams

def get_bitri(word_list):
    #Gets bigrams and trigrams for all words in word_list
    bigrams = {}
    trigrams = {}
    for wrd in word_list:
        bigrams[wrd] = get_bigrams(wrd)
        trigrams[wrd] = get_trigrams(wrd)
    return bigrams, trigrams

def jaccard(lis1, lis2):
    lis1and2 = set(lis1).intersection(lis2)
    lis1or2 = set.union(set(lis1),set(lis2))

    if len(lis1or2) > 0:
        return float(len(lis1and2))/float(len(lis1or2))
    else:
        return 0

def available(words): return set(w for w in words if w in prior_hashtable)

def spellcheck(word):
    candidates = available([word]) or available(edit_distance_1(word)) or edit_distance_1(word) or [word]
    print max(candidates, key=prior_hashtable.get)
    final_list = []

    for key, value in prior_hashtable.iteritems():
        if (candidates.__contains__(key)):
            final_list.append((key,value))
    final_list.sort(key = itemgetter(1),reverse=True)
    print nlargest(10, final_list,key=prior_hashtable.get)

    return max(candidates, key=prior_hashtable.get)

def gen_candidates(wrd, all_bigrams_dict, all_trigrams_dict, inverted_idx_dic):
    trigrams = get_trigrams(wrd)
    bigrams = get_bigrams(wrd)

    bi_matchset = set()
    tri_matchset = set()

    for bigram in bigrams:
        for word_match in inverted_idx_dic[bigram]:
            bi_matchset.add(word_match)

    for trigram in trigrams:
        for word_match in inverted_idx_dic[trigram]:
            tri_matchset.add(word_match)

    bi_scores = dict()
    tri_scores = dict()

    for bi_match in bi_matchset:
        lis2 = all_bigrams_dict[bi_match]
        bi_scores[bi_match] = jaccard(bigrams,lis2)

    for tri_match in tri_matchset:
        lis2 = all_trigrams_dict[tri_match]
        tri_scores[tri_match] = jaccard(trigrams,lis2)

    bi_scores_sorted = sorted(bi_scores.items(), key=itemgetter(1),reverse=True)
    tri_scores_sorted = sorted(tri_scores.items(), key=itemgetter(1),reverse=True)
    return (bi_scores_sorted[:5], tri_scores_sorted[:5])

def gen_inverted_idx(all_bigram_dict, all_trigram_dict):
    temp_idx_dic = {}
    for key in all_bigram_dict.keys():
        print "Bigram for", key
        for val in all_bigram_dict[key]:
            if val not in temp_idx_dic.keys():
                temp_idx_dic[val] = []
            temp_idx_dic[val].append(key)

    for key in all_trigram_dict.keys():
        print "Trigram for", key
        for val in all_trigram_dict[key]:
            if val not in temp_idx_dic.keys():
                temp_idx_dic[val] = []
            temp_idx_dic[val].append(key)
    return temp_idx_dic

def loadgrams():
    #Load bi- and tri-grams
    f = open('bi_tri_index.save', 'rb')
    (in_bigrams, in_trigrams, inverted_idx_dic) = cPickle.load(f)
    f.close()
    return (in_bigrams, in_trigrams, inverted_idx_dic)

def savegrams():
    in_words = words(file('word.list').read())
    in_bigrams, in_trigrams = get_bitri(in_words)
    inverted_idx_dic = gen_inverted_idx(in_bigrams, in_trigrams)

    save_tuple = (in_bigrams, in_trigrams, inverted_idx_dic)

    f = file('bi_tri_index.save', 'wb')
    cPickle.dump(save_tuple, f, protocol=cPickle.HIGHEST_PROTOCOL)
    f.close()

#------------------Main--------------------#
(in_bigrams, in_trigrams, inverted_idx_dic) = loadgrams()
savegrams()
with open(sys.argv[1], 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
        input_word = row[0]
        (bi_scores_sorted, tri_scores_sorted) = gen_candidates(input_word, in_bigrams, in_trigrams, inverted_idx_dic)
        print "Word: ",input_word
        print "Bigram matches: ", bi_scores_sorted
        print "Trigram matches: ", tri_scores_sorted