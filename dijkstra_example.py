# https://gist.github.com/avrilcoghlan/7466166
# https://avrilomics.blogspot.com/2013/11/dijkstras.html
# https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.sparse.csgraph.dijkstra.html
genes = ['g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7']

G1 = 0
G2 = 1
G3 = 2
G4 = 3
G5 = 4
G6 = 5
G7 = 6

START_NODE = [G1, G7]
END_NODE = G2

Matrix = [[0 for i in range(len(genes))] for j in range(len(genes))]

Matrix[G1][G4] = 12
# Matrix[G4][G1] = 12
Matrix[G1][G3] = 23
# Matrix[G3][G1] = 23
Matrix[G2][G3] = 5
# Matrix[G3][G2] = 5
Matrix[G2][G7] = 16
# Matrix[G7][G2] = 16
Matrix[G3][G5] = 17
# Matrix[G5][G3] = 17
Matrix[G3][G4] = 9
# Matrix[G4][G3] = 9
Matrix[G4][G5] = 18
# Matrix[G5][G4] = 18
# Matrix[G4][G6] = 25
# Matrix[G6][G4] = 25
# Matrix[G5][G6] = 7
# Matrix[G6][G5] = 7
Matrix[G5][G7] = 22
# Matrix[G7][G5] = 22

# make a sparse matrix
from scipy.sparse import csr_matrix
Matrix_sparse = csr_matrix(Matrix)

# run Dijkstra's algorithm, starting at index 0
from scipy.sparse.csgraph import dijkstra
distances, predecessors = dijkstra(Matrix_sparse, directed= False, unweighted=True, indices=START_NODE,return_predecessors=True)

print(distances)
print(predecessors)

# print out the distance to END_NODE
print("distance to {} = {}".format(genes[END_NODE], distances[END_NODE]))

# build up path
path = []
i = END_NODE
while i != START_NODE:
    path.append(genes[i])
    i = predecessors[i]
path.append(genes[START_NODE])

# print out the path
print("path=",path[::-1])