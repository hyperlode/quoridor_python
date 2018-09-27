import wall
import pawn
import board
# import quori_constants
import logging

PLAYER_TO_NORTH = 0
PLAYER_TO_SOUTH = 1

NUMBER_OF_WALLS = 10


class Player:
    def __init__(self, name, player_direction):
        logging.info("player created with name: {}".format(name))
        self.name = name
        
        # create walls
        self.walls = [wall.Wall(wall.TYPE_PLAYER, i) for i in range(NUMBER_OF_WALLS)]
        
        # create pawn
        self.pawn = pawn.Pawn( board.PAWN_INIT_POS[player_direction])
        self.board = None
        self.player_direction = player_direction
        
        #at_move
        self._active = False
        
    def __repr__(self):
        return str("Player {} at position: {}".format(self.name, self.pawn.position))
        
    def set_board(self, board_instance):
        self.board = board_instance
    
    def get_pawn_on_winning_position(self):
        return self.pawn.position in board.PAWN_WINNING_POS[self.player_direction]
                
    def get_unplaced_wall(self):
        # returns first unused wall.
        # None if all walls are placed.
        
        found = False
        index = 0
        while not found and index < NUMBER_OF_WALLS:
            if self.walls[index].status == wall.STATUS_NOT_PLACED:
                return self.walls[index]
            else:
                index += 1
        return None 
        
    def place_wall(self, verbose_position):
        playWall = self.get_unplaced_wall()
        if playWall is None:
            status = "Error: no free walls for this player available"
            logging.info(status)
            print(status)
            return False
       
        # temporarily set wall
        placed = playWall.set_position(verbose_position, tentative=True)
        if not placed:
            logging.info("error in placing wall")
            return False
            
        # check validity
        valid = self.board.place_wall(playWall)
        
        # deal with outcome
        if not valid:
            logging.info("illegal wall placement")
            playWall.reset_position()
            return False
        else:
            playWall.consolidate_position()
            return True
        
    @property
    def active(self):
        return self._active
    
    @active.setter
    def active(self, is_active):
        self._active = is_active
    
    @property
    def direction(self):
        return self.player_direction
        
    def get_possible_pawn_moves(self):
        # list up all possible directions.
        
        # ortho
        # self.board_instance.
        
        # jump
        
        # diagonal
        
        # print("direction to node:")
        # self.board.direction_to_node(self.pawn.position, pawn.WEST)
        print("not yet implemented")
        pass

    def undo_move_pawn(self):

        current_pos = self.pawn.position
        # print("hsitore: {}".format(self.pawn.positions_history))
        move_back_pos = self.pawn.positions_history[-2]
        self.board.move_pawn(current_pos, move_back_pos)
        self.pawn.previous_position()
        return True


    def move_pawn(self, direction):
    
        # direction i.e. pawn.NORTH
        if direction in pawn.DIRECTIONS_ORTHO:
            new_position = self.board.direction_to_node(self.pawn.position, direction)
            
            if new_position is None:
                status = "Pawn cannot move outside board"
                logging.info("ASSERT ERROR: checked neighbour node is not valid. Most probably pawn hits edge.")
                logging.info(status)
                # print(status)
                return False
            
            if self.board.pawn_on_node(new_position):
                
                status ="pawn on neighbour."
                # print("Error: " + status)
                logging.info("RULE VIOLATION: " + status)
                return False 
                
            if not self.board.nodes_directly_connected(self.pawn.position, new_position):
                
                status ="No move possible through wall."
                # print("Error:" + status)
                logging.info("RULE VIOLATION: " +status)
                
                
                return False
        
        elif direction in pawn.DIRECTIONS_ORTHO_JUMP:
            
            # get neighbour node
            neighbour_node = self.board.direction_to_node(self.pawn.position, pawn.FIRST_DIRECTION_FOR_ORTHO_JUMPS[direction])
            if neighbour_node is None:
                logging.warning("ASSERT ERROR: checked neighbour node is not valid. ")
                return False
            
            # check for pawn on neighbour node
            if not self.board.pawn_on_node(neighbour_node):
                # self.board.check_pawn_positions()
                # no pawn on neighbour node
                status = "No pawn on neighbour node"
                logging.info("RULE VIOLATION: "+ status)
                # print("Error: " + status)
                return False
                
            if not self.board.nodes_directly_connected(self.pawn.position, neighbour_node):
                # wall between jumper and jumpee
                 # no pawn on neighbour node
                status = "Wall in the way"
                logging.info("RULE VIOLATION: "+ status)
                # print("Error: " + status)
                return False
            
            # check the jump node
            new_position = self.board.direction_to_node(self.pawn.position, direction)
            
            if new_position is None:
                status = "Jump node is not valid."
                logging.info("RULE VIOLATION: "+ status)
                # print("Error: " + status)
                return False
            
            # check wall to jump node
            if not self.board.nodes_directly_connected(neighbour_node, new_position):
                status = "Wall encountered to jump node."
                logging.info("RULE VIOLATION: "+ status)
                # print("Error: " + status)
                return False
            
            # print("jump valid")    
            
        elif direction in pawn.DIRECTIONS_DIAGONAL_JUMP:
        
            #there are two routes for this one move to be completed. If one is not working, the other one needs to be tested
            
            # get neighbour node
            first_node_direction = None
            neighbour_node = None
            for first_step_direction in pawn.FIRST_DIRECTION_FOR_DIAGONAL_JUMPS[direction]:
                neighbour_node = self.board.direction_to_node(self.pawn.position, first_step_direction)
                
                if neighbour_node is not None:
                    if self.board.pawn_on_node(neighbour_node):
                        first_node_direction = first_step_direction
                        break
          
            if None in [neighbour_node, first_node_direction]:
                logging.info("ASSERT ERROR: No adjacent squares contain neighbour, no jumping allowed...... ")
                return False
            
                
            # check for pawn on neighbour node
            if not self.board.pawn_on_node(neighbour_node):
                # self.board.check_pawn_positions()
                # no pawn on neighbour node
                logging.info("error: no pawn on neighbour node")
                return False
                
            if not self.board.nodes_directly_connected(self.pawn.position, neighbour_node):
                # wall between jumper and jumpee
                logging.info("wall in the way")
                return False
            
            # check wall or edge behind pawn (there needs to be one)
            straight_jump_node = self.board.direction_to_node(self.pawn.position, pawn.ORTHO_JUMP_FROM_SINGLE_DIRECTION[first_node_direction])
            
            if straight_jump_node is not None:
                if self.board.nodes_directly_connected(neighbour_node, straight_jump_node):
                    logging.info("there should be a wall behind the jumped pawn to deflect left or right. None encountered.")
                    return False
            else:
                pass # no problem, board edge counts as wall
                
            # check the jump node
            new_position = self.board.direction_to_node(self.pawn.position, direction)
            if new_position is None:
                logging.info("ASSERT ERROR: jump end position is not valid. ")
                return False
            
            # check wall to jump node
            if not self.board.nodes_directly_connected(neighbour_node, new_position):
                logging.info("wall encountered between neighbour pawn and final node")
                return False
            
            
        else:
            info.warning("ASSERT ERROR: illegal direction ({})".format(direction))
            return False
        
            # valid = self.board.node_direction_ok(self.pawn.position, direction)
        
        # check if move possible.
    
        logging.info("move from: {}  to:{}".format(self.pawn.position, new_position))
        self.board.move_pawn(self.pawn.position, new_position)
        self.pawn.position = new_position
        return True


if __name__ == "__main__":
    test = Player("superlode", PLAYER_TO_NORTH)
    
    
    
        
            