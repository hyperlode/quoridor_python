class Pawn():
    def __init__(player, pos):
        self.player = player
        self.position = pos

    @property
    def position(self):
        return self.position

    @position.setter
    def position(self,value):
        self.position = value
