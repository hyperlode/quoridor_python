import player
import board
import pawn
import wall

import logging

import sys
import time
import os

NOTATION_TO_DIRECTION = {
    "N":pawn.NORTH,
    "E":pawn.EAST,
    "S":pawn.SOUTH ,
    "W":pawn.WEST,
    "NN":pawn.NORTH_NORTH,
    "SS":pawn.SOUTH_SOUTH,
    "WW":pawn.WEST_WEST,
    "EE":pawn.EAST_EAST,
    "SW":pawn.SOUTH_WEST,
    "NW":pawn.NORTH_WEST,
    "SE":pawn.SOUTH_EAST,
    "NE":pawn.NORTH_EAST,
    
    #moves should be in upper case, but for the ease of thing on the input side, lower is allowed. the only ambiguity possible is with "e": E or line e for walls?
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
        self.distance_history =  [self.gameBoard.distances_to_winning_node()]  # keeps track of pawn to winning square distances per move.
        if "game" in list(self.settings):
            #if game in it, play automatically till end of recording.
            #game = string with space between every move.
            moves= self.settings["game"].split(" ")

            # self.play_sequence(moves, 200)
            self.play_sequence(moves, None)

                
    def game_user_input(self):
         #ask user for move if not provided.
        success = None
        while success is None:
            active_player_char = self.gameBoard.get_player_char(self.players[self.playerAtMoveIndex].player_direction, True)
           
            logging.info( "move history: {}".format(self.move_history))
            
            self.print_board()
            move = input("player {} {} input move(h for help)): ".format(self.players[self.playerAtMoveIndex].name, active_player_char))

            if move in ["u", "undo"]:
                self.undo_turn()
            elif move in ["m", "moves"]:
                 # self.print_message("move history: {}".format(self.move_history))
                 self.print_message(self.history_as_string())
            elif move in ["q", "exit", "quit"]:
                 user_input = input("Type y if you really want to abort the game.[n]") or "no"
                 if user_input == "y":
                    exit()
            elif move == "test":
                self.print_message(self.distance_history)
            
            elif move == "wide":
               self.gameBoard.wide_display_toggle()
            
            elif move in ["r", "rotate"]:
                self.gameBoard.rotate_board(None)
                
            elif move in ["h", "help"]:
                self.print_message("\n"+
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
                "h or help   for this help\n"+
                "wide        to toggle wider board\n"+
                "q or exit   for exit"+
                "r or rotate      for rotating the board 180DEG"
                "\n"               
                )
              
                
            else:
                self.play_turn(move)
                
    def pause(self):
        tmp = input("press any key to continue...") or None
        
    def history_as_string(self, include_distance_history=True):
        lines = []
        col_width  = len(self.players[0].name)
        if len(self.players[0].name) < len(self.players[1].name):
            col_width = len(self.players[1].name)
        col_width += 3
        # lines.append("{:{width}}test".format(width = 10))
        lines.append("{0:<{w}} | {1:<{w}} | {2:<{w}} | d{1:<{w}}| d{2:<{w}}".format("", self.players[0].name,self.players[1].name,w = col_width))
        # split history per two moves (= one turn)
       
        # incremental distance history
        distance_history_incremental = []
       
        for i, dist in enumerate(self.distance_history[:-1]):
            distance_history_incremental.append(( self.distance_history[i+1][0] - dist [0], self.distance_history[i+1][1] - dist[1]))
        
        distances_output = "incremental per turn"
        
        if distances_output=="incremental per turn":
            
            # incremental once per complete turn
            turns = []
            for i in range(0,len(self.move_history),2):
                if i >= len(self.move_history)-1:
                    # make sure there is an even number of turns
                    turns.append((self.move_history[i], "", distance_history_incremental[i][0] , + distance_history_incremental[i][1]))
                else:
                    turns.append((self.move_history[i], self.move_history[i+1], 
                    distance_history_incremental[i][0] + distance_history_incremental[i+1][0], 
                    distance_history_incremental[i][1] + distance_history_incremental[i+1][1]))
        elif distances_output=="incremental":
            # incremental distances
            turns = []
            for i in range(0,len(self.move_history),2):
                print(i)
                print(len(self.move_history))
                if i >= len(self.move_history)-1:
                    # make sure there is an even number of turns
                    turns.append((self.move_history[i], "", distance_history_incremental[i], ""))
                else:
                    turns.append((self.move_history[i], self.move_history[i+1], 
                    distance_history_incremental[i], 
                    distance_history_incremental[i+1]))
        elif distances_output=="absolute":    
               
            # absolute distances
            turns = []
            for i in range(0,len(self.move_history),2):
                if i >= len(self.move_history)-1:
                    # make sure there is an even number of turns
                    turns.append((self.move_history[i], "", self.distance_history[i], ""))
                else:
                    turns.append((self.move_history[i], self.move_history[i+1], 
                    self.distance_history[i], 
                    self.distance_history[i+1]))
        else:
            logging.error("ASSERT ERROR: no distances column print option")
        # create the columns
        for i, turn in enumerate(turns):
            if include_distance_history:
                # print(turn)
                lines.append("{0:>{w}} | {1:<{w}} | {2:<{w}} | {3:<{w}} | {4:<{w}}".format(i, turn[0], turn[1], str(turn[2]), str(turn[3]), w=col_width))   
            else:
                lines.append("{0:>{w}} | {1:<{w}} | {2:<{w}}".format(i, turn[0], turn[1], w=col_width))
        return "\n".join(lines)
        
    def print_board (self):
        console_clear()
        print(self)
    
    def print_message(self, message):
        print(message)
        self.pause()

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
        self.distance_history.pop()
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
        #move in standard notation.
        status = "Play turn ( {} playing move: {})".format(self.players[self.playerAtMoveIndex].name, move)
        logging.info(status)
        
        move = move.lower()  # clean up first, the only problem move is E3 vs e3  (pawn move over line three vs wall placement).
        move_made = False
        
        if move in NOTATION_TO_DIRECTION:
            #move pawn
            move = move.upper()
            move_made = self.move_pawn(move)
            logging.info("moved made?:{}".format(move_made))
           
            
        elif wall.Wall._notation_to_lines_and_orientation(move) is not None:
            move_made = self.place_wall(move)
        else:
            status = "Move {} has a wrong notation or is not yet implemented".format(move)
            self.print_message(status)
            logging.info("INPUT VIOLATION: "+ status)

        #add valid move to history
        if not move_made:
            status = "move not made"
            logging.info(status)
            self.print_message(status)
        else:
            self.move_history.append(move)
        
        return move_made

    def play_sequence(self, moves, animation_time_ms = None):
        success = False
        for move in moves:
            success = self.play_turn(move)
            if not success:
                status = "Illegal move in sequence! Aborting auto play. Provided sequence:{}. Played moves: {}".format(
                    moves, self.move_history)
                logging.info(status)
                self.print_message(status)
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
        self.distance_history.append(distances_to_win)
        
        if None in distances_to_win:
            # board invalid(None indicates infinite distance to winning position for pawn), undo turn
            self.undo_turn(as_independent_turn=False)
            played = False
            status = "ERROR: move not executed. There always must be a path to at least one of the winning squares for all players."
            self.print_message(status)
            logging.info("RULE VIOLATION: no winning path for both players. (dist pl1,dist pl2)(None = no path): {}".format(distances_to_win))
            return False
    
        #check for winner
        game_finished = self.players[self.playerAtMoveIndex].get_pawn_on_winning_position()
        if game_finished:
            self.print_board()
            self.print_message("Game won by {}".format(str(self.players[self.playerAtMoveIndex])))
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
        #deactivate current player
        self.players[self.playerAtMoveIndex].active = False
                
        #activate next player
        self.playerAtMoveIndex += 1
        if self.playerAtMoveIndex >= len(self.players):
            self.playerAtMoveIndex = 0
        
        self.players[self.playerAtMoveIndex].active = True
        
        status = "-----------Change player to {}".format(self.players[self.playerAtMoveIndex].name)
        logging.info(status)
        # self.print_message(status)

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
    game_Joos_Lode = {"player_1":"Joos", "player_2":"Lode", "game":"n s n s n s n 6e 4d 4g e5 6c a6 b6 4b 5a 3a c3 1c 2b 1a 2d 1e 2f 1g 3h h1 sw"}
    game_Brecht_Lode_wall_isolates_part_of_board = {"player_1":"Lode", "player_2":"Brecht", "game":"n s n s 7a"}
    
    # q = Quoridor(game_Brecht_Lode_wall_isolates_part_of_board)
    q = Quoridor(game_Brecht_Lode)
    q.game_user_input()
    # print(str(q))
   