import wall

BOARD_WIDTH = 9 
BOARD_HEIGHT = 9 
NORTH = lambda (x, y): (x, y-1)
EAST  = lambda (x, y): (x+1, y)
SOUTH = lambda (x, y): (x, y+1)
WEST  = lambda (x, y): (x-1, y)
NORTH_NORTH = lambda x:  NORTH(NORTH(x))

# efef
SOUTH_WEST = lambda x: SOUTH(WEST(x))



ORTHO_DIRECTIONS = [NORTH, EAST, SOUTH, WEST]


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
            valid_neighbours = [dir(node) for dir in ORTHO_DIRECTIONS if dir(node) in nodes]    
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
        
    def __str__(self):
        output = ""
        # return str(self.board_graph)
        for x in range(BOARD_WIDTH):
            # line = ""
            for y in range(BOARD_HEIGHT):
                # line += self.board_graph[(x,y)] 
                output += "{} {} {}\n".format(x,y, str(self.board_graph[(x,y)]))
        return output

if __name__ == "__main__":
    qboard = Board()
    print(qboard)
    print(SOUTH((1,2)))
    print(NORTH_NORTH((1,2)))
    
