TYPE_EDGE = 0
TYPE_PLAYER = 1

STATUS_NOT_PLACED = 0
STATUS_SIMULATION = 1
STATUS_PLACED = 2 

NORTH_SOUTH = 0
EAST_WEST = 1

class Wall():

    def __init__(self, type, id):
        self.type = type
        if type == TYPE_EDGE:
            self.status = STATUS_PLACED
        else:
            self.status = STATUS_NOT_PLACED
        self.id = id
        
        self.position_cells = None
   
    # def place(pos):
        # self.placed = True
        # self.position = pos
    
    @property
    def cells(self):
        return self.position_verbose_to_cells
    
    @staticmethod
    def position_verbose_to_cells(verbose):
        #i.e.    "3d" -> ((5,3)(6,3))
        
        verbose = verbose.lower()
        
        try:
            a, b = verbose 
            
            self.orientation = None
            if a.isdigit() and b.isalpha():
                self.orientation = EAST_WEST
                digit = a
                letter = b
                
                col = ord(letter) -96  # a = 97
                row = digit
                
                
            elif a.isalpha() and b.isdigit():
                self.orientation = NORTH_SOUTH
                digit = b
                letter = a
            else:
                raise Exception("ASSERT ERROR: verbose notation wrong. Should be of the kind: 3f  or b0. Provide string was: {}".format(verbose))
            
                
            
        except :
            raise
            pass
            
        
    @property
    def status(self):
        return self.position
    @status.setter
    def status(self,status):
        
        self.status = status
        return True

    def place(position_verbose):
        if self.position is not None:
            print("ASSERT ERROR: wall can only be place once")
            return False

if __name__ == "__main__":
    w = Wall(TYPE_PLAYER, "test")
    
    pass
    