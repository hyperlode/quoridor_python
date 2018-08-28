import wall

BOARD_WIDTH = 9 
BOARD_HEIGHT = 9 

#board output (ASCII) visualization
BOARD_CELL_EMPTY = " "
BOARD_CELL_PLAYER_1= "1"
BOARD_CELL_PLAYER_2= "2"
BOARD_CELL_WALL = "O"
BOARD_CELL_LINE_HORIZONTAL = "-"
BOARD_CELL_LINE_VERTICAL = "|"
BOARD_CELL_LINE_CROSSING = "+"

#directions
NORTH = lambda (x, y): (x, y-1)
EAST  = lambda (x, y): (x+1, y)
SOUTH = lambda (x, y): (x, y+1)
WEST  = lambda (x, y): (x-1, y)

NORTH_NORTH = lambda x:  NORTH(NORTH(x))
SOUTH_SOUTH = lambda x:  SOUTH(SOUTH(x))
WEST_WEST = lambda x:  WEST(WEST(x))
EAST_EAST = lambda x:  EAST(EAST(x))

SOUTH_WEST = lambda d: SOUTH(WEST(d))
NORTH_WEST = lambda d: NORTH(WEST(d))
SOUTH_EAST = lambda d: SOUTH(EAST(d))
NORTH_EAST = lambda d: NORTH(EAST(d))

DIRECTIONS_ORTHO = [NORTH, EAST, SOUTH, WEST]
DIRECTIONS_ORTHO_JUMP = [NORTH_NORTH, EAST_EAST, SOUTH_SOUTH, WEST_WEST]
DIRECTIONS_DIAGONAL_JUMP = [NORTH_EAST, NORTH_WEST, SOUTH_EAST, SOUTH_WEST]

class Board():

    #pawn cells for 
    '''the board is split in two sub board
    pawnBoard = 9x9 nodes with positions for the pawn.

     0 1 2 3 4 5 6 7 8  = pawn nodes. 
    refer to a node with a tuple (x,y)
    '''
    
    def __init__(self):
        nodes = [(x,y) for x in range(BOARD_WIDTH) for y in range(BOARD_HEIGHT)]
        
        self.board_graph = {node:{"edges":None, "pawn":None} for node in nodes}
        # https://www.python.org/doc/essays/graphs/
        
        for node in nodes:
            x,y = node
            # neighbours = [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
            valid_neighbours = [dir(node) for dir in DIRECTIONS_ORTHO if dir(node) in nodes]    
            self.board_graph[node]["edges"] = valid_neighbours
        
        
    def move_pawn(self, direction, simulate = True):
        pass
        
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
        
        #lines
        
        
        
        # borders
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
                    
                # board_array[cells_vertical - 1][col] = BOARD_CELL_LINE_HORIZONTAL
            
        return board_array
        
    def __str__(self):
        output = ""
        board = self.board_array()
        # print(board)
        return "\n".join(["".join(row) for row in board])
        
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
    qboard = Board()
    print(str(qboard))
    print(SOUTH((1,2)))
    print(NORTH_NORTH((1,2)))
    
