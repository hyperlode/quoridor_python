import player
import pawn

BOARD_WIDTH = 9 
BOARD_HEIGHT = 9 

#board output (ASCII) visualization
BOARD_CELL_EMPTY = " "
BOARD_CELL_PLAYER_TO_NORTH = "1"
BOARD_CELL_PLAYER_TO_SOUTH = "2"
BOARD_CELL_WALL = "O"
BOARD_CELL_LINE_HORIZONTAL = "-"
BOARD_CELL_LINE_VERTICAL = "|"
BOARD_CELL_LINE_CROSSING = "+"

PAWN_INIT_POS = [(4, 0), (4, 8)] 
# = (PAWN_INIT_POS_X, 0), (PAWN_INIT_POS_X, BOARD_HEIGHT-1)

PAWN_WINNING_POS = [(x,8) for x in range(BOARD_WIDTH)], [(x,0) for x in range(BOARD_WIDTH)]
        

        
class Board():

    #pawn cells for 
    '''the board is split in two sub board
    pawnBoard = 9x9 nodes with positions for the pawn.

     0 1 2 3 4 5 6 7 8  = pawn nodes. 
    refer to a node with a tuple (x,y)
    '''
    
    # def __init__(self,players):
    def __init__(self):
        nodes = [(x,y) for x in range(BOARD_WIDTH) for y in range(BOARD_HEIGHT)]
        
        # self.players = players
        
        self.board_graph = {node:{"edges":None, "pawn":None} for node in nodes}
        # https://www.python.org/doc/essays/graphs/
        
        for node in nodes:
            x,y = node
            # neighbours = [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
            valid_neighbours = [dir(node) for dir in pawn.DIRECTIONS_ORTHO if dir(node) in nodes]    
            self.board_graph[node]["edges"] = valid_neighbours
            
        self.players = []
        
    def addPlayer(self, player_instance):
        self.players.append(player_instance)
        self.board_graph[player_instance.pawn.position]["pawn"] = player_instance
        
    def move_pawn(self, position, simulate = True):
        pass
        
    # def get_cell_neighbours(self, node, ortho = True, jump = False, diag = False):
        # if (ortho):
            # cell.
    def get_node_content(self, node):
        return self.board_graph[node]
        pass
        
    def direction_to_node(self, node, direction):
        #direction i.e. pawn.NORTH
        #returns None if board edge reached.
        node_neighbour = direction(node)
        print("node from direction: {}".format(node_neighbour))
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
        print(node)
        # print(self.board_graph[node]["pawn"])
        print(self.board_graph[node])
        if self.board_graph[node]["pawn"] is None:
            return False
        else:
            return True
        
    def place_wall(self, wall, simulate = True):
        #nodes contains the two affected nodes as list
        # if type(cells) != list:
            # raise Exception("ASSERT ERROR: list expected")
             
        # if len(cells) != 2:
            # raise Exception("ASSERT ERROR: wall placement needs two cell positions (list with two elements)")
                
        #check if cells occupied
        # for position in cells:
            # if self.wallBoard[position] is not None:
                # return False
            # else:
                # self.wallBoard[position]
        #check if route free
        
        pass
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
                    board_array[row][col] = BOARD_CELL_WALL
        
                elif row%2 == 0 and col%2 == 0:
                    board_array[row][col] = BOARD_CELL_LINE_CROSSING
                
                elif row%2 == 0:
                    board_array[row][col] = BOARD_CELL_LINE_HORIZONTAL
                
                elif col%2 == 0:
                    board_array[row][col] = BOARD_CELL_LINE_VERTICAL
                    
        #add pawns
        for p in self.players:
            x,y = p.pawn.position
            print("pawn pos id: {}: x{}, y{}".format(p.id,x,y))
            col, row = x, y
            if p.direction == player.PLAYER_TO_NORTH:
                board_array[row*2 + 1][col*2 + 1] = BOARD_CELL_PLAYER_TO_NORTH
            elif p.direction == player.PLAYER_TO_SOUTH:
                board_array[row*2 + 1][col*2 + 1] = BOARD_CELL_PLAYER_TO_SOUTH
            else:
                print("ASSERT ERROR: no correct direction indicated")
              
        
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
    qboard = Board()
    print(str(qboard))

    
