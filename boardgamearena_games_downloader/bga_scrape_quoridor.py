# import urllib.request
# import base64

# theurl = 'https://boardgamearena.com/playernotif'
# theurl = 'https://boardgamearena.com'

# req = urllib.request.Request(theurl)

# credentials = ('%s:%s' % (username, password))
# encoded_credentials = base64.b64encode(credentials.encode('ascii'))
# req.add_header('Authorization', 'Basic %s' % encoded_credentials.decode("ascii"))


# with urllib.request.urlopen(req) as response:
#     print(response.read())
# # with urllib.request.urlopen(req) as response, open(out_file_path, 'wb') as out_file:
# #     data = response.read()
# #     out_file.write(data)

import requests
import json
import time
import datetime
import traceback
import logging
from pathlib import Path

import bga_scraping_database_operations

DATA_BASE_PATH = r"C:\Data\Generated_program_data\boardgamearena_quoridor_scraper"
# https://github.com/tpq/bga/blob/master/py/bga.py

class BoardGameArenaScraper:
    
    # Initialize a Game object from the html "logs" of a BGA game
    def __init__(self, email=None, password=None, db_path=None, logger=None):
        
        self.logger = logger or logging.getLogger(__name__)
        self.logger.info("BoardGameArenaScraper Logging init.  ".format(
        ))
       
        
        if db_path is not None:
            self.db = bga_scraping_database_operations.BoardGameArenaDatabaseOperations(db_path,self.logger)
            self.logger.info('database set up: {}'.format(
                db_path,
                )) 

        if email is None or password is None:
            self.logger.info('Offline mode. Will not connect to boardgamearena.com'.format(
                )) 
            return 

        self.session = requests.session()

        # Login to Board Game Arena
        url_login = "http://en.boardgamearena.com/account/account/login.html"
        prm_login = {'email': email, 'password': password, 'rememberme': 'on',
                     'redirect': 'join', 'form_id': 'loginform'}

        r = self.session.post(url_login, params = prm_login)
        if r.status_code != 200:
            self.logger.error("Error trying to login!", exc_info=True)
    
    def close(self):
        self.session.close()

    def scrape_player_games_metadata_by_page(self, player_id, page):
        player_id = str(player_id)
        
        url_player_games = "https://boardgamearena.com/gamestats/gamestats/getGames.html?player={}&opponent_id=0&game_id=43&finished=1&page={}&updateStats=0&dojo.preventCache=1605921362257".format(
            player_id,
            page,
        )
        r = self.session.get(url_player_games)
        if r.status_code != 200:
            self.logger.error("Error trying to load the games per player page!", exc_info=True)

        return r.text

    def get_full_game_raw(self, table_id):
        
        table_id = str(table_id)
        
        # Define parameters to access to Board Game Arena
       
        url_game = "http://en.boardgamearena.com/gamereview?table=" + table_id
        url_log = "http://en.boardgamearena.com/archive/archive/logs.html"
        prm_log = {"table": table_id, "translated": "true"}
            
        # Generate the log files
        r = self.session.get(url_game)
        if r.status_code != 200:
             self.logger.error("Error trying to load the gamereview page!", exc_info=True)

        # (r.headers)
        # (r.request.headers)
        
        # Retrieve the log files
        r = self.session.get(url_log, params = prm_log)
        if r.status_code != 200:
            self.logger.error("Error trying to load the log file!", exc_info=True)
        raw_data = r.text
        
        with open(Path(DATA_BASE_PATH,r"games_by_table_id_raw/{}.txt".format(table_id)),"w") as f:
            f.write(raw_data)

        return raw_data
       
    def scrape_player_games_metadata(self, player_id):

        # IMPORTANT: the number of games downloaded is less than shown on the player's webpage. This is because abandoned games are not included in the downloaded data.
        # also: 4 player games are also existing. We will not study those, but the table_id is included, and we save the number of players. Just to make sure they are obvious.

        self.logger.info("-----scrape player {} -------".format(player_id))
        start_t = time.time()
        previous_t = start_t

        self.db.update_player_status(player_id, "BUSY_SCRAPING", True)
       
        ran_over_all_player_games = False
        page = 1

        while not ran_over_all_player_games:
            result_raw = self.scrape_player_games_metadata_by_page(player_id, page)
            
            result_parsed = self.parse_scraped_games_metadata(result_raw, player_id)
                
            for game in result_parsed:
                self.db.add_game_metadata(game["table_id"],game,False)

            if len(result_parsed) == 0:
                ran_over_all_player_games = True
                self.db.update_player_status(player_id, "UP_TO_DATE", True)
                self.logger.info(" {:.2f}s since start, {:.2f}s since previous, empty data return --> scraping FINISHED for this player)".format(
                    time.time() - start_t,
                    time.time() - previous_t,
                    ))

            else:
                self.db.commit()

                self.logger.info(" {:.2f}s since start, {:.2f}s since previous, downloaded page {})".format(
                    time.time() - start_t,
                    time.time() - previous_t,
                    page,
                    ))

                page += 1

            previous_t = time.time()

    def parse_scraped_games_metadata (self, raw, from_scraped_player_id):
        data_json = json.loads(raw)
        
        games = data_json["data"]["tables"]

        if len(games) == 0:
            # no data sent
            return []
        
        games_meta_data = []
        for game in games:
            game_meta_data = {}
            
            scores =  game["scores"].split(",")
            ranks =  game["ranks"].split(",")
            player_names =  game["player_names"].split(",")
            player_ids =  game["players"].split(",")

            game_meta_data["table_with_player_id"] = "{}_{}".format(
                game["table_id"],
                from_scraped_player_id,
                )
            game_meta_data["table_id"] = str(game["table_id"])
            game_meta_data["time_start"] = str(game["start"])
            game_meta_data["time_end"] = str(game["end"])
            game_meta_data["concede"] = str(game["concede"])
            game_meta_data["unranked"] = str(game["unranked"])
            game_meta_data["normalend"] = str(game["normalend"])
            game_meta_data["player_1_id"] = str(player_ids[0])
            game_meta_data["player_2_id"] = str(player_ids[1])
            game_meta_data["player_1_name"] = str(player_names[0])
            game_meta_data["player_2_name"] = str(player_names[1])
            game_meta_data["player_1_score"] = str(scores[0])
            game_meta_data["player_2_score"] = str(scores[1])
            game_meta_data["player_1_rank"] = str(ranks[0])
            game_meta_data["player_2_rank"] = str(ranks[0])
            game_meta_data["players_count"] = str(len(player_ids))
            game_meta_data["elo_after"] = str(game["elo_after"])
            game_meta_data["elo_win"] = str(game["elo_win"])
            game_meta_data["player_id_scraped_player"] = str(from_scraped_player_id)

            games_meta_data.append(game_meta_data)
        return games_meta_data

    def scrape_all_players_to_be_scraped_metadata(self):

        while True:
            status = "TO_BE_SCRAPED"

            scrapee_data = self.db.get_player_ids(status,1)
            
            if len(scrapee_data) == 0:
                self.logger.info("No more players to be scraped in table 'players' with status: {}".format(
                    status,
                    ))
                return 

            # get a player to be scraped
            scrapee_player_id = list(scrapee_data.keys())[0]  # player_id is key

            # scrape his games
            self.scrape_player_games_metadata(scrapee_player_id)

    # def repair_busy_status_to_todo(self):
    #     while True:
    #         player_ids = self.db.get_player_ids("BUSY_SCRAPING")

    #         if len(player_ids) == 0:
    #             return 
                
    #         for player_id in player_ids:
    #             self.db.update_player_status(player_id, "TO_BE_SCRAPED", False)
    #         self.db.commit()

    def scrape_all_players_and_keep_updating_players(self, start_empty=False):

        # on new database, no players yet, we have to kickstart it.
        if start_empty:
            # 84401637
            self.scrape_player_games_metadata(84401637)

        while True:
            # do all players
            self.scrape_all_players_to_be_scraped_metadata()
            
            # save all new players
            self.db.update_players_from_games()

            # check if there are players to be scraped
            if len(self.db.get_player_ids("TO_BE_SCRAPED",1)) == 0:
                self.logger.info("No players TO_BE_SCRAPED left")
                return
    
    def parse_scraped_gamedata(self, raw, table_id):

        game_moves_gba_notation = []
        reflexion_times = []
        absolute_timestamps = []
        reflexion_time_delta = None
        reflexion_time_max = None
        starting_player = None
        non_starting_player = None
        process_state = "PARSING"

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
                print(t_type)

            if at_first_move:
                reflexion_time_delta = int(t_data[2]["args"]['delta'])
                # reflexion_time_delta = t_data["data"][2]["args"]['delta']
                # print(reflexion_time_delta)
                reflexion_time_max = int(t_data[2]["args"]['max'])
                starting_player = int(t_data[1]["args"]['active_player'])
                non_starting_player = int(t_data[2]["args"]['player_id'])
                
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

                # print(reflexion)

                reflexion_times.append((reflexion[str(starting_player)],reflexion[str(non_starting_player)]))

            if process_notation:
                game_moves_gba_notation.append( t_data[0]["args"]["quoridorstrats_notation"])

        game_data_parsed = {
            "table_id":table_id,
            "process_state":process_state,
            "game_moves_gba_notation":game_moves_gba_notation,
            "reflexion_times":reflexion_times,
            "absolute_timestamps":absolute_timestamps,
            "reflexion_time_delta":reflexion_time_delta,
            "reflexion_time_max":reflexion_time_max,
            "starting_player":starting_player,
            "non_starting_player":non_starting_player
        }

        return game_data_parsed

    def get_gamedata_from_table(self, table_id, download_delay_seconds=30):
      
        cached = True

        try:
            # Cached? first, check if already existing offline (previously downloaded. )
            game_raw = self.get_offine_gamedata_raw(table_id)

            # download if not cached
            if game_raw is None:
                cached = False
                self.logger.info("Wait for a delay of {}s...".format(
                    download_delay_seconds,
                    ))
                time.sleep(download_delay_seconds)  # do first, in order to never ever have multiple downloads in quick succession.
                game_raw = self.get_full_game_raw(table_id)

            downloaded_raw_length = len(game_raw)
            parsed_game_data = self.parse_scraped_gamedata(game_raw, table_id)

        except Exception as e:
            logger.error("error during retrieving and parsing game data from table: {} ({})".format(
                table_id,
                e,
                ), exc_info=True)
            parsed_game_data = None

        
        self.logger.info("Scraped raw data from table {} Was Cached?:{}, Downloadsize:{})".format(
            table_id,
            cached,
            downloaded_raw_length,
            ))

        return parsed_game_data

    def get_gamedata_from_tables(self, table_ids, download_delay_seconds=30):

        start_t = time.time()  
        previous_t = start_t

        data_games = {}
        for i,table_id in enumerate(table_ids):

            data = self.get_gamedata_from_table(table_id, download_delay_seconds)
            data_games[table_id] = data

            self.logger.info("Retrieved data from table {} ({}/{}) process time: {:.2f} (total time: {:.2f} after a delay of {}s.))".format(
                table_id,
                i+1,
                len(table_ids),
                time.time() - previous_t,
                time.time() - start_t,
                download_delay_seconds,
                ))

            previous_t = time.time()

        return data_games

    def get_offine_gamedata_raw(self, table_id):
        # offline_bga = BoardGameArenaScraper()

        # table_id = 124984142
        path = Path(DATA_BASE_PATH, r"games_by_table_id_raw\{}.txt".format(
            table_id))

        if not path.exists():
            return None

        with open(path,"r") as f:
            game_raw = f.read()

        # parsed_game_data = self.parse_scraped_gamedata(game_raw, table_id)

        return game_raw

    def game_data_by_playerid(self, player_id, count=4, download_delay_seconds=30):
        table_ids = self.db.get_and_mark_game_ids_for_player(player_id, count)

        if len (table_ids) == 0:
            return []

        parsed_data_games = self.get_gamedata_from_tables(table_ids, download_delay_seconds)
        self.db.set_status_of_game_ids(table_ids,"DONE")
        return parsed_data_games

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

def get_account_info(index):
    # zero account is the actual account I use. So, take care with that one.
    accounts = [
        ("lode"+"ameije"+"@"+"gma" + "il.com", "sl"+  "8" + "af" + "val"),
        ("sun"+"setonalo"+"nelybea" + "ch"+"@"+"gma" + "il.com", "w8"+  "w" + "oo" + "rd"),
        ("sun"+"setonalo"+"nely.bea" + "ch"+"@"+"gma" + "il.com", "w8"+  "w" + "oo" + "rd"),
    ]
    return accounts[index]

def create_bga_instance(logger, account_index, database_name ):
    db_path = Path(DATA_BASE_PATH, database_name)
    id, pwd = get_account_info(account_index)
    bga = BoardGameArenaScraper(id, pwd, db_path= db_path , logger=logger)
    return bga

# --------------------------------------------------------------
# SCRAPER FUNCTIONALITY 
# --------------------------------------------------------------


def testing(bga):
    print(bga.db.get_player_id_from_name("superlode"))

def scrape_game_metadata(bga, start_empty=False, clean_up_busy_states=False):
    # Get games metadata. (there are 120 000 000 million games on bga, so we need to go by player to get the right games.)

    # clean_up_busy_states: if multiple instances running: make sure to set to false! This is only to clean up after you have let it run with many parallel processes. To repair parsings that were stopped halfway.
    if clean_up_busy_states:
        bga.db.repair_busy_status_to_todo()

    try:
        # init (log in )
        bga.scrape_all_players_and_keep_updating_players(start_empty)

    except Exception as e:
        logger.error("Error in main thread during scraping. {} ".format(e), exc_info=True)

    finally:
        bga.close()
    
def all_game_data_by_player(bga, player):
    # player can be player_id or player_name 

    # player can be given as int (for the id) or string (id as string or player_name)
    try:
        player_id = int(player)

    except Exception as e:
        player_id = bga.db.get_player_id_from_name(player)
        if player_id is None:
            logger.error("Could not get player id from name ({})".format(
                player,
                ))
            return False 

    continue_scraping = True
    all_parsed_games = []
    while continue_scraping:
        logger.info(player_id)
        parsed_games = bga.game_data_by_playerid(player_id, count=10, download_delay_seconds=30)
        if len(parsed_games) == 0:
            continue_scraping = False
        all_parsed_games.extend(parsed_games)
    return all_parsed_games

def get_gamedata(bga, table_ids,download_delay_seconds=30):
    parsed_data_games = bga.get_gamedata_from_tables(table_ids, download_delay_seconds)

    return parsed_data_games

if __name__ == "__main__":
    
    logger = logging_setup(logging.INFO, Path(DATA_BASE_PATH,  r"logs", "bga_scrape_quoridor.log"), "SESSION" )
    bga_instance = create_bga_instance(logger, 1, r"bga_quoridor_data.db")
    testing(bga_instance)

    # --- scrape meta data ----------------------------------------
    # get as much games data and players data as possible
    # scrape_game_metadata(bga_instance, False, True)
    
    # --- scrape actual games ----------------------------------------
    # table_id = 124984142
    # # table_id = 3156753
    # # table_id = 124984142
    # table_id = 126439858  # superlode 2020-11-23   times superlode; 1:42 , 1:46, 1:22 , 1:38, 0:23, 1:31
    # table_ids = [3156753, 124984142, 126439858]
    # table_ids = [3156753] # old
    # table_ids = [6584339] # old
    # table_ids = [10652513]
    # table_ids = [124984142, 126456011, 94224007,8925907,26381891, 31425340] 
    # table_ids = [   117864158] 
    table_ids = [130697191] 

    # game_data = get_gamedata(bga_instance, table_ids, 3)    
    # all_game_data_by_player(bga_instance, 84945751)
    # all_game_data_by_player(bga_instance, "superlode")

    # --- info ----------------------------------------


    # logger.info(game_data)
    
    # exit()

    # player_id_scraped_player = 84781397
    # offline_bga = BoardGameArenaScraper()
    # raw = '''{"status":1,"data":{"tables":[{"table_id":"67953988","game_name":"quoridor","game_id":"43","start":"1584979102","end":"1584979326","concede":"0","unranked":"0","normalend":"1","players":"85429074,84781397","player_names":"kimy711,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-10","elo_after":"1418","arena_win":null,"arena_after":"1.1500"},{"table_id":"67952662","game_name":"quoridor","game_id":"43","start":"1584978660","end":"1584979082","concede":"0","unranked":"0","normalend":"1","players":"85429074,84781397","player_names":"kimy711,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-11","elo_after":"1429","arena_win":null,"arena_after":"1.1500"},{"table_id":"67951262","game_name":"quoridor","game_id":"43","start":"1584978149","end":"1584978644","concede":"0","unranked":"0","normalend":"1","players":"85429074,84781397","player_names":"kimy711,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-12","elo_after":"1440","arena_win":null,"arena_after":"1.1500"},{"table_id":"67949743","game_name":"quoridor","game_id":"43","start":"1584977614","end":"1584978115","concede":"1","unranked":"0","normalend":"1","players":"84781397,85429074","player_names":"Mehrschad,kimy711","scores":"0,0","ranks":"1,2","elo_win":"30","elo_after":"1452","arena_win":null,"arena_after":"1.1500"},{"table_id":"67948267","game_name":"quoridor","game_id":"43","start":"1584977077","end":"1584977592","concede":"0","unranked":"0","normalend":"1","players":"85429074,84781397","player_names":"kimy711,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-11","elo_after":"1422","arena_win":null,"arena_after":"1.1500"},{"table_id":"67946990","game_name":"quoridor","game_id":"43","start":"1584976567","end":"1584977013","concede":"0","unranked":"0","normalend":"1","players":"85429074,84781397","player_names":"kimy711,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-11","elo_after":"1432","arena_win":null,"arena_after":"1.1500"},{"table_id":"67944981","game_name":"quoridor","game_id":"43","start":"1584975850","end":"1584976544","concede":"0","unranked":"0","normalend":"1","players":"85429074,84781397","player_names":"kimy711,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-19","elo_after":"1444","arena_win":null,"arena_after":"1.1500"},{"table_id":"67911877","game_name":"quoridor","game_id":"43","start":"1584961221","end":"1584961865","concede":"0","unranked":"0","normalend":"1","players":"83961560,84781397","player_names":"Syl20rrr,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-42","elo_after":"1463","arena_win":null,"arena_after":"1.1500"},{"table_id":"67910754","game_name":"quoridor","game_id":"43","start":"1584960759","end":"1584961181","concede":"0","unranked":"0","normalend":"1","players":"84781397,83961560","player_names":"Mehrschad,Syl20rrr","scores":"1,0","ranks":"1,2","elo_win":"20","elo_after":"1505","arena_win":null,"arena_after":"1.1500"},{"table_id":"67899669","game_name":"quoridor","game_id":"43","start":"1584953283","end":"1584953448","concede":"1","unranked":"0","normalend":"1","players":"84781397,85124665","player_names":"Mehrschad,elijo","scores":"0,0","ranks":"1,2","elo_win":"32","elo_after":"1468","arena_win":null,"arena_after":"1.1500"}],"stats":[]}}'''
    # print(offline_bga.parse_scraped_games_metadata(raw, player_id_scraped_player))

  