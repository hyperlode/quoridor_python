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
        self.pawn = pawn.Pawn( board.PAWN_INIT_POS[player_direction], board.PAWN_WINNING_POS[player_direction])
        
        #id
        self.player_direction = player_direction
    
    def set_board(self, board_instance):
        self.board = board_instance
        
    def place_wall(self, position):
        pass
    # @property
    # def pawn(self):
        # return self.pawn.
    
    
    
    @property
    def direction(self):
        return self.player_direction
        
        
    def get_possible_pawn_moves(self):
        #list up all possible directions.
        
        #ortho
        # self.board_instance.
        
        #jump
        
        #diagonal
        
        print("direction to node:")
        self.board.direction_to_node(self.pawn.position, pawn.WEST)
        
        pass
        
    def move_pawn(self, direction):
    
        #direction i.e. pawn.NORTH
        
        #get neighbour cell
        # self.get_possible_pawn_moves()
        
        
        valid = False
        
        if direction in pawn.DIRECTIONS_ORTHO:
            neighbourNode = self.board.direction_to_node(self.pawn.position, direction)
            valid = self.board.nodes_directly_connected(self.pawn.position, neighbourNode)
        
        elif direction in pawn.DIRECTIONS_ORTHO_JUMP:
            neighbourNode = self.board.direction_to_node(self.pawn.position, pawn.FIRST_DIRECTION_FOR_ORTHO_JUMPS[direction])
            if neighbourNode is None:
                print ("ASSERT ERROR: checked neighbour node is not valid. ")
                return False
                
                
            
            #check for pawn on neighbour node
            pawn_on_adjecent_node = self.board.pawn_on_node(neighbourNode)
            
            #check if no wall in between.
            no_wall_in_the_way = self.board.nodes_directly_connected(self.pawn.position, neighbourNode)
            
            
            if pawn_on_adjecent_node and no_wall_in_the_way:
                valid = True
            else:
                valid = False
            print ("jump validness? {}".format(valid))    
            
        elif direction in pawn.DIRECTIONS_DIAGONAL_JUMP:
            valid = False
            pass
        else:
            valid = False
            print("ASSERT ERROR: illegal direction ({})".format(direction))
            return False
        
         # valid = self.board.node_direction_ok(self.pawn.position, direction)
        
        #check if move possible.
        if (valid):
            print("neigh: {} {}".format(self.pawn.position, neighbourNode))
            self.pawn.position = neighbourNode
            print(self.pawn.position)
            return True
        else:
        
            return False #not successful
        
if __name__ == "__main__":
    test = Player("superlode", PLAYER_TO_NORTH)
    
    
    
        
            