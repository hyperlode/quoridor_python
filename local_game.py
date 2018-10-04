import quoridor

import logging
import sys
import os

LOG_PATH = "c:/temp/"
LOG_FILENAME= "quoridor_local_games.log"
class Quoridor_local_game():
    
    def __init__(self, player_1_name=None, player_2_name=None, moves=None, loop = False):
        # loop for automatic restart after game end.
        # name will be asked when player names None 
        # for computer player: auto_1 --> 1 level deep brute force
        # for computer player: auto_2 --> 2 level deep brute force
        # moves: list or array with sequence of verbose moves as game starting point.
    
        self.player_names = [player_1_name, player_2_name]
        
        for i, name in enumerate(self.player_names):
            if name is None:
                name = input("Name for player {} going {}. auto for automatic [player{}]".format(i+1, ["north", "south"][i], i+1)) or "player{}".format(i+1)
                self.player_names[i] = name
                
        # loop is mainly used to let computers fight each other.
        self.loop = loop
        if self.loop:
            self.pause_enabled = False
        else:
            self.pause_enabled = True
        
        self.init_dict = {"player_1": self.player_names[0], "player_2": self.player_names[1], "game":moves}
        self.pause()
        self.q = quoridor.Quoridor(self.init_dict)
        self.game_loop()   
        
    def save_to_stats_file(self, stats):
        stats_file = open("c:/temp/{}_{}.txt".format(self.player_names[0],self.player_names[1]),"a") 
        stats_file.write("{}\n".format(stats))
        stats_file.close()
        
    def game_loop(self):
        # ask user for move if not provided.
        playing = True
        while playing:
            # display the board
            self.print_board()
            self.check_state()
            
            if self.q.get_state() == quoridor.GAME_STATE_PLAYING:
                # get user input move
                if "auto" in self.q.players[self.q.playerAtMoveIndex].name:
                    self.auto_turn()
                else:
                    self.human_turn()    
                    
            elif self.q.get_state() == quoridor.GAME_STATE_NOT_STARTED:
                pass
                # # get user input move
                # if auto in self.q.players[self.q.playerAtMoveIndex].name:
                    # self.q.auto_turn(depth=1)
                # else:
                    # self.human_turn()    

            elif self.q.get_state() == quoridor.GAME_STATE_FINISHED:
                if not self.loop:
                    self.command("m")
                    command = input("game finished. Please enter command.(h for help, enter for exit)") or "exit"
                    test = self.command(command)
                else:
                    # restart game.
                    self.command("save_stats")
                    self.q = quoridor.Quoridor(self.init_dict)
            else:
                logging.error("wrong game state: {}".format(self.q.get_state()))
                print("eoije")
                
            feedback_message = self.q.get_status_message()
            if feedback_message != "":
                self.print_message(feedback_message)
        
    def check_state(self):
        state = self.q.get_state()
        
        # if state == quoridor.GAME_STATE_FINISHED:
            # self.print_message("Game wooon by {}".format(str(self.q.active_player())))
            # user_input = input("Press any key to exit the game. Press m for menu options.") or "exit"

            # if user_input in ["m"]:
                # # self.q.set_state(quoridor.GAME_STATE_PLAYING)
                # self.q.execute_command("help")
            # else:
                # sys.exit()
        
    def auto_turn(self):
        name = self.q.players[self.q.playerAtMoveIndex].name
        if name == "auto_1":
            self.q.auto_turn(depth=1)
        elif name == "auto_2":
            self.q.auto_turn(depth=2)
        else:
            self.q.auto_turn()
    
    def human_turn(self):

        active_player_char = self.q.gameBoard.get_player_char(self.q.active_player().player_direction, True)
        logging.info("move history: {}".format(self.q.move_history))

        move = input("player {} {} input move(h for help)): ".format(self.q.active_player().name,
                                                                     active_player_char))
        success = self.command(move, True)
    
    def command(self, command, allow_moves = True):
       
       # process input
        if command in ["u", "undo"]:
            self.q.execute_command("undo")
        
        elif command == "test":
            self.print_message(self.q.execute_command("test"))
            
        elif command in ["m", "moves"]:
            self.print_message(self.q.execute_command("history"))
        
        elif command in ["save_stats"]:
            self.save_to_stats_file(str(self.q.execute_command("history")))
            
        elif command in ["stats"]:
            self.print_message(self.q.execute_command("history_nice"))
            
        elif command in ["q", "exit", "quit"]:
            user_input = input("Type y if you really want to abort the game.[n]") or "no"
            if user_input == "y":
                exit()
        
        elif command == "lev1":
            self.print_message(self.q.execute_command("suggest_level_1"))
            pass
            
        elif command == "lev2":
            self.print_message(self.q.execute_command("suggest_level_2"))
            pass
            
        elif command == "wide":
            self.q.execute_command("wide")

        elif command in ["r", "rotate"]:
            self.q.execute_command("rotate")

        elif command == ["wall"]:
            positions, delta = self.q.auto_wall_place_suggestion()
            self.print_message("Path length difference change (neg is in active player's advantage): {} by placing a wall on : {}".format(
                    delta, positions))

        elif command in [" ", "auto"]:
            result = self.q.execute_command("automove")
            
            if type(result) is list:
                execute_input = input(
                    "Multiple suggestions. Press enter to execute move: {} from: {}. Anything else to cancel.".format(
                        result[0], result)) or None
                if execute_input is None:
                    self.q.execute_command(result[0])
                else:
                    self.q.execute_command(execute_input)

        elif command in ["h", "help"]:
            self.print_message(self.q.execute_command("help"))

        else:
            return self.q.play_turn(command)
    def pause(self):
        if self.pause_enabled:
          tmp = input("press any key to continue...") or None
                
    def print_board(self):
        board_string = self.q.board_as_string() 
        console_clear()
        print(board_string)
            
    def print_message(self, message):
        print(message)
        self.pause()
        
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
    logging.basicConfig(filename='{}{}'.format(LOG_PATH, LOG_FILENAME), level=logging.ERROR)
    formatter = logging.Formatter(fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.info('<<<<<<<<<<<<<<<<<<Start of new logging session.>>>>>>>>>>>>>>>>>>>>')

    # self.logger = logging.getLogger()    
    # handler = logging.StreamHandler()
    # formatter = logging.Formatter(
            # '%(asctime)s %n
    # (name)-12s %(levelname)-8s %(message)s')
    # handler.setFormatter(formatter)
    # self.logger.addHandler(handler)
    # self.logger.setLevel(logging.DEBUG)

    # self.logger.debug('often makes a very good meal of %s', 'visiting tourists')
    
if __name__ == "__main__":
    logging_setup()
    # l = Quoridor_local_game()
    # l = Quoridor_local_game(None, "auto")
    # l = Quoridor_local_game(None, "auto_2")
    # l = Quoridor_local_game("auto_1", "auto_1", loop=True)
    # l = Quoridor_local_game("auto_1", "auto_2", loop=True)
    # l = Quoridor_local_game("auto_2", "auto_2", loop=True)
    l = Quoridor_local_game("a", "b", ['n', 's', '1e', '3e', 'n', '8c', '4d', 'e', '2f', '4f', '3g', '7b', 'w', 's', 'n', 's', 'w', 's', 'n', '2c', '1h', 'c7', '1a', 'b5', 'n', '5a', '6f', 'h6', 'g4', 'd6', 'c5', 'w', '4h', 'n', 'n', 'n', 'w', 'n', 'w', 'n', 'n', 'w', 'n'])
    # l = Quoridor_local_game("fromAI1", "fromAI2", ['n', 's', '1e', '7c', '1c', 'e2', '3f', '2b', 'n', '3d', 'w', 'c3', '1g', 'a1', 's', '5h', 'w', '5f', 'w', '2h', 's', '8b', 'e', 'w', 'b7', 'e', 'e', 's', 'e', 'w', '6c', 'e', 'c5', 's', 'e', 's', 'e', 's', 'e', 'e', 'e', 'e', 'n', 'e', 'w', 's', 'h1', 'n', '3a', 'n', '7e', 'w', 'w', 'w', 'n', 'w', 'e', 'n', 'n', 'n', 'w', 'e', 'w', 'e', 'n', 'n', 'w', 'n', 'n', 'w', 'e', 'w', 'n', 'w', 'e', 'w', 'n', 'w', 'n'])
    # l = Quoridor_local_game("fromAI1", "fromAI2", ['n', 's', '1e', '7c', '1c', 'e2', '3f', '2b', 'n', '3d', 'w', 'c3', '1g', 'a1', 's', '5h', 'w', '5f', 'w', '2h', 's', '8b', 'e', 'w', 'b7', 'e', 'e', 's', 'e', 'w', '6c', 'e', 'c5'])
    # l = Quoridor_local_game("auto_1", "auto_1", ['n', 's', '1e', '7c', '1c', 'e2', '3f', '2b', 'n', '3d', 'w', 'c3', '1g', 'a1', 's', '5h', 'w', '5f', 'w', '2h', 's'], loop=True)
    # l = Quoridor_local_game("fromAI1", "fromAI2", ['n', 's', 'n', 's', '2d', '7e', '3e', 'd3', 'e', 's', 'e', 'h2', 'n', '7g', 'e', 'g3', 'e', '2g', '3c', '4h', 's', '4f', 's', '7a', 's', 'f3', 'd5', 'n', 'd7', 'e', 'f6', 's', '5f', 'w', '6h', 's', 'w', 'e', 'w', 'e', '2a', 'e', '1b', 'n', 'n', 'w', 'w', 'n', 'w', 'e', 'w', 'e', 'w', 'n', 'n', 'w', 'w', 'w', 'n', 'w', 'n', 'w', 'n', 'n', 'n', 'w', 'e', 's', 'n', 's', 'n'])