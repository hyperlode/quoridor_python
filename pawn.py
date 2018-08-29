
# POSITION_INIT = 0
# POSITION_GAME = 1
# POSITION_END = 2

class Pawn():
    def __init__(self, position_init, positions_win):
        # self.player = player
        self.position_init = position_init
        self.position = position_init
        self.positions_win = positions_win
        self.positions_history = [self.position]
        
    def win(self):
        return self.position in self.positions_win
        
    @property
    def position(self):
        return self.position

    @position.setter
    def position(self,value):
        self.position = value
        self.positions_history.append(self.position)