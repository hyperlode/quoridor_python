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
            print("no free walls for this player available")
            return False
       
        # temporarily set wall
        placed = playWall.set_position(verbose_position, tentative=True)
        if not placed:
            print("error in placing wall")
            return False
            
        # check validity
        valid = self.board.place_wall(playWall)
        
        # deal with outcome
        if not valid:
            print("illegal wall placement")
            playWall.reset_position()
            return False
        else:
            playWall.consolidate_position()
            return True
        
    # @property
    # def pawn(self):
        # return self.pawn.
    
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
                print("ASSERT ERROR: checked neighbour node is not valid. ")
                return False
            
            if self.board.pawn_on_node(new_position):
                print("error: pawn on neighbour.")
                return False 
                
            if not self.board.nodes_directly_connected(self.pawn.position, new_position):
                print("no move possible: wall")
                return False
        
        elif direction in pawn.DIRECTIONS_ORTHO_JUMP:
            
            # get neighbour node
            neighbour_node = self.board.direction_to_node(self.pawn.position, pawn.FIRST_DIRECTION_FOR_ORTHO_JUMPS[direction])
            if neighbour_node is None:
                print("ASSERT ERROR: checked neighbour node is not valid. ")
                return False
            
            # check for pawn on neighbour node
            if not self.board.pawn_on_node(neighbour_node):
                # self.board.check_pawn_positions()
                # no pawn on neighbour node
                print("error: no pawn on neighbour node")
                return False
                
            if not self.board.nodes_directly_connected(self.pawn.position, neighbour_node):
                # wall between jumper and jumpee
                print("wall in the way")
                return False
            
            # check the jump node
            new_position = self.board.direction_to_node(self.pawn.position, direction)
            
            if new_position is None:
                print("ASSERT ERROR: jump node is not valid. ")
                return False
            
            # check wall to jump node
            if not self.board.nodes_directly_connected(neighbour_node, new_position):
                print("wall encountered to jump node")
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
                        print("found pawn!!!")
                        first_node_direction = first_step_direction
                        break
            print(neighbour_node)
            print(first_node_direction)
            if None in [neighbour_node, first_node_direction]:
                print("ASSERT ERROR: No adjacent squares contain neighbour, no jumping allowed...... ")
                return False
            
                
            # check for pawn on neighbour node
            if not self.board.pawn_on_node(neighbour_node):
                # self.board.check_pawn_positions()
                # no pawn on neighbour node
                print("error: no pawn on neighbour node")
                return False
                
            if not self.board.nodes_directly_connected(self.pawn.position, neighbour_node):
                # wall between jumper and jumpee
                print("wall in the way")
                return False
            
            # check wall or edge behind pawn (there needs to be one)
            straight_jump_node = self.board.direction_to_node(self.pawn.position, pawn.ORTHO_JUMP_FROM_SINGLE_DIRECTION[first_node_direction])
            
            if straight_jump_node is not None:
                if self.board.nodes_directly_connected(neighbour_node, straight_jump_node):
                    print("there should be a wall behind the jumped pawn to deflect left or right. None encountered.")
                    return False
            else:
                pass # no problem, board edge counts as wall
                
            # check the jump node
            new_position = self.board.direction_to_node(self.pawn.position, direction)
            if new_position is None:
                print("ASSERT ERROR: jump end position is not valid. ")
                return False
            
            # check wall to jump node
            if not self.board.nodes_directly_connected(neighbour_node, new_position):
                print("wall encountered between neighbour pawn and final node")
                return False
            
            
        else:
            print("ASSERT ERROR: illegal direction ({})".format(direction))
            return False
        
            # valid = self.board.node_direction_ok(self.pawn.position, direction)
        
        # check if move possible.
    
        print("move from: {}  to:{}".format(self.pawn.position, new_position))
        self.board.move_pawn(self.pawn.position, new_position)
        self.pawn.position = new_position
        return True


if __name__ == "__main__":
    test = Player("superlode", PLAYER_TO_NORTH)
    
    
    
        
            