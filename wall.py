TYPE_EDGE = 0
TYPE_PLAYER = 1

STATUS_NOT_PLACED = 0
STATUS_SIMULATION = 1
STATUS_PLACED = 2 

NORTH_SOUTH = 0
EAST_WEST = 1

class Wall():

    def __init__(self, type, id):
        self._type = type
        
        if type == TYPE_EDGE:
            self._status = STATUS_PLACED
        else:
            self._status = STATUS_NOT_PLACED
        
        self._id = id
        self._position_nodes = None
        self._position_verbose = None
        self._position_lines_orientation = None   # format (horiline, vertiline,orientation) lines as digits, from 1 to 8, orientation NORTH_SOUTH or EAST_WEST
        
    @staticmethod    
    def position_verbose_to_nodes(verbose):
        position_lines_orientation = Wall._notation_to_lines_and_orientation(verbose)
        
        if position_lines_orientation is None:
            print ("failed to interpret wall notation")
            return None, None
        
        nodes =  Wall._position_lines_to_nodes(position_lines_orientation)
        if nodes is None:
            return None, None
        return nodes, position_lines_orientation
        
    @staticmethod
    def _position_lines_to_nodes( position_lines_orientation):
        hori_line, vert_line, orientation = position_lines_orientation
        
        # there are four nodes (2x2) involved per wall. get 2 x and 2 y coords.
        x_nodes = [vert_line - 1, vert_line]
        y_nodes = [hori_line - 1, hori_line]

        if orientation == EAST_WEST:
            # define node which links will be severed by the wall.
            edge_cut_0 = ((x_nodes[0], y_nodes[0]), (x_nodes[0], y_nodes[1]))
            edge_cut_1 = ((x_nodes[1], y_nodes[0]), (x_nodes[1], y_nodes[1]))

        elif orientation == NORTH_SOUTH:
            # define node which links will be severed by the wall.
            edge_cut_0 = ((x_nodes[0], y_nodes[0]), (x_nodes[1], y_nodes[0]))
            edge_cut_1 = ((x_nodes[0], y_nodes[1]), (x_nodes[1], y_nodes[1]))
                       
        else:
            # raise Exception("ASSERT ERROR: verbose notation wrong. Should be of the kind: 3f  or b0. Provide string was: {}".format(verbose))
            print("ASSERT ERROR: verbose notation wrong. Should be of the kind: 3f  or b0. Provide string was: {}".format(verbose))
            return None
        
        return [edge_cut_0, edge_cut_1]
    
    # @staticmethod
    # def _notation_to_wall_lines_numbers( letter, digit):

        # #notation to wall line numbers
        # vert_line = ord(letter) - 96  # a = 97
        # hori_line = int(digit)
        
        # #check boundaries
        # if vert_line<1 or vert_line > 8 or hori_line<1 or hori_line>8:
            # print("outside boundaries. a1 to h8. Submission:letter {} digit".format(letter,digit))
            # return None, None

        # #there are four nodes (2x2) involved per wall. get 2 x and 2 y coords.
        # x_nodes = [vert_line - 1, vert_line]
        # y_nodes = [hori_line - 1, hori_line]
        
        # return x_nodes, y_nodes
    
    @staticmethod
    def _notation_to_lines_and_orientation(verbose):
        # notation a1 to 8h
        
        verbose = verbose.lower()
        
        if len(verbose) != 2:
            print("notation wrong: {}".format(verbose))
            return None
        
        a, b = verbose 
        
        orientation = None
        if a.isdigit() and b.isalpha():
            orientation = EAST_WEST
            digit = a
            letter = b
            
        elif a.isalpha() and b.isdigit():
            orientation = NORTH_SOUTH
            digit = b
            letter = a
           
        # notation to wall line numbers
        vert_line = ord(letter) - 96  # a = 97
        hori_line = int(digit)
        
        # check boundaries
        if vert_line<1 or vert_line > 8 or hori_line<1 or hori_line>8:
            print("outside boundaries. a1 to h8. Submission:letter {} digit".format(letter,digit))
            return None
        
        return (hori_line, vert_line, orientation)
                       
    @property
    def type(self):
        return self._type
    
    @property
    def id(self):
        return self._id
    
        
    @property
    def status(self):
        return self._status


    @status.setter
    def status(self,s):
        self._status = s
        return True
    
    def get_position(self, notation = "verbose"):
        # notation = "verbose", "lines_orientation", "nodes"

        if self._status == STATUS_NOT_PLACED:  
            return None

        if notation == "nodes":
            return self._position_nodes
        elif notation == "verbose":
            return self._position_verbose
        elif notation == "lines_orientation":
            return self._position_lines_orientation
        else:
            print("please provide notation")
            return None

    def reset_position(self, allow_reset_placed_wall = False):
        if self._status == STATUS_SIMULATION or self._status == STATUS_NOT_PLACED or allow_reset_placed_wall:
            self._position_nodes = None
            self._position_verbose = None
            self._position_lines_orientation = None   
            return True
        else:
            print("once a wall is placed, it cannot be undone")
            return False
            
    def consolidate_position(self):
        if self._status == STATUS_SIMULATION:
            self._status = STATUS_PLACED
            return True
        elif self._status == STATUS_PLACED:
            print ("already consolidated")
            return True
        elif self._status == STATUS_NOT_PLACED:
            print ("nothing to consolidate")
            return False
        else:
            print ("ASSERT ERROR: illegal status")
            return False
    def set_position(self, position_verbose, tentative = False):
        #position is verbose.
        
        if self._status != STATUS_NOT_PLACED:
            print("ASSERT ERROR: wall can only be placed once")
            return False
        
        nodes, position_lines_orientation = Wall.position_verbose_to_nodes(position_verbose)
        
        print("nodes: {}".format(nodes))
            
        if nodes is not None:
            self._position_nodes = nodes
            self._position_verbose = position_verbose
            self._position_lines_orientation = position_lines_orientation
            if tentative:
                self._status = STATUS_SIMULATION
            else:
                self._status = STATUS_PLACED
            return True
        else:
            return False
    
    def __str__(self):
        if self._status != STATUS_PLACED:
            return "Wall with id {} was not yet placed".format(self._id)
        else:
            return "Wall with id {0}, was played on position {1}. (horizontal line:{2[0]}, vertical line: {2[1]:}, orientation(0=north-south): {2[2]}) and affects nodes: {3}".format(
            self._id, self._position_verbose, self._position_lines_orientation, self._position_nodes)    
        
if __name__ == "__main__":
    w = Wall(TYPE_PLAYER, "test")
    print( str(w))
    print("wrong position")
    w.set_position("e9")
    print(str(w))
    print("placing wall")
    w.set_position("e3")
    print( str(w))
    w.set_position("3e")
    pass
    