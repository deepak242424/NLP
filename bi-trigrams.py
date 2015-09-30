import re, collections
from operator import itemgetter

def words(text): return re.findall('[a-z]+', text.lower())
in_words = words(file('big.txt').read())

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
        return cnt/float(len(lis2))
    else:
        return 0

def gen_candidates(wrd, all_bigrams_dict, all_trigrams_dict):
    tri = get_trigrams(wrd)
    bi = get_bigrams(wrd)
    bi_scores = []
    tri_scores = []
    for key in all_bigrams_dict.keys():
        score = match_grams(bi, all_bigrams_dict[key])
        bi_scores.append((key,score))
    for key in all_trigrams_dict.keys():
        score = match_grams(tri, all_trigrams_dict[key])
        tri_scores.append((key,score))
    bi_scores.sort(key = itemgetter(1),reverse=True)
    tri_scores.sort(key = itemgetter(1), reverse=True)
    return bi_scores[:10], tri_scores[:10]


in_bigrams, in_trigrams = get_bitri(in_words)
print gen_candidates('corect', in_bigrams, in_trigrams)