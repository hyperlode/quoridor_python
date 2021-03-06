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
    
    def __init__(self, settings = None, output_encoding = None, logger=None):
        
        self.logger = logger or logging.getLogger(__name__)
        
        self.game_state = GAME_STATE_NOT_STARTED
        self.status_message = ""
        
        self.output_encoding = output_encoding
        
        self.logger.info("Init Quoridor game ")
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

        player1 = player.Player(player1_name, player.PLAYER_TO_NORTH, self.logger)
        player2 = player.Player(player2_name, player.PLAYER_TO_SOUTH, self.logger)
        
        self.players = [player1, player2]
        self.gameBoard = board.Board(self.output_encoding, self.logger)
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
        
        self.last_auto_moves = None  # for debugging
        

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
    
    def execute_command(self, move):
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
        
        elif move in [ "suggest_previous_move_level_1", "spml1"]:
            # used to check what on earth the computer was thinking.
            undone_move = self.move_history[-1]            
            self.undo_turn(as_independent_turn = True)
            suggestion = self.auto_level_1(True)
            self.play_turn(undone_move)
            return suggestion
        
        elif move in [ "suggest_previous_move_level_2", "spml2"]:
            # used to check what on earth the computer was thinking.
            undone_move = self.move_history[-1]
            
            self.undo_turn(as_independent_turn = True)
            suggestion = self.auto_level_2(True, verbose=False)
            self.play_turn(undone_move)
            return suggestion
            
        elif move in [ "suggest_previous_move_level_3", "spml3"]:
            # used to check what on earth the computer was thinking.
            undone_move = self.move_history[-1]
            
            self.undo_turn(as_independent_turn = True)
            suggestion = self.auto_level_3(True, verbose=False)
            self.play_turn(undone_move)
            return suggestion
        
        elif move in ["suggest_level_1", "sl1"]:
            return self.auto_level_1(True)
            
        elif move in ["suggest_level_2", "sl2"]:
            return self.auto_level_2(True, verbose=True)
            
        elif move in ["suggest_level_3", "sl3"]:
            return self.auto_level_3(True, verbose=False)
            
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
                self.logger.error("unvalid auto move directions. {}".format(auto_move_directions))
                
        elif move == "auto_mind_read":
            if self.last_auto_moves is not None:
                return self.last_auto_moves 
            else:
                return "no auto move history available"
                
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
                    "history       also for move history\n" +
                    "history_nice  extensive history analysis\n" +
                    "sl1           level 1 auto suggestions\n" +
                    "sl2           level 2 auto suggestions\n" +
                    "sl3           level 3 auto suggestions\n" +
                    "spml1         level 1 PREVIOUS MOVE auto suggestions\n" +
                    "spml2         level 2 PREVIOUS MOVE auto suggestions\n" +
                    "spml3         level 3 PREVIOUS MOVE auto suggestions\n" +
                    "automove      to auto move pawn on shortest path\n" +
                    "h or help     for this help\n" +
                    "wide          to toggle wider board\n" +
                    
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
        elif depth == 3:
            return self.auto_level_3(simulate)
        else:
            self.logger.error("auto_turn parameter not correct. ")
            
    def auto_level_1(self, simulate=False):
        # brute force one move 
        # simulate returns all (move,pathdelta) pairs with best delta (is most path shortening) for active player.
        
        deltas = self.analyse_level()
        best = min(deltas.values())
        
        self.last_auto_moves = deltas
        
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
        # print("tijteietj{}".format(deltas))
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
        suggestions = {move:dist for move,dist in all_level_2_moves_with_delta.items() if dist == best}
        self.last_auto_moves = suggestions
        
        if simulate:
            return suggestions
        else:
            suggestions = [move for move,dist in suggestions.items() if dist == best]
            index = random.randint(0, len(suggestions)-1)
            self.play_turn(suggestions[index][0])
            return suggestions[index][0]
    

    def auto_level_3(self, simulate=False, verbose=False, opponent_as_level_2_player=False):
        # check ALL level1 moves (not just the best level1 moves!!!)
        # brute force three moves 
        # simulate: only return list of equal distance suggestions.
        
        all_level_3_moves_with_delta = {}
        opponent = self.inactive_player().direction

        # level 1
        moves_level_1 = self.analyse_level()
        
        if verbose:
            print("level1 deltas: {}" .format(moves_level_1))

        # level 2
        for i, (pos_level_1, delta_level_1) in enumerate(moves_level_1.items()): # run through all possible level 1 moves.

            drawProgressBar(i/len(moves_level_1.items()))
            if verbose:
                print("level1move: {}".format(pos_level_1))
                
            # make level 1 move
            success = self.make_move(pos_level_1)
            if verbose:    
                # print(self.board_as_string())
                pass
                
            #change the player to opponent for analysis level 2 move
            self.active_player().active = False
            self.playerAtMoveIndex += 1
            if self.playerAtMoveIndex >= len(self.players):
                self.playerAtMoveIndex = 0
            self.active_player().active = True
            
            # obtain all level 2 moves
            #  select the moves the opponent player can make.
            
            if opponent_as_level_2_player:
                # check if the opponent thinks as level 2
                best_opponent_moves_with_deltas = self.auto_level_2(simulate=True)
                best_opponent_moves_with_deltas = {k[0]:v for k,v in best_opponent_moves_with_deltas.items()}
                # print(best_opponent_moves_with_deltas)  
                # raise
            else:
                # let the opponent play as level 1
                best_opponent_moves_with_deltas = self.auto_level_1(simulate=True)
            
            # inverted to reflect deltas for current player.
            best_opponent_moves_with_deltas_inverted = {m:-d for m,d in best_opponent_moves_with_deltas.items()}
            
            # added moves with total delta.
            level_2_moves_with_delta = {(pos_level_1, m): (delta_level_1, d) for m,d in best_opponent_moves_with_deltas_inverted.items()}
            # level_2_moves_with_delta = {(pos_level_1, m): delta + d for m,d in best_opponent_moves_with_deltas.items()}
            
            # level3 : run through all level2 moves
            for i, (pos_level_2, prev_move_deltas) in enumerate(level_2_moves_with_delta.items()): # run through all possible level 2 moves.
                delta_level_2 = sum(prev_move_deltas)
                level_2_move = pos_level_2[1]
                
                # do level 2 move
                success = self.make_move(level_2_move)
                if verbose:
                    # print(self.board_as_string())   
                    pass
                
                #change the player to self for level 3 analysis 
                self.active_player().active = False
                self.playerAtMoveIndex += 1
                if self.playerAtMoveIndex >= len(self.players):
                    self.playerAtMoveIndex = 0
                self.active_player().active = True

                # do level3 analysis.
                best_moves_at_level3_with_deltas = self.auto_level_1(simulate=True)
                
                if verbose:    
                    print(best_moves_at_level3_with_deltas)
                    
                    print("lev2 with delta:{}".format(level_2_moves_with_delta))
                # input("feifjeijfijijijijijii")
                #do level3 move
                
                #analyse level3 and add to moves
                
                # added moves with total delta.
                level_3_moves_with_delta = {(pos_level_1, level_2_move, m): {"delta_1":prev_move_deltas[0], "delta_2":prev_move_deltas[1], "delta_3":d, "total_delta": prev_move_deltas[0] + prev_move_deltas[1] + d} for m,d in best_moves_at_level3_with_deltas.items()}
                
                # add to the dict.
                all_level_3_moves_with_delta.update(level_3_moves_with_delta)

                
                #change the player back to opponent to undo level 2 move. 
                self.active_player().active = False
                self.playerAtMoveIndex += 1
                if self.playerAtMoveIndex >= len(self.players):
                    self.playerAtMoveIndex = 0
                self.active_player().active = True

                # undo level2 move (done for analysing level3)
                if level_2_move in NOTATION_TO_DIRECTION:
                    # move pawn
                    success = self.active_player().undo_move_pawn()
                else:
                    # if wall : remove wall
                    success = self.active_player().undo_place_wall(level_2_move)
                                        

            #change the player to level 1 to undo the level 1 move.
            self.active_player().active = False
            self.playerAtMoveIndex += 1
            if self.playerAtMoveIndex >= len(self.players):
                self.playerAtMoveIndex = 0
            self.active_player().active = True
                
            # undo level 1 move (done when analysing level2)
            if pos_level_1 in NOTATION_TO_DIRECTION:
                # move pawn
                success = self.active_player().undo_move_pawn()
            else:
                # if wall : remove wall
                success = self.active_player().undo_place_wall(pos_level_1)
                
        #from the list of options, choose the ones with best overal delta path length.
        all_deltas = all_level_3_moves_with_delta.values()
        best = None
        best = min([d["total_delta"] for d in all_deltas])
        print("best move delta: {}".format(best))
        suggestions = {move:deltas for move,deltas in all_level_3_moves_with_delta.items() if deltas["total_delta"] == best}
        
        
        
        # from options, chose between move 1 and 3 (the one with the biggest immediate impact delta wise).
        suggestions_direct_impact = {}
        for moves, deltas_moves in suggestions.items():
            a,b,c = moves
            # check impact of level_3 move IF played at level_1 (first move). --> only check if possible. i.e. there might be no South going available at that time.
            if c in moves_level_1:
                # print("---------========================================")
                # print(moves)
                # print(deltas_moves)
                # print(moves_level_1)
                delta_pretend_level_1_move = moves_level_1[c]
                # print(delta_pretend_level_1_move)
            
                if deltas_moves["delta_1"] > delta_pretend_level_1_move or ( (deltas_moves["delta_1"] == delta_pretend_level_1_move) and c in ALL_PAWN_DIRECTIONS) :
                    moves = (c,b,a)
                    deltas_moves = {"delta_1":deltas_moves["delta_3"], "delta_2":deltas_moves["delta_2"], "delta_3": deltas_moves["delta_1"], "total_delta": deltas_moves["total_delta"] }
                    print("swapped!: {}".format(moves))
            suggestions_direct_impact[moves] = deltas_moves
            
        # print(suggestions_direct_impact)
        # print(suggestions)
        
        suggestions = suggestions_direct_impact
        
        # from wall suggenstions, choose the ones that are not set between itself and "goal" row
        # ONLY DO AFTER BIGGEST DELTA PATH processing. (this is a filter for when chosing between equal length deltas)
        x,y = self.active_player().get_position() # i.e. starts from 1 (from bottom).
        suggestions_filter_out_walls_ahead = []
        for moves in suggestions:
            #filter wall moves.
            wall_notation = wall.Wall._notation_to_lines_and_orientation(moves[0], self.logger)
            
            print(moves)
            print(wall_notation)
            if wall_notation is not None:
                hori,vert,isHori = wall_notation  # i.e. 4c = 4,3,1
                
                if self.active_player().direction == player.PLAYER_TO_NORTH:
                    #wall behind = 
                    if hori - 1 < x:
                        # this means wall more south of player (which is "good" because it is "behind" player)
                        suggestions_filter_out_walls_ahead.append(moves)
                    else:
                        print("didn't survive wall ahead filter: {}".format(moves))
                else:
                    if hori > x:
                        suggestions_filter_out_walls_ahead.append(moves)
                    else:
                        print("didn't survive wall ahead filter: {}".format(moves))
            else:
                # if move is not a wall, it survives the filter.
                suggestions_filter_out_walls_ahead.append(moves)
                # print(wall_notation)
                
                # print(self.inactive_player().get_position()) # i.e. starts from 1 (from bottom).   (x, y)  most South west square is 0,0
        if len(suggestions_filter_out_walls_ahead) > 0:
            suggestions = {moves:suggestions[moves] for moves in suggestions_filter_out_walls_ahead}    
        else:
            print("there were no filter survivers, filter not applied")
                
            

        # from options, chose the one where the first one is a pawn move. In order to save walls (and because of silly wall placements).
        suggestions_pawn_move = []
        for moves in suggestions: # takes items.
            if moves[0] in ALL_PAWN_DIRECTIONS:
                suggestions_pawn_move.append(moves)
        if len(suggestions_pawn_move) != 0:
            suggestions = {moves:suggestions[moves] for moves in suggestions_pawn_move}
            # suggestions = suggestions_pawn_move
            

        self.last_auto_moves = suggestions
        
        
        
        #final processing
        suggestion_moves = list(suggestions.keys())
        if simulate:
            if verbose:
                print(suggestion_moves)
            return suggestion_moves
        else:
            print(suggestion_moves)
            # input("pause for dramatic effect")
            index = random.randint(0, len(suggestion_moves)-1)
            # input("chosen_moves:{}".format(suggestion_moves[index]))
            self.play_turn(suggestion_moves[index][0])
            return suggestion_moves[index][0]
    
    def analyse_level(self):
        # return all possible moves and their delta.
        one_level_deep_with_distances = self.check_all_moves()
        # print("uhseiisjei one level eedpep: {}".format(one_level_deep_with_distances))
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
            self.logger.error("ASSERT ERROR: no distances column print option")
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
                self.logger.info("nothing to undo")
                return False

            # check what the previous move was.
            self.distance_history.pop()
            move_to_undo = self.move_history.pop()
            
            if as_independent_turn:
                previous_player_index = self.get_previous_player_index()
                self.logger.info("undo previous move:{} by {}".format(move_to_undo, self.players[previous_player_index].name))
            else:
                previous_player_index = self.playerAtMoveIndex
                
            
            if move_to_undo in NOTATION_TO_DIRECTION:
                # move pawn
                self.logger.info("undo pawn move")
                success = self.players[previous_player_index].undo_move_pawn()

            else:
                # if wall : remove wall
                self.logger.info("undo wall move")
                success = self.players[previous_player_index].undo_place_wall(move_to_undo)

            if success:
                if as_independent_turn:
                    # activate previous player.
                    self.playerAtMoveIndex = previous_player_index
                else:
                    pass
            else:
                self.logger.error("undo unsuccessful, move to undo: {}".format(
                    move_to_undo,
                    ))
                raise Exception("Big troubles at undoing.")
    
    def make_move(self, move):
        # move in standard notation.
       
        move_made = False
        
        if move in NOTATION_TO_DIRECTION:
            # move pawn
            move = move.upper()
            move_made = self.move_pawn(move)
            if not move_made:
                self.logger.info("moved made?:{}".format(move_made))

        elif wall.Wall._notation_to_lines_and_orientation(move, self.logger) is not None:
            move_made = self.place_wall(move)
        else:
            status = "Move {} has a wrong notation or is not yet implemented".format(move)
            self.set_status(status)
            self.logger.info("INPUT VIOLATION: "+ status)
        return move_made

    def play_sequence(self, moves, animation_time_ms = None):
        for move in moves:
            success = self.play_turn(move)
            if not success:
                status = "Illegal move in sequence! Aborting auto play. Provided sequence:{}. Played moves: {}".format(
                    moves, self.move_history)
                self.logger.info(status)
                self.set_status(status)
                return False
            elif animation_time_ms is not None:
                time.sleep(animation_time_ms / 1000)
                board_string = self.board_as_string() 
                print(board_string)
        return True

    def play_turn(self, move):
        status = "Play turn ( {} playing move: {})".format(self.active_player().name, move)
        self.logger.info(status)
        
        move = move.lower()  # clean up first, the only problem move is E3 vs e3  (pawn move over line three vs wall placement).
        
        played = self.make_move(move)

        # add valid move to history
        if not played:
            status = "move not made"
            self.logger.info(status)
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
            self.logger.info("RULE VIOLATION: no winning path for both players. (dist pl1,dist pl2)(None = no path): {}".format(distances_to_win))
            return False

        # check for winner
        game_finished = self.active_player().get_pawn_on_winning_position()
        if game_finished:
            self.logger.info("Game finished.")
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
        self.logger.info(status)

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

    def check_all_wall_placements(self, only_include_when_shortest_path_blocked=False):
        ''' all valid possible wall positions with distances.
        
        only_include_when_shortest_path_blocked : only when a path is blocked, move is included. can come in handy for automatic players.
        '''
        
        wall_placements_effect = {}

        
        distances_before_wall_placement = self.gameBoard.distances_to_winning_node()
        
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
            cuts, _ = wall.Wall.position_verbose_to_nodes(pos, self.logger)
            cut1, cut2 = cuts
            recalculate_paths = cut1 in node_crossings or cut2 in node_crossings
            # recalculate_paths = True  # uncomment to UNDO optimization

            if recalculate_paths:  # will not trigger when False or None(None = a path is not valid)

                # 2 check shortest distance
                distances = self.gameBoard.distances_to_winning_node()
                # check if end node is reachable
                if None not in distances:
                    wall_placements_effect[pos] = distances
            elif not only_include_when_shortest_path_blocked:
                wall_placements_effect[pos] = distances_before_wall_placement
            else:
                #wall placement not added as a move.
                pass
                
            # 1b undo move
            success = self.active_player().undo_place_wall(pos)
            if not success:
                self.logger.error("ASSERT ERROR undo wall during all wall placements for testing failed.")
                raise Exception

        return wall_placements_effect
        
    def check_all_pawn_moves(self):
        # return all possible pawn moves with their distance to end  as dictionary. 
    
        valid_directions = {}
        for dir in ALL_PAWN_DIRECTIONS:
            #1 simulate pawn move
            #1a do move
            # print("test move directions:{}".format(dir))
            success = self.move_pawn(dir, fail_silent=True)
            
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

    def move_pawn(self, move_verbose, fail_silent=False):
    
        # check for pawn or wall move
        direction = NOTATION_TO_DIRECTION[move_verbose]

        # move pawn
        success = self.active_player().move_pawn(direction,fail_silent=fail_silent)
        if success:
            self.logger.info("pawn moved.")
        else:
            self.logger.info("pawn not moved.")
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
   