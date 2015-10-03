import re
import cPickle
import math

def words(text): return re.findall('[a-z]+', text.lower())

def getWordList():
   s = words(file('word.list').read())
   out = dict.fromkeys(s, 0)
   return out

prior_hashtable = getWordList()
prior_hashtable

vocab = words(file('brownuntagged.txt').read())
vocab = set(vocab)
vocab_size = len(vocab)
vocab_count = {}



def find_neighbours(word_list, given_word, window):
    neighbours = []
    for count, wrd in enumerate(word_list):
        if wrd == given_word:
            neighbours += word_list[max(count-window,0):count] + wrd_list[count+1:min(count+window+1, len(word_list))]
    return neighbours

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





pickle_file = open('likelihoods_WSD.save', 'rb')
(likelihood_dict,vocab_count) = cPickle.load(pickle_file)
pickle_file.close()

common_words = ['the','of','and','to','a','in','for','is','on','that','by','this','with','i','you','it','not','or','be',
                'are','from','at','as','your','all','have','new','more','an','was','we','will','can','us','about','if',
                'my','has','search','free','but','our','one','other','do','no','they','he','up','may','what','which',
                'their','out','use','any','there','see','only','so','his','when','here','who']


wrd_list = words(open('sample_big.txt', 'r').read())
print len(wrd_list)
#candidates = ['earth', 'eat','death' , 'ear']
candidates = ['earth', 'car']

neigh_suspect = find_neighbours(wrd_list, 'eath', window=5)
dic_result = {}
#print likelihood_dict[candidates[0]]
#print likelihood_dict[candidates[1]]
#print neigh_suspect

for candid in candidates:
    if candid in likelihood_dict:
        #intersection = set(likelihood_dict[candid].keys()).intersection(set(neigh_suspect))
        #intersection = neigh_suspect
#        print "For " + candid + ": "
#        print intersection
        #total_likelihood = [likelihood_dict[candid][k] for k in intersection]
        #total_likelihood = [likelihood_dict[candid][k] for k in neigh_suspect if k in prior_hashtable]
        total_likelihood = []

        vocab_size = len(words(file('word.list').read()))


        for k in neigh_suspect:
            if k in likelihood_dict[candid]:
                total_likelihood.append(likelihood_dict[candid][k])
            else:
                total_likelihood.append(math.log((1/(float(vocab_count[candid])+len(vocab_count)))))

        print total_likelihood
    if sum(total_likelihood) in dic_result:
        dic_result[sum(total_likelihood)].append(candid)
    else:
        dic_result[sum(total_likelihood)] = [candid]
    # what if candid not in likelihood_dict

print dic_result[max(dic_result.keys())]
print dic_result