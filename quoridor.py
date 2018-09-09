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

GAME_STATUS_NOT_STARTED = 0
GAME_STATUS_PLAYING = 1
GAME_STATUS_FINISHED = 2


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
    
    def game_user_input(self):
         #ask user for move if not provided.
        success = None
        while success is None:
            
            if self.players[self.playerAtMoveIndex].player_direction == 0:
                symbol = board.BOARD_CELL_PLAYER_TO_NORTH    
            else:
                symbol = board.BOARD_CELL_PLAYER_TO_SOUTH    
            
            move = input("player {} ({}) input move: ".format(self.players[self.playerAtMoveIndex].id, symbol))
            played = self.play_turn(move)
            self.turn_aftermath(played = played, display_board = True)
            
    def turn_prelude (self):\
        console_clear()
        
    def turn_aftermath(self, played = True, display_board = True):
        
        game_finished = False
        if played:
            #check winner
            game_finished = self.players[self.playerAtMoveIndex].get_pawn_winning_position()
            if game_finished:
                print("Game won by {}".format(str(self.players[self.playerAtMoveIndex])))
            else:
                self.nextPlayer()
            
        if game_finished:
            print("game should be stopped now....")

        if display_board:
           
            print(self)
            
       
        
    def play_turn(self, move):
        console_clear()   
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
            
            
       
        return played
    
    def play_turn_animated(self, move, animation_time_ms = 100):
       
        if self.play_turn(move):
            self.turn_aftermath()
           
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
        
    def state_as_dict(self):
        pass 
        
    def state_as_json(self):
        import json
    
        # r = {'is_claimed': 'True', 'rating': 3.5}
        json = json.dumps(r) # note i gave it a different name
        file.write(str(r['rating']))
        # def load_json():
        
        
    def __str__(self):
        return str(self.gameBoard)

def game_from_archive(gameString):
    pass
    
def game_to_archive(game, outputFile):
    pass

def game_from_json(json):
    pass
    
def game_to_json(game):

    pass
    
    
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
   
    q.game_user_input()
   
    game_20180908_Brecht_Lode_0 = {"player_1":"Lode", "player_2":"Brecht", "remarks":"fictional demo game" , "date":"20180908", "game":["n s n s n s n s"]}  
    
    