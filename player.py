import wall
import pawn
import board
# import quori_constants
import logging

PLAYER_TO_NORTH = 0
PLAYER_TO_SOUTH = 1
PLAYER_DIRECTIONS = [PLAYER_TO_NORTH, PLAYER_TO_NORTH]
NUMBER_OF_WALLS = 10


class Player:
    def __init__(self, name, player_direction, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.logger.info("player created with name: {}".format(name))
        self.name = name
        
        # create walls
        self.walls = [wall.Wall(wall.TYPE_PLAYER, i) for i in range(NUMBER_OF_WALLS)]

        # create pawn
        self.pawn = pawn.Pawn(board.PAWN_INIT_POS[player_direction])
        self.board = None
        self.player_direction = player_direction
        
        # at_move
        self._active = False
        
    def __repr__(self):
        return str("Player {} at position: {}".format(self.name, self.pawn.position))
      
    @property
    def active(self):
        #player at move?
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
    
    def set_board(self, board_instance):
        self.board = board_instance
    
    def get_pawn_on_winning_position(self):
        return self.pawn.position in board.PAWN_WINNING_POS[self.player_direction]
    
    def number_of_unplaced_walls(self):
        number = 0
        for w in self.walls:
            if w.status == wall.STATUS_NOT_PLACED:
                number += 1
        return number

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
            self.logger.info(status)
            # print(status)
            return False
       
        # temporarily set wall
        placed = playWall.set_position(verbose_position, tentative=True)
        if not placed:
            self.logger.info("error in placing wall")
            return False
            
        # check validity
        valid = self.board.place_wall(playWall)
        
        # deal with outcome
        if not valid:
            self.logger.info("illegal wall placement")
            playWall.reset_position()
            return False
        else:
            playWall.consolidate_position()
            return True

    def undo_place_wall(self, position_verbose):
        return self.remove_wall(position_verbose)

    def remove_wall(self, position_verbose):
       
        success = False
        for w in self.walls:
            if w.get_position("verbose") == position_verbose:
                self.logger.info("ok, wall found")
                success = self.board.remove_wall(w)

                if success:
                    success = w.reset_position(allow_reset_placed_wall=True)
                else:
                    self.logger.error("wall not removed from board")

                if not success:
                    self.logger.error("wall not reset.")
                break
        if success:
            self.logger.info("wall removed from player")
        else:
            self.logger.warning("Wall {} not removed. was it available? {}".format(
                position_verbose,
                [w.get_position() for w in self.walls],
            ))

        return success
    
    def move_pawn(self, direction, fail_silent=False):
        # direction i.e. pawn.NORTH
        if direction in pawn.DIRECTIONS_ORTHO:
            new_position = self.board.direction_to_node(self.pawn.position, direction)
            
            if new_position is None:
                if not fail_silent:
                    status = "Pawn cannot move outside board"
                    self.logger.info("ASSERT ERROR: checked neighbour node is not valid. Most probably pawn hits edge.")
                    self.logger.info(status)
                return False
            
            if self.board.pawn_on_node(new_position):
                if not fail_silent:
                    status ="pawn on neighbour."
                    # print("Error: " + status)
                    self.logger.info("RULE VIOLATION: " + status)
                return False 
                
            if not self.board.nodes_directly_connected(self.pawn.position, new_position):
                if not fail_silent:
                    status ="No move possible through wall."
                    # print("Error:" + status)
                    self.logger.info("RULE VIOLATION: " +status)
                return False
        
        elif direction in pawn.DIRECTIONS_ORTHO_JUMP:
            
            # get neighbour node
            neighbour_node = self.board.direction_to_node(self.pawn.position, pawn.FIRST_DIRECTION_FOR_ORTHO_JUMPS[direction])
            if neighbour_node is None:
                if not fail_silent:
                    self.logger.warning("ASSERT ERROR: checked neighbour node is not valid. orthojump direction:{}".format(direction))
                    raise Exception
                return False
            
            # check for pawn on neighbour node
            if not self.board.pawn_on_node(neighbour_node):
                # self.board.check_pawn_positions()
                # no pawn on neighbour node
                if not fail_silent:

                    status = "No pawn on neighbour node"
                    self.logger.info("RULE VIOLATION: "+ status)
                # print("Error: " + status)
                return False
                
            if not self.board.nodes_directly_connected(self.pawn.position, neighbour_node):
                if not fail_silent:

                    # wall between jumper and jumpee
                     # no pawn on neighbour node
                    status = "Wall in the way"
                    self.logger.info("RULE VIOLATION: "+ status)
                    # print("Error: " + status)
                return False
            
            # check the jump node
            new_position = self.board.direction_to_node(self.pawn.position, direction)
            
            if new_position is None:
                if not fail_silent:

                    status = "Jump node is not valid."
                    self.logger.info("RULE VIOLATION: "+ status)
                    # print("Error: " + status)
                return False
            
            # check wall to jump node
            if not self.board.nodes_directly_connected(neighbour_node, new_position):
                if not fail_silent:
                
                    status = "Wall encountered to jump node."
                    self.logger.info("RULE VIOLATION: "+ status)
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
                if not fail_silent:

                    self.logger.info("ASSERT ERROR: No adjacent squares contain neighbour, no jumping allowed...... ")
                return False

            # check for pawn on neighbour node
            if not self.board.pawn_on_node(neighbour_node):
                # self.board.check_pawn_positions()
                # no pawn on neighbour node
                if not fail_silent:

                    self.logger.info("error: no pawn on neighbour node")
                return False
                
            if not self.board.nodes_directly_connected(self.pawn.position, neighbour_node):
                # wall between jumper and jumpee
                if not fail_silent:

                    self.logger.info("wall in the way")
                return False
            
            # check wall or edge behind pawn (there needs to be one)
            straight_jump_node = self.board.direction_to_node(self.pawn.position, pawn.ORTHO_JUMP_FROM_SINGLE_DIRECTION[first_node_direction])
            
            if straight_jump_node is not None:
                if self.board.nodes_directly_connected(neighbour_node, straight_jump_node):
                    if not fail_silent:

                        self.logger.info("there should be a wall behind the jumped pawn to deflect left or right. None encountered.")
                    return False
            else:
                pass # no problem, board edge counts as wall
                
            # check the jump node
            new_position = self.board.direction_to_node(self.pawn.position, direction)
            if new_position is None:
                if not fail_silent:

                    self.logger.info("ASSERT ERROR: jump end position is not valid. ")
                return False
            
            # check wall to jump node
            if not self.board.nodes_directly_connected(neighbour_node, new_position):
                if not fail_silent:

                    self.logger.info("wall encountered between neighbour pawn and final node")
                return False
            
            
        else:
            if not fail_silent:

                info.warning("ASSERT ERROR: illegal direction ({})".format(direction))
            return False
        
            # valid = self.board.node_direction_ok(self.pawn.position, direction)
        
        # check if move possible.
        if not fail_silent:
            self.logger.info("move from: {}  to:{}".format(self.pawn.position, new_position))
        self.board.move_pawn(self.pawn.position, new_position)
        self.pawn.position = new_position
        return True
    
    def get_position(self):
        return self.pawn.position

    def undo_move_pawn(self):

        current_pos = self.pawn.position
        history = "pawn move history: {}".format(self.pawn.positions_history)
        self.logger.info(history)
        self.logger.info("pawn history: {}".format(history))
        move_back_pos = self.pawn.positions_history[-2]
        success = self.board.move_pawn(current_pos, move_back_pos)

        if not success:
            self.logger.error("undo pawn fail at board move.")
            return False

        self.pawn.previous_position()
        return True


if __name__ == "__main__":
    test = Player("superlode", PLAYER_TO_NORTH)
    
    
    
        
            