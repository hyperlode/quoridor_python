import player
import pawn
import wall
import dijkstra

BOARD_WIDTH = 9 # 9 is default should be an odd number of squares, for the pawn to be able to start in the middle.
BOARD_HEIGHT = 9# 9 is default

# board output (ASCII) visualization
BOARD_CELL_EMPTY = " "
# BOARD_CELL_PLAYER_TO_NORTH = "1"
BOARD_CELL_PLAYER_TO_NORTH =  '\u25b2'
BOARD_CELL_PLAYER_TO_SOUTH = '\u25bc' # "2"
BOARD_CELL_WALL = "O"
BOARD_CELL_WALL_BORDER = "."
BOARD_CELL_LINE_HORIZONTAL = "-"
BOARD_CELL_LINE_VERTICAL = "|"
BOARD_CELL_LINE_CROSSING = "+"

startPosX = BOARD_WIDTH // 2   # for width 9 --> 4  

PAWN_INIT_POS = [(startPosX, 0), (startPosX, BOARD_HEIGHT-1)] 
# = (PAWN_INIT_POS_X, 0), (PAWN_INIT_POS_X, BOARD_HEIGHT-1)

PAWN_WINNING_POS = [(x,BOARD_HEIGHT-1) for x in range(BOARD_WIDTH)], [(x,0) for x in range(BOARD_WIDTH)]
        

        
class Board():

    #pawn cells for 
    '''
    
    board graph:  9x9 nodes with positions for the pawn.
    wall are broken edges between nodes.
    refer to a node with a tuple (x,y)
    
    
    8
    7
    6
    5         wall lines
    4
    3
    2
    1
     a   b   c   d   e   f   g   h
     
     
    8 
    7
    6
    5
    4
    3           nodes
    2
    1
    0
       0  1   2   3   4   5   6   7   8   
       
   



    
    '''    
    
    def __init__(self):
        nodes = [(x,y) for x in range(BOARD_WIDTH) for y in range(BOARD_HEIGHT)]
        
        self.board_graph = {node:{"edges":None, "pawn":None} for node in nodes}
        # https://www.python.org/doc/essays/graphs/
        
        for node in nodes:
            x,y = node
            # neighbours = [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
            valid_neighbours = [dir(node) for dir in pawn.DIRECTIONS_ORTHO if dir(node) in nodes]    
            self.board_graph[node]["edges"] = valid_neighbours
            
        self.players = []
    
    
    def add_player(self, player_instance):
        self.players.append(player_instance)
        self.board_graph[player_instance.pawn.position]["pawn"] = player_instance
    
    def check_pawn_positions(self):
        for pl in self.players:
            node = pl.pawn.position
            okOnBoard = self.pawn_on_node(node)
            print("player {} at postion {}, ok on board:{} ".format(pl.name, node, okOnBoard))
          
    def move_pawn(self, old, new):
            self.board_graph[new]["pawn"] = self.board_graph[old]["pawn"]
            self.board_graph[old]["pawn"] = None

    def remove_wall(self,position_verbose):
        #used for undo or backwards replay.

        success = False

        # check with placed walls
        for pl in self.players:
            for w in pl.walls:
                if w.get_position("verbose") == position_verbose:
                    print("wall found")

                    #reconnect nodes
                    for node1, node2 in w.get_position("nodes"):
                        success = self.link_nodes(node1, node2)
                        if not success:
                            print(
                                "connections on the board could not be connected when removing the wall. Board might be corrupt")
                            raise Exception("board potentially corrupt.")
                            return False

                    w.reset_position(allow_reset_placed_wall=True)
                    success = True
        if not success:
            print("wall not found. check if verbose position is accurate: {}".format(position_verbose))

        return success

    def place_wall(self, new_wall):
        hori_new,vert_new,orientation_new = new_wall.get_position("lines_orientation")
        
        #check with placed walls
        for pl in self.players:
            for w in pl.walls:
                if w.status == wall.STATUS_PLACED:
                    hori, vert, orientation = w.get_position("lines_orientation")
                    
                    #check for overlapping center points.
                    if hori == hori_new and vert ==vert_new :
                        # centerpoint is the same, so for sure a failure. We just have to check what kind of failure:
                        if orientation==orientation_new:
                            print("attempt to place wall on exactly the same location of another wall.")
                        else:
                            print("attempt to place wall with same centerpoint as other wall (but in another orientation).")
                        return False

                    # check for overlapping wall (placed in same direction, on same line, not sharing center point, just half a wall overlap.
                    if orientation == orientation_new:
                        # print("oooorientation_newohori_newoehoorientation_newheohorientation_newhehoeoh")
                        # print (orientation)
                        # print ("x:{},y:{}".format(vert, hori))
                        # print ("x:{},y:{}".format(vert_new, hori_new))
                        # print (w)
                        # print ("new_wall:{}".format(new_wall))
                        if orientation == wall.NORTH_SOUTH:
                            #x is the same.
                            #check for y at least 2 different.
                            if (vert == vert_new) and abs(hori - hori_new) < 2:
                                #overlap!
                                print("north south walls on same line and overlapping")
                                return False
                                
                        elif orientation == wall.EAST_WEST:
                            if (hori == hori_new) and abs(vert - vert_new) < 2:
                                #overlap!
                                print("east-west walls are on the same line and overlapping")
                                return False

        print("wall can be placed.")

        #unlink nodes that are separated by the wall
        for node1, node2 in new_wall.get_position("nodes"):
            success = self.unlink_nodes(node1, node2)
            if not success:
                print("connections on the board could not be severed when placing the wall. Board might be corrupt")
                raise Exception("board potentially corrupt.")
                return False
        return True

    def check_wall_valid(self, new_wall):
        pass
        
    def distances_to_winning_node(self):    
        # returns tuple with distances for each player to nearest winning square. None if not reachable
        shortest_path = [None,None]
        
        #get proper weighted graph
        board_graph_weighted = {node: {n:1 for n in self.board_graph[node]["edges"] } for node in list(self.board_graph)}
        
        # for node in list(board_graph_weighted):
            # print("{}:{}".format(node, board_graph_weighted[node]))
        # print("nodes: {}".format(len(list(board_graph_weighted))) )
        nodes_sorted = sorted( list(board_graph_weighted), key = lambda pos: 10*pos[0]+pos[1])
        # print("board nodes:")
        # for n in nodes_sorted:
            # print("{}:{}".format(n,board_graph_weighted[n]))
           
        
            
        # board_graph_weighted = {}
        # print(self.board_graph)
        # for node in list(self.board_graph):
            # print(self.board_graph[node]["edges"])
            # edges_weighted = {neigh:1 for neigh in self.board_graph[node]["edges"]}
            # board_graph_weighted[node] = edges_weighted
        # print(board_graph_weighted)
        
        #solve dijkstra for board graph
        # dijkstra.
        
        for pl in self.players:
            # print("situation for player {}".format(pl.name))
            pawn_position = pl.pawn.position

            # distance from all reachable nodes to pawn position
            board_node_distances_to_pawn = dijkstra.dijkstra_graph_isolated_nodes_enabled(board_graph_weighted, pawn_position)


            # nodes_sorted_after_dijkstra = sorted( list(board_node_distances_to_pawn), key = lambda pos: 10*(pos[0])+pos[1])
            # print("nodes sorted after dijkstra:{}".format(nodes_sorted_after_dijkstra))
            # print("dijkstra for node: {}".format(pawn_position))
            # for n in nodes_sorted_after_dijkstra:
                # print("{} --> {}".format(n,board_node_distances_to_pawn[n] ))

            # distance from winning nodes to pawn
            board_winning_nodes_to_pawn = {}

            dist_to_win = None  # None is +inf
            closest_winning_node = None           
            for node in PAWN_WINNING_POS[pl.player_direction]:

                if node in board_node_distances_to_pawn:
                    dist = board_node_distances_to_pawn[node]
                    board_winning_nodes_to_pawn[node] = dist

                    # check for shortest distance
                    if dist_to_win is None or dist_to_win > dist:
                        dist_to_win  = dist
                        closest_winning_node = node
                else:
                    board_winning_nodes_to_pawn[node] = None  # None is +inf

            print("Distances to winning nodes for player {}: {}".format(pl.name, board_winning_nodes_to_pawn))

            # print("Distances to winning nodes for player {}: from west to east".format(pl.name, board_winning_nodes_to_pawn))

            shortest_path[pl.player_direction]= dist_to_win

        return shortest_path

    def link_nodes(self, node1, node2):
        if node2 not in self.board_graph[node1]["edges"]:
            self.board_graph[node1]["edges"].append(node2)
        else:
            print ("ASSERT ERROR: nodes already connected.")
            return False

        if node1 not in self.board_graph[node2]["edges"]:
            self.board_graph[node2]["edges"].append(node1)
        else:
            print("ASSERT ERROR: nodes already connected")
            return False
        return True

    def unlink_nodes(self, node1, node2):
        #will destroy edge between two nodes
        #check if wall already placed
        if node2 in self.board_graph[node1]["edges"]:
            if node1 not in self.board_graph[node2]["edges"]:
                print ("ASSERT ERROR: assymetrical links between two nodes.")
                return False
            
            #now remove edges.
            self.board_graph[node1]["edges"].remove(node2)
            self.board_graph[node2]["edges"].remove(node1)
            print("wall placed between {} and {}".format(node1, node2))
            return True
        else:
            print("no link between two nodes. Indicates a placed wall")
            return False
            
    def get_node_content(self, node):
        return self.board_graph[node]
        pass
        
    def direction_to_node(self, node, direction):
        #direction i.e. pawn.NORTH
        #returns None if board edge reached.
        node_neighbour = direction(node)
        
        #check if node exists
        if node_neighbour not in list(self.board_graph):
            print("node not existing: {}".format(node_neighbour))
            return None
        return node_neighbour
    
    def nodes_directly_connected(self, node, node_test):
        #check if no wall between nodes. of if node_test is an ortho neighbour.
        if node_test in self.board_graph[node]["edges"]:
            return True
        else:
            return False
            
    def node_direction_ok(self, node, direction):
        node_neigh = self.direction_to_node(node, direction)
        if node_neigh is None:
            return False
        return self.nodes_directly_connected(node, node_neigh)
    
    def pawn_on_node(self, node):
        
        # print(self.board_graph[node]["pawn"])
        print("what is on node({})?: {}".format(node,self.board_graph[node]))
        if self.board_graph[node]["pawn"] is None:
            return False
        else:
            return True
        

    def board_array(self):
        #setup
        board_array = []
        cells_vertical = BOARD_HEIGHT * 2 + 1
        cells_horizontal = BOARD_WIDTH * 2 + 1
        for row in range(cells_vertical):
            line = []
            for col in range(cells_horizontal):
                line.append(BOARD_CELL_EMPTY)
            board_array.append(line)
        
        # empty board: borders and lines
        for col in range(cells_horizontal):
            for row in range(cells_vertical):
                if row == 0 or row == cells_vertical-1 or col == 0 or col == cells_horizontal-1:
                    board_array[row][col] = BOARD_CELL_WALL_BORDER
        
                elif row%2 == 0 and col%2 == 0:
                    board_array[row][col] = BOARD_CELL_LINE_CROSSING
                
                elif row%2 == 0:
                    board_array[row][col] = BOARD_CELL_LINE_HORIZONTAL
                
                elif col%2 == 0:
                    board_array[row][col] = BOARD_CELL_LINE_VERTICAL
        
        #add row and column indicators
        for row in range(1,BOARD_WIDTH):        
            board_array[row*2 ][0] = str(row)
            board_array[row*2 ][BOARD_WIDTH * 2 ] = str(row)
        for col in range(1,BOARD_HEIGHT):        
            board_array[0][col*2] = str(chr(col + 96))
            board_array[BOARD_HEIGHT * 2][col*2] = str(chr(col + 96))

        for p in self.players:

            #add pawns
            x,y = p.pawn.position
            # print("pawn pos id: {}: x{}, y{}".format(p.name,x,y))
            col, row = x, y
            if p.direction == player.PLAYER_TO_NORTH:
                board_array[row*2 + 1][col*2 + 1] = BOARD_CELL_PLAYER_TO_NORTH
            elif p.direction == player.PLAYER_TO_SOUTH:
                board_array[row*2 + 1][col*2 + 1] = BOARD_CELL_PLAYER_TO_SOUTH
            else:
                print("ASSERT ERROR: no correct direction indicated")
              
            #add walls
            for w in p.walls:
                if w.status == wall.STATUS_PLACED:
                    hori, vert, orientation = w.get_position("lines_orientation")
                    
                    board_array[hori*2 ][vert*2 ] = BOARD_CELL_WALL
                    if orientation == wall.NORTH_SOUTH:
                        board_array[hori*2 -1 ][vert*2] = BOARD_CELL_WALL
                        board_array[hori*2 +1][vert*2] = BOARD_CELL_WALL

                    elif orientation == wall.EAST_WEST:
                        board_array[hori*2][vert*2 -1 ] = BOARD_CELL_WALL
                        board_array[hori*2][vert*2 + 1] = BOARD_CELL_WALL
              
        # for pos in list(self.board_graph):
            # cell= self.board_graph[pos]
            # pawn = cell["pawn"]
            # if pawn is not None:
                # if pawn.direction == player.PLAYER_TO_NORTH:
                    # board_array[pos[1]*2 + 1][pos[0]*2 + 1] = BOARD_CELL_PLAYER_TO_NORTH
                # elif pawn.direction == player.PLAYER_TO_SOUTH:
                    # board_array[pos[1]*2 + 1][pos[0]*2 + 1] = BOARD_CELL_PLAYER_TO_SOUTH
                # else:
                    # print("ASSERT ERROR: no correct direction indicated")
                    
        #add walls
        
        return board_array
        
    def __str__(self):
        output = ""
        board = self.board_array()
        # print(board)
        return "\n".join(["".join(row) for row in board[::-1]])
        
        # # return str(self.board_graph)
        # for y in range(BOARD_HEIGHT):
            # #wall line 
            # line = ""
            # for x in range(BOARD_WIDTH):    
                # if y==0:
                    # #top row
                
                # # line += self.board_graph[(x,y)] 
                # # output += "{} {} {}\n".format(x,y, str(self.board_graph[(x,y)]))
                
             # #pawn line
        # return output

if __name__ == "__main__":
    # player1 = player.Player("lode")
    # player2 = player.Player("brecht")
    # players = [player1, player2]
    # qboard = Board(players)
    # qboard = Board()
    # qboard.place_wall((2,3),(3,3))
    # print(str(qboard))
    pass
    
