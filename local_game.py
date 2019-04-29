#!/usr/bin/env python
# -*- coding: utf-8 -*-
import quoridor

import logging
import sys
import os
import time

LOG_PATH = "c:/temp/"
LOG_FILENAME= "quoridor_local_games.log"
class Quoridor_local_game():
    
    def __init__(self, player_1_name=None, player_2_name=None, moves=None, loop = False):
        # loop for automatic restart after game end.
        # name will be asked when player names None 
        # for computer player: auto_1 --> 1 level deep brute force
        # for computer player: auto_2 --> 2 level deep brute force
        # for computer player: auto_3 --> 3 level deep brute force
        # moves: list or array with sequence of verbose moves as game starting point.
    
        self.player_names = [player_1_name, player_2_name]
        
        for i, name in enumerate(self.player_names):
            if name is None:
                name = input("---INPUT PLAYERS--- \nType auto_1, auto_2 or auto_3 for computer player (1 is easy, 3 is hard).\nName for player {} going {}. [player{}]:".format(i+1, ["north", "south"][i], i+1)) or "player{}".format(i+1)
                self.player_names[i] = name
                
        # loop is mainly used to let computers fight each other.
        self.loop = loop
        if self.loop:
            self.pause_enabled = False
        else:
            self.pause_enabled = True
        
        self.init_dict = {"player_1": self.player_names[0], "player_2": self.player_names[1], "game":moves}
        # self.pause()
        
        output_encoding = sys.stdout.encoding  # check for command line encoding. utf-8 is desired.
        
        self.q = quoridor.Quoridor(self.init_dict, output_encoding)
        self.game_loop()   
        
    def save_to_stats_file(self, stats):
        path = "{}{}_{}.txt".format(LOG_PATH,self.player_names[0],self.player_names[1])
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        stats_file = open(path,"a") 
        stats_file.write("{}\n".format(stats))
        stats_file.close()
        self.print_message("History appended to file: {} ".format(path))
        
    def game_loop(self):
        # ask user for move if not provided.
        playing = True
        while playing:
            # display the board
            # self.pause()
            self.print_board()

            self.check_state()
            if self.q.get_state() == quoridor.GAME_STATE_PLAYING:
                start_millis = int(round(time.time() * 1000))

                # get user input move
                if "auto" in self.q.players[self.q.playerAtMoveIndex].name:
                    self.auto_turn()
                else:
                    self.human_turn()

                calc_time = int(round(time.time() * 1000)) - start_millis
                print("calc time = {} millis".format(calc_time))
                
                # self.print_message("___end of turn____")
                    
            elif self.q.get_state() == quoridor.GAME_STATE_NOT_STARTED:
                pass
                # # get user input move
                # if auto in self.q.players[self.q.playerAtMoveIndex].name:
                    # self.q.auto_turn(depth=1)
                # else:
                    # self.human_turn()    

            elif self.q.get_state() == quoridor.GAME_STATE_FINISHED:
                if not self.loop:
                    # self.command("moves")
                    self.command("stats")
                    self.command("save_stats")
                    command = input("game finished. Please enter u for undoing, r for restart or enter for exit") or "exit"
                    if command in ["u", "undo"]:
                        self.q.set_state(quoridor.GAME_STATE_PLAYING)
                        self.q.execute_command("undo")
                        self.q.execute_command("undo")
                    elif command in ["r", "restart"]:
                        self.q = quoridor.Quoridor(self.init_dict)    
                    else:
                        exit()
                    # test = self.command(command)
                else:
                    # restart game.
                    self.command("save_stats")
                    self.q = quoridor.Quoridor(self.init_dict)
            else:
                logging.error("wrong game state: {}".format(self.q.get_state()))
                
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
        elif name == "auto_3":
            self.q.auto_turn(depth=3)
        else:
            self.q.auto_turn()
    
    def human_turn(self):

        active_player_char = self.q.gameBoard.get_player_char(self.q.active_player().player_direction)
        logging.info("move history: {}".format(self.q.move_history))

        move = input("player {} {} input move(h for help)): ".format(self.q.active_player().name,
                                                                     active_player_char))
        feedback = self.command(move, True)
    
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
            
        # elif command in ["df"]:
            # self.q.execute_command("dijkstra fast")
            # self.pause()
            
        elif command in ["stats"]:
            self.print_message(self.q.execute_command("history_nice"))
            
        elif command in ["q", "exit", "quit"]:
            user_input = input("Type y if you really want to abort the game.[n]") or "no"
            if user_input == "y":
                self.command("save_stats")
                exit()
        
        elif command == "analyse":
            moves_with_delta = self.q.execute_command("analyse")
            
            deltas = sorted(list(set( moves_with_delta.values())))
            moves_sorted_by_delta = {}
            for d in deltas:
                moves_sorted_by_delta[d] = sorted([k for k,v in moves_with_delta.items() if d == v])
                
            self.print_message("\n".join(["delta: {}:{}\n".format(k,v) for k,v in moves_sorted_by_delta.items()]))
            
        elif command == "lev1":
            start_millis = int(round(time.time() * 1000))
            suggestions = self.q.execute_command("suggest_level_1")
            calc_time =int(round(time.time() * 1000)) -  start_millis 
            print("calc time = {} millis".format(calc_time))
            self.print_message(suggestions)
            
        elif command == "lev2":
            start_millis = int(round(time.time() * 1000))
            suggestions = self.q.execute_command("suggest_level_2")
            calc_time =int(round(time.time() * 1000)) -  start_millis 
            print("calc time = {} millis".format(calc_time))
            self.print_message(suggestions)
        
        elif command == "lev3":
            start_millis = int(round(time.time() * 1000))
            suggestions = self.q.execute_command("suggest_level_3")
            calc_time =int(round(time.time() * 1000)) -  start_millis 
            print("calc time = {} millis".format(calc_time))
            self.print_message(suggestions)
        
        elif command == "wide":
            self.q.execute_command("wide")

        elif command in ["r", "rotate"]:
            self.q.execute_command("rotate")

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
            help = self.q.execute_command("help")
            local_game_help = (   
                "\n"+
                "RENAMED commands: \n"+
                "lev1          level 1 auto suggestions\n" +
                "lev2          level 2 auto suggestions\n" +
                "SPACE or auto to auto move pawn\n" +
                "stats         for complete game statistics\n" 
            )
            
            self.print_message(help + local_game_help)
        else:
            feedback = self.q.execute_command(command)
            if feedback is not None:
                self.print_message( feedback)
            
            
    def pause(self):
        if self.pause_enabled:
          tmp = input("press ENTER to continue...(no commands accepted here)") or None
                
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
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    logging.basicConfig(filename='{}{}'.format(LOG_PATH, LOG_FILENAME), level=logging.ERROR)
    # logging.basicConfig(filename='{}{}'.format(LOG_PATH, LOG_FILENAME), level=logging.INFO)
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
    #l = Quoridor_local_game()
    l = Quoridor_local_game(None, "auto_2")
    # computer stuck: l = Quoridor_local_game(None, "fake2", ['n', 's', 'n', '8d', 'n', '8f', '3d', 's', '3f', 's', 'n', 'ss', 'n', '8b', 'n', 'f7', 'w', 'a7', '5a', 'b6', '8h', 'c7', '5c', '6d', '5e', 'e', 'e', 'w', 'e', 'e', 's', 'w', 'w', 'e', 'w', 'w', 'w', 'e', 'n', 'w', 'n', 'e', 'w', 'w', 's', 'e', 's', 'w'])

    # l = Quoridor_local_game(None, "auto_2")
    #wouterAuto = ['n', 's', 'n', '8d', 'n', '8f', 'n', '8b', 'n', '8h', '5d', 'w', '5h', 's', '5f', 'w', 'w', 's', '5b', '6a', '1a', '6c', 'e6', 'w', 'e', 'w', 'n', 's', 'w', 's', 'w', 'e', 'n', 'a8', 's', 'b6', 'n', 's', 'w', 'e', '1c', 'e', 'd3','n', 's', 's', 'w', 'n', 'n', 'w']
    #l = Quoridor_local_game("tmp", "tmp2", wouterAuto)
    # l = Quoridor_local_game(None, "au", ['n', 's', 'n', '8d', 'n', '8f', '3d', '8b', '3f', '8h', 'n', 's', 'w', 's', 'w', 's', 'n', 's', '5a', 'a6', '5c', '7b', 'd6', '6c', 'd4'])
    # l = Quoridor_local_game(None, "auto_1",['n', 's', 'n', '8d', '7e', 'w', '7c', '8g', 'n', 'w', 'n', 'w', '7a', 'e', 'e', 'e', 'n', 'f6', '4f', '5e', 'w', 'e4', 'w', '5c', 'w', 'e2', 'w', '7h', 's', '6g', 's', 'e', 'e', 'e', 's', 'e', 's', 'c1', 'n', 's', 'e', 'e', 'e', 'e', 's', 's', '5h', 'w', 'h3', 'w', 's', 's', 'e', 'e', 'e', 's', '3g', 'w', 'e', 'w', 'f2', 's', 'n', 's'])
    #l = Quoridor_local_game("lode", "auto_3")
    # l = Quoridor_local_game("auto_1", "auto_1")
    # l = Quoridor_local_game("auto_1", "auto_1", loop=True)
    # l = Quoridor_local_game("auto_1", "auto_2", loop=True)
    # l = Quoridor_local_game("auto_2", "auto_2", loop=True)
    l = Quoridor_local_game("auto_2", "auto_3", loop=True)

    # l = Quoridor_local_game("auto_2", "auto_2")

    ## test cases
    #l = Quoridor_local_game("test", "tttt", ['n', 's', 'n', 's','n','e','n','s','n','s'] )
    
    # l = Quoridor_local_game("Lode", "from AI2", ['n', 's', 'n', '8d', 'n', '8f', '3d', '8b', 'n', '8h', 'w', 's', 'w', 's', '4a', 's', '4c', 's', 'n'], loop=False)  # next auto_2 move was ", 'g7'" why??
    
    
    # l = Quoridor_local_game("a", "b", ['n', 's', 'n', 's', 'n', '7f', 'n', '8c', '1d', '7d', 'e', '7h', 'n', 'e6', '6d', 'f4', 'b7', '5f', '6b', 'g5'])
    # l = Quoridor_local_game("bramz", "wasAuto1", ['n', 's', 'n', 's', 'n', 's', '3d', '4d', 'e', '6e', 'e5', '6g', '4b', '7h', 'a5', 'w', 'a7', 'n', 'g7', 'e3', 's', '2f', '3f', 'c2', 'e', 'd1', 'e', 'g2', 's', '1g', 'e', 'n', 's', 'w', 'w', 'w', '8b', 'e', 'c7', 's', '7d', 's', 'w', 'e', 'w', 'n', 'n', 'e', 'w', 'e', 'n', 'n', 'w', 'w', 's', 'w', 's', 'n', 'w', 'w', 'n', 'w', 'n', 'w', 'n', 's', 'w', 's', 'w', 's', 'n', 'ss', 'n', 's', 'n', 's', 'n', 's'])
    # l = Quoridor_local_game("fromAI1", "fromAI2", ['n', 's', '1e', '7c', '1c', 'e2', '3f', '2b', 'n', '3d', 'w', 'c3', '1g', 'a1', 's', '5h', 'w', '5f', 'w', '2h', 's', '8b', 'e', 'w', 'b7', 'e', 'e', 's', 'e', 'w', '6c', 'e', 'c5', 's', 'e', 's', 'e', 's', 'e', 'e', 'e', 'e', 'n', 'e', 'w', 's', 'h1', 'n', '3a', 'n', '7e', 'w', 'w', 'w', 'n', 'w', 'e', 'n', 'n', 'n', 'w', 'e', 'w', 'e', 'n', 'n', 'w', 'n', 'n', 'w', 'e', 'w', 'n', 'w', 'e', 'w', 'n', 'w', 'n'])
    # l = Quoridor_local_game("fromAI1", "fromAI2", ['n', 's', '1e', '7c', '1c', 'e2', '3f', '2b', 'n', '3d', 'w', 'c3', '1g', 'a1', 's', '5h', 'w', '5f', 'w', '2h', 's', '8b', 'e', 'w', 'b7', 'e', 'e', 's', 'e', 'w', '6c', 'e', 'c5'])
    # l = Quoridor_local_game("auto_1", "auto_1", ['n', 's', '1e', '7c', '1c', 'e2', '3f', '2b', 'n', '3d', 'w', 'c3', '1g', 'a1', 's', '5h', 'w', '5f', 'w', '2h', 's'], loop=True)
    # l = Quoridor_local_game("fromAI1", "fromAI2", ['n', 's', 'n', 's', '2d', '7e', '3e', 'd3', 'e', 's', 'e', 'h2', 'n', '7g', 'e', 'g3', 'e', '2g', '3c', '4h', 's', '4f', 's', '7a', 's', 'f3', 'd5', 'n', 'd7', 'e', 'f6', 's', '5f', 'w', '6h', 's', 'w', 'e', 'w', 'e', '2a', 'e', '1b', 'n', 'n', 'w', 'w', 'n', 'w', 'e', 'w', 'e', 'w', 'n', 'n', 'w', 'w', 'w', 'n', 'w', 'n', 'w', 'n', 'n', 'n', 'w', 'e', 's', 'n', 's', 'n'])
