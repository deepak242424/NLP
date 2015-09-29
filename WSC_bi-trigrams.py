import re, collections
from operator import itemgetter
import cPickle

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
        return cnt/float(len(set.union(set(lis2),set(lis1))))
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

def gen_inverted_idx(all_bigram_dict, all_trigram_dict):
    temp_idx_dic = {}
    for key in all_bigram_dict.keys():
        for val in all_bigram_dict[key]:
            if val not in temp_idx_dic.keys():
                temp_idx_dic[val] = []
            temp_idx_dic[val].append(key)

    for key in all_trigram_dict.keys():
        for val in all_trigram_dict[key]:
            if val not in temp_idx_dic.keys():
                temp_idx_dic[val] = []
            temp_idx_dic[val].append(key)
    return temp_idx_dic

in_bigrams, in_trigrams = get_bitri(in_words)
inverted_idx_dic = gen_inverted_idx(in_bigrams, in_trigrams)

save_tuple = (in_bigrams, in_trigrams, inverted_idx_dic)

f = file('bi_tri_index.save', 'wb')
cPickle.dump(save_tuple, f, protocol=cPickle.HIGHEST_PROTOCOL)
f.close()


#print gen_candidates('furnitur', in_bigrams, in_trigrams)