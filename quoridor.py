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
    
    def __init__(self, settings = None):
        # settings = dict. 
    
        if settings is None:
            # start from scratch
            player1_name = input("Name for player 1 (going north) [player_1]:") or "player_1"
            player2_name = input("Name for player 2 (going south) [player_2]:") or "player_2"
            self.settings = {}
        else:
            # scrape the dict to see what settings are available
            
            player1_name = settings["player_1"]
            player2_name = settings["player_2"]
            self.settings = settings
            #if direction of player 1 is not North, change it here.
            
        
        player1 = player.Player(player1_name, player.PLAYER_TO_NORTH)
        player2 = player.Player(player2_name, player.PLAYER_TO_SOUTH)
        
        self.players = [player1, player2]
        self.gameBoard = board.Board()
        self.gameBoard.add_player(player1)
        self.gameBoard.add_player(player2)
        
        for pl in self.players:
            pl.set_board(self.gameBoard)
            
        self.playerAtMoveIndex = 0
        
        self.move_history = []
        if "game" in list(self.settings):
            #if game in it, play automatically till end of recording.
            #game = string with space between every move.
            moves= self.settings["game"].split(" ")
            
            for move in moves:
                self.play_turn(move)
            
    def game_user_input(self):
         #ask user for move if not provided.
        success = None
        while success is None:
            
            if self.players[self.playerAtMoveIndex].player_direction == 0:
                symbol = board.BOARD_CELL_PLAYER_TO_NORTH    
            else:
                symbol = board.BOARD_CELL_PLAYER_TO_SOUTH    
            self.print_board()
            print("move history: {}".format(self.move_history))

            move = input("player {} {} input move(u to undo)): ".format(self.players[self.playerAtMoveIndex].name, symbol))

            if move == "u":
                print("undo previous move")
                self.undo_turn()
            else:
                self.play_turn(move)

            
    def print_board (self):
        console_clear()
        print(self)

    # def turn_aftermath(self, played=True, display_board=True):

        # pass
        # if display_board:
            # self.print_board()

    def undo_turn(self, steps=1):
        # undoing a turn.

        if len(self.move_history)==0:
            print("nothing to undo")
            return False

        # check what the previous move was.

        move_to_undo = self.move_history.pop()
        previous_player_index = self.get_previous_player_index()
        success = False

        print("previous move:{} by {}".format(move_to_undo, self.players[previous_player_index].name))
        if move_to_undo in NOTATION_TO_DIRECTION:
            # if pawn move : set back to previous position
            #move pawn
            # played = self.move_pawn(move)
            print("undo pawn move")
            self.players[previous_player_index].undo_move_pawn()
            success = True
        else:
            # if wall : remove wall
            print("undo wall move")
            success = self.gameBoard.remove_wall(move_to_undo)

        if success:
            # activate previous player.
            self.playerAtMoveIndex = previous_player_index
        else:
            raise Exception("Big troubles at undoing.")
        # remake the previous statistics
        pass

        #take away wall, undo move. --> remember previous absolute position.

    def play_turn(self, move):
        console_clear()   
        print("----play turn ( {} playing move: {})------".format(self.players[self.playerAtMoveIndex].name, move))
        #move in standard notation.
        
        move = move.lower()
        played = False
        
        if move in NOTATION_TO_DIRECTION:

            #move pawn
            played = self.move_pawn(move)

        elif wall.Wall._notation_to_lines_and_orientation(move) is not None:
            played = self.place_wall(move)
            
        else:
            print("Move {} has a wrong notation or is not yet implemented".format(move))


        #check validity of board
        distances_to_win = self.gameBoard.distances_to_winning_node()

        if None in distances_to_win:

            played = False
            # undo turn.

        else:
            # valid
            pass

        #add valid move to history
        if played:
            self.move_history.append(move)
        
        game_finished = False
        if played:
            #check winner
            game_finished = self.players[self.playerAtMoveIndex].get_pawn_on_winning_position()
            if game_finished:
                print("Game won by {}".format(str(self.players[self.playerAtMoveIndex])))
                  
                print("game should be stopped now.... work with game statusses!")
            else:
                self.next_player()
        return played
    
    def play_turn_animated(self, move, animation_time_ms = 100):
        time.sleep(animation_time_ms/1000)
        self.print_board()
        if self.play_turn(move):
            self.turn_aftermath()
            return True
        else:
            #no success == no animation
            try:
                tmp = input("wrong move notation, press key to continue.")
            except:
                pass
            return False

    def get_previous_player_index(self):
        #returns the previous player index.
        previous = self.playerAtMoveIndex - 1
        if previous < 0:
            previous = len(self.players) - 1
        return previous

    def next_player(self):
        #activate next player
        self.playerAtMoveIndex += 1
        if self.playerAtMoveIndex >= len(self.players):
            self.playerAtMoveIndex = 0

        print("change player. new player at move: {}".format(self.players[self.playerAtMoveIndex].name))

    def place_wall(self, position_verbose) :
        success = self.players[self.playerAtMoveIndex].place_wall(position_verbose)
        return success

    def move_pawn(self, move_verbose):
        print("move pawn:")
        # check for pawn or wall move
        direction = NOTATION_TO_DIRECTION[move_verbose]
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
    
    # q.game_user_input()
   
    game_20180908_Brecht_Lode_0 = {"player_1":"Lode", "player_2":"Brecht", "remarks":"fictional demo game" , "date":"20180908", "game":"n s n s n s n s"}  
    game_Brecht_Lode = {"player_1":"Lode", "player_2":"Brecht"}  
    game_Brecht_Lode_wall_isolates_part_of_board = {"player_1":"Lode", "player_2":"Brecht", "game":"n s n s 7a"}  
    
    # q = Quoridor(game_Brecht_Lode_wall_isolates_part_of_board)
    q = Quoridor(game_Brecht_Lode)
    q.game_user_input()
    # print(str(q))
   