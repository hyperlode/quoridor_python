import quoridor
import logging


positions_to_notations = {(0,-2):"SS",
(0,-1):"S",
(0,1):"N",
(0,2):"NN",
(-2,0):"WW",
(-1,0):"W",
(1,0):"E",
(2,0):"EE",
(1,-1):"SE",
(-1,-1):"SW",
(1,1):"NE",
(-1,1):"NW",
}



def bga_moves_to_relative(previous_bga_position, current_bga_position):

    # get horizontal movement
    horizontal_movement = ord(current_bga_position[0]) - ord(previous_bga_position[0])
    if horizontal_movement not in [-2,-1,0,1,2]:
        logger.error("illegal move. {} to {}".format(
            previous_bga_position,
            current_bga_position,
        ))
    
    # get horizontal movement
    vertical_movement = int(current_bga_position[1]) - int(previous_bga_position[1])
    if vertical_movement not in [-2,-1,0,1,2]:
        logger.error("illegal move. {} to {}".format(
            previous_bga_position,
            current_bga_position,
        ))
    
    return positions_to_notations[(horizontal_movement, vertical_movement)]
    
def isolate_player_moves(moves, player_1_else_player_2):
    if player_1_else_player_2:
        moves_player_isolated = [m for i,m in enumerate(bga) if i%2==0 ]
    else:
        moves_player_isolated = [m for i,m in enumerate(bga) if i%2!=0 ]

    only_moves = filter_out_walls(moves_player_isolated)

    if player_1_else_player_2:
        start_position = 'e1'
    else:
        start_position = 'e9'

    return [start_position] + only_moves

def filter_out_walls(moves):
    return [m for m in moves if ("h" not in m and "v" not in m)]

def print_moves_nicely(moves_as_array):
    # make length even: 
    if len(moves_as_array)%2==1:
        moves_as_array.append(" ")
    
    pretty_str = "\tpl1\tpl2\t\n"
    for i, round_tuple in enumerate(zip(moves_as_array[::2], moves_as_array[1::2])):
        
        pretty_str += "{}\t{}\t{}\t\n".format(
            i+1,
            round_tuple[0],
            round_tuple[1],
        )
    return pretty_str

def test():


    print(bga_moves_to_relative("e1", "e2"))
    print(bga_moves_to_relative("e2", "e1"))
    print(bga_moves_to_relative("e2", "d2"))
    print(bga_moves_to_relative("d2", "e2"))
    
    print(bga_moves_to_relative("e1", "e3"))
    print(bga_moves_to_relative("e3", "e1"))
    print(bga_moves_to_relative("e2", "c2"))
    print(bga_moves_to_relative("d2", "f2"))

    print(bga_moves_to_relative("e1", "d2"))
    print(bga_moves_to_relative("e1", "f2"))
    print(bga_moves_to_relative("e2", "d1"))
    print(bga_moves_to_relative("e2", "f1"))

def convert_game_bga_to_lode(game_bga, return_as_string_else_array=False):
    # example of boardgamearena game: "e2 e8 e3 e7 e4 e6 e3h f6h c6h a6h d3v e4h g4v h6h d1v f5h g6v d5h f4 c4v c2h g3h"
    print(type(game_bga))
    if type(game_bga) is str:
        bga_str = game_bga
        bga_str = bga_str.strip()  # remove leading and trailing whitespace
        bga = bga_str.split(" ")

    elif type(game_bga) is list:
        bga = game_bga
    
    # keep track of both players turn

    player_1_previous_position_bga = "e1" # start position
    player_2_previous_position_bga = "e9" # start position
    player_1_playing_else_player_2 = True
    
    moves_converted = []
    for m in bga:
        logger.info("convert move: {}".format(
            m,
            ))

        if m[-1] == "v":
            m_converted = m[0:2]

        elif m[-1]=="h":
            # wall placement
            m_converted = m[-2:-4:-1]  # will swap letters
        
        elif player_1_playing_else_player_2:
            m_converted = bga_moves_to_relative(player_1_previous_position_bga, m)
            player_1_previous_position_bga = m

        elif not player_1_playing_else_player_2:
            m_converted = bga_moves_to_relative(player_2_previous_position_bga, m)
            player_2_previous_position_bga = m

        else:
            logger.error("illegal state")
        player_1_playing_else_player_2 = not player_1_playing_else_player_2
        moves_converted.append(m_converted)
    
    if return_as_string_else_array:
        return " ".join(moves_converted)
    else:
        return moves_converted

if __name__ == "__main__":
    # create logger
    logger = logging.getLogger(__name__)  # 
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
   
    logger.propagate = 0  # prevents every displaying thing twice on console 




    bga_table_124984142_str = "e2 e8 e3 e7 e4 e6 e3h f6h c6h a6h d3v e4h g4v h6h d1v f5h g6v d5h f4 c4v c2h g3h"
    bga_table_125651498_str = "e2 d2v c2h e2h f2 e8 g2 g2h f1v e7 h2 h4h f4v e6 i2 e5 e3h e6 i3 f6h h6v f6 g5h h8h g6v e6 i4 e7 h4 h3v g4 d7 g5 f8h d6h d8h h5 c7 i5 c6 i6 b6 i7 b5 a3h c5 c4h b5 i8 b4 h8 c4 g8 c3 f8 b3 e8 a1h d8 b2 c8 c2 c9"
    
    bga_table_26381891 = ['e2', 'e8', 'e3', 'e7', 'd6h', 'f7', 'f6h', 'h6v', 'g7v', 'e8v', 'd3', 'e6v', 'h4h', 'f4v', 'g3h', 'f5h', 'h2h', 'f2v', 'g1h', 'f8', 'c3', 'g8', 'g8h', 'f8', 'c4', 'f9', 'c5', 'g9', 'c6', 'b6h', 'b6', 'a6v', 'b5', 'a7h']
    bga_table_31425340 = ['e2', 'e8', 'e3', 'd3h', 'c3v', 'e7', 'c1v', 'f7h', 'd7v', 'h7h', 'b7h', 'e6', 'f3', 'f3h', 'g3', 'g2v', 'f1v', 'd8h', 'g2', 'c6h', 'g1', 'e7v', 'b4h', 'a5h', 'e5v', 'e5', 'h1', 'e4', 'h2', 'f4', 'h3', 'g4', 'h4', 'i4', 'h3h', 'g4', 'f4', 'e4', 'd4', 'e5', 'd5v', 'e4', 'd5', 'd4', 'd6', 'd5', 'c6', 'c5', 'b6', 'b5', 'c7v', 'a5', 'a6', 'a4', 'a7', 'a3', 'a8', 'a8h', 'b8', 'a2', 'c8', 'a1'] # highest quality by games_count
    # bga_table_31425340 = ['e2', 'e8', 'e3', 'd3h', 'c3v', 'e7', 'c1v', 'f7h', 'd7v', 'h7h', 'b7h', 'e6', 'f3', 'f3h', 'g3', 'g2v', 'f1v', 'd8h', 'g2', 'c6h', 'g1', 'e7v', 'b4h', 'a5h', 'e5v', 'e5', 'h1', 'e4', 'h2']
    
    bga_table_130697191 = ['e2', 'e8', 'f2', 'e7', 'e6h', 'e7h', 'f3', 'c7h', 'g3', 'f6v', 'g4', 'f5h', 'g5', 'h5h', 'f5', 'e4v', 'f4', 'b6v', 'f3', 'd7', 'c5h', 'd6', 'd4h', 'b4v', 'e3', 'b2v', 'd3', 'e6', 'd2', 'e5', 'c2', 'd5', 'c1', 'c5', 'b1', 'c4', 'c3h', 'd4', 'd2v', 'e2v', 'b2', 'e4', 'b3', 'e3', 'b4', 'e2', 'b5', 'e1']
    game_to_convert = bga_table_124984142_str
    logger.info(game_to_convert)
    
    data_return_as_string_else_array= False
    moves_converted = convert_game_bga_to_lode(game_to_convert, data_return_as_string_else_array)

    csv_string = ",".join(moves_converted)
    
    logger.info(csv_string  )
    logger.info(moves_converted)

    print( print_moves_nicely(moves_converted))


    # test()




