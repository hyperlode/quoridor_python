import quoridor

import logging
import sys
import os

LOG_PATH = "c:/temp/"
LOG_FILENAME= "quoridor_local_games.log"
class Quoridor_local_game():
    
    def __init__(self, player_1_name=None, player_2_name=None, moves=None):
    
        # preloaded game
        # q = Quoridor({"player_1":"Lode", "player_2":"Brecht", "remarks":"fictional demo game" , "date":"20180908", "game":"n s n s n s n s"})
        # q = Quoridor({"player_1":"Lode", "player_2":"Brecht"} )
        # q = Quoridor({"player_1":"Joos", "player_2":"Lode", "game":"n s n s n s n 6e 4d 4g e5 6c a6 b6 4b 5a 3a c3 1c 2b 1a 2d 1e 2f 1g 3h h1 sw"})
        # q = Quoridor{("player_1":"Joos", "player_2":"Lode", "game":"1c d2 3d e2 1f"})
        # q = Quoridor({"player_1":"Lode", "player_2":"Brecht", "game":"n s n s 7a"})

      
        player_names = [player_1_name, player_2_name]
        
        for i, name in enumerate(player_names):
            if name is None:
                name = input("Name for player {} going {}. auto for automatic [player{}]".format(i+1, ["north", "south"][i], i+1)) or "player{}".format(i+1)
                player_names[i] = name
                
        # {"player_1": player_1_name, "player_2": player_2_name}
        
        self.q = quoridor.Quoridor({"player_1": player_names[0], "player_2": player_names[1], "game":moves})
        self.game_loop()   
    
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
                    name = self.q.players[self.q.playerAtMoveIndex].name
                    if name == "auto_1":
                        self.q.auto_turn(depth=1)
                    elif name == "auto_2":
                        self.q.auto_turn(depth=2)
                    else:
                        self.q.auto_turn()
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
                self.command("m")
                command = input("game finished. Please enter command.(h for help, enter for exit)") or "exit"
                test = self.command(command)

            else:
                logging.error("wrong game state.juilk")
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
            
        elif command in ["s", "stats"]:
            self.print_message(self.q.execute_command("history_nice"))
            
        elif command in ["q", "exit", "quit"]:
            user_input = input("Type y if you really want to abort the game.[n]") or "no"
            if user_input == "y":
                exit()
        
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

        elif command in ["h", "help"]:
            self.print_message(self.q.execute_command("help"))

        else:
            return self.q.play_turn(command)
        
        
        
    
    def pause(self):
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
    l = Quoridor_local_game("auto_1", "auto_2")
    # l = Quoridor_local_game("fromAI1", "fromAI2", ['n', 's', '1e', '7c', '1c', 'e2', '3f', '2b', 'n', '3d', 'w', 'c3', '1g', 'a1', 's', '5h', 'w', '5f', 'w', '2h', 's', '8b', 'e', 'w', 'b7', 'e', 'e', 's', 'e', 'w', '6c', 'e', 'c5', 's', 'e', 's', 'e', 's', 'e', 'e', 'e', 'e', 'n', 'e', 'w', 's', 'h1', 'n', '3a', 'n', '7e', 'w', 'w', 'w', 'n', 'w', 'e', 'n', 'n', 'n', 'w', 'e', 'w', 'e', 'n', 'n', 'w', 'n', 'n', 'w', 'e', 'w', 'n', 'w', 'e', 'w', 'n', 'w', 'n'])
    # l = Quoridor_local_game("fromAI1", "fromAI2", ['n', 's', 'n', 's', '2d', '7e', '3e', 'd3', 'e', 's', 'e', 'h2', 'n', '7g', 'e', 'g3', 'e', '2g', '3c', '4h', 's', '4f', 's', '7a', 's', 'f3', 'd5', 'n', 'd7', 'e', 'f6', 's', '5f', 'w', '6h', 's', 'w', 'e', 'w', 'e', '2a', 'e', '1b', 'n', 'n', 'w', 'w', 'n', 'w', 'e', 'w', 'e', 'w', 'n', 'n', 'w', 'w', 'w', 'n', 'w', 'n', 'w', 'n', 'n', 'n', 'w', 'e', 's', 'n', 's', 'n'])