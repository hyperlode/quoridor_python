import getter_setter_property_example as tmp
# POSITION_INIT = 0
# POSITION_GAME = 1
# POSITION_END = 2

#directions
NORTH = lambda pos: (pos[0], pos[1]+1)
EAST  = lambda pos: (pos[0]+1, pos[1])
SOUTH = lambda pos: (pos[0], pos[1]-1)
WEST  = lambda pos: (pos[0]-1, pos[1])

NORTH_NORTH = lambda x:  NORTH(NORTH(x))
SOUTH_SOUTH = lambda x:  SOUTH(SOUTH(x))
WEST_WEST = lambda x:  WEST(WEST(x))
EAST_EAST = lambda x:  EAST(EAST(x))

SOUTH_WEST = lambda d: SOUTH(WEST(d))
NORTH_WEST = lambda d: NORTH(WEST(d))
SOUTH_EAST = lambda d: SOUTH(EAST(d))
NORTH_EAST = lambda d: NORTH(EAST(d))




DIRECTIONS_ORTHO = [NORTH, EAST, SOUTH, WEST]

FIRST_DIRECTION_FOR_ORTHO_JUMPS = {
    NORTH_NORTH:NORTH,
    EAST_EAST:EAST,
    SOUTH_SOUTH:SOUTH,
    WEST_WEST:WEST
}


DIRECTIONS_ORTHO_JUMP = [NORTH_NORTH, EAST_EAST, SOUTH_SOUTH, WEST_WEST]
DIRECTIONS_DIAGONAL_JUMP = [NORTH_EAST, NORTH_WEST, SOUTH_EAST, SOUTH_WEST]


class Pawn():
    def __init__(self, position_init, positions_win):
        # self.player = player
        self.position_init = position_init
        self._position = position_init
        self.positions_win = positions_win
        self.positions_history = [self._position]
        
        
    def win(self):
        return self._position in self.positions_win
   
   
    # def move(self, direction,simulation=False):
        # #direction is one of the lambda functions (NORTH, SOUTH,....
        # self._position = direction(self._position)
        
        
    @property
    def position(self):
        return self._position

    @position.setter
    def position(self,value):
        # print("ieifjeijf")
        self._position = value
        self.positions_history.append(self._position)
        # print("posssef: {}".format(self._position))
        
if __name__ == "__main__":
    print(SOUTH((1,2)))
    print(NORTH_NORTH((1,2)))
    test = Pawn("bkj","bibiji")
    test.position = 3
    temp = tmp.Celsius()
    temp.temperature = 30