import player
import board
import pawn
import wall

import logging

import sys
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
        logging.info("Init Quoridor game ")
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

            self.play_sequence(moves, 200)

                
    def game_user_input(self):
         #ask user for move if not provided.
        success = None
        while success is None:
            
            if self.players[self.playerAtMoveIndex].player_direction == 0:
                symbol = board.BOARD_CELL_PLAYER_TO_NORTH    
            else:
                symbol = board.BOARD_CELL_PLAYER_TO_SOUTH    
           
            logging.info( "move history: {}".format(self.move_history))
            
            self.print_board()
            move = input("player {} {} input move(h for help)): ".format(self.players[self.playerAtMoveIndex].name, symbol))

            if move in ["u", "undo"]:
                self.undo_turn()
            elif move in ["m", "moves"]:
                 print("move history: {}".format(self.move_history))
            elif move in ["h", "help"]:
                print("\n"+
                "QUORIDOR game\n"+
                "    see ameije.com for rules\n"+
                "\n"+
                "PAWN movement commands:\n"+
                "    uses the compass rose notation (i.e. n for north)\n"+
                "n,e,s,w     for ortho movement\n"+
                "nn,ee,ss,ww for jumping over pawn\n"+
                "ne,nw,se,sw for diagonal jumping over pawn\n"+
                "\n"+
                "WALL placement commands:\n"+
                "    letters and digits are written on the board\n"+
                "[1-8][a-h]  for east-west wall placement (i.e. 2e)\n"+
                "[a-h][1-8]  for north-south wall placement (i.e h5)\n"+
                "\n"+
                "GENERAL commands:\n"+
                "u or undo   for undo last move\n"+
                "m or moves  for move history\n"+
                "h or help   for this help"+
                "\n"               
                )
                tmp = input("press any key to continue...") or None
                
            else:
                self.play_turn(move)

            
    def print_board (self):
        console_clear()
        print(self)

    # def turn_aftermath(self, played=True, display_board=True):

        # pass
        # if display_board:
            # self.print_board()

    def undo_turn(self, as_independent_turn=True, steps=1):
        # undoing a turn. 
        # as_independent_turn  if False --> we assume that we are in the middle of a turn, stays the same player.
        
        if len(self.move_history)==0:
            logging.info("nothing to undo")
            return False

        # check what the previous move was.

        move_to_undo = self.move_history.pop()
        
        if as_independent_turn:
            previous_player_index = self.get_previous_player_index()
        else:
            previous_player_index = self.playerAtMoveIndex
            
        success = False
        logging.info("undo previous move:{} by {}".format(move_to_undo, self.players[previous_player_index].name))
        if move_to_undo in NOTATION_TO_DIRECTION:
            #move pawn
            logging.info("undo pawn move")
            self.players[previous_player_index].undo_move_pawn()
            success = True
        else:
            # if wall : remove wall
            logging.info("undo wall move")
            success = self.gameBoard.remove_wall(move_to_undo)

        if success:
            if as_independent_turn:
                # activate previous player.
                self.playerAtMoveIndex = previous_player_index
            else:
                pass

        else:
            logging.error("undo unsuccessful")
            raise Exception("Big troubles at undoing.")
        # remake the previous statistics
        pass

    def make_move(self, move):
        # console_clear()   
        status = "Play turn ( {} playing move: {})".format(self.players[self.playerAtMoveIndex].name, move)
        # print(status)
        logging.info(status)
        #move in standard notation.
        
        move = move.lower()
        move_made = False
        
        if move in NOTATION_TO_DIRECTION:

            #move pawn
            move_made = self.move_pawn(move)
            logging.info("moved made?:{}".format(move_made))
        elif wall.Wall._notation_to_lines_and_orientation(move) is not None:
            move_made = self.place_wall(move)
            
        else:
            status = "Move {} has a wrong notation or is not yet implemented".format(move)
            print(status)
            logging.info("INPUT VIOLATION: "+ status)

        #add valid move to history
        if move_made:
            self.move_history.append(move)
        else:
            logging.info("move not made")
        
        return move_made

    def play_sequence(self, moves, animation_time_ms = None):


        success = False

        for move in moves:
            success = self.play_turn(move)
            if not success:
                status = "Illegal move in sequence! Aborting auto play. Provided sequence:{}. Played moves: {}".format(
                    moves, self.move_history)
                logging.info(status)
                print(status)

                return False
            elif animation_time_ms is not None:
                time.sleep(animation_time_ms / 1000)
                self.print_board()

        return True



    def play_turn(self, move):
        
        played = self.make_move(move)
            
        if not played:
            return False

        #check validity of board
        distances_to_win = self.gameBoard.distances_to_winning_node()
        if None in distances_to_win:
            # board invalid(None indicates infinite distance to winning position for pawn), undo turn
            self.undo_turn(as_independent_turn=False)
            played = False
            status = "ERROR: move not executed. There always must be a path to at least one of the winning squares for all players."
            print(status)
            logging.info("RULE VIOLATION: no winning path for both players. (dist pl1,dist pl2)(None = no path): {}".format(distances_to_win))
            return False
    
        #check for winner
        game_finished = self.players[self.playerAtMoveIndex].get_pawn_on_winning_position()
        if game_finished:
            self.print_board()
            print("Game won by {}".format(str(self.players[self.playerAtMoveIndex])))
            user_input = input("Press any key to exit the game. Press u for undo move.") or "exit"
            
            if user_input in ["u", "undo"]:
                self.undo_turn(as_independent_turn=False)
            else:
                sys.exit()
        else:
            self.next_player()
                
        return played
    
    # def play_turn_animated(self, move, animation_time_ms = 100):
    #     time.sleep(animation_time_ms/1000)
    #     self.print_board()
    #     if self.play_turn(move):
    #         # self.turn_aftermath()
    #         return True
    #     else:
    #         #no success == no animation
    #         try:
    #             tmp = input("wrong move notation, press key to continue.")
    #         except:
    #             pass
    #         return False


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

        status = "-----------Change player to {}".format(self.players[self.playerAtMoveIndex].name)
        logging.info(status)
        # print(status)

    def place_wall(self, position_verbose) :
        success = self.players[self.playerAtMoveIndex].place_wall(position_verbose)
        return success

    def move_pawn(self, move_verbose):

        # check for pawn or wall move
        direction = NOTATION_TO_DIRECTION[move_verbose]

        #move pawn
        success = self.players[self.playerAtMoveIndex].move_pawn(direction)
        if success:
            logging.info("pawn moved.")
        else:
            logging.info("pawn not moved.")
        return success
        
    def state_as_dict(self):
        pass 

    def state_as_json(self):
        import json
    
        # r = {'is_claimed': 'True', 'rating': 3.5}
        # json = json.dumps(r) # note i gave it a different name
        # file.write(str(r['rating']))
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
    
def logging_setup():
    # https://docs.python.org/3/howto/logging.html
    # logging.basicConfig(filename='c:/temp/quoridortest.log', level=logging.INFO)
    logging.basicConfig(filename='c:/temp/quoridortest.log', level=logging.INFO)
    formatter = logging.Formatter(fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.info('<<<<<<<<<<<<<<<<<<Start of new logging session.>>>>>>>>>>>>>>>>>>>>')

    # self.logger = logging.getLogger()    
    # handler = logging.StreamHandler()
    # formatter = logging.Formatter(
            # '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    # handler.setFormatter(formatter)
    # self.logger.addHandler(handler)
    # self.logger.setLevel(logging.DEBUG)

    # self.logger.debug('often makes a very good meal of %s', 'visiting tourists')
    
    
if __name__ == "__main__":
    logging_setup()
    # q.game_user_input()
   
    game_20180908_Brecht_Lode_0 = {"player_1":"Lode", "player_2":"Brecht", "remarks":"fictional demo game" , "date":"20180908", "game":"n s n s n s n s"}  
    game_Brecht_Lode = {"player_1":"Lode", "player_2":"Brecht"}  
    game_Brecht_Lode_wall_isolates_part_of_board = {"player_1":"Lode", "player_2":"Brecht", "game":"n s n s 7a"}
    
    # q = Quoridor(game_Brecht_Lode_wall_isolates_part_of_board)
    q = Quoridor(game_Brecht_Lode)
    q.game_user_input()
    # print(str(q))
   