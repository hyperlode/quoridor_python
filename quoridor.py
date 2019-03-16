import player
import board
import pawn
import wall


import logging
import random
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
    
    #moves should be in upper case, but for the ease of things on the input side, lower is allowed. the only ambiguity possible is with "e": E or line e for walls?
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

ALL_PAWN_DIRECTIONS = ["N","E","S","W","NN","EE","SS","WW","NE","SE","NW","SW"]


GAME_STATE_NOT_STARTED = 0
GAME_STATE_PLAYING = 1
GAME_STATE_FINISHED = 2
GAMES_STATES = [GAME_STATE_FINISHED, GAME_STATE_NOT_STARTED, GAME_STATE_PLAYING]

SIDE_BAR_EMPTY_SPACE = " "


class Quoridor():
    
    def __init__(self, settings = None, output_encoding = None):
        
        self.game_state = GAME_STATE_NOT_STARTED
        self.status_message = ""
        
        self.output_encoding = output_encoding
        
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
        self.gameBoard = board.Board(self.output_encoding)
        self.gameBoard.add_player(player1)
        self.gameBoard.add_player(player2)

        for pl in self.players:
            pl.set_board(self.gameBoard)
            
        self.playerAtMoveIndex = 0
        
        self.move_history = []
        self.distance_history =  [self.gameBoard.distances_to_winning_node()]  # keeps track of pawn to winning square distances per move.
        self.game_state = GAME_STATE_PLAYING 
        if "game" in list(self.settings):
            #if game in it, play automatically till end of recording.
            data = self.settings["game"]
            if data is None:
                pass
            elif type(data) is str:
                #game = string with space between every move.
                moves= data.split(" ")
                self.play_sequence(moves, None)
            elif type(data) is list:
                moves = data
                self.play_sequence(moves, None)
                
        

    # ADMINISTRATION
    
    def get_state(self):
        return self.game_state
        # if self.game_state == GAME_STATE_FINISHED:
        
    def set_state(self, state):
        if state in GAMES_STATES:
            self.game_state = state
            return True
        else:
            return False
     
    def set_status(self, message):
        self.status_message += message
    
    def get_status_message(self, erase_after_reading=True):
        tmp = self.status_message
        self.status_message = ""
        return tmp
        
    def active_player(self):
        # return active player object
        return self.players[self.playerAtMoveIndex]
    
    def inactive_player(self):
        # return the non playing player
        return self.players[self.get_previous_player_index()]
        
    # ACTION
    
    def execute_command (self, move):
        # move can be a valid move or a commmand.
       
        # process input
        if move == "undo":
            steps = len(['a' for player in self.players if "auto" in player.name]) + 1
            self.undo_turn(steps = steps)
            
        elif move == "history":
            return self.move_history
            
        elif move == "history_nice":
            return self.history_as_string()
            
        elif move in ["new", "restart"]:
            #restart game.
            pass
            
        elif move == "wide":
            self.gameBoard.wide_display_toggle()

        elif move == "rotate":
            self.gameBoard.rotate_board(None)
            
        elif move == "suggest_level_2":
            return self.auto_level_2(True, verbose=True)
        
        elif move == "suggest_level_1":
            return self.auto_level_1(True)
            
        elif move == "analyse":
            # all moves with delta for one level deep
            return self.analyse_level()
            
        elif move == "automove":
            auto_move_directions = self.auto_pawn_move_suggestion()
            if len(auto_move_directions) > 1:
                return auto_move_directions
                
            elif len(auto_move_directions) == 1:
                return self.play_turn(auto_move_directions[0])
            else:
                logging.error("unvalid auto move directions. {}".format(auto_move_directions))
        elif move == "test":
            # return self.analyse_level()
            # return self.auto_level_2(True)

            paths =  self.gameBoard.paths_to_winning_node()

            crossed_wall_lines = set()
            for path in paths:
                for index in range(len(path) - 1):
                    crossed_wall_lines.add((path[index], path[index+1]))
                    crossed_wall_lines.add((path[index+1], path[index]))

            print(crossed_wall_lines)
            print( "paths: {}, with distances: {}".format(paths, self.gameBoard.distances_to_winning_node()))
            print(  self.check_wall_affects_shortest_paths("a3"))
            print(  self.check_wall_affects_shortest_paths("d1"))
            print(  self.check_wall_affects_shortest_paths("1d"))
        elif move in ["help"]:
            return ("\n" +
                    "QUORIDOR game\n" +
                    "    see ameije.com for rules\n" +
                    "\n" +
                    "PAWN movement commands:\n" +
                    "    uses the compass rose notation (i.e. n for north)\n" +
                    "n,e,s,w       for ortho movement\n" +
                    "nn,ee,ss,ww   for jumping over pawn\n" +
                    "ne,nw,se,sw   for diagonal jumping over pawn\n" +
                    "\n" +
                    "WALL placement commands:\n" +
                    "    letters and digits for each line are indicated on the board\n" +
                    "    first char: indicates line and direction, second char: center point\n" +
                    "[1-8][a-h]    for east-west wall placement (i.e. 2e)\n" +
                    "[a-h][1-8]    for north-south wall placement (i.e h5)\n" +
                    "\n" +
                    "GENERAL commands:\n" +
                    "u or undo     for undo last move\n" +
                    "m or moves    for move history\n" +
                    "lev1          level 1 auto suggestions\n" +
                    "lev2          level 2 auto suggestions\n" +
                    "stats         for complete game statistics\n" +
                    "h or help     for this help\n" +
                    "wide          to toggle wider board\n" +
                    "SPACE or auto to auto move pawn\n" +
                    "analyse       to see all moves with their effect on players path\n" +
                    "q or exit     for exit\n" +
                    "r or rotate   for rotating the board 180DEG"
                    "\n"
                    )
        else:
            self.play_turn(move)
   
    def auto_turn(self, depth=1, simulate=False):
   
        if depth == 1:
            return self.auto_level_1(simulate)
        elif depth == 2:
            return self.auto_level_2(simulate)
        else:
            logging.error("auto_turn parameter not correct. ")
            
    def auto_level_1(self, simulate=False):
        # brute force one move 
        # simulate returns all (move,pathdelta) pairs with best delta (is most path shortening).
        
        deltas = self.analyse_level()
        best = min(deltas.values())
        
        if simulate:
            suggestions = {move:dist for move,dist in deltas.items() if dist == best}
            return suggestions
        else:
            suggestions = [move for move,dist in deltas.items() if dist == best]
            index = random.randint(0, len(suggestions)-1)
            self.play_turn(suggestions[index])
        
    def auto_level_2(self, simulate=False, verbose=False):
        # brute force two moves 
        # simulate: only return list of equal distance suggestions.

        deltas = self.analyse_level()
        
        # level 1
        all_level_2_moves_with_delta = {}
        all_moves_level_2 = {}  # for multiple levels: a move is a list of the next moves as key. value is the delta 
        opponent = self.inactive_player().direction

        if verbose:
            print(deltas)
        # level 2
        for i, (pos_level_1, delta) in enumerate(deltas.items()): # run through all possible level 1 moves.

            drawProgressBar(i/len(deltas.items()))
            if verbose:
                print("level1move: {}".format(pos_level_1))
            # make level 1 move
            success = self.make_move(pos_level_1)
            
            #change the player to opponent
            self.active_player().active = False
            self.playerAtMoveIndex += 1
            if self.playerAtMoveIndex >= len(self.players):
                self.playerAtMoveIndex = 0
            self.active_player().active = True
            
            # obtain all realistic level 2 moves
            # as this is only to level 2, select the best moves this player will make. (if deeper levels would be considered, we would keep all moves).
            # get most likely opponent moves (moves that shorten opponents path most).
            best_opponent_moves_with_deltas = self.auto_level_1(simulate=True)
            
            #change the player to current
            self.active_player().active = False
            self.playerAtMoveIndex += 1
            if self.playerAtMoveIndex >= len(self.players):
                self.playerAtMoveIndex = 0
            self.active_player().active = True 

            # inverted to reflect deltas for current player.
            best_opponent_moves_with_deltas_inverted = {m:-d for m,d in best_opponent_moves_with_deltas.items()}
            
            # added moves with total delta.
            level_2_moves_with_delta = {(pos_level_1, m): delta + d for m,d in best_opponent_moves_with_deltas_inverted.items()}
            
            # add to the dict.
            all_level_2_moves_with_delta.update(level_2_moves_with_delta)
            
            # undo level 1 move
            if pos_level_1 in NOTATION_TO_DIRECTION:
                # move pawn
                success = self.active_player().undo_move_pawn()
            else:
                # if wall : remove wall
                success = self.active_player().undo_place_wall(pos_level_1)
                       
        #from the list of options, check what cause 
        best = min(all_level_2_moves_with_delta.values())
        suggestions = [move for move,dist in all_level_2_moves_with_delta.items() if dist == best]

        if simulate:
            return suggestions
        else:
            index = random.randint(0, len(suggestions)-1)
            self.play_turn(suggestions[index][0])
            return suggestions[index][0]
        
    def analyse_level(self):
        # return all possible moves and their delta.
        one_level_deep_with_distances = self.check_all_moves()
        current_distances = self.gameBoard.distances_to_winning_node()
        deltas = self.calculate_delta_improvement(current_distances, one_level_deep_with_distances, self.active_player().direction)
        return deltas
    
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
        
        # distances_output = "incremental per turn"
        distances_output = "absolute"
        
        if distances_output=="incremental per turn":
            
            # incremental once per complete turn (that's the two players each playing once)
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
        
    def board_as_string (self):
        return(str(self))
        
    def board_as_html (self):
        plain = str(self)
        html = "<p style=\"font-family:courier;\">" + plain.replace("\n","<br>").replace(" ", "&nbsp") + "</p>"
        return html
    
    def __str__(self):
        return "".join(self.screen_output_lines())
        
    def screen_output_lines(self):
        # side bar statistics and board combined.

        # side bar
        board_output_lines = self.gameBoard.output_lines()
        side_bar_stats_lines = []
        
        col_width  = len(self.players[0].name)
        if len(self.players[0].name) < len(self.players[1].name):
            col_width = len(self.players[1].name)
        if col_width < 5:
            col_width = 5
            
        first_col_width = 5
        
        if self.output_encoding == "utf-8":
            # draw statistics box (https://en.wikipedia.org/wiki/Box-drawing_character)
            side_bar_stats_lines.append(" {0:<{fw}} \u250C\u2500{1:\u2500<{w}}\u2500\u252C\u2500{2:\u2500<{w}}\u2510".format("", "","",w = col_width, fw = first_col_width))
            side_bar_stats_lines.append(" {0:<{fw}} \u2502 {1:<{w}} \u2502 {2:<{w}}\u2502".format(" ", self.players[0].name,self.players[1].name,w = col_width, fw = first_col_width))
            side_bar_stats_lines.append("\u250C{0:\u2500<{fw}}\u2500\u253C\u2500{1:\u2500<{w}}\u2500\u253c\u2500{2:\u2500<{w}}\u2524".format("", "","",w = col_width, fw = first_col_width))
            side_bar_stats_lines.append("\u2502{0:<{fw}} \u2502 {1:<{w}} \u2502 {2:<{w}}\u2502".format("Pawn", self.gameBoard.get_player_char(0), self.gameBoard.get_player_char(1),  w = col_width, fw = first_col_width))
            side_bar_stats_lines.append("\u2502{0:<{fw}} \u2502 {1:<{w}} \u2502 {2:<{w}}\u2502".format("Path", self.distance_history[-1][0], self.distance_history[-1][1], w = col_width, fw = first_col_width))
            side_bar_stats_lines.append("\u2502{0:<{fw}} \u2502 {1:<{w}} \u2502 {2:<{w}}\u2502".format("Walls", self.players[0].number_of_unplaced_walls(), self.players[1].number_of_unplaced_walls(), w = col_width, fw = first_col_width))
            side_bar_stats_lines.append("\u2514{0:\u2500<{fw}}\u2500\u2534\u2500{1:\u2500<{w}}\u2500\u2534\u2500{2:\u2500<{w}}\u2518".format("", "","",w = col_width, fw = first_col_width))
        else:
            # draw statistics box (https://en.wikipedia.org/wiki/Box-drawing_character)
            side_bar_stats_lines.append("{0:<{fw}}   {1:<{w}}   {2:<{w}}".format(" ", self.players[0].name,self.players[1].name,w = col_width, fw = first_col_width))
            side_bar_stats_lines.append("{0:<{fw}}   {1:<{w}}   {2:<{w}}".format("Pawn", self.gameBoard.get_player_char(0), self.gameBoard.get_player_char(1),  w = col_width, fw = first_col_width))
            side_bar_stats_lines.append("{0:<{fw}}   {1:<{w}}   {2:<{w}}".format("Path", self.distance_history[-1][0], self.distance_history[-1][1], w = col_width, fw = first_col_width))
            side_bar_stats_lines.append("{0:<{fw}}   {1:<{w}}   {2:<{w}}".format("Walls", self.players[0].number_of_unplaced_walls(), self.players[1].number_of_unplaced_walls(), w = col_width, fw = first_col_width))
        side_bar_width = len(max(side_bar_stats_lines, key=lambda x:len(x)))
        side_bar_whitespace = "{s:{padchar}<{w}}".format(s="", padchar=SIDE_BAR_EMPTY_SPACE, w=side_bar_width)

        # side bar top space
        for i in range(15):
            side_bar_stats_lines.insert(0, side_bar_whitespace)

        # side bar bottom space
        while len(side_bar_stats_lines) < len(board_output_lines)-2:
            side_bar_stats_lines.append(side_bar_whitespace)

        # make one line from the two columns
        combined_lines = [line_bar + " " + line_board + "\n" for line_bar, line_board in zip(side_bar_stats_lines, board_output_lines)]
        return combined_lines
            
    def undo_turn(self, as_independent_turn=True, steps=1):
        # undoing a turn. 
        # as_independent_turn  if False --> we assume that we are in the middle of a turn, stays the same player.
        
        for step in range(steps):
            if len(self.move_history) == 0:
                logging.info("nothing to undo")
                return False

            # check what the previous move was.
            self.distance_history.pop()
            move_to_undo = self.move_history.pop()
            
            if as_independent_turn:
                previous_player_index = self.get_previous_player_index()
                logging.info("undo previous move:{} by {}".format(move_to_undo, self.players[previous_player_index].name))
            else:
                previous_player_index = self.playerAtMoveIndex
                
            
            if move_to_undo in NOTATION_TO_DIRECTION:
                # move pawn
                logging.info("undo pawn move")
                success = self.players[previous_player_index].undo_move_pawn()

            else:
                # if wall : remove wall
                logging.info("undo wall move")
                success = self.players[previous_player_index].undo_place_wall(move_to_undo)

            if success:
                if as_independent_turn:
                    # activate previous player.
                    self.playerAtMoveIndex = previous_player_index
                else:
                    pass
            else:
                logging.error("undo unsuccessful")
                raise Exception("Big troubles at undoing.")
    
    def make_move(self, move):
        # move in standard notation.
       
        move_made = False
        
        if move in NOTATION_TO_DIRECTION:
            # move pawn
            move = move.upper()
            move_made = self.move_pawn(move)
            if not move_made:
                logging.info("moved made?:{}".format(move_made))

        elif wall.Wall._notation_to_lines_and_orientation(move) is not None:
            move_made = self.place_wall(move)
        else:
            status = "Move {} has a wrong notation or is not yet implemented".format(move)
            self.set_status(status)
            logging.info("INPUT VIOLATION: "+ status)
        return move_made

    def play_sequence(self, moves, animation_time_ms = None):
        for move in moves:
            success = self.play_turn(move)
            if not success:
                status = "Illegal move in sequence! Aborting auto play. Provided sequence:{}. Played moves: {}".format(
                    moves, self.move_history)
                logging.info(status)
                self.set_status(status)
                return False
            elif animation_time_ms is not None:
                time.sleep(animation_time_ms / 1000)
                board_string = self.board_as_string() 
                print(board_string)
        return True

    def play_turn(self, move):
        status = "Play turn ( {} playing move: {})".format(self.active_player().name, move)
        logging.info(status)
        
        move = move.lower()  # clean up first, the only problem move is E3 vs e3  (pawn move over line three vs wall placement).
        
        played = self.make_move(move)

        # add valid move to history
        if not played:
            status = "move not made"
            logging.info(status)
            self.set_status(status)
            return False
        else:
            self.move_history.append(move)

        # check validity of board
        distances_to_win = self.gameBoard.distances_to_winning_node()
        self.distance_history.append(distances_to_win)

        if None in distances_to_win:
            # board invalid(None indicates infinite distance to winning position for pawn), undo turn
            self.undo_turn(as_independent_turn=False)
            played = False
            status = "ERROR: move not executed. There always must be a path to at least one of the winning squares for all players."
            self.set_status(status)
            logging.info("RULE VIOLATION: no winning path for both players. (dist pl1,dist pl2)(None = no path): {}".format(distances_to_win))
            return False

        # check for winner
        game_finished = self.active_player().get_pawn_on_winning_position()
        if game_finished:
           self.game_state = GAME_STATE_FINISHED
        else:
            self.next_player()

        return played

    def get_previous_player_index(self):
        # returns the previous player index.
        previous = self.playerAtMoveIndex - 1
        if previous < 0:
            previous = len(self.players) - 1
        return previous

    def next_player(self):
        # deactivate current player
        self.active_player().active = False
                
        # activate next player
        self.playerAtMoveIndex += 1
        if self.playerAtMoveIndex >= len(self.players):
            self.playerAtMoveIndex = 0
        
        self.active_player().active = True
        status = "-----------Change player to {}".format(self.active_player().name)
        logging.info(status)

    def auto_pawn_move_suggestion(self):
        # list of all pawn directions with equal (minimum) distance to a winning square.
        all_directions = self.check_all_pawn_moves()

        minimum_dist = min(all_directions.values())

        return [direction for direction in all_directions.keys() if all_directions[direction] == minimum_dist]
    
    def check_all_moves(self):
        # all possible moves and their distances.
        
        # merge two dicts: https://stackoverflow.com/questions/38987/how-to-merge-two-dictionaries-in-a-single-expression
        return {**self.check_all_wall_placements(), **self.check_all_pawn_moves()}

    def get_shortest_paths(self):
        return self.gameBoard.paths_to_winning_node()  # all the nodes from both players shortest paths

    def get_all_node_crossings_from_shortest_paths(self):
        '''Will return a set of all the node corssings, back and forth that both players pawn will cross
        when going on the shortest path to a winning square
        returns None if there is a path not valid
        '''
        paths = self.get_shortest_paths()
        if None in paths:  # check for invalid path
            return None

        crossed_wall_lines = set()
        for path in paths:
            for index in range(len(path) - 1):
                crossed_wall_lines.add((path[index], path[index + 1]))
                crossed_wall_lines.add((path[index + 1], path[index]))
        return crossed_wall_lines
    '''
    def check_wall_affects_shortest_paths(self, wall_verbose):
        
        # check if in the current game, placing a wall would affect any pawn to make a longer path.
        # This is implemented to avoid calculating dijkstra for every wall placement when brute forcing all possible wall
        # positions for automatic players

        # returns None if no valid path found for a player.
        
        #1. get shortest paths dijkstra

        #2. get all node crossings from shortest paths
        node_crossings = self.get_all_node_crossings_from_shortest_paths()
        print(node_crossings)
        if node_crossings is None:
            return None

        #3. check if wall affects any path
        print(wall.Wall.position_verbose_to_nodes(wall_verbose))
        cuts, _ = wall.Wall.position_verbose_to_nodes(wall_verbose)
        cut1, cut2 = cuts
        print(cuts)
        if cut1 in node_crossings or cut2 in node_crossings:
            return True
        else:
            return False
    '''

    def check_all_wall_placements(self):

        # all valid possible wall positions with distances.
        wall_placements_effect = {}
        # get shortest paths for current situation. Only if a wall blocks this path, we have to calculate new distances.

        node_crossings = self.get_all_node_crossings_from_shortest_paths()
        if node_crossings is None:
            print ("ASSERT ERROR: should start from a valid board at the beginning of the wall placement checking.")
            raise

        for pos in board.NOTATION_VERBOSE_WALL_POSITIONS:
            success = self.place_wall(pos)
            if not success:
                continue

            # enormous optimization: will only recalculate path if the newly placed wall is somehow blocking the existing shortest path for both players.
            cuts, _ = wall.Wall.position_verbose_to_nodes(pos)
            cut1, cut2 = cuts
            recalculate_paths = cut1 in node_crossings or cut2 in node_crossings
            # recalculate_paths = True  # uncomment to UNDO optimization

            if recalculate_paths:  # will not trigger when False or None(None = a path is not valid)

                # 2 check shortest distance
                distances = self.gameBoard.distances_to_winning_node()
                # check if end node is reachable
                if None not in distances:
                    wall_placements_effect[pos] = distances
            # 1b undo move
            success = self.active_player().undo_place_wall(pos)
            if not success:
                logging.error("ASSERT ERROR undo wall during all wall placements for testing failed.")
                raise Exception

        return wall_placements_effect
        
    def check_all_pawn_moves(self):
        # return all possible pawn moves with their distance to end  as dictionary. 
    
        valid_directions = {}
        for dir in ALL_PAWN_DIRECTIONS:
            #1 simulate pawn move
            #1a do move
            success = self.move_pawn(dir)
            
            if success:
                #2 check shortest distance
                distances = self.gameBoard.distances_to_winning_node()
                
                # 1b undo move
                self.active_player().undo_move_pawn()
                
                #save
                valid_directions[dir] = distances
                
        return valid_directions
    
    def calculate_delta_improvement(self, reference_distances, distances_dict, player_direction, offset = 0):
        # takes in list with distances, and generates delta (difference in distance)  negative: player_to_check got a short
        
        # negative is "improved" situation for player to North 
        # offset is a previous distance that will be added to the result delta . i.e. searching two levels deep, previous level got an -3 delta --> will be added.
        
        # i.e.   ref: (8, 9)   ---> (5,7)    8-9 = -1 (advantage player north) , 5 - 7= -2 (two steps advantage player north)    -2 - (-1) = -1  (-1 overall delta improvement means advantage for player to north)
        # i.e.   ref: (7, 9)   ---> (8,7)    7-9 = -2 (2 advantage player north) , 8 - 7= 1 (one steps advantage player south)    1 - (-2) = 3  (3 overall delta improvement means advantage for player to south)
        
        # inverter swaps all around. this way, deltas can be normalized for the provided player.
        
        inverter = 1
        if player_direction == player.PLAYER_TO_SOUTH:
            inverter = -1
        
        d01, d02 = reference_distances
        deltas = {}
        delta0 = d01 - d02
        for pos, (d11, d12) in distances_dict.items():
            deltas[pos] = inverter * ( (d11 - d12) -  delta0 ) + offset
        
        return deltas
        
    def place_wall(self, position_verbose) :
        success = self.active_player().place_wall(position_verbose)
        return success

    def move_pawn(self, move_verbose):
    
        # check for pawn or wall move
        direction = NOTATION_TO_DIRECTION[move_verbose]

        # move pawn
        success = self.active_player().move_pawn(direction)
        if success:
            logging.info("pawn moved.")
        else:
            logging.info("pawn not moved.")
        return success
        
    def state_as_dict(self):
        pass

    def state_as_json(self):
        pass
        import json
    
        # r = {'is_claimed': 'True', 'rating': 3.5}
        # json = json.dumps(r) # note i gave it a different name
        # file.write(str(r['rating']))
        # def load_json():


def game_from_archive(gameString):
    pass

    
def game_to_archive(game, outputFile):
    pass


def game_from_json(json):
    pass

    
def game_to_json(game):
    pass

def drawProgressBar(percent, barLen = 20):
    # https://stackoverflow.com/questions/3002085/python-to-print-out-status-bar-and-percentage/15801617#15801617
    # percent float from 0 to 1. 
    sys.stdout.write("\r")
    progress = ""
    sys.stdout.write("[{:<{}}] {:.0f}%".format("=" * int(barLen * percent), barLen, percent * 100))
    sys.stdout.flush()
    

def logging_setup():
    # https://docs.python.org/3/howto/logging.html
    # logging.basicConfig(filename='c:/temp/quoridortest.log', level=logging.INFO)
    logging.basicConfig(filename='c:/temp/quoridortest.log', level=logging.INFO)
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
    # logging_setup()
    
    # preloaded game
    # q = Quoridor({"player_1":"Lode", "player_2":"Brecht", "remarks":"fictional demo game" , "date":"20180908", "game":"n s n s n s n s"})
    # q = Quoridor({"player_1":"Lode", "player_2":"Brecht"} )
    # q = Quoridor({"player_1":"Joos", "player_2":"Lode", "game":"n s n s n s n 6e 4d 4g e5 6c a6 b6 4b 5a 3a c3 1c 2b 1a 2d 1e 2f 1g 3h h1 sw"})
    # q = Quoridor{("player_1":"Joos", "player_2":"Lode", "game":"1c d2 3d e2 1f"})
    # q = Quoridor({"player_1":"Lode", "player_2":"Brecht", "game":"n s n s 7a"})
    
    # two computers game
    # q = Quoridor({"player_1": "auto_1", "player_2": "auto_2"})
    
    # computer against lode game
    # q = Quoridor({"player_1": "Lode", "player_2": "auto"})
    
    # fresh from scratch game
    # q = Quoridor()
   
    print(q.board_as_string())
    

    # q.game_loop()
    pass
   