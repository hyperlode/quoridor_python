import player
import pawn
import wall
import dijkstra
# import dijkstra_fast

import sys
import logging
import time

BOARD_WIDTH = 9 # 9 is default should be an odd number of squares, for the pawn to be able to start in the middle.
BOARD_HEIGHT = 9 # 9 is default

# board output in terminal
# https://en.wikipedia.org/wiki/Box-drawing_character
# BOARD_CELL_EMPTY = " "
# BOARD_CELL_PLAYER_TO_TOP =  '\u25b2'
# BOARD_CELL_PLAYER_TO_BOTTOM = '\u25bc' 
# BOARD_CELL_WALL = '+'  # "O"
# BOARD_CELL_WALL_HORIZONTAL = '\u2550'  # "O"
# BOARD_CELL_WALL_VERTICAL = '\u2551'  # "O"
# BOARD_CELL_WALL_BORDER_VERTICAL = "\u2502"
# BOARD_CELL_WALL_BORDER_HORIZONTAL = "\u2500"
# BOARD_CELL_LINE_HORIZONTAL = '\u2500'  # "-"
# BOARD_CELL_LINE_VERTICAL = '\u2502'  # "|"
# BOARD_CELL_LINE_CROSSING =  '\u253c'  # "+"

CHARS_UTF8 = {
    "BOARD_CELL_EMPTY" : " ",
    "BOARD_CELL_PLAYER_TO_TOP":'\u25b2',
    "BOARD_CELL_PLAYER_TO_BOTTOM" : '\u25bc' ,
    "BOARD_CELL_WALL" : '+',  # "O",
    "BOARD_CELL_WALL_HORIZONTAL" : '\u2500',  # "O",
    "BOARD_CELL_WALL_VERTICAL" : '\u2502',  # "O",
    "BOARD_CELL_WALL_BORDER_VERTICAL" : "\u2502",
    "BOARD_CELL_WALL_BORDER_HORIZONTAL" : "\u2500",
    "BOARD_CELL_WALL_BORDER_TOP_LEFT" : "\u2514",
    "BOARD_CELL_WALL_BORDER_TOP_RIGHT" : "\u2510",
    "BOARD_CELL_WALL_BORDER_BOTTOM_LEFT" : "\u250C",
    "BOARD_CELL_WALL_BORDER_BOTTOM_RIGHT" : "\u2518",
    "BOARD_CELL_LINE_HORIZONTAL" : ' ',  # "-",
    "BOARD_CELL_LINE_VERTICAL" : ' ',  # "|",
    "BOARD_CELL_LINE_CROSSING" :  '\u253c',  # "+",
    "EXTENDED_BOARD_EMPTY_SPACE" : " ",
    "ROSE_VERTICAL" : '\u2502',
    "ROSE_ARROW_UP" :'\u25b2',
    "ROSE_ARROW_DOWN" :'\u25bc',
    "ROSE_CROSSING" : '\u253c'
    }

CHARS_ASCII = {
    "BOARD_CELL_EMPTY" : " ",
    "BOARD_CELL_PLAYER_TO_TOP" :  '^',
    "BOARD_CELL_PLAYER_TO_BOTTOM" : 'v' ,
    "BOARD_CELL_WALL" : '+',  # "O",
    "BOARD_CELL_WALL_HORIZONTAL" : '.',  # "O",
    "BOARD_CELL_WALL_VERTICAL" : '|',  # "O",
    "BOARD_CELL_WALL_BORDER_VERTICAL" : ".",
    "BOARD_CELL_WALL_BORDER_HORIZONTAL" : ".",
    "BOARD_CELL_WALL_BORDER_TOP_LEFT" : ".",
    "BOARD_CELL_WALL_BORDER_TOP_RIGHT" : ".",
    "BOARD_CELL_WALL_BORDER_BOTTOM_LEFT" : ".",
    "BOARD_CELL_WALL_BORDER_BOTTOM_RIGHT" : ".",
    "BOARD_CELL_LINE_HORIZONTAL" : ' ',  # "-",
    "BOARD_CELL_LINE_VERTICAL" : ' ',  # "|",
    "BOARD_CELL_LINE_CROSSING" :  '.',  # "+",
    "EXTENDED_BOARD_EMPTY_SPACE" : " ",
    "ROSE_VERTICAL": '|',
    "ROSE_ARROW_UP":'^',
    "ROSE_ARROW_DOWN":'v',
    "ROSE_CROSSING":'+'
    }

startPosX = BOARD_WIDTH // 2   # for width 9 --> 4  

PAWN_INIT_POS = [(startPosX, 0), (startPosX, BOARD_HEIGHT-1)] 
# = (PAWN_INIT_POS_X, 0), (PAWN_INIT_POS_X, BOARD_HEIGHT-1)

DISPLAY_ORIENTATION = ["player_north_to_top", "player_north_to_bottom"]  # , "active_player_to_top", "active_player_to_bottom"]

# all possible verbose wall positions
WINNING_ROWS = [BOARD_HEIGHT-1, 0]
NOTATION_VERBOSE_WALL_POSITIONS_NORTH_SOUTH = ["{}{}".format(chr(line + 96), midpoint)  for midpoint in range(1, BOARD_HEIGHT) for line in range(1, BOARD_WIDTH)]
NOTATION_VERBOSE_WALL_POSITIONS_EAST_WEST = ["{}{}".format(line, chr(midpoint + 96)) for midpoint in range(1, BOARD_WIDTH) for line in range(1, BOARD_HEIGHT)]
NOTATION_VERBOSE_WALL_POSITIONS = NOTATION_VERBOSE_WALL_POSITIONS_NORTH_SOUTH + NOTATION_VERBOSE_WALL_POSITIONS_EAST_WEST

def node_to_index( node):
    #used in sparse matrix where there is one identifier for each node.
    return BOARD_WIDTH*node[1] + node[0]

def index_to_node( index):
    return (index//BOARD_WIDTH, index%BOARD_WIDTH)
    
PAWN_WINNING_POS = [(x,BOARD_HEIGHT-1) for x in range(BOARD_WIDTH)], [(x,0) for x in range(BOARD_WIDTH)]
PAWN_WINNING_POS_INDECES =[[node_to_index(pos) for pos in PAWN_WINNING_POS[p]] for p in range(2)]

        
class Board():

    #pawn cells for 
    '''
    
    board graph:  9x9 nodes with positions for the pawn.
    wall are broken edges between nodes.
    refer to a node with a tuple (x,y)  
    
    ^
    |
    y
    |___x___>
    
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
    
    def __init__(self, output_encoding, logger=None):
        
        self.logger = logger or logging.getLogger(__name__)

        nodes = [(x,y) for x in range(BOARD_WIDTH) for y in range(BOARD_HEIGHT)]
        
        self.board_graph = {node:{"edges":None, "pawn":None} for node in nodes}
        # https://www.python.org/doc/essays/graphs/
        
        for node in nodes:
            x,y = node
            # neighbours = [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
            valid_neighbours = [dir(node) for dir in pawn.DIRECTIONS_ORTHO if dir(node) in nodes]    
            self.board_graph[node]["edges"] = valid_neighbours
            
        self.players = []
        self.wide_display = True
        self.display_orientation = DISPLAY_ORIENTATION[0]
        
        
        if output_encoding == "utf-8":
            self.chars = CHARS_UTF8
        else:
            self.chars = CHARS_ASCII
        
    # ADMINISTRATION 
    
       
    def add_player(self, player_instance):
        self.players.append(player_instance)
        self.board_graph[player_instance.pawn.position]["pawn"] = player_instance
    
    # CHECKING BOARD
    
    def check_pawn_positions(self):
        for pl in self.players:
            node = pl.pawn.position
            okOnBoard = self.pawn_on_node(node)
            self.logger.info("player {} at postion {}, ok on board:{} ".format(pl.name, node, okOnBoard))
            
    def check_wall_valid(self, new_wall):
        pass
    
    def distances_to_winning_node(self):    
        return self.distances_to_winning_node_optimized()
        # if dijkstra.USE_SCIPY:
            # return self.distances_to_winning_node_with_import()
        # else:
            # return self.distances_to_winning_node_no_imports()
    
    def distances_to_winning_node_optimized(self):
        #minimize overhead.
        
        # get proper weighted graph
        board_graph_unweighted = {node:value["edges"] for node, value in self.board_graph.items()}
        
        dists = [None,None]
        dists[player.PLAYER_TO_NORTH] = dijkstra.dijkstra_quoridor(board_graph_unweighted, self.players[player.PLAYER_TO_NORTH].pawn.position,WINNING_ROWS[player.PLAYER_TO_NORTH])
        if dists[player.PLAYER_TO_NORTH] is None:
            return [None,None]
        
        dists[player.PLAYER_TO_SOUTH] = dijkstra.dijkstra_quoridor(board_graph_unweighted, self.players[player.PLAYER_TO_SOUTH].pawn.position,WINNING_ROWS[player.PLAYER_TO_SOUTH])
        return dists

    def paths_to_winning_node(self):
        # get proper weighted graph
        board_graph_unweighted = {node:value["edges"] for node, value in self.board_graph.items()}

        # print("nor th pawn pos: {}".format( self.players[player.PLAYER_TO_NORTH].pawn.position))
        paths = [None,None]
        paths[player.PLAYER_TO_NORTH] = dijkstra.dijkstra_quoridor(board_graph_unweighted,
                                                                   self.players[player.PLAYER_TO_NORTH].pawn.position,
                                                                   WINNING_ROWS[player.PLAYER_TO_NORTH],
                                                                   True)

        if paths[player.PLAYER_TO_NORTH] is None:
            return [None,None]

        paths[player.PLAYER_TO_SOUTH] = dijkstra.dijkstra_quoridor(board_graph_unweighted,
                                                                   self.players[player.PLAYER_TO_SOUTH].pawn.position,
                                                                   WINNING_ROWS[player.PLAYER_TO_SOUTH],
                                                                   True)
        return paths

    def distances_to_winning_node_with_import(self):
        # scipy faster dijkstra algoritm
        
        # perpare board as sparse matrix.
        board_matrix_sparse = [[0 for x in range(BOARD_WIDTH*BOARD_HEIGHT)] for y in range(BOARD_WIDTH*BOARD_HEIGHT)]
        #non directed, non weigthed. all nodes on x and y axis, for connected nodes, the value is set to 1. 
        
        for node, value in self.board_graph.items():
            row_index = node_to_index(node)
            for edge in value["edges"]:
                col_index = node_to_index(edge)
                board_matrix_sparse[row_index][col_index] = 1
        
        # perform dijkstra     
        distances_per_player = dijkstra.dijkstra_fast(board_matrix_sparse, [node_to_index(self.players[0].pawn.position), node_to_index(self.players[1].pawn.position)])
        
        #get distances to winnning nodes
        shortest_dists = [None, None]
        for player in self.players:
            dist_to_winning_pos = [ distances_per_player[player.player_direction][i] for i in PAWN_WINNING_POS_INDECES[player.player_direction] ]
            shortest = min(dist_to_winning_pos)
            if shortest != float("inf"):
                shortest_dists[player.player_direction] = int(shortest)
            
        return shortest_dists 
    
    def distances_to_winning_node_no_imports(self):
        # returns tuple with shortest distance to a winning node for both players (distance_player_to_north, distance_player_to_south) i.e.  (17,4)
        # returns tuple with distances for each player to nearest winning square. None if not reachable
        shortest_path = [None, None]
        
        # solve dijkstra for board graph
        for player in self.players:
            shortest_path[player.player_direction] = self.shortest_distances_to_winning_node(player)  # empty list when no winning nodes reachable --> None as +inf distance
        return shortest_path
          
    def shortest_distances_to_winning_node(self, player):
        # return shortest to reachable winning nodes for a given player or None for unreachable.
        
        # get proper weighted graph
        board_graph_unweighted = {node:value["edges"] for node, value in self.board_graph.items()}
        # print("before dijk: {}".format(int(round(time.time() * 1000))))
        # distance from all reachable nodes to pawn position
        board_node_distances_to_pawn = dijkstra.dijkstra_graph_isolated_nodes_enabled_unweighted(board_graph_unweighted, player.pawn.position)
        # print("after dijk: {}".format(int(round(time.time() * 1000))))
        # distance from winning node to pawn
        return min([dist for node,dist in board_node_distances_to_pawn.items() if node in PAWN_WINNING_POS[player.player_direction]], default=None)
        
    def distances_to_all_winning_nodes_include_unreachables(self, player):
        # return dict node:dist of distances to winning nodes for a given player. None for +inf. aka unreachable.
        
        #get proper weighted graph
        board_graph_unweighted = {node:value["edges"] for node, value in self.board_graph.items()}
       
        # distance from all reachable nodes to pawn position
        board_node_distances_to_pawn = dijkstra.dijkstra_graph_isolated_nodes_enabled_unweighted(board_graph_unweighted, player.pawn.position)

        # distance from winning nodes to pawn
        board_winning_nodes_to_pawn = {}
             
        for node in PAWN_WINNING_POS[player.player_direction]:

            if node in board_node_distances_to_pawn:
                board_winning_nodes_to_pawn[node] = board_node_distances_to_pawn[node]
            else:
                board_winning_nodes_to_pawn[node] = None  # None is +inf

        # self.logger.info("Distances to winning nodes for player {}: {}".format(player.name, board_winning_nodes_to_pawn))
        return board_winning_nodes_to_pawn
        
    # ACTION      
    def move_pawn(self, old, new):
        self.board_graph[new]["pawn"] = self.board_graph[old]["pawn"]
        self.board_graph[old]["pawn"] = None
        return True

    def remove_wall(self, wall_to_remove):
        #used for undo or backwards replay.

        success = False

        #reconnect nodes
        for node1, node2 in wall_to_remove.get_position("nodes"):
            success = self._link_nodes(node1, node2)
            if not success:
                self.logger.warning(
                    "connections on the board could not be connected when removing the wall. Board might be corrupt")
                raise Exception("board potentially corrupt.")
                return False

        if not success:
            self.logger.error("error: wall not found. check if verbose position is accurate: {}".format(wall_to_remove.get_position("verbose")))
        else:
            self.logger.info("wall removed from board")
        return success

    def place_wall(self, new_wall):
        hori_new,vert_new,orientation_new = new_wall.get_position("lines_orientation")
        
        #check with placed walls
        for pl in self.players:
            for w in pl.walls:
                if w.status == wall.STATUS_PLACED:
                    hori, vert, orientation = w.get_position("lines_orientation")
                    
                    #check for overlapping center points.
                    if hori == hori_new and vert == vert_new :
                        # centerpoint is the same, so for sure a failure. We just have to check what kind of failure:
                        if orientation==orientation_new:
                            self.logger.info("attempt to place wall on exactly the same location of another wall.")
                        else:
                            self.logger.info("attempt to place wall with same centerpoint as other wall (but in another orientation).")
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
                                self.logger.info("north south walls on same line and overlapping")
                                return False
                                
                        elif orientation == wall.EAST_WEST:
                            if (hori == hori_new) and abs(vert - vert_new) < 2:
                                #overlap!
                                self.logger.info("east-west walls are on the same line and overlapping")
                                return False

        self.logger.info("wall can be placed.")

        #unlink nodes that are separated by the wall
        for node1, node2 in new_wall.get_position("nodes"):
            success = self._unlink_nodes(node1, node2)
            if not success:
                print("connections on the board could not be severed when placing the wall. Board might be corrupt")
                raise Exception("board potentially corrupt.")
                return False
        return True
          
    def _link_nodes(self, node1, node2):
        if node2 not in self.board_graph[node1]["edges"]:
            self.board_graph[node1]["edges"].append(node2)
        else:
            self.logger.warning("ASSERT ERROR: nodes already connected.")
            return False

        if node1 not in self.board_graph[node2]["edges"]:
            self.board_graph[node2]["edges"].append(node1)
        else:
            self.logger.warning("ASSERT ERROR: nodes already connected")
            return False
        return True

    def _unlink_nodes(self, node1, node2):
        #will destroy edge between two nodes
        #check if wall already placed
        if node2 in self.board_graph[node1]["edges"]:
            if node1 not in self.board_graph[node2]["edges"]:
                self.logger.warning("ASSERT ERROR: assymetrical links between two nodes.")
                return False
            
            #now remove edges.
            self.board_graph[node1]["edges"].remove(node2)
            self.board_graph[node2]["edges"].remove(node1)
            self.logger.info("wall placed between {} and {}".format(node1, node2))
            return True
        else:
            self.logger.warning("no link between two nodes. Indicates a placed wall")
            return False
         
    def direction_to_node(self, node, direction):
        #direction i.e. pawn.NORTH
        #returns None if board edge reached.
        node_neighbour = direction(node)
        
        #check if node exists
        if node_neighbour not in list(self.board_graph):
            self.logger.info("node not existing: {}".format(node_neighbour))
            return None
        return node_neighbour
    
    def nodes_directly_connected(self, node, node_test):
        #check if no wall between nodes. of if node_test is an ortho neighbour.
        if node_test in self.board_graph[node]["edges"]:
            return True
        else:
            return False
            
    def node_connection_by_direction_(self, node, direction):
        #check if neighbour node reachable by direction. (i.e. pawn.NORTH)
        node_neigh = self.direction_to_node(node, direction)
        if node_neigh is None:
            return False
        return self.nodes_directly_connected(node, node_neigh)
    
    def pawn_on_node(self, node):
        # check if a pawn is on the provided node (in graph)
        # self.logger.debug("what is on node({})?: {}".format(node,self.board_graph[node]))
        return self.board_graph[node]["pawn"] is not None
    
    # DISPLAY BOARD
    
    def wide_display_toggle(self):
        # output board wide or normal
        self.wide_display = not self.wide_display
        
    def rotate_board(self, north_player_to_top=None):
        if north_player_to_top is None:
            if self.display_orientation == "player_north_to_top":
                self.display_orientation = "player_north_to_bottom"
            else:
                self.display_orientation = "player_north_to_top"
            # just rotate 180
        elif north_player_to_top:
            # north top
            self.display_orientation = "player_north_to_top"
        else:
            #north is bottom
            self.display_orientation = "player_north_to_bottom"
        
    def get_player_char(self,direction):
        
        # if self.display_orientation in ["active_player_to_top", "active_player_to_bottom"]:
            # self.logger.error("active player board orientation not yet implemented.")
            # raise Exception
            
        if direction == player.PLAYER_TO_NORTH and self.display_orientation == "player_north_to_top":
            return self.chars["BOARD_CELL_PLAYER_TO_TOP"]
        elif direction == player.PLAYER_TO_NORTH and self.display_orientation == "player_north_to_bottom":
            return self.chars["BOARD_CELL_PLAYER_TO_BOTTOM"]
        elif direction == player.PLAYER_TO_SOUTH and self.display_orientation == "player_north_to_top":
            return self.chars["BOARD_CELL_PLAYER_TO_BOTTOM"]
        elif direction == player.PLAYER_TO_SOUTH and self.display_orientation == "player_north_to_bottom":
            return self.chars["BOARD_CELL_PLAYER_TO_TOP"]
        else:
            self.logger.error("troubles in paradise. ")
            raise Exception 
        
    def board_array(self):
        # converts the graph to an array with cells. for display use.
        board_array = []
        
        if self.wide_display:
            # number of extra chars added per square in horizontal direction
            hori_extra = 2
        else:
            hori_extra = 0
       
        if self.display_orientation == "player_north_to_top":
            char_player_to_north = self.chars["BOARD_CELL_PLAYER_TO_TOP"]
            char_player_to_south = self.chars["BOARD_CELL_PLAYER_TO_BOTTOM"]
            
            #corners of the board
            char_edge_corner_south_west = self.chars["BOARD_CELL_WALL_BORDER_BOTTOM_LEFT"]
            char_edge_corner_north_west = self.chars["BOARD_CELL_WALL_BORDER_TOP_LEFT"]
            char_edge_corner_south_east = self.chars["BOARD_CELL_WALL_BORDER_BOTTOM_RIGHT"]
            char_edge_corner_north_east = self.chars["BOARD_CELL_WALL_BORDER_TOP_RIGHT"]
        
        elif self.display_orientation == "player_north_to_bottom":
            char_player_to_north = self.chars["BOARD_CELL_PLAYER_TO_BOTTOM"]
            char_player_to_south = self.chars["BOARD_CELL_PLAYER_TO_TOP"]
            
             #corners of the board
            char_edge_corner_south_west = self.chars["BOARD_CELL_WALL_BORDER_TOP_LEFT"]
            char_edge_corner_north_west = self.chars["BOARD_CELL_WALL_BORDER_BOTTOM_LEFT"]
            char_edge_corner_south_east = self.chars["BOARD_CELL_WALL_BORDER_TOP_RIGHT"]
            char_edge_corner_north_east = self.chars["BOARD_CELL_WALL_BORDER_BOTTOM_RIGHT"]
        
        else:
            self.logger.log("orientation not implemented")
        
            
       
        cells_vertical = BOARD_HEIGHT * 2 + 1
        cells_horizontal = BOARD_WIDTH * (2 + hori_extra) + 1
        
        for row in range(cells_vertical):
            line = []
            for col in range(cells_horizontal):
                line.append(self.chars["BOARD_CELL_EMPTY"])
            board_array.append(line)
        
        
        # empty board: borders and lines
        for col in range(cells_horizontal):
            for row in range(cells_vertical):
                if row == 0 or row == cells_vertical-1:
                    board_array[row][col] = self.chars["BOARD_CELL_WALL_BORDER_HORIZONTAL"]
                    
                elif col == 0 or col == cells_horizontal-1:
                    board_array[row][col] = self.chars["BOARD_CELL_WALL_BORDER_VERTICAL"]
                    
                elif row%2 == 0 and col% (2+hori_extra) == 0:
                    board_array[row][col] = self.chars["BOARD_CELL_LINE_CROSSING"]
                
                elif row%2 == 0:
                    board_array[row][col] = self.chars["BOARD_CELL_LINE_HORIZONTAL"]
                
                elif col%2 == 0:
                    board_array[row][col] = self.chars["BOARD_CELL_LINE_VERTICAL"]
        
        #corners of the board
        board_array[cells_vertical-1][0]                    = char_edge_corner_south_west
        board_array[0][0]                                   = char_edge_corner_north_west
        board_array[0][cells_horizontal - 1]                = char_edge_corner_south_east
        board_array[cells_vertical-1][cells_horizontal - 1] = char_edge_corner_north_east
        
        for p in self.players:

            #add pawns
            x,y = p.pawn.position
            # print("pawn pos id: {}: x{}, y{}".format(p.name,x,y))
            col, row = x, y
            if p.direction == player.PLAYER_TO_NORTH:
                board_array[row*2 + 1][col*(2+hori_extra) + 1 + (hori_extra//2)] = char_player_to_north
            elif p.direction == player.PLAYER_TO_SOUTH:
                board_array[row*2 + 1][col*(2+hori_extra) + 1 + (hori_extra//2)] = char_player_to_south
            else:
                self.logger.warning("ASSERT ERROR: no correct direction indicated")
              
            #add walls
            for w in p.walls:
                if w.status == wall.STATUS_PLACED:
                    hori, vert, orientation = w.get_position("lines_orientation")
                    
                    # board_array[hori*2 ][vert*2 ] = self.chars["BOARD_CELL_WALL_CENTER"
                    if orientation == wall.NORTH_SOUTH:
                        board_array[hori*2 -1 ][vert*(2+hori_extra)] = self.chars["BOARD_CELL_WALL_VERTICAL"]
                        # board_array[hori*2 ][vert*2 ] = self.chars["BOARD_CELL_WALL_VERTICAL)  # center
                        board_array[hori*2 +1][vert*(2+hori_extra)] = self.chars["BOARD_CELL_WALL_VERTICAL"]

                    elif orientation == wall.EAST_WEST:
                        board_array[hori*2][vert*(2+hori_extra) -1 ] = self.chars["BOARD_CELL_WALL_HORIZONTAL"]
                        # board_array[hori*2 ][vert*2 ] = self.chars["BOARD_CELL_WALL_HORIZONTAL)  # center
                        board_array[hori*2][vert*(2+hori_extra) + 1] = self.chars["BOARD_CELL_WALL_HORIZONTAL"]
                        if (hori_extra == 2):
                            board_array[hori*2][vert*(2+hori_extra) -2 ] = self.chars["BOARD_CELL_WALL_HORIZONTAL"   ] 
                            board_array[hori*2][vert*(2+hori_extra) -3 ] = self.chars["BOARD_CELL_WALL_HORIZONTAL" ]  
                            board_array[hori*2][vert*(2+hori_extra) +2 ] = self.chars["BOARD_CELL_WALL_HORIZONTAL"]    
                            board_array[hori*2][vert*(2+hori_extra) +3 ] = self.chars["BOARD_CELL_WALL_HORIZONTAL"]    

        # add row and column indicators (1->8 , a-> h)
        #     extend array 
        cells_border_offset = 3
        extended_board = board_array[::]
       
        margin = [self.chars["EXTENDED_BOARD_EMPTY_SPACE"] for i in range(cells_border_offset)]
        extended_board = [ margin + row + margin for row in board_array]
        
        extra_row = [self.chars["EXTENDED_BOARD_EMPTY_SPACE"] for i in range(len(extended_board[0]))] 
        for i in range(cells_border_offset):
            extended_board.append(extra_row[::])
            extended_board.insert(0,extra_row[::])
        
        #     add indicators        
        o = cells_border_offset
        for row in range(1,BOARD_HEIGHT):        
            extended_board[row*2 + o][0 + o - 1] = str(row)
            extended_board[row*2 + o][BOARD_WIDTH * (2+hori_extra) + o + 1] = str(row)
        for col in range(1,BOARD_WIDTH):        
            extended_board[0 + o - 1][col*(2+hori_extra) + o] = str(chr(col + 96))
            extended_board[BOARD_HEIGHT * 2 + o + 1][col*(2+hori_extra) + o] = str(chr(col + 96))
         
        return extended_board
    
    def __str__(self):
        board_rows_for_output = self.output_lines()
        board_string = "\n".join(board_rows_for_output)
        return board_string
    
    def output_lines(self):
        output = ""
        board = self.board_array()
        
        if self.display_orientation == "player_north_to_top":
            
            board_rows_for_output= [[self.chars["EXTENDED_BOARD_EMPTY_SPACE"] for i in range(6)] + row for row in board[::-1]]
            x = 0
            y = 1
 
            board_rows_for_output[y][x+3] = "N"
            board_rows_for_output[y+1][x+3] = self.chars["ROSE_ARROW_UP"] # "^"
            board_rows_for_output[y+2][x+3] = self.chars["ROSE_VERTICAL"]  # "|"
            board_rows_for_output[y+3][x+3] = self.chars["ROSE_CROSSING"]  # "+"
            board_rows_for_output[y+3][x+1] = 'W'  # "+"
            board_rows_for_output[y+3][x+5] = 'E'  # "+"
            board_rows_for_output[y+4][x+3] = self.chars["ROSE_VERTICAL"]  # "|"
            board_rows_for_output[y+5][x+3] = 'S'  
        elif self.display_orientation == "player_north_to_bottom":
            board_rows_for_output= [[self.chars["EXTENDED_BOARD_EMPTY_SPACE"] for i in range(6)] + row for row in board]
            x = 0
            y = 1
            board_rows_for_output[y][x+3] = "S"
            
            board_rows_for_output[y+1][x+3] = self.chars["ROSE_VERTICAL"]  # "|"
            board_rows_for_output[y+2][x+3] = self.chars["ROSE_CROSSING"]  # "+"
            board_rows_for_output[y+2][x+1] = 'E'  # "+"
            board_rows_for_output[y+2][x+5] = 'W'  # "+"
            board_rows_for_output[y+3][x+3] = self.chars["ROSE_VERTICAL"]  # "|"
            board_rows_for_output[y+4][x+3] = self.chars["ROSE_ARROW_DOWN"]  # "v"
            board_rows_for_output[y+5][x+3] = 'N'  
        else:
            self.logger.error("unvalid orientation ")
            return False

        return ["".join(row) for row in board_rows_for_output]

        
if __name__ == "__main__":
    # player1 = player.Player("lode")
    # player2 = player.Player("brecht")
    # players = [player1, player2]
    # qboard = Board(players)
    # qboard = Board()
    # qboard.place_wall((2,3),(3,3))
    # print(str(qboard))
    pass
    
