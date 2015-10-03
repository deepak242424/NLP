import re
import cPickle
import math

def words(text): return re.findall('[a-z]+', text.lower())

vocab = words(file('brownuntagged.txt').read())
vocab = set(vocab)
vocab_size = len(vocab)
vocab_count = {}


def get_neighbour_counts(window, word_list):
    main_dict = {}
    for count, wrd in enumerate(word_list):
        local_neighbours = word_list[max(count-window,0):count] + wrd_list[count+1:min(count+window+1, len(word_list))]
        if wrd not in main_dict:
            main_dict[wrd] = {}
        for neigh in local_neighbours:
            if neigh not in main_dict[wrd]:
                main_dict[wrd][neigh] = 0
            main_dict[wrd][neigh] += 1
        print 'GN'+ str(count)
    return main_dict

def get_likelihoods(neighbours):
    dict_likeli = neighbours.copy()
    for iteration, wrd in enumerate(neighbours.keys()):
        count = sum(neighbours[wrd].values())
        vocab_count[wrd] = count
        for neigh in neighbours[wrd]:
            dict_likeli[wrd][neigh] = math.log((1+neighbours[wrd][neigh])/(float(count)+vocab_size))
        print iteration
    return dict_likeli

wrd_list = words(open('brownuntagged.txt', 'r').read())
neighbours_dict = get_neighbour_counts(window=5, word_list=wrd_list)
likelihoods_dict = get_likelihoods(neighbours_dict)

#print likelihoods_dict

tostore = (likelihoods_dict, vocab_count)

pickle_file = open('likelihoods_WSD.save', 'wb')
cPickle.dump(tostore, pickle_file, protocol=cPickle.HIGHEST_PROTOCOL)
pickle_file.close()
