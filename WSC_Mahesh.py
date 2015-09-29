__author__ = 'Student'

__author__ = 'Student'

import re, collections
import sys
from heapq import nlargest
from operator import itemgetter

def words(text): return re.findall('[a-z]+', text.lower())

flag = 0
prior = words(file('C:/Users/Student/Desktop/big.txt').read())
prior_hashtable = collections.defaultdict(lambda: 1)
for line in prior:

    # temp = line.split("\t")
    # prior_hashtable [temp[0].lower()] = temp[1]
    #print line
    prior_hashtable[line] += 1

# test1 = open('C:/Users/Student/Desktop/spell-errors.txt', 'r')
# sample = collections.defaultdict(lambda: 1)
# for line in test1:
#     temp1 = line.split(":")
#     temp2 = line.split(",")

alphabet = 'abcdefghijklmnopqrstuvwxyz'

def edit_distance_1(text):
   #print 'test1'
   s = [(text[:i], text[i:]) for i in range(len(text) + 1)]
   deletion    = [a + b[1:] for a, b in s if b]
   transposition = [a + b[1] + b[0] + b[2:] for a, b in s if len(b)>1]
   replacement   = [a + c + b[1:] for a, b in s for c in alphabet if b]
   insertion   = [a + c + b     for a, b in s for c in alphabet]
   #print 'test2'
   return set(deletion + transposition + replacement + insertion)

def edit_distance_2(text):
    #print 'test'
    return set(e2 for e1 in edit_distance_1(text) for e2 in edit_distance_2(e1) if e2 in prior_hashtable)


def available(words): return set(w for w in words if w in prior_hashtable)

def spellcheck(word):
    candidates = available([word]) or available(edit_distance_1(word)) or edit_distance_1(word) or [word]
    #print candidates
    print max(candidates, key=prior_hashtable.get)
    # x = max(candidates, key=prior_hashtable.get)
    # print prior_hashtable[x]
    final_list = []
    # final_list.append(x,prior_hashtable[x])
    # print final_list

    for key, value in prior_hashtable.iteritems():
        if (candidates.__contains__(key)):
            final_list.append((key,value))
    final_list.sort(key = itemgetter(1),reverse=True)
    #print final_list
    # print (x,prior_hashtable[x])
    print nlargest(10, final_list,key=prior_hashtable.get)

    return max(candidates, key=prior_hashtable.get)


in_words = words(file('C:/Users/Student/Desktop/big.txt').read())


def get_bigrams(wrd):
    bigrams = []
    for i in range(len(wrd)-1):
        bigrams.append(wrd[i:i+2])
    return bigrams

def get_trigrams(wrd):
    trigrams = []
    for i in range(len(wrd)-2):
        trigrams.append(wrd[i:i+3])
    return trigrams

def get_bitri(word_list):
    bigrams = {}
    trigrams = {}
    for wrd in word_list:
        bigrams[wrd] = get_bigrams(wrd)
        trigrams[wrd] = get_trigrams(wrd)
    return bigrams, trigrams

def match_grams(lis1, lis2):
    cnt = 0
    for val1 in lis1:
        for val2 in lis2:
            if val1 == val2:
                cnt += 1
    if len(lis2) !=0:
        return cnt/float(len(set.union(set(lis1),set(lis2))))
    else:
        return 0

def gen_candidates(wrd, all_bigrams_dict, all_trigrams_dict):
    tri = get_trigrams(wrd)
    bi = get_bigrams(wrd)
    bi_scores = []
    tri_scores = []
    for key in all_bigrams_dict.keys():
        score = match_grams(bi, all_bigrams_dict[key])
        if (len(wrd) - len(key)) <3:
            bi_scores.append((key,score))
            #print len(key)
    for key in all_trigrams_dict.keys():
        score = match_grams(tri, all_trigrams_dict[key])
        if (len(wrd) - len(key)) <3:
            tri_scores.append((key,score))
            #print len(key)
    bi_scores.sort(key = itemgetter(1),reverse=True)
    tri_scores.sort(key = itemgetter(1), reverse=True)


    return bi_scores[:10], tri_scores[:10]


in_bigrams, in_trigrams = get_bitri(in_words)
# input_word = raw_input('Enter a word: ')
# spellcheck(input_word)
# in_bigrams, in_trigrams = get_bitri(in_words)
# bitri_hashtable = collections.defaultdict(lambda: 1)
# bitri_hashtable = gen_candidates(input_word, in_bigrams, in_trigrams)
# print gen_candidates(input_word, in_bigrams, in_trigrams)



def final_output():
    input_word = raw_input('Enter a word: ')
    spellcheck(input_word)
    print gen_candidates(input_word, in_bigrams, in_trigrams)
    input_continue = raw_input('Do you want to continue? (y/n) ')
    input_continue = input_continue.lower()
    #print input_continue
    while (input_continue != 'n'):
       final_output()
    print('Thank You')
    sys.exit()

if (flag == 0):
    flag = flag + 1
    final_output()

#print ('test')


# input_word = raw_input('Enter a word: ')
# spellcheck(input_word)
# print gen_candidates(input_word, in_bigrams, in_trigrams)
# final_output()

