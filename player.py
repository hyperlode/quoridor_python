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
                    
        if direction in pawn.DIRECTIONS_ORTHO:
            new_position = self.board.direction_to_node(self.pawn.position, direction)
            
            if new_position is None:
                print ("ASSERT ERROR: checked neighbour node is not valid. ")
                return False
            
            if self.board.pawn_on_node(new_position):
                print ("error: pawn on neighbour.")
                return False 
                
            if not self.board.nodes_directly_connected(self.pawn.position, new_position):
                print ("no move possible: wall")
                return False
             
        
        elif direction in pawn.DIRECTIONS_ORTHO_JUMP:
            
            #get neighbour node
            neighbourNode = self.board.direction_to_node(self.pawn.position, pawn.FIRST_DIRECTION_FOR_ORTHO_JUMPS[direction])
            if neighbourNode is None:
                print ("ASSERT ERROR: checked neighbour node is not valid. ")
                return False
            
            #check for pawn on neighbour node
            if not self.board.pawn_on_node(neighbourNode):
                self.board.check_pawn_positions()
                #no pawn on neighbour node
                print ("error: no pawn on neighbour node")
                return False
                
            if not self.board.nodes_directly_connected(self.pawn.position, neighbourNode):
                #wall between jumper and jumpee
                print ("wall in the way")
                return False
            
            #check the jump node
            new_position = self.board.direction_to_node(self.pawn.position, direction)
            
            if new_position is None:
                print ("ASSERT ERROR: jump node is not valid. ")
                return False
            
            #check wall to jump node
            if not self.board.nodes_directly_connected(neighbourNode, new_position):
                print("wall encountered to jump node")
                return False
            
            # print ("jump valid")    
            
        elif direction in pawn.DIRECTIONS_DIAGONAL_JUMP:
            # valid = False
            print ("not yet implemented. ")
            return False
            pass
        else:
            print("ASSERT ERROR: illegal direction ({})".format(direction))
            return False
        
         # valid = self.board.node_direction_ok(self.pawn.position, direction)
        
        #check if move possible.
    
        print("move from: {}  to:{}".format(self.pawn.position, new_position))
        self.board.move_pawn(self.pawn.position, new_position)
        self.pawn.position = new_position
        return True
        
if __name__ == "__main__":
    test = Player("superlode", PLAYER_TO_NORTH)
    
    
    
        
            