import quoridor

class Quoridor_local_game():
    
    def __init__(self):
        q = quoridor.Quoridor({"player_1": "auto", "player_2": "auto"})
        # q = Quoridor({"player_1": "auto", "player_2": "auto"})

        # q = Quoridor({"player_1": "auto", "player_2": "auto"})
        # q = Quoridor()
        q.game_loop()   
    
  


if __name__ == "__main__":
    l = Quoridor_local_game()
    