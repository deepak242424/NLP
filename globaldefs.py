__author__ = 'Abhishek'
import numpy as np
import csv
import cPickle

def loadPriorHashTable():
    f = open('prior_hashtable.save', 'rb')
    prior_hashtable = cPickle.load(f)
    f.close()
    return prior_hashtable

def getConfusionMatrices():
    rev_mat = np.loadtxt(open('confusion/rev.txt','r'),delimiter=' ',skiprows=0)+1
    ins_mat = np.loadtxt(open('confusion/ins.txt','r'),delimiter=' ',skiprows=0)+1
    del_mat = np.loadtxt(open('confusion/del.txt','r'),delimiter=' ',skiprows=0)+1
    sub_mat = np.loadtxt(open('confusion/sub.txt','r'),delimiter=' ',skiprows=0).T+1
    toreturn = (rev_mat,ins_mat,del_mat,sub_mat)
    return toreturn

def getBigramMatrix():

    bigrammat = np.zeros((26,26))
    f = open('count_2l.txt','r')
    x = csv.reader(f,delimiter='\t')
    for elem in list(x):
        i1 = alphabet.index(elem[0][0])
        i2 = alphabet.index(elem[0][1])
        bigrammat[i1][i2]=int(elem[1])
    return bigrammat


DICTIONARY_PATH = 'word.list'
alphabet = 'abcdefghijklmnopqrstuvwxyz~'
prior_hashtable = loadPriorHashTable()
prior_hashtable_keys = set(prior_hashtable.keys())
(rev_mat,ins_mat,del_mat,sub_mat) = getConfusionMatrices()
bigrammat = getBigramMatrix()
print "Loading dictionaries..."
#(in_bigrams, in_trigrams, inverted_idx_dic) = loadgrams()
print "Dictionaries loaded!"
