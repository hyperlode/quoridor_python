import quoridor

import logging
import sys
import os

LOG_PATH = "c:/temp/"
LOG_FILENAME= "quoridor_local_games.log"
class Quoridor_local_game():
    
    def __init__(self, player_1_name=None, player_2_name=None):
    
        # preloaded game
        # q = Quoridor({"player_1":"Lode", "player_2":"Brecht", "remarks":"fictional demo game" , "date":"20180908", "game":"n s n s n s n s"})
        # q = Quoridor({"player_1":"Lode", "player_2":"Brecht"} )
        # q = Quoridor({"player_1":"Joos", "player_2":"Lode", "game":"n s n s n s n 6e 4d 4g e5 6c a6 b6 4b 5a 3a c3 1c 2b 1a 2d 1e 2f 1g 3h h1 sw"})
        # q = Quoridor{("player_1":"Joos", "player_2":"Lode", "game":"1c d2 3d e2 1f"})
        # q = Quoridor({"player_1":"Lode", "player_2":"Brecht", "game":"n s n s 7a"})

        # two computers game
        # q = Quoridor({"player_1": "auto", "player_2": "auto"})

        # computer against lode game
        # q = Quoridor({"player_1": "Lode", "player_2": "auto"})

        # fresh from scratch game
        # q = Quoridor()
        player_names = [player_1_name, player_2_name]
        
        for i, name in enumerate(player_names):
            if name is None:
                name = input("Name for player {} going {}. auto for automatic [player{}]".format(i+1, ["north", "south"][i], i+1)) or "player{}".format(i+1)
                player_names[i] = name
                
        # {"player_1": player_1_name, "player_2": player_2_name}
        
        self.q = quoridor.Quoridor({"player_1": player_names[0], "player_2": player_names[1]})
        self.game_loop()   
    
    def game_loop(self):
        # ask user for move if not provided.
        playing = True
        while playing:
            # display the board
            self.print_board()
            self.check_state()
            
            # get user input move
            if self.q.players[self.q.playerAtMoveIndex].name == "auto":
                self.q.auto_turn()
            else:
                self.human_turn()    
            
            feedback_message = self.q.get_status_message()
            if feedback_message != "":
                self.print_message(feedback_message)
        
    def check_state(self):
        state = self.q.get_state()
        
        if state == quoridor.GAME_STATE_FINISHED:
            self.print_message("Game won by {}".format(str(self.q.active_player())))
            user_input = input("Press any key to exit the game. Press u for undo move.") or "exit"

            if user_input in ["u", "undo"]:
                self.q.execute_command("undo")
            else:
                sys.exit()
        
    def human_turn(self):

        active_player_char = self.q.gameBoard.get_player_char(self.q.active_player().player_direction, True)
        logging.info("move history: {}".format(self.q.move_history))

        move = input("player {} {} input move(h for help)): ".format(self.q.active_player().name,
                                                                     active_player_char))

        # process input
        if move in ["u", "undo"]:
            self.q.execute_command("undo")
            
        elif move in ["m", "moves"]:
            self.print_message(self.q.execute_command("history"))
            
        elif move in ["q", "exit", "quit"]:
            user_input = input("Type y if you really want to abort the game.[n]") or "no"
            if user_input == "y":
                exit()
        
        elif move == "wide":
            self.q.execute_command("wide")

        elif move in ["r", "rotate"]:
            self.q.execute_command("rotate")

        elif move == ["wall"]:
            positions, delta = self.q.auto_wall_place_suggestion()
            self.print_message("Path length difference change (neg is in active player's advantage): {} by placing a wall on : {}".format(
                    delta, positions))

        elif move in [" ", "auto"]:
            result = self.q.execute_command("automove")
            
            if type(result) is list:
                execute_input = input(
                    "Multiple suggestions. Press enter to execute move: {} from: {}. Anything else to cancel.".format(
                        result[0], result)) or None
                if execute_input is None:
                    self.q.execute_command(result[0])

        elif move in ["h", "help"]:
            self.print_message(self.q.execute_command("help"))

        else:
            self.q.play_turn(move)
            
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
    logging.basicConfig(filename='{}{}'.format(LOG_PATH, LOG_FILENAME), level=logging.INFO)
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
    l = Quoridor_local_game(None, "auto")
    # l = Quoridor_local_game("auto", "auto")
    
    