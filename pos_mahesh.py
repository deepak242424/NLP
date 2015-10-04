import nltk
from nltk.corpus import state_union
from nltk.tokenize import PunktSentenceTokenizer
import cPickle
from nltk.tag import pos_tag, map_tag
import math

def save_custom_tokenizer():
    train_text = file('brownuntagged.txt').read()
    custom_sent_tokenizer= PunktSentenceTokenizer(train_text)
    pickle_file = open('custom_tokenizer.save', 'wb')
    cPickle.dump(custom_sent_tokenizer,pickle_file, protocol=cPickle.HIGHEST_PROTOCOL)
    pickle_file.close()

def load_custom_tokenizer():
    pickle_file = open('custom_tokenizer.save', 'rb')
    custom_sent_tokenizer = cPickle.load(pickle_file)
    pickle_file.close()
    return custom_sent_tokenizer

def save_brown_tagged(window, leftORright):
    # leftORright will tell whether to look on left or right of the word to generate
    # POS tag.
    train_text = file('brownuntagged.txt').readlines()
    tagged_corpra_list = []
    corpra_dict = {}
    word_list = []
    for count, line in enumerate(train_text):
        text = nltk.word_tokenize(line)
        posTagged = pos_tag(text)
        simplifiedTags = [(word, map_tag('en-ptb', 'universal', tag)) for word, tag in posTagged]
        tagged_corpra_list += simplifiedTags
        word_list += text
        print count
    if leftORright == 'left' :
        for count, (word, tag) in enumerate(tagged_corpra_list[window:]):
            if word not in corpra_dict:
                corpra_dict[word] = {}
            joined_tag = ''
            for i in range(window):
                joined_tag += tagged_corpra_list[count+i][1]
            if joined_tag not in corpra_dict[word]:
                corpra_dict[word][joined_tag] = 0
            corpra_dict[word][joined_tag] += 1

    if leftORright == 'right':
         for count, (word, tag) in enumerate(tagged_corpra_list[:-window]):
            if word not in corpra_dict:
                corpra_dict[word] = {}
            joined_tag = ''
            for i in range(window):
                joined_tag += tagged_corpra_list[count+i+1][1]
            if joined_tag not in corpra_dict[word]:
                corpra_dict[word][joined_tag] = 0
            corpra_dict[word][joined_tag] += 1

    if leftORright == 'both':
         for count, (word, tag) in enumerate(tagged_corpra_list[window:-window]):
            if word not in corpra_dict:
                corpra_dict[word] = {}
            joined_tag = ''
            for i in range(window):
                joined_tag += tagged_corpra_list[count+i][1]
            temp_count = count+window+1
            for i in range(window):
                joined_tag += tagged_corpra_list[temp_count+i][1]
            if joined_tag not in corpra_dict[word]:
                corpra_dict[word][joined_tag] = 0
            corpra_dict[word][joined_tag] += 1

    # print tagged_corpra_list
    # print train_text[:1]
    # print corpra_dict
    pickle_file = open('brown_tagged_win' + str(window) + '_' + leftORright + '.save', 'wb')
    cPickle.dump(corpra_dict, pickle_file, protocol=cPickle.HIGHEST_PROTOCOL)
    pickle_file.close()

def load_brown_tagged():
    pickle_file = open('brown_tagged_win' + str(window) + '_' + leftORright + '.save', 'rb')
    tagged_corprus = cPickle.load(pickle_file)
    pickle_file.close()
    return tagged_corprus

def get_tagged_label_for_incorrect_word(simplifiedTags, given_word, window):
    joined_tag = ''
    if leftORright == 'left':
        for count, (word, tag) in enumerate(simplifiedTags):
            if word == given_word:
                for i in range(window):
                    joined_tag += simplifiedTags[count-window+i][1]

    if leftORright == 'right':
        for count, (word, tag) in enumerate(simplifiedTags[:-window]):
            if word == given_word:
                for i in range(window):
                    joined_tag += simplifiedTags[count+i+1][1]

    if leftORright == 'both':
        for count, (word, tag) in enumerate(simplifiedTags[:-window]):
            if word == given_word:
                for i in range(window):
                    joined_tag += simplifiedTags[count-window+i][1]
                for i in range(window):
                    joined_tag += simplifiedTags[count+i+1][1]

    return joined_tag

#--------------------------------Globals----------------------------
window = 1
vocab_size = 12 ** window
smooth_constant = 1e-5
leftORright = 'both'
#-------------------------------------------------------------------


#----------------------------------Main-----------------------------
#save_brown_tagged(window, 'left')
#save_brown_tagged(window, 'right')
#save_brown_tagged(window, 'both')


tagged_corpus = load_brown_tagged()
incorrectwords = ['powre']
suggestions = ['power', 'progress', 'pure', 'pores']
sentence = 'The powre has now shift to they east'
tokens = nltk.word_tokenize(sentence)
posTagged = pos_tag(tokens)
simplifiedTags = [(word, map_tag('en-ptb', 'universal', tag)) for word, tag in posTagged]
output_likelihoods = dict.fromkeys(suggestions)



# print simplifiedTags
# print get_tagged_label_for_incorrect_word(simplifiedTags, incorrectwords[0], window)
# print tagged_corpus
#
sum_count_dict = {}
for iteration, wrd in enumerate(tagged_corpus.keys()):
    sum_count_dict[wrd] = sum(tagged_corpus[wrd].values())

for incorrectword in incorrectwords:
    label = get_tagged_label_for_incorrect_word(simplifiedTags, incorrectword, window)
    print label
    for suggestion in suggestions:
        if suggestion in tagged_corpus:
            output_likelihoods[suggestion] = 0
            if label in tagged_corpus[suggestion]:
                #print math.log(tagged_corpus[suggestion][label])
                print suggestion, tagged_corpus[suggestion][label]
                output_likelihoods[suggestion] += math.log((smooth_constant+tagged_corpus[suggestion][label])/float((sum_count_dict[wrd]+smooth_constant*vocab_size)))
            else:
                #print math.log(smooth_constant/float((sum_count_dict[suggestion]+smooth_constant*vocab_size)))
                output_likelihoods[suggestion] += math.log(smooth_constant/float((sum_count_dict[suggestion]+smooth_constant*vocab_size)))

print output_likelihoods
