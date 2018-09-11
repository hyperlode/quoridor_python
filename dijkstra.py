# nodes = ('A', 'B', 'C', 'D', 'E', 'F', 'G')
# distances = {
    # 'B': {'A': 5, 'D': 1, 'G': 2},
    # 'A': {'B': 5, 'D': 3, 'E': 12, 'F' :5},
    # 'D': {'B': 1, 'G': 1, 'E': 1, 'A': 3},
    # 'G': {'B': 2, 'D': 1, 'C': 2},
    # 'C': {'G': 2, 'E': 1, 'F': 16},
    # 'E': {'A': 12, 'D': 1, 'C': 1, 'F': 2},
    # 'F': {'A': 5, 'E': 2, 'C': 16}}

    
# def dijkstra(graph, start_node):
    # unvisited = {node: None for node in nodes} #using None as +inf
    # visited = {}
    # current = start_node
    # currentDistance = 0
    # unvisited[current] = currentDistance

    # while True:
        # for neighbour, distance in distances[current].items():
            # if neighbour not in unvisited: continue
            # newDistance = currentDistance + distance
            # if unvisited[neighbour] is None or unvisited[neighbour] > newDistance:
                # unvisited[neighbour] = newDistance
        # visited[current] = currentDistance
        # del unvisited[current]
        # if not unvisited: break
        # candidates = [node for node in unvisited.items() if node[1]]
        # current, currentDistance = sorted(candidates, key = lambda x: x[1])[0]

    # return visited

def dijkstra_graph(graph, start_node):
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
                    unvisited[neighbour] = newDistance
                    visited[current] = currentDistance

        del unvisited[current]
        if not unvisited: 
            break
         
        candidates = [node for node in unvisited.items() if node[1]]
        print(candidates)
       
        current, currentDistance = sorted(candidates, key = lambda x: x[1])[0]
    return visited
    
def dijkstra_graph_unweighted(graph, start_node):
    #graph = {node:[neighbour1, neigh2,...], node2:[neighbournode1,...]}
    unvisited = {node: None for node in list(graph)} #using None as +inf
    visited = {}
    current = start_node
    currentDistance = 0
    unvisited[current] = currentDistance

    while True:
        for neighbour in graph[current]:
            distance = 1
            if neighbour not in unvisited: continue
            newDistance = currentDistance + distance
            if unvisited[neighbour] is None or unvisited[neighbour] > newDistance:
                unvisited[neighbour] = newDistance
        visited[current] = currentDistance
        del unvisited[current]
        if not unvisited: break
        candidates = [node for node in unvisited.items() if node[1]]
        current, currentDistance = sorted(candidates, key = lambda x: x[1])[0]
    return visited
    
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
    # print(graph)
    # print(dijkstra_graph(graph, 'B')) # return the distances to all nodes.
    
    nodes = ('A', 'B', 'C', 'D', 'E', 'F', 'G')
    
    # distances_D_isolated = {
    # 'B': {'A': 5,  'G': 2},
    # 'A': {'B': 5,  'E': 12, 'F' :5},
    # 'D':{'A':5},
    # 'G': {'B': 2, 'D':2,  'C': 2},
    # 'C': {'G': 2, 'E': 1, 'F': 16},
    # 'E': {'A': 12, 'C': 1, 'F': 2},
    # 'F': {'A': 5, 'E': 2, 'C': 16}}
    nodes = ('A', 'B',  'D')
    distances_D_isolated = {
    'B': {'A': 5 },
    'A': {'B': 5, 'D':2},
    'D': {'A':3, 'B':3}}
    
    print("weighted d isolated:")
    graph = {node:distances_D_isolated[node] for node in nodes}
    print(graph)
    print(dijkstra_graph(graph, 'B')) # return the distances to all nodes.
    
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