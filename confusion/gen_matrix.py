f_rev = open('rev.txt','r')
f_add = open('add.txt','r')
f_sub = open('sub.txt','r')
f_del = open('del.txt','r')

def create_mat(in_file):
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


rev_mat = create_mat(f_rev)
add_mat = create_mat(f_add)
del_mat = create_mat(f_del)
sub_mat = create_mat(f_sub)

#print rev_mat[3][8]
