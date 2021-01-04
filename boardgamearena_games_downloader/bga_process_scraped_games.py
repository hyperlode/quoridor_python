

import logging
import datetime
import json
from pathlib import Path

import bga_scraping_database_operations
import boardgamearena_convert_notation 

DATABASE_PATH = r"C:\Data\Generated_program_data\boardgamearena_quoridor_scraper"
DATABASE_NAME = r"bga_quoridor_data.db"
RAW_GAME_DATA_FOLDER = r"games_by_table_id_raw"

def get_downloaded_raw_game_data_table_ids(logger):
    path = Path(DATABASE_PATH, RAW_GAME_DATA_FOLDER)

    files = Path(path).glob('*.*')

    table_ids = [int(f.stem) for f in files]
    return table_ids

def get_offine_gamedata_raw( table_id):
    path = Path(DATABASE_PATH, RAW_GAME_DATA_FOLDER, r"{}.txt".format(
        table_id))

    if not path.exists():
        return None

    with open(path,"r") as f:
        game_raw = f.read()
    return game_raw
    
class ProcessScrapedGames():

    def __init__(self, db_path=None, logger=None):
        
        self.logger = logger or logging.getLogger(__name__)
        self.logger.info("Board game arena scraping project. Process parsed data. Logging init.".format(
        ))
       
        if db_path is not None:
            self.db = bga_scraping_database_operations.BoardGameArenaDatabaseOperations(db_path,self.logger)
            self.logger.info('database set up: {}'.format(
                db_path,
                )) 

    def get_game_ids_for_player_confrontations(self, player_1, player_2):
        player_1_id = self.db.normalize_player_to_player_id(player_1)
        player_2_id = self.db.normalize_player_to_player_id(player_2)
        self.logger.info(self.db.get_game_ids_for_player_confrontations(player_1_id, player_2_id))
    
    def finalize_games(self, table_ids):
        for table_id in table_ids:
            self.finalize_game(table_id)

    def finalize_game(self, table_id):

        # get raw data (if available)
        raw_data = get_offine_gamedata_raw(table_id)

        # parse raw
        parsed_game_data = self.parse_scraped_gamedata(raw_data,table_id)

        # get other game data

        # def add_games_data_from_meta_data(self, table_id):
        # get metadata from table_id
        game_metadata = self.db.get_game_metadata(table_id)

        game_data = parsed_game_data
        game_data.update(game_metadata)

        # put to database
        self.db.add_game(game_data)

    def parse_scraped_gamedata(self, raw, table_id):

        game_moves_bga_notation = []
        reflexion_times = []
        absolute_timestamps = []
        reflexion_time_delta = None
        reflexion_time_max = None
        starting_player = None
        non_starting_player = None
        process_state = "COMPLETE"

        first_move_done = False
        at_first_move = False
        process_notation = False

        data_json = json.loads(raw)

        if "code" in list(data_json):
                
            if data_json["code"] == 100:
                self.logger.error("Error parsing raw data. --> run into limit? {}".format(data_json) )
                raise
                # "code": 100,
                # "error": "You have reached a limit (replay)",
                # "expected": 1,
                # "status": "0"
        try:
            turns_data = data_json["data"]["data"]["data"]

        except Exception as e:
            self.logger.warning(json.dumps(data_json, indent=4, sort_keys=True))
            exit()
        
        for i,t in enumerate(turns_data):
            
            # t_type =t["data"]["type"]            
            t_data = t["data"]
            t_type =t_data[0]["type"]

            if "time" not in list(t):
                # parsed = json.loads(t)
                self.logger.warning(json.dumps(t, indent=4, sort_keys=True))
                timestamp = None
            else:
                timestamp = int(t["time"])
            
            process_move = False
            process_notation = False

            if t_type == "playWall":
                process_move = True
                process_notation = True

                if not first_move_done:
                    at_first_move = True
                
            elif t_type == "playToken":
                process_move = True
                process_notation = True

                if not first_move_done:
                    at_first_move = True

            elif t_type == "playerConcedeGame":
                process_move = True
                # conceding_player = t_data[0]["args"]["player_name"]

                if not first_move_done:
                    at_first_move = True
            
            elif t_type == "gameStateChange":
                pass
            elif t_type == "updateMoves":
                pass
            else:
                self.logger.warning("Unknown type: t_type = {}".format(
                    t_type,
                    ))

            if at_first_move:

                try:
                    # example: table:131487175
                    reflexion_time_delta = int(t_data[2]["args"]['delta'])
                    reflexion_time_max = int(t_data[2]["args"]['max'])
                    starting_player = int(t_data[1]["args"]['active_player'])
                    non_starting_player = int(t_data[2]["args"]['player_id'])
                except Exception as e:
                    # example: table:23864679
                    non_starting_player = int(t_data[3]["args"]['player_id'])
                    starting_player = int(t_data[2]["args"]['active_player'])
                    reflexion_time_delta = int(t_data[3]["args"]['delta'])
                    reflexion_time_max = int(t_data[3]["args"]['max'])

                at_first_move = False
                first_move_done = True

            if process_move:
                absolute_timestamps.append(timestamp)
                try:
                    reflexion = t_data[1]["args"]["reflexion"]["total"]

                except Exception as e:
                    try:
                        reflexion = t_data[2]["args"]["reflexion"]["total"]

                    except Exception as ee:
                        self.logger.error("Parsing move {}: reflexion times not found. ({})({}) ".format(
                            i,
                            e,
                            ee,
                            ),exc_info=True)
                        self.logger.error(json.dumps(t_data, indent=4, sort_keys=True))

                reflexion_times.append((reflexion[str(starting_player)],reflexion[str(non_starting_player)]))

            if process_notation:
                game_moves_bga_notation.append( t_data[0]["args"]["quoridorstrats_notation"])
                
        game_moves_lode_notation = boardgamearena_convert_notation.convert_game_bga_to_lode(game_moves_bga_notation, False, self.logger)

        game_data_parsed = {
            "table_id":table_id,
            "process_state":process_state,
            "moves_bga_notation":str(game_moves_bga_notation),
            "moves_lode_notation": str(game_moves_lode_notation),
            "thinking_times":str(reflexion_times),
            "absolute_timestamps":str(absolute_timestamps),
            "reflexion_time_delta":reflexion_time_delta,
            "reflexion_time_max":reflexion_time_max,
            "starting_player":starting_player,
            "non_starting_player":non_starting_player
        }

        return game_data_parsed



    def fill_in_games_data(self):
        # get games

        # timestamp

        # restriction = "WHERE games_played=100"
        restriction = ""

        # get games data
        sql = "SELECT table_id, time_start, time_end FROM {} {}".format(
            self.games_table_name,
            restriction,
        )
        self.logger.info(sql)
        rows = self.db.execute_sql_return_rows(sql)

        games_data = defaultdict(dict)
        
        # process data
        for table_id, timestamp_start, timestamp_end in rows:
           
            games_data[table_id]["time_start_ISO"] = datetime.datetime.fromtimestamp(timestamp_start).strftime("%Y.%m.%d-%H.%M.%S")
            games_data[table_id]["time_end_ISO"] = datetime.datetime.fromtimestamp(timestamp_end).strftime("%Y.%m.%d-%H.%M.%S")

        self.db.add_column_to_existing_table("games","time_start_ISO", "TEXT", "null")
        self.db.add_column_to_existing_table("games","time_end_ISO", "TEXT", "null")
        
        # write every games's stats
        number_of_games = len(list(games_data))
        for i, (table_id, data) in enumerate(games_data.items()):
            # add to table
            sql = "UPDATE '{}' SET time_start_ISO='{}', time_end_ISO='{}' WHERE table_id = {}".format(
            self.games_table_name,
            data["time_start_ISO"],
            data["time_end_ISO"],
            table_id,
            )

            self.db.execute_sql(sql)
            if i%1000 == 0:
                self.logger.info("{} ({}/{})".format(
                    table_id,
                    i+1,
                    number_of_games,
                    ))
        self.commit()     

    def fill_in_games_data_from_player(self):

        # get player stats
        # get all games 
        # applying player stats
        # get games data
        
        # restriction = "WHERE games_played=100"
        restriction = ""
        # get player data
        sql = "SELECT player_id, games_played, avg_elo_games_count_mult, high_elo_games_count_mult FROM {} {}".format(
            self.players_table_name,
            restriction,
        )
        player_rows = self.db.execute_sql_return_rows(sql)

        players_strength_data = {id:(count,avg,high) for id,count,avg,high in player_rows}

        # self.logger.info(players_strength_data[9668513])
        
        # get games data
        sql = "SELECT table_id, player_1_id, player_2_id FROM {} {}".format(
            self.games_table_name,
            restriction,
        )
        rows = self.db.execute_sql_return_rows(sql)

        games_data = defaultdict(dict)

         # process data
        for table_id, player_1, player_2 in rows:
            try:
                count1,avg1, high1 = players_strength_data[int(player_1)]
                count2,avg2, high2 = players_strength_data[int(player_2)]
            except Exception as e:
                # self.logger.warning("error: most probably, one of the players is not known in the database. {}".format(e), exc_info=True)
                continue

            avg_total = avg1*avg2
            high_total = high1*high2
            count_total = count1*count2

            games_data[table_id] = (count_total, avg_total, high_total)
        
        self.db.add_column_to_existing_table("games","game_quality_count", "INT", "null")
        self.db.add_column_to_existing_table("games","game_quality_eloavg", "INT", "null")
        self.db.add_column_to_existing_table("games","game_quality_elohigh", "INT", "null")
        
        # self.db.add_column_to_existing_table("games","game_quality_gamesplayed", "TEXT", "null")

        # write every player's stats
        number_of_games = len(list(games_data))
        self.logger.info("number of games to be checked: {}".format(number_of_games))
        for i, (table_id,  (count_total, avg_total, high_total)) in enumerate(games_data.items()):
            # add to table
            sql = "UPDATE '{}' SET game_quality_count={}, game_quality_eloavg={}, game_quality_elohigh={} WHERE table_id = {}".format(
            self.games_table_name,
            count_total,
            avg_total,
            high_total,
            # data["game_quality_count"],
            # data["game_quality_eloavg"],
            # data["game_quality_elohigh"],
            table_id,
            )

            self.db.execute_sql(sql)
            if i%1000 == 0:
                self.logger.info("{} ({}/{})".format(
                    table_id,
                    i+1,
                    number_of_games,
                    ))
        self.commit()     
   

def logging_setup(level = logging.INFO, log_path = None, new_log_file_creation="", flask_logger=None):
    '''    
        if using flask, provide flask_logger as ; app.logger

        new_log_file_creation : 
        "SESSION" --> every time program restarted, new file
        "MIDNIGHT" --> new file every day
        "" or "NEVER" --> single file
        log_path: full filename (as pathlib.Path)
    '''    
    message_format =  logging.Formatter('%(threadName)s\t%(levelname)s\t%(asctime)s\t:\t%(message)s\t(%(module)s/%(funcName)s/%(lineno)d)')
   
    if flask_logger is None:
        logger = logging.getLogger(__name__)  # will resort to name  __main__
    else:
        # flask has its own logger (app.logger)
        logger = flask_logger
    
    logger.setLevel(level=level)  # necessary magic line....
    logger.propagate = 0
    
    if log_path is not None:
        # log to file
        # check/create log filepath
        log_path = Path(log_path)
        log_path.mkdir(parents=True, exist_ok=True) 

        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        filename = "{}_{}{}".format(log_path.stem,  timestamp_str, log_path.suffix)
        log_path_with_starttime = Path(log_path.parent, filename)

        if new_log_file_creation == "" or new_log_file_creation == "NEVER":
            f_handler = logging.FileHandler(log_path)
            f_handler.setLevel(level=level)
            f_handler.setFormatter(message_format)

        elif new_log_file_creation == "MIDNIGHT":
             # do start a new log file for each startup of program. too.
            f_handler = logging.handlers.TimedRotatingFileHandler(
                log_path_with_starttime, when="midnight",
                interval=1,
                backupCount=100,
                )  # will first create the log_path name for the actual logging, and then, when time is there, copy this file to a name with the correct time stamp. 
            f_handler.setLevel(level=level)
            f_handler.setFormatter(message_format)
            f_handler.suffix = "_%Y-%m-%d_%H.%M.%S.txt"

        elif new_log_file_creation == "SESSION":
            # new file at every startup of program.
            f_handler = logging.FileHandler(log_path_with_starttime)
            f_handler.setLevel(level=level)
            f_handler.setFormatter(message_format)
    
        else:
            logger.info("error: uncorrect log file creation identifier:{}".format(new_log_file_creation))
            
        logger.addHandler(f_handler)

    # log to console (this needs to put last. If set before logging to file, everything is outputted twice to console.)
    c_handler = logging.StreamHandler()
    c_handler.setLevel(level=level)
    c_handler.setFormatter(message_format)
       
    logger.addHandler(c_handler)

    return logger
if __name__ == "__main__":
    logger = logging_setup(logging.INFO, Path(DATABASE_PATH,  r"logs", "bga_process_scraped_games.log"), "SESSION" )

    # add to table games (best to delete the table before executing this)
    scrapedGamesAnalyser = ProcessScrapedGames(Path(DATABASE_PATH,DATABASE_NAME), logger)
    
    
    # table_ids = get_downloaded_raw_game_data_table_ids(logger)  # from offline downloaded data
    # scrapedGamesAnalyser.finalize_games(table_ids)  # parse and add to database
    
    # scrapedGamesAnalyser.get_game_ids_for_player_confrontations("tdhr", "FreshPrinceEric")
    # scrapedGamesAnalyser.get_game_ids_for_player_confrontations("slimeB", "FreshPrinceEric")
    scrapedGamesAnalyser.get_game_ids_for_player_confrontations("Godalec", "FreshPrinceEric")

