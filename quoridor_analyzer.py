import quoridor


class QuoridorAnalyzer():

    def __init__(self):
    
        
        self.current_analyzed_game = None  # contains a move string.
        self.current_analyzed_game_moves = None
        self.games_index = None
        pass
    
    
    def set_current_game(self, moves):
        self.current_game = QuoridorGameAnalyzer(moves)
        self.current_game.display()
    
    def set_games(self, path):
        self.games = QuoridorGamesAnalyzer()
        self.games.load_games_from_csv(PATH)
        self.set_current_game ( self.games.load_next_game())
        # self.games.get_moves_from_game(self.games_index)
        
        
    def command(self, command, allow_moves = False):
       
       # process input
        if command in ["load csv", "l"]:
            self.set_games(PATH)
        elif command in [ "next game", "ng"]:
            self.set_current_game( self.games.load_next_game())
                    
        elif command in [ "previous game", "pg"]:
            self.set_current_game( self.games.load_previous_game())
            
        elif command in [ "previous move", "p"]:
            
            self.current_game.previous_move()
        
        elif command in [ "winner", "w"]:
            print(self.current_game.get_winner())
            
        elif command in [ "overal_winner", "o"]:
            print(self.games.get_overall_winner())
            
        elif command in [ "next move", "n"]:
            self.current_game.next_move()
        else: 
            print ("command not found. available commands: next move, n, previous move p, next game, ng, previous game, pg, load csv")

    def input_loop(self):
        while True:
            command = input("command:")
            self.command(command)
    
        
class QuoridorGameAnalyzer():

    def __init__(self, moves):
        self.current_analyzed_game_moves = moves
        self.moves_index = None
        
        moves_as_string = " ".join(moves)        
        self.current_analyzed_game = quoridor.Quoridor({"player_1":"A", "player_2":"B", "game":moves_as_string})
        
    def previous_move(self):
        if self.moves_index is None:
            self.moves_index = len(self.current_analyzed_game_moves) - 2
        
        elif self.moves_index > 0:
            self.moves_index -= 1
        
        else:    
            print("error, not executed. (already af first move?)")
            return

        print("self.moves index {}".format(self.moves_index))
        self.display(self.moves_index)
        
    def next_move(self):
        if self.moves_index is None:
            self.moves_index = 0
        
        elif self.moves_index < len(self.current_analyzed_game_moves)-2:
            self.moves_index += 1
        
        else:    
                print("error, not executed. (already af first move?)")
                return
                
        self.display(self.moves_index)
            
    
    def get_winner(self):
        # print(len(self.current_analyzed_game_moves))
        # print(self.current_analyzed_game.get_shortest_paths())
        if len(self.current_analyzed_game_moves) % 2 == 0: # true = player 2 is winner, else player 1
            return 1
        else:
            return 0
            
    def display(self, specific_moves_index=None):
        '''If specific_moves = None: load all moves
        '''
        if specific_moves_index is None:
            moves  = self.current_analyzed_game_moves
        else:
        
            moves = self.current_analyzed_game_moves[:specific_moves_index]
        
        moves_as_string = " ".join(moves)
        self.current_analyzed_game = quoridor.Quoridor({"player_1":"A", "player_2":"B", "game":moves_as_string})
        print(self.current_analyzed_game.board_as_string())
        print(self.current_analyzed_game.execute_command("history_nice"))
        


class QuoridorGamesAnalyzer():
    def __init__(self):
        self.games = None
        pass
        
    def load_games_from_csv(self, csv_path):
        #expects file with games, saved as a list of verbose moves.
        games = []
        with open(csv_path, "r") as f:
            for line in f:
                # game_string = f.readline()
                game = eval(line)
                # game = " ".join(game)
                games.append(game)
                # print(game)
        self.games = games      
        
        self.games_index = None
    
    def load_next_game(self):
        if self.games_index is None:
            self.games_index = 1
        else:
            self.games_index += 1
        if self.games_index >= len(self.games):
            print("Can't go forward. Reached last game.")
        
        return self.get_moves_from_game(self.games_index)
    
    def load_previous_game(self):
        if self.games_index is None:
            self.games_index = len(self.games)-1
        elif self.games_index < 0:
            self.games_index = len(self.games)-1
            print("Last game loaded. ")
        else:
            self.games_index -= 1
            
        return self.get_moves_from_game(self.games_index)
        
    def get_moves_from_game(self, index):
        return self.games[self.games_index]
    
    
    def get_overall_winner(self):
        winning_games = [0,0] # player1 at index 0, player 2 at index 1
        for game in self.games:
            qa = QuoridorGameAnalyzer(game)
            winning_games[qa.get_winner()] += 1
        return winning_games
    
if __name__ == "__main__":

    PATH = r"C:\Temp\auto_2_auto_3.txt"
    GAME = ['n', 's', 'n', '8d', 'n', '8f', '3d', '8b', '3f', '8h', 'n', 's', 'w', 's', 'w', 's', 'n', 's', '5a', 'a6', '5c', '7b', 'd6', '6c', 'd4', 'n', 'w', 'e', 'g4', 'e', '5f', 'w', 'e6', 'w', 'n', 'n', 'e', 'n', 'e', 'n', 'n', 'e', 'w', 'e', 'w', '7h', 'w', 's', 'n']

    qa = QuoridorAnalyzer()
    qa.set_current_game(GAME)
    qa.input_loop()