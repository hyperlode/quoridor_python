# POSITION_INIT = 0
# POSITION_GAME = 1
# POSITION_END = 2

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


class Pawn():
    def __init__(self, position_init, positions_win):
        # self.player = player
        self.position_init = position_init
        self.position = position_init
        self.positions_win = positions_win
        self.positions_history = [self.position]
        
        
    def win(self):
        return self.position in self.positions_win
   
   
    # def move(self, direction,simulation=False):
        # #direction is one of the lambda functions (NORTH, SOUTH,....
        # self.position = direction(self.position)
        
        
    @property
    def position(self):
        return self.position

    @position.setter
    def position(self,value):
        self.position = value
        self.positions_history.append(self.position)
        
if __name__ == "__main__":
    print(SOUTH((1,2)))
    print(NORTH_NORTH((1,2)))