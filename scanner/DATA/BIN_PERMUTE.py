'''
Calculates the number of optional iterations for 0,1 over a list of X.
converts these into matrix of 4x4, and lastly [super slow] check for 'push' duplications,
eg:  given: 1234[2341, 3412, 4123] are considered duplicates
'''
import math
import itertools
import numpy as np

# i = 0
# length = 9
# shapeAsMatrix = []

# allOptions = list(itertools.product([0, 1], repeat=length))
# for option in allOptions:
#     shapeAsMatrix.append(np.array(option).reshape(3, 3))

# print('\n', len(allOptions))



arr =[[0,0,0,1,0,1,0,1,0],[1,0,1,1,1,1,1,1,1],[0,1,1,1,1,1,1,1,1],[1,0,1,0,1,0,0,1,0],[1,0,0,0,1,0,0,1,0],[1,0,1,0,0,0,0,0,0],[0,0,0,1,0,1,0,1,0],[1,1,1,1,0,1,0,1,0],[0,1,1,1,0,1,1,0,0],[0,1,0,1,1,1,1,0,1],[1,1,0,1,0,0,0,0,0],[1,0,1,0,0,1,0,1,1],[0,0,0,1,1,0,0,0,0],[0,0,0,0,1,1,1,0,0],[0,1,0,1,1,1,0,0,0],[0,1,0,1,1,1,1,1,1],[1,1,1,0,0,0,1,1,0],[0,0,0,1,1,1,1,1,1],[1,1,0,1,1,0,0,0,0],[0,1,1,0,0,0,0,0,0],[1,1,1,1,1,1,1,0,0],[1,0,1,0,0,1,1,1,0],[1,0,1,0,1,0,0,0,0],[1,1,0,0,1,0,0,0,0]]


c=0
for i in arr:
    npi = np.reshape(i, (3, 3))
    for j in range(0,4):
        mat=  np.rot90(npi, j,(-1,0))
        print ('\n',np.reshape(mat, (3,3)))
           # print(mat.flatten())
        c+= 1
    print (c/4, "----------")    




