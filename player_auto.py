import player
   
class Player_auto(Player):   
    def __init__(level=None):
        # level = level of autoplayer. 0= random, 1 = 1 move deep, 2= 2 moves deep.
        self.depth = level
        
        
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
        
    def auto_level_2(self, simulate=False):
        # brute force two moves 
        # simulate: only return list of equal distance suggestions.
        
        deltas = self.analyse_level()
        
        # level 1
        all_level_2_moves_with_delta = {}
        all_moves_level_2 = {}  # for multiple levels: a move is a list of the next moves as key. value is the delta 
        opponent = self.inactive_player().direction
        
        # level 2
        for i, (pos_level_1, delta) in enumerate(deltas.items()): # run through all possible level 1 moves.
            drawProgressBar(i/len(deltas.items()))
            
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
    