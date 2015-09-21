import operator

def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    operations = ['i','d','s']

    previous_row = range(len(s2) + 1)
    min_prev_row = 0
    min_curr = 0
    min_row = 0
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        min_prev_row = min_row
        min_row = 999
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            min_index, min_value = min(enumerate([insertions,deletions,substitutions]), key=operator.itemgetter(1))
            min_curr = min_value

            if min_curr < min_row:
                min_row = min_curr
                loc = [i,j]
                operation = min_index
            current_row.append(min_value)

#            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
        print min_row
#        if min_prev_row < min_row:
#            print s1,s2
#            print s1[loc[0]],s2[loc[1]], operations[operation]

    return previous_row[-1]

levenshtein('ba', 'ab')