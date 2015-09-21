import operator
import networkx as nx

def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    levenmat = [[0 for col in range(len(s2))] for row in range(len(s1))]

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    operations = ['i','s','d']

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            min_index, min_value = min(enumerate([insertions,deletions,substitutions]), key=operator.itemgetter(1))
            levenmat[i][j] = min_value

            current_row.append(min_value)
#            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    print levenmat

    curr_min = [0,0]
    edits = [];

    while curr_min[0]!=len(s1) & curr_min[1]!=len(s2):
        curr_min_val = levenmat[curr_min[0]][curr_min[1]]
        nbrs = [levenmat[curr_min[0]+1][curr_min[1]], levenmat[curr_min[0]+1][curr_min[1]+1], levenmat[curr_min[0]+1][curr_min[1]+1]]
        nbrlocs = [[1,0],[1,1],[0,1]]
        min_index, min_value = min(enumerate(nbrs))
        if min_value > curr_min_val:
            edits.append((operations[min_index], s1[i]))

        curr_min
        print min_value

    return previous_row[-1]

def getLevenPath(G, currnode, levenmat, i, j):
    rows = len(levenmat)
    cols = len(levenmat[0])
    if i== rows and j==cols:
        return tree
    else:
        #Look at the three neighbours
        nbrlocs = [[i+1,j],[i+1,j+1],[i,j+1]]
        validnbrs = []
        validvals = []
        for n in range(3):
            if(nbrlocs[n][0]<=rows and nbrlocs[n][1] <= cols):
                validnbrs.append(nbrlocs[n])
                validvals.append(levenmat[nbrlocs[n][0]][nbrlocs[n][1]])

        minval = min(validvals)
        for validnbr in validnbrs:
            if levenmat[validnbr[0]][validnbr[1]] == minval:
                 tree.add_node


print levenshtein('correct', 'corect')