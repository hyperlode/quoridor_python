import wall
import pawn

NUMBER_OF_WALLS = 10

class Player():
    def __init__(self, id):
        self.id = id
        
        #create walls
        self.walls = [wall.Wall(wall.TYPE_PLAYER, i) for i in range(NUMBER_OF_WALLS)]
        
        #create pawn
        
    # def place_wall(self, position):
        
            