import wall

BOARD_WIDTH = 9 
BOARD_HEIGHT = 9 
WALLBOARD_WIDTH = BOARD_WIDTH + 1
WALLBOARD_HEIGHT = BOARD_HEIGHT + 1

class Board():

    #pawn cells for 
    '''the board is split in two sub board
    pawnBoard = 9x9 cells with positions for the pawn.
    wallBoard = 10x10 with the other positions fixed walls

    0 1 2 3 4 5 6 7 8 9 = wall cells. 0 and 10 are the edges
    
     0 1 2 3 4 5 6 7 8  = pawn cells. 
    refer to a cell with a tuple (x,y)
    '''
    
    
    
    def __init__(self):
        cells = [(x,y) for x in range(BOARD_HEIGHT) for y in range(BOARD_WIDTH)]
        self.pawnBoard = {cell:None for cell in cells}
        cells = [(x,y) for x in range(WALLBOARD_HEIGHT) for y in range(WALLBOARD_WIDTH)]
        self.wallBoard = {cell:None for cell in cells}

        self.edgeWall = wall.Wall(wall.TYPE_EDGE, "EGDE")
        self.edgeWall.placed = True
        
        #create board edges
        for x in range(WALLBOARD_HEIGHT):
            self.wallBoard[(x,0)] = self.edgeWall
            self.wallBoard[(x,9)] = self.edgeWall
            
        for y in range(WALLBOARD_WIDTH):
            self.wallBoard[(0,y)] = self.edgeWall
            self.wallBoard[(9,y)] = self.edgeWall
                
        print(self.pawnBoard)
        print(self.wallBoard)
    
    def move_pawn(self, direction, simulate = True):
        pass
        
    def place_wall(self, wall, simulate = True):
        #cells contains the two affected cells as list
        # if type(cells) != list:
            # raise Exception("ASSERT ERROR: list expected")
             
        # if len(cells) != 2:
            # raise Exception("ASSERT ERROR: wall placement needs two cell positions (list with two elements)")
                
        #check if cells occupied
        for position in cells:
            if self.wallBoard[position] is not None:
                return False
            else:
                self.wallBoard[position]
        #check if route free
        
        pass
        
    def __str__():
        output = ""
        for x in range(

if __name__ == "__main__":
    qboard = Board()
    
