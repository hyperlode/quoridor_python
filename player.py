import wall
import pawn
import board
import quori_constants

PLAYER_TO_NORTH = 0
PLAYER_TO_SOUTH = 1

NUMBER_OF_WALLS = 10



class Player():
    def __init__(self, id, player_direction):
    
        
        self.id = id
        
        #create walls
        self.walls = [wall.Wall(wall.TYPE_PLAYER, i) for i in range(NUMBER_OF_WALLS)]
        
        #create pawn
        
        #id
        self.pawn = pawn.Pawn( board.PAWN_INIT_POS[player_direction], board.PAWN_WINNING_POS[player_direction])
        self.player_direction = player_direction
    # def place_wall(self, position):
    
    # @property(self):
    
    @property
    def direction(self):
        return self.player_direction
        
if __name__ == "__main__":
    test = Player("superlode", PLAYER_TO_NORTH)
        
            