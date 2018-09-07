import player
import board
import pawn
import wall

TEST = 10



NOTATION_TO_DIRECTION = {
    "n":pawn.NORTH,
    "e":pawn.EAST,
    "s":pawn.SOUTH ,
    "w":pawn.WEST,
    "nn":pawn.NORTH_NORTH,
    "ss":pawn.SOUTH_SOUTH,
    "ww":pawn.WEST_WEST,
    "ee":pawn.EAST_EAST,
    "sw":pawn.SOUTH_WEST,
    "nw":pawn.NORTH_WEST,
    "se":pawn.SOUTH_EAST,
    "ne":pawn.NORTH_EAST
}

WALL_NOTATION_TO_POSITION = {
    

}

class Quoridor():
    
    def __init__(self):
        player1 = player.Player("lode", player.PLAYER_TO_NORTH)
        player2 = player.Player("brecht", player.PLAYER_TO_SOUTH)
        self.players = [player1, player2]
        self.gameBoard = board.Board()
        self.gameBoard.add_player(player1)
        self.gameBoard.add_player(player2)
        
        for pl in self.players:
            pl.set_board(self.gameBoard)
            
        self.playerAtMoveIndex = 0
            
        
    def playTurn(self, move):
        print("----play turn ( {} playing move: {})------".format(self.players[self.playerAtMoveIndex].id, move))
        #move in standard notation.
        
        move = move.lower()
        played = False
        
        if move in NOTATION_TO_DIRECTION:
        
            #check for pawn or wall move
            direction = NOTATION_TO_DIRECTION[move]
            #move pawn
            played = self.movePawn(direction)

        else:
            # print(wall.Wall.position_verbose_to_cells(move))
            played = self.players[self.playerAtMoveIndex].place_wall(move)
        
        if played:
            self.nextPlayer()
        
        return played
        
    def nextPlayer(self):
        #swap player
        self.playerAtMoveIndex += 1
        
        if self.playerAtMoveIndex >= len(self.players):
            self.playerAtMoveIndex = 0
        print("change player. new player at move: {}".format(self.players[self.playerAtMoveIndex].id))
    
    def movePawn(self, direction):
        print("move pawn:")
        #move pawn
        success = self.players[self.playerAtMoveIndex].move_pawn(direction)
        
        
        print("succes?:{}".format(success))
        return success
        
    def __str__(self):
        return str(self.gameBoard)
        
if __name__ == "__main__":
    q = Quoridor()
    
    # q.playTurn()
    q.playTurn("n")
    q.playTurn("s")
    q.playTurn("n")
    q.playTurn("s")
    q.playTurn("n")
    q.playTurn("s")
    q.playTurn("n")
    q.playTurn("ss")
    # q.playTurn("e")
    # q.playTurn("e")
    
    q.playTurn("ss")
    q.playTurn("ss")
    q.playTurn("ss")
    q.playTurn("s")
    q.playTurn("e4")
    q.playTurn("5e")
    q.playTurn("e6")
    q.playTurn("NN")
    q.playTurn("NN")
    q.playTurn("NN")
    q.playTurn("NW")
    print(q)
    
    