import player
import board
import pawn
import wall

import time
import os

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
            
        
    def playTurn(self, move = None):
    
        #ask user for move if not provided.
        if move is None:
            move = input("player {} input move: ".format(self.players[self.playerAtMoveIndex].id))
            
    
        print("----play turn ( {} playing move: {})------".format(self.players[self.playerAtMoveIndex].id, move))
        #move in standard notation.
        
        move = move.lower()
        played = False
        
        if move in NOTATION_TO_DIRECTION:
            #check for pawn or wall move
            direction = NOTATION_TO_DIRECTION[move]
            #move pawn
            played = self.movePawn(direction)

        elif wall.Wall._notation_to_lines_and_orientation(move) is not None:
            
            played = self.players[self.playerAtMoveIndex].place_wall(move)
        else:
            print("Move {} has a wrong notation or is not yet implemented".format(move))
        if played:
            self.nextPlayer()
        return played
    
    def play_turn_animated(self, move, animation_time_ms = 100):
    
        
        if self.playTurn(move):
            console_clear()
            print(self)
            time.sleep(animation_time_ms/1000)
            return True
        else:
            #no success == no animation
            try:
                tmp = input("wrong move notation, press key to continue.")
            except:
                pass
                
            return False
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

def console_clear():
    '''
    Clears the terminal screen and scroll back to present
    the user with a nice clean, new screen. Useful for managing
    menu screens in terminal applications.
    '''
    os.system('cls' if os.name == 'nt' else 'echo -e \\\\033c')
        
if __name__ == "__main__":
    q = Quoridor()
    print(str(q))
    while True:
        q.play_turn_animated( None, 100)
    # q.playTurn()
    # q.play_turn_animated("k")
    q.play_turn_animated("n")
    q.play_turn_animated("s")
    q.play_turn_animated("n")
    q.play_turn_animated("s")
    q.play_turn_animated("n")
    q.play_turn_animated("s")
    q.play_turn_animated("n")
    q.play_turn_animated("ss")
    q.play_turn_animated("ss")
    q.play_turn_animated("ss")
    q.play_turn_animated("ss")
    # q.play_turn_animated("s")
    q.play_turn_animated("e4")
    q.play_turn_animated("5e")
    q.play_turn_animated("e6")
    q.play_turn_animated("NN")
    q.play_turn_animated("NN")
    q.play_turn_animated("NN")
    q.play_turn_animated("NW")
    q.play_turn_animated("3d")
    q.play_turn_animated("se")
    q.play_turn_animated("sw")
    q.play_turn_animated("ww")
    # q.play_turn_animated("1i")
  
    
    