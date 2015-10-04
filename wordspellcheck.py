__author__ = 'abhishek'
#This script takes a file name containing 1 incorrect word per line as input, and prints the output in the specified output file

import re, collections
import sys
import csv
from heapq import nlargest
from operator import itemgetter
import cPickle
import numpy as np
import os
import math
from metaphone import doublemetaphone
import globaldefs


def words(text): return re.findall('[a-z]+', text.lower())

def getWordList():
    s = words(file(globaldefs.DICTIONARY_PATH).read())
    out = dict.fromkeys(s, 0)
    return out

def savePriorHashTable():
    prior = words(file('brownuntagged.txt').read())
    prior_hashtable = {}

    for line in prior:
        if line not in prior_hashtable:
            prior_hashtable[line] = 1
        prior_hashtable[line.lower()] += 1

    f = file('prior_hashtable.save', 'wb')
    cPickle.dump(prior_hashtable, f, protocol=cPickle.HIGHEST_PROTOCOL)
    f.close()

# def loadPriorHashTable():
#     f = open('prior_hashtable.save', 'rb')
#     prior_hashtable = cPickle.load(f)
#     f.close()
#     return prior_hashtable

def edit_distance_1(text):
    #Returns all words at edit distance 1 from the input word,"text"
    s = [(text[:i], text[i:]) for i in range(len(text) + 1)]
    deletion    = [a + b[1:] for a, b in s if b]
    transposition = [a + b[1] + b[0] + b[2:] for a, b in s if len(b)>1]
    replacement   = [a + c + b[1:] for a, b in s for c in globaldefs.alphabet if b]
    insertion   = [a + c + b     for a, b in s for c in globaldefs.alphabet]
    return set(deletion + transposition + replacement + insertion)

def edit_distance_2(text):
    #Returns all words at edit distance 2 from the input word,"text"
    return set(e2 for e1 in edit_distance_1_transform(text) for e2 in edit_distance_2(e1) if e2 in globaldefs.prior_hashtable)

def edit_distance_1_transform(text):
    #Returns all words at edit distance 1 from the input word,"text"
    edit_dict = {}
    s = [(text[:i], text[i:]) for i in range(len(text) + 1)]

#    deletion    = [a + b[1:] for a, b in s if b]
    for a, b in s:
        if a and b:
            word = a + b[1:]
            if word in edit_dict:
                edit_dict[word].append('d'+a[-1]+b[0])
            else:
                edit_dict[word] = ['d'+a[-1]+b[0]]
        elif not a and b:
            word = a + b[1:]
            if word in edit_dict:
                edit_dict[word].append('d'+'~'+b[0])
            else:
                edit_dict[word] = ['d'+'~'+b[0]]

#    transposition = [a + b[1] + b[0] + b[2:] for a, b in s if len(b)>1]
    for a, b in s:
        if len(b)>1:
            word = a + b[1] + b[0] + b[2:]
            if word in edit_dict:
                edit_dict[word].append('t'+b[0]+b[1])
            else:
                edit_dict[word] = ['t'+b[0]+b[1]]

#    substitution   = [a + c + b[1:] for a, b in s for c in alphabet if b]
    for a, b in s:
        for c in globaldefs.alphabet[0:25]:
            if b:
                word = a + c + b[1:]
                if word in edit_dict:
                    edit_dict[word].append('s'+b[0]+c)
                else:
                    edit_dict[word] = ['s'+b[0]+c]

#    insertion   = [a + c + b     for a, b in s for c in alphabet]
    for a, b in s:
        for c in globaldefs.alphabet[0:25]:
            if a:
                word = a + c + b
                if word in edit_dict:
                    edit_dict[word].append('i'+a[-1]+c)
                else:
                    edit_dict[word] = ['i'+a[-1]+c]
            else:
                word = a + c + b
                if word in edit_dict:
                    edit_dict[word].append('i'+'~'+c)
                else:
                    edit_dict[word] = ['i'+'~'+c]

    if text in edit_dict:
        edit_dict.pop(text,None)

    return edit_dict

def edit_distance_2_transform(orig_word, edit_dict1):
    #Returns all words at edit distance 2 from the input word,"text"
    edit_dict2 = {}

    for key,val in edit_dict1.iteritems():
        edit_dict_test = edit_distance_1_transform(key)
        available_keys = globaldefs.prior_hashtable_keys.intersection(set(edit_dict_test.keys()))-set(orig_word)
        for key_bad in list(set(edit_dict_test.keys()) - set(available_keys)):
            edit_dict_test.pop(key_bad,None)

        for key_test,val_test in edit_dict_test.iteritems():
            for val_test_elem in val_test:
                for val_elem in val:
                    if key_test not in edit_dict2:
                        edit_dict2[key_test] = []
                    edit_dict2[key_test].append(val_elem+val_test_elem)
    return edit_dict2

def vector(in_file):
   lines = in_file.readlines()

   lines = map(lambda x : x.strip(),lines)
   lines = [int(float(line)) for line in lines]

   mat = [[0 for x in range(26)] for x in range(26)]
   k = 0
   for i in range(26):
       for j in range(26):
           mat[i][j] = lines[k]
           k = k+1
   return mat

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

def available(words, prior_hashtable):
    return set(w for w in words if w in prior_hashtable.keys())

def mergedict(dict1, dict2):
    outdict = dict()
    for key in dict1:
        outdict[key] = [dict1[key]]
    for key in dict2:
        if key in dict1:
            outdict[key].append(dict2[key])
        else:
            outdict[key] = [dict2[key]]
    return outdict

def Pchange(operation):
    #Given a sequence of operations, computes its probability of occurrence using the confusion matrices
    if operation[1] in globaldefs.alphabet:
        index1 = globaldefs.alphabet.index(operation[1])
    else:
        index1 = 0
    if operation[2] in globaldefs.alphabet:
        index2 = globaldefs.alphabet.index(operation[2])
    else:
        index2 = 0

    if operation[0]=='d':
        if index1 == 26:
            out = globaldefs.del_mat[index1][index2] / sum(globaldefs.bigrammat[:][index2])
        else:
            out = globaldefs.del_mat[index1][index2] / globaldefs.bigrammat[index1][index2]
    elif operation[0]=='i':
        out = globaldefs.ins_mat[index1][index2] / sum(globaldefs.bigrammat[index2][:])
    elif operation[0]=='s':
        out = globaldefs.sub_mat[index1][index2] / sum(globaldefs.bigrammat[index1][:])
    else:
        out = globaldefs.rev_mat[index1][index2] / globaldefs.bigrammat[index1][index2]
    return out

def getBayesian0(word):
    prior_hashtable = globaldefs.loadPriorHashTable()
    candidates = available([word], prior_hashtable) or available(edit_distance_1(word), prior_hashtable) or edit_distance_1(word) or [word]
    print max(candidates, key=prior_hashtable.get)
    final_list = []

    for key, value in prior_hashtable.iteritems():
        if (candidates.__contains__(key)):
            final_list.append((key,value))
    final_list.sort(key = itemgetter(1),reverse=True)
    print nlargest(10, final_list,key=prior_hashtable.get)

    return max(candidates, key=prior_hashtable.get)

def getBayesian1(word, numsuggestions=5):
    edit1worddict = edit_distance_1_transform(word)
    edit2worddict = edit_distance_2_transform(word, edit1worddict)

    probabdict = {}

    #Remove incorrect edit 1 words
    available_keys = globaldefs.prior_hashtable_keys.intersection(set(edit1worddict.keys()))
    for key_bad in list(set(edit1worddict.keys()) - set(available_keys)):
        edit1worddict.pop(key_bad,None)

    for edit1word,vals in edit1worddict.iteritems():
        p = 0
        for val in vals:
            p += Pchange(val)
        probabdict[edit1word]=p

    for edit2word,vals in edit2worddict.iteritems():
        if edit2word in probabdict:
            p = probabdict[edit2word]
        else:
            p=0
        for val in vals:
            p += Pchange(val[0:3])*Pchange(val[3:])
        probabdict[edit2word]=p

    if word in globaldefs.prior_hashtable:
        # print "The word, "+ word+ " is correct."
        probabdict[word] = 1

    sorted_probab_dict = sorted(probabdict.items(), key=itemgetter(1),reverse=True)
    return sorted_probab_dict[0:numsuggestions]

def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    levenmat = [[0 for col in range(len(s2))] for row in range(len(s1))]

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    operations = ['i','d','s']
    costs = [1,1,2];
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + costs[0] # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + costs[1]       # than s2
            substitutions = previous_row[j] + costs[2]*(c1 != c2)
            min_index, min_value = min(enumerate([insertions,deletions,substitutions]), key=itemgetter(1))
            levenmat[i][j] = min_value

            current_row.append(min_value)
#            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return levenmat[-1][-1]

def gen_candidates(wrd, all_bigrams_dict, all_trigrams_dict, inverted_idx_dic, mode):
    bigrams = get_bigrams(wrd)
    bi_matchset = set()
    for bigram in bigrams:
        if bigram in inverted_idx_dic:
            for word_match in inverted_idx_dic[bigram]:
                bi_matchset.add(word_match)
    bi_scores = dict()
    for bi_match in bi_matchset:
        lis2 = all_bigrams_dict[bi_match]
        bi_scores[bi_match] = jaccard(bigrams,lis2)
    bi_scores_sorted = sorted(bi_scores.items(), key=itemgetter(1),reverse=True)

    if mode == "bitri":
        tri_matchset = set()
        trigrams = get_trigrams(wrd)
        for trigram in trigrams:
            if trigram in inverted_idx_dic:
                for word_match in inverted_idx_dic[trigram]:
                    tri_matchset.add(word_match)
        tri_scores = dict()
        for tri_match in tri_matchset:
            lis2 = all_trigrams_dict[tri_match]
            tri_scores[tri_match] = jaccard(trigrams,lis2)
        tri_scores_sorted = sorted(tri_scores.items(), key=itemgetter(1),reverse=True)

    if mode == "bitri":
        return (bi_scores_sorted[:5], tri_scores_sorted[:5])
    else:
        return (bi_scores_sorted[:5])

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
    in_words = words(file(globaldefs.DICTIONARY_PATH).read())
    in_bigrams, in_trigrams = get_bitri(in_words)
    inverted_idx_dic = gen_inverted_idx(in_bigrams, in_trigrams)

    save_tuple = (in_bigrams, in_trigrams, inverted_idx_dic)

    f = file('bi_tri_index.save', 'wb')
    cPickle.dump(save_tuple, f, protocol=cPickle.HIGHEST_PROTOCOL)
    f.close()

def cleanbrown():
    files = os.listdir('brown/')
#    regex = re.compile(r"/[a-z]+", re.IGNORECASE)
    fout = open('brownuntagged.txt','w')
    for file in files:
        f = open('brown/'+file,'r')
        text = f.readlines()
        for line in text:
            line = re.sub("/[a-z]*", "", line)
            line = re.findall('[a-z]+', line.lower())
            if line!=[]:
                fout.writelines(' '.join(line))
        f.close()
    fout.close()

def getphoneticsuggestions():
    1

def saveMetaphoneIndices():
    wordphonedict = {}
    bigrams_phone = {}
    inverted_bigram_phone = {}
    in_words = words(file(globaldefs.DICTIONARY_PATH).read())
    for count,word in enumerate(in_words):
        phone_rep = doublemetaphone(word)[0]
        wordphonedict[word] = phone_rep
        bigrams_phone[word] = get_bigrams(phone_rep)
        for bigram in bigrams_phone[word]:
            if bigram not in inverted_bigram_phone:
                inverted_bigram_phone[bigram] = []
            inverted_bigram_phone[bigram].append(word)

        if count % 10000 == 0:
           print count

    towrite = (wordphonedict, bigrams_phone, inverted_bigram_phone)
    f = file('phone_indices.save', 'wb')
    cPickle.dump(towrite, f, protocol=cPickle.HIGHEST_PROTOCOL)
    f.close()

def loadMetaPhoneIndices():
    f = open('phone_indices.save', 'rb')
    (wordphonedict, bigrams_phone, inverted_bigram_phone) = cPickle.load(f)
    f.close()
    return (wordphonedict, bigrams_phone, inverted_bigram_phone)

def getWordSuggestions(input_word, numsuggestions=5, giveprobabs=0):
        x = getBayesian1(input_word,numsuggestions)
        # (bi_scores_sorted, tri_scores_sorted) = gen_candidates(input_word, in_bigrams, in_trigrams, inverted_idx_dic,"bitri")
        # print "Word: ",input_word
        # print "Bigram matches: ", bi_scores_sorted
        # print "Trigram matches: ", tri_scores_sorted
        # return x[0:numsuggestions]

        if giveprobabs == 0:
            out = []
            for i in range(min(len(x),numsuggestions)):
                out.append(x[i][0])
            return out
        else:
            return x[0:numsuggestions]

def getWordSuggestionsForFile(filename,numsuggestions=5):
    suggestionDict = {}
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            input_word = row[0]
            suggestionDict[input_word]=getWordSuggestions(input_word, numsuggestions,1)
    f.close()
    return suggestionDict

def writeDictToFile(suggestiondict, fin, fout, maxnum):
    fo = open(fout,'w')

    with open(fin, 'rb') as fi:
        reader = csv.reader(fi)
        for row in reader:
            input_word = row[0]
            towrite = input_word+'\t'
            for count, word in enumerate(suggestiondict[input_word]):
                if count == maxnum:
                    break
                towrite += word[0] + '\t' + str(word[1]) + '\t'
            fo.write(towrite + '\n')
    fi.close()
    fo.close()


# ---------------Global variables----------------------------
#----------------Run only in main----------------------------
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "usage: python wordspellcheck.py <input_file>"
        sys.exit(1)

    fin = sys.argv[1]
    # print getWordSuggestionsForFile(sys.argv[1])
    # fin = 'test'
    suggestiondict = getWordSuggestionsForFile(fin)
    writeDictToFile(suggestiondict, fin, fin+'WSC', 10)
    print "Output written to " + fin+'WSC'
#------------------------------------------------------------
