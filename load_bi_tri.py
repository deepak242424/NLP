import cPickle

f = open('bi_tri_index.save', 'rb')
(in_bigrams, in_trigrams, inverted_idx_dic) = cPickle.load(f)

print in_trigrams['correct']
print in_bigrams['correct']
print inverted_idx_dic['rre']
print inverted_idx_dic['rr']

f.close()