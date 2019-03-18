import logging

try:
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import dijkstra
    USE_SCIPY = True
except ImportError:
    USE_SCIPY = False
    logging.error("Module scipy not found. Install for faster computer player....")

    
def dijkstra_quoridor(graph, start_node, winning_row, return_path_else_distance=False):
    # lode optimized for quoridor
    # will perform algorithm, until one of the target nodes is reached.
    # in unweigthed graphs, the first reached target node is the closest node to start_node
    # if return_path_else_distance = True: return path with passed nodes.
    #      if path will be returned: it INCLUDES start AND winning node. there will be one node more than there are steps needed to go to the end.
    # print("target nodes: {}".format(target_nodes))
    # print("\n".join([ "{}:{}".format(key, value) for key, value in graph.items()]))
    unvisited = {}
    visited = {}
    current = start_node
    currentDistance = 0
    unvisited[current] = currentDistance

    if return_path_else_distance:
        parents = {}  # stores the parent for each node (so the shortest path can be reassembled afterwards)

    unvisited_shortest_dist_node = None
    unvisited_shortest_dist = 10000
    
    #if start IS on the winning row, there is nothing to be done here.
    if start_node[1] == winning_row:
        if return_path_else_distance:
            return []
        else:
            return 0

    while True:
        #visit current node
        for neighbour in graph[current]:  # go over all neighbours of current node.

            if neighbour[1] == winning_row:
                # # this is the optimization. When target node found, return right away!
                # print("winning row...for neighbour:{} dist: {}".format(neighbour, currentDistance + 1))
                # print(neighbour)
                if return_path_else_distance:

                    # reconstruct path
                    node = current
                    path = [neighbour]
                    while True:
                        path.insert(0, node)

                        try:
                            node = parents[node]
                        except:
                            # probable cause: so close to winning line, that there was never a chance to create the child:parent node.
                            # todo: make sure this is the case!
                            #print (parents)
                            #print(node)
                            #print(path)
                            #print("startnod:{}".format(start_node))
                            node = start_node
                            #raise ("panic")



                        if node == start_node:
                            #print("fieef: {}  {}".format(parents, path))
                            path.insert(0, node)
                            break
                    return path
                else:
                    return currentDistance + 1
                
            if neighbour not in visited: 
                newDistance = currentDistance + 1  # check distance
                if neighbour not in unvisited or unvisited[neighbour] > newDistance:  # if new distance less, apply!
                    if return_path_else_distance:
                        # set the parent so the shortest path can be reconstructed afterwards
                        parents[neighbour] = current

                    unvisited[neighbour] = newDistance  #
                    if newDistance < unvisited_shortest_dist:
                        unvisited_shortest_dist_node = neighbour
                
                
        visited[current] = currentDistance
        
        del unvisited[current]
       
        # pick next node as current. (always the one with shortest path length! This makes the algorithm work)
        if unvisited:  # length > 0
            if (unvisited_shortest_dist == 10000):
                # a lot of hassle to try to avoid the sorted algorithm (results in minor time savings).
                current, currentDistance = sorted(unvisited.items(), key = lambda x: x[1])[0]
            else:
                current = unvisited_shortest_dist_node
                currentDistance = unvisited_shortest_dist
                unvisited_shortest_dist = 10000
        else:
            return None #at a given point when locked, there is no unvisited left.

'''
def dijkstra_quoridor_path(graph, start_node, winning_row, return_path_else_distance=False):
    # lode optimized for quoridor
    # will perform algorithm, until one of the target nodes is reached.
    # in unweigthed graphs, the first reached target node is the closest node to start_node
    # if return_path_else_distance = True: return path with passed nodes.
    # print("target nodes: {}".format(target_nodes))
    # print("\n".join([ "{}:{}".format(key, value) for key, value in graph.items()]))
    unvisited = {}
    visited = {}
    current = start_node
    currentDistance = 0
    unvisited[current] = currentDistance

    unvisited_shortest_dist_node = None
    unvisited_shortest_dist = 10000

    # if start IS on the winning row, there is nothing to be done here.
    if start_node[1] == winning_row:
        if return_path_else_distance:
            return []
        else:
            return 0

    while True:
        # visit current node
        for neighbour in graph[current]:  # go over all neighbours of current node.

            if neighbour[1] == winning_row:
                # # this is the optimization. When target node found, return right away!
                # print("winning row...for neighbour:{} dist: {}".format(neighbour, currentDistance + 1))
                # print(neighbour)
                if return_path_else_distance:
                    return visited
                else:
                    return currentDistance + 1

            if neighbour not in visited:
                newDistance = currentDistance + 1  # check distance
                if neighbour not in unvisited or unvisited[neighbour] > newDistance:  # if new distance less, apply!
                    unvisited[neighbour] = newDistance
                    if newDistance < unvisited_shortest_dist:
                        unvisited_shortest_dist_node = neighbour

        visited[current] = currentDistance

        del unvisited[current]

        # pick next node as current. (always the one with shortest path length! This makes the algorithm work)
        if unvisited:  # length > 0
            if (unvisited_shortest_dist == 10000):
                # a lot of hassle to try to avoid the sorted algorithm (results in minor time savings).
                current, currentDistance = sorted(unvisited.items(), key=lambda x: x[1])[0]
            else:
                current = unvisited_shortest_dist_node
                currentDistance = unvisited_shortest_dist
                unvisited_shortest_dist = 10000
        else:
            return None  # at a given point when locked, there is no unvisited left.
'''
def dijkstra_distance_to_target(graph, start_node, target_nodes):
    # lode optimized for quoridor
    # will perform algorithm, until one of the target nodes is reached.
    # in unweigthed graphs, the first reached target node is the closest node to start_node
    
    # print("target nodes: {}".format(target_nodes))
    # print("\n".join([ "{}:{}".format(key, value) for key, value in graph.items()]))
    unvisited = {}
    visited = {}
    current = start_node
    currentDistance = 0
    unvisited[current] = currentDistance
   
    unvisited_shortest_dist_node = None
    unvisited_shortest_dist = 10000
    while True:
        #visit current node
        for neighbour in graph[current]:  # go over all neighbours of current node.
            if neighbour in target_nodes:
                # this is the optimization. When target node found, return right away!
                return currentDistance + 1
            if neighbour not in visited: 
                newDistance = currentDistance + 1  # check distance
                if neighbour not in unvisited or unvisited[neighbour] > newDistance:  # if new distance less, apply!
                    unvisited[neighbour] = newDistance
                    if newDistance < unvisited_shortest_dist:
                        unvisited_shortest_dist_node = neighbour
                    
        visited[current] = currentDistance
        
        del unvisited[current]
       
        # pick next node as current. (always the one with shortest path length! This makes the algorithm work)
        if unvisited:  # length > 0
            if (unvisited_shortest_dist == 10000):
                # a lot of hassle to try to avoid the sorted algorithm (results in minor time savings).
                current, currentDistance = sorted(unvisited.items(), key = lambda x: x[1])[0]
            else:
                current = unvisited_shortest_dist_node
                currentDistance = unvisited_shortest_dist
                unvisited_shortest_dist = 10000
        else:
            return None #at a given point when locked, there in no unvisited left.
    
# def dijkstra_distance_to_target(graph, start_node, target_nodes):
    # # lode optimized for quoridor
    # # will perform algorithm, until one of the target nodes is reached.
    # # in unweigthed graphs, the first reached target node is the closest node to start_node
    
    # # print("target nodes: {}".format(target_nodes))
    # # print("\n".join([ "{}:{}".format(key, value) for key, value in graph.items()]))
    # unvisited = {node: None for node in graph.keys()} #using None as +inf
    # visited = {}
    # current = start_node
    # currentDistance = 0
    # unvisited[current] = currentDistance
    # toBeVisited = [current]
    
    # while len(toBeVisited) > 0:
        # #visit current node
        # # print("current:{}".format(current))
        # for neighbour in graph[current]:  # go over all neighbours of current node.
            # if neighbour in target_nodes:
                # # print("target node!: {}".format(neighbour))
                # return currentDistance + 1
            # if neighbour in unvisited: 
                # toBeVisited.append(neighbour)
                
                # newDistance = currentDistance + 1  # check distance
                # if unvisited[neighbour] is None or unvisited[neighbour] > newDistance:  # if new distance less, apply!
                    # unvisited[neighbour] = newDistance
                    
        # visited[current] = currentDistance #was erroneously tabbed!
        
        # toBeVisited.remove(current)
        # del unvisited[current]
         
        # candidates = [node for node in unvisited.items() if node[1]]  # if node is not None (infinite), add it to candidates.
       
       # # pick next node as current. (always the one with shortest 
        # if candidates:  # length > 0
            # current, currentDistance = sorted(candidates, key = lambda x: x[1])[0]
        # else:
            # return None # no candidates at a given point when locked in.
            
    # # none of the target nodes was reached.
    # return None
    
    
def dijkstra_fast(matrix, start_nodes):
    #matrix is a list of lists: default value is zero. all nodes on x axis, all nodes on y axis. When nodes connected, on x and y axis, node crossing, set it to 1.
    # unweighted, undirected.
    # for row in matrix:
    # print(matrix[80])
    Matrix_sparse = csr_matrix(matrix)
    # run Dijkstra's algorithm, starting at index 0
    # distances, predecessors = dijkstra(Matrix_sparse, directed=False, unweighted=True, indices=start_nodes ,return_predecessors=True)
    distances = dijkstra(Matrix_sparse, directed=False, unweighted=True, indices=start_nodes ,return_predecessors=False)

    # print(distances)
    # print(predecessors)
    return (distances)
    # print out the distance to END_NODE
    # print("distance to {} = {}".format(genes[END_NODE], distances[END_NODE]))

def dijkstra_graph(graph, start_node):
    #graph = {node:{neighbour1:dist, neigh2:dist,...}, node2:{neighbournode1:dist,...}}
    unvisited = {node: None for node in list(graph)} #using None as +inf
    visited = {}
    current = start_node
    currentDistance = 0
    unvisited[current] = currentDistance

    while True:
        for neighbour, distance in graph[current].items():
            
            if neighbour in unvisited: 
                
                newDistance = currentDistance + distance
                if unvisited[neighbour] is None or unvisited[neighbour] > newDistance:
                    print("neigh: {}".format(neighbour))
                    unvisited[neighbour] = newDistance
        visited[current] = currentDistance
        print("visited:{}".format(visited))

        del unvisited[current]
        if not unvisited: 
            break
         
        candidates = [node for node in unvisited.items() if node[1]]
        print("candidates: {}".format(candidates))
       
        current, currentDistance = sorted(candidates, key = lambda x: x[1])[0]
        
        print("current: {}".format(current))
        
    return visited

    
def dijkstra_graph_isolated_nodes_enabled(graph, start_node):
    #graph = {node:{neighbour1:dist, neigh2:dist,...}, node2:{neighbournode1:dist,...}}
    unvisited = {node: None for node in list(graph)} #using None as +inf
    visited = {}
    current = start_node
    currentDistance = 0
    unvisited[current] = currentDistance
    toBeVisited = [current]
    
    while len(toBeVisited) > 0:
        #visit current node
        for neighbour, distance in graph[current].items():  # go over all neighbours of current node.
            
            if neighbour in unvisited: 
                toBeVisited.append(neighbour)
                
                newDistance = currentDistance + distance  # check distance
                if unvisited[neighbour] is None or unvisited[neighbour] > newDistance:  # if new distance less, apply!
                    unvisited[neighbour] = newDistance
        visited[current] = currentDistance #was erroneously tabbed!
        
        toBeVisited.remove(current)
        del unvisited[current]
         
        candidates = [node for node in unvisited.items() if node[1]]  # if node is not None (infinite), add it to candidates.
              
        if len(candidates)>0:
            current, currentDistance = sorted(candidates, key = lambda x: x[1])[0]
        else:
            break
    return visited    

def dijkstra_graph_isolated_nodes_enabled_unweighted(graph, start_node):
    #all distances considered 1
    #graph = {node:[neighbour1, neigh2,...], node2:[neighbournode1,...]}
    unvisited = {node: None for node in list(graph)} #using None as +inf
    visited = {}
    current = start_node
    currentDistance = 0
    unvisited[current] = currentDistance
    toBeVisited = [current]
    
    while len(toBeVisited) > 0:
        #visit current node
        for neighbour in graph[current]:  # go over all neighbours of current node.
            
            if neighbour in unvisited: 
                toBeVisited.append(neighbour)
                
                newDistance = currentDistance + 1  # check distance
                if unvisited[neighbour] is None or unvisited[neighbour] > newDistance:  # if new distance less, apply!
                    unvisited[neighbour] = newDistance
        visited[current] = currentDistance #was erroneously tabbed!
        
        toBeVisited.remove(current)
        del unvisited[current]
         
        candidates = [node for node in unvisited.items() if node[1]]  # if node is not None (infinite), add it to candidates.
              
        if len(candidates)>0:
            current, currentDistance = sorted(candidates, key = lambda x: x[1])[0]
        else:
            break
    return visited 
    
# def dijkstra_graph_unweighted(graph, start_node):
#     #graph = {node:[neighbour1, neigh2,...], node2:[neighbournode1,...]}
#     unvisited = {node: None for node in list(graph)} #using None as +inf
#     visited = {}
#     current = start_node
#     currentDistance = 0
#     unvisited[current] = currentDistance
#
#     while True:
#         for neighbour in graph[current]:
#             distance = 1
#             if neighbour not in unvisited: continue
#             newDistance = currentDistance + distance
#             if unvisited[neighbour] is None or unvisited[neighbour] > newDistance:
#                 unvisited[neighbour] = newDistance
#         visited[current] = currentDistance
#         del unvisited[current]
#         if not unvisited: break
#         candidates = [node for node in unvisited.items() if node[1]]
#         current, currentDistance = sorted(candidates, key = lambda x: x[1])[0]
#     return visited
    
if __name__ == "__main__":

    print("Dijkstra weighted:")
    nodes = ('A', 'B', 'C', 'D', 'E', 'F', 'G')
    distances = {
    'B': {'A': 5, 'D': 1, 'G': 2},
    'A': {'B': 5, 'D': 3, 'E': 12, 'F' :5},
    'D': {'B': 1, 'G': 1, 'E': 1, 'A': 3},
    'G': {'B': 2, 'D': 1, 'C': 2},
    'C': {'G': 2, 'E': 1, 'F': 16},
    'E': {'A': 12, 'D': 1, 'C': 1, 'F': 2},
    'F': {'A': 5, 'E': 2, 'C': 16}}
    graph = {node:distances[node] for node in nodes}
    print(graph)
    print(dijkstra_graph(graph, 'B')) # return the distances to all nodes.
    print("-------------------------------")
    nodes = ('A', 'B', 'C', 'D', 'E', 'F', 'G')
    
    distances_D_isolated = {
    'B': {'A': 5,  'G': 2},
    'A': {'B': 5,  'E': 12, 'F' :5},
    'D':{'A':5},
    'G': {'B': 2, 'D':2,  'C': 2},
    'C': {'G': 2, 'E': 1, 'F': 16},
    'E': {'A': 12, 'C': 1, 'F': 2},
    'F': {'A': 5, 'E': 2, 'C': 16}}
    # nodes = ('A', 'B',  'D')
    # distances_D_isolated = {
    # 'B': {'A': 5 },
    # 'A': {'B': 5},
    # 'D': {'A':3, 'B':3}}
    
    print("weighted d isolated:")
    graph = {node:distances_D_isolated[node] for node in nodes}
    print(graph)
    print(dijkstra_graph(graph, 'B')) # return the distances to all nodes.
    print("-------------------------------")
    print("Dijkstra weighted as 1:")
    nodes = ('A', 'B', 'C', 'D', 'E', 'F', 'G')
    distances = {
    'B': {'A': 1, 'D': 1, 'G': 1},
    'A': {'B': 1, 'D': 1, 'E': 1, 'F' :1},
    'D': {'B': 1, 'G': 1, 'E': 1, 'A': 1},
    'G': {'B': 1, 'D': 1, 'C': 1},
    'C': {'G': 1, 'E': 1, 'F': 1},
    'E': {'A': 1, 'D': 1, 'C': 1, 'F': 1},
    'F': {'A': 1, 'E': 1, 'C': 1}}
    graph = {node:distances[node] for node in nodes}
    # print(graph)
    # print(dijkstra_graph(graph, 'B')) # return the distances to all nodes.
    
    print("Dijkstra unweighted:")
   
    nodes = ('A', 'B', 'C', 'D', 'E', 'F', 'G')
    neighbours = {
     'B': ['A', 'D', 'G'],
    'A': ['B', 'D', 'E', 'F'],
    'D': ['B', 'G', 'E', 'A'],
    'G': ['B', 'D', 'C'],
    'C': ['G', 'E', 'F'],
    'E': ['A', 'D', 'C', 'F'],
    'F': ['A', 'E', 'C']}
    graph = {node:neighbours[node] for node in nodes}
    # print(graph)
    # print(dijkstra_graph_unweighted(graph, 'B')) # return the distances to all nodes.