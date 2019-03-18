import quoridor



    
class Quoridor_analyzer():
    def __init__(self):
        self.all_games = None
        self.current_analyzed_game = None  # contains a move string.
        self.current_analyzed_game_moves = None
        self.games_index = None

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
                
        self.all_games = games
        self.games_index = 0
        
        
    def command(self, command, allow_moves = False):
       
       # process input
        if command in ["load csv"]:
            # path = input("provide path")
            self.load_games_from_csv(PATH)
            self.set_current_game(self.games_index)
            
        elif command in [ "next game", "ng"]:
            self.games_index += 1
            if self.games_index >= len(self.all_games):
                print("Can't go forward. Reached last game.")
            self.set_current_game(self.games_index)
            
        
        elif command in [ "previous game", "pg"]:
            self.games_index -= 1
            if self.games_index < 0:
                print("Can't go back. Reached first game already")
                return
                
            self.set_current_game(self.games_index)
                
        elif command in [ "previous move", "p"]:
            
            if self.moves_index is None:
                self.moves_index = len(self.current_analyzed_game_moves) - 2
            
            elif self.moves_index > 0:
                self.moves_index -= 1
            
            else:    
                    print("error, not executed. (already af first move?)")
                    return
            print("self.moves index {}".format(self.moves_index))
            self.display_current_game(self.moves_index)
        
        elif command in [ "next move", "n"]:
            
            if self.moves_index is None:
                self.moves_index = 0
            
            elif self.moves_index < len(self.current_analyzed_game_moves)-2:
                self.moves_index += 1
            
            else:    
                    print("error, not executed. (already af first move?)")
                    return
                    
            self.display_current_game(self.moves_index)
                
        else: 
            print ("command not found:")

    def set_current_game(self, index):
        self.current_analyzed_game_moves = self.all_games[self.games_index]
        self.moves_index = None
        self.display_current_game()
        
    
    def display_current_game(self, specific_moves_index=None):
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
        
        
    def input_loop(self):
        while True:
            command = input("command:")
            self.command(command)
    

    
if __name__ == "__main__":

    PATH = r"C:\Temp\auto_2_auto_2.txt"
    
    qa = Quoridor_analyzer()
    qa.input_loop()