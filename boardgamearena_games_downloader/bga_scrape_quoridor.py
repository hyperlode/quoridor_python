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
import random
from pathlib import Path

import bga_scraping_database_operations

DATABASE_PATH = r"C:\Data\Generated_program_data\boardgamearena_quoridor_scraper"
RAW_GAME_DATA_FOLDER = r"games_by_table_id_raw"
# https://github.com/tpq/bga/blob/master/py/bga.py

class BoardGameArenaScraper:
    
    # Initialize a Game object from the html "logs" of a BGA game
    def __init__(self, email=None, password=None, db_path=None, logger=None):
        
        self.logger = logger or logging.getLogger(__name__)
        self.logger.info("BoardGameArenaScraper Logging init.".format(
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
        else:
            self.logger.info("will login as {}".format(
                email,
                ))

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
        
        return raw_data

    # --------------------------------------------------------------------------------
    # --- GAME META DATA -------------------------------------------------------------------
    # --------------------------------------------------------------------------------

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

    def scrape_all_players_and_keep_updating_players(self, start_empty=False):
        # there is no way to know all quoridor playing players.
        # So we have to download games, and find out the players that played it.
        # Every found player becomes a scrapee.

        # in new database, no players yet, we have to kickstart it.
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
    
    # --------------------------------------------------------------------------------
    # ---GAME DATA -------------------------------------------------------------------
    # --------------------------------------------------------------------------------

    def scrape_game_data_from_table(self, table_id, download_delay_seconds=30):
      
        cached = True

        try:

            available_offline = False
            # Cached? first, check if already existing offline (previously downloaded. )
            game_raw = self.get_offine_gamedata_raw(table_id)

            # download if not cached
            if game_raw is not None:
                available_offline = True


            if not available_offline:
                cached = False
                total_delay_seconds = download_delay_seconds + random.randint(0,4)
                self.logger.info("Wait for a delay of {}s...".format(
                    total_delay_seconds,
                    ))
                time.sleep(total_delay_seconds)  # do first, in order to never ever have multiple downloads in quick succession.
                game_raw = self.get_full_game_raw(table_id)

            downloaded_raw_length = len(game_raw)

            data_json = json.loads(game_raw)

            if "code" in list(data_json):
                    
                if data_json["code"] == 100:
                    self.logger.warning("Failed Download. Code 100 received. {}".format(data_json) )
                    
                    if data_json["expected"] == 1:
                        # limit reached
                        # {'status': '0', 'error': 'You have reached a limit (replay)', 'expected': 1, 'code': 100}
                        pass
                    elif data_json["expected"] == 0:
                        # archived table
                        # {'status': '0', 'error': 'Cannot find gamenotifs log file of an archived table', 'expected': 0, 'code': 100}
                        pass

                    # "code": 100,
                    # "error": "You have reached a limit (replay)",
                    # "expected": 1,
                    # "status": "0"
                
                else:
                    self.logger.info("Return packet code: {}".format(
                        data_json["code"],
                        ))
            else:
                if not available_offline:
                    with open(Path(DATABASE_PATH, RAW_GAME_DATA_FOLDER, r"{}.txt".format(table_id)),"w") as f:
                        f.write(game_raw)

        except Exception as e:
            logger.error("error during retrieving and parsing game data from table: {} ({})".format(
                table_id,
                e,
                ), exc_info=True)
        
        self.logger.info("Scraped raw data from table {} Was Cached?:{}, Downloadsize:{})".format(
            table_id,
            cached,
            downloaded_raw_length,
            ))

        # return parsed_game_data

    def scrape_game_data_from_tables(self, table_ids, download_delay_seconds=30):

        start_t = time.time()  
        previous_t = start_t

        for i,table_id in enumerate(table_ids):

            self.scrape_game_data_from_table(table_id, download_delay_seconds)

            self.logger.info("Table {} game scraped. ({}/{}) process time: {:.2f} (total time: {:.2f} ))".format(
                table_id,
                i+1,
                len(table_ids),
                time.time() - previous_t,
                time.time() - start_t,
                ))

            previous_t = time.time()

    def get_offine_gamedata_raw(self, table_id):
        path = Path(DATABASE_PATH, RAW_GAME_DATA_FOLDER, r"{}.txt".format(
            table_id))

        if not path.exists():
            return None

        with open(path,"r") as f:
            game_raw = f.read()
        return game_raw

    def game_data_by_playerid(self, player_id, count=4, download_delay_seconds=30):
        table_ids = self.db.get_and_mark_game_ids_for_player(player_id, count)

        if len (table_ids) == 0:
            return []

        self.scrape_game_data_from_tables(table_ids, download_delay_seconds)
        # parsed_data_games = self.scrape_game_data_from_tables(table_ids, download_delay_seconds)
        self.db.set_status_of_game_ids(table_ids,"DONE")
        # return parsed_data_games

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
        ("offline_mode", None),
        ("lode"+"ameije"+"@"+"gma" + "il.com", "sl"+  "8" + "af" + "val"),
        ("sun"+"setonalo"+"nelybea" + "ch"+"@"+"gma" + "il.com", "w8"+  "w" + "oo" + "rd"),
        ("sun"+"setonalo"+"nely.bea" + "ch"+"@"+"gma" + "il.com", "w8"+  "w" + "oo" + "rd"),
    ]
    return accounts[index]

def create_bga_instance(logger, account_index, database_name ):
    db_path = Path(DATABASE_PATH, database_name)
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

    player_id = self.db.normalize_player_to_player_id(player)

    continue_scraping = True
    all_parsed_games = []
    while continue_scraping:
        logger.info(player_id)
        parsed_games = bga.game_data_by_playerid(player_id, count=10, download_delay_seconds=30)
        if len(parsed_games) == 0:
            continue_scraping = False
        all_parsed_games.extend(parsed_games)
    return all_parsed_games

def scrape_game_data(bga, table_ids,download_delay_seconds=30):
    bga.scrape_game_data_from_tables(table_ids, download_delay_seconds)

if __name__ == "__main__":
    
    logger = logging_setup(logging.INFO, Path(DATABASE_PATH,  r"logs", "bga_scrape_quoridor.log"), "SESSION" )
    bga_instance = create_bga_instance(logger, 3, r"bga_quoridor_data.db")
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
    # table_ids = [130697191] 
    FreshPrinceEric_vs_tdhr = [132281453, 131090390, 130750291, 129683879, 125846414, 125845691, 125253474, 125253713, 125252052, 125241359, 125244248, 125240696, 125054355, 125054614, 125051082, 125052651, 125042679, 125041468, 125044076, 125046015, 125048863, 125045003, 125031629, 124977598, 124971037, 124972675, 124977844, 124975263, 124978162, 124971391, 124964829, 118134184, 117872711, 117864158, 106868598, 103539190, 57349388, 57349049, 57348463, 132281453, 131090390, 130750291, 129683879, 125846414, 125845691, 125253474, 125253713, 125252052, 125241359, 125244248, 125240696, 125054355, 125054614, 125051082, 125052651, 125042679, 125041468, 125044076, 125046015, 125048863, 125045003, 125031629, 124977598, 124971037, 124972675, 124977844, 124975263, 124978162, 124971391, 124964829, 118134184, 117872711, 117864158, 106868598, 103539190, 57349388, 57349049, 57348463]
    FreshPrinceEric_vs_slimeB = [131487175, 131483434, 131489182, 131057193, 126298542, 125440437, 125443565, 125442372, 116411253, 116410081, 114039124, 103907195, 101502232, 131487175, 131483434, 131489182, 131057193, 126298542, 125440437, 125443565, 125442372, 116411253, 116410081, 114039124, 103907195, 101502232]
    drejt_vs_FreshPrinceEric = [123756731, 120420129, 120424617, 120420584, 120211209, 123756731, 120420129, 120424617, 120420584, 120211209]
    Godalec_vs_FreshPrinceEric = [132205382, 131931995, 131746775, 130763337, 130760506, 130768015, 130764024, 130763421, 130519088, 130515887, 130516537, 130517706, 130516954, 129103235, 129101054, 129100323, 129100832, 127671700, 127664959, 127665319, 127667968, 127663548, 127668397, 127669927, 127663186, 127661416, 127664275, 127669105, 127664064, 127664573, 127663333, 127666352, 127665202, 127667551, 127668490, 127662550, 127004521, 127005900, 126997109, 126990038, 126784619, 126780377, 126782066, 126782015, 126786414, 126788403, 126010725, 126015193, 126011441, 125957083, 125953733, 125951682, 125952222, 125957571, 125957911, 125958910, 125788562, 125781690, 125778465, 125777614, 125777371, 124924544, 124925183, 123131687, 121746607, 121741406, 118212102, 118218361, 118215890, 117159246, 117151575, 116739851, 116733490, 
        116738230, 116727379, 116728319, 106848359, 132205382, 131931995, 131746775, 130763337, 130760506, 130768015, 130764024, 130763421, 130519088, 130515887, 130516537, 130517706, 130516954, 129103235, 129101054, 129100323, 129100832, 127671700, 127664959, 127665319, 127667968, 127663548, 127668397, 127669927, 127663186, 127661416, 127664275, 127669105, 127664064, 127664573, 127663333, 127666352, 127665202, 127667551, 127668490, 127662550, 127004521, 127005900, 126997109, 126990038, 126784619, 126780377, 126782066, 126782015, 126786414, 126788403, 126010725, 126015193, 126011441, 125957083, 125953733, 125951682, 125952222, 125957571, 125957911, 125958910, 125788562, 125781690, 125778465, 125777614, 125777371, 124924544, 124925183, 123131687, 121746607, 121741406, 118212102, 118218361, 118215890, 117159246, 117151575, 116739851, 116733490, 116738230, 116727379, 116728319, 106848359]
    table_ids = Godalec_vs_FreshPrinceEric


    logger.info(len(table_ids))
    # exit()
    scrape_game_data(bga_instance, table_ids, 3)    
    # all_game_data_by_player(bga_instance, 84945751)
    # all_game_data_by_player(bga_instance, "superlode")

    # --- info ----------------------------------------


    # logger.info(game_data)
    
    # exit()

    # player_id_scraped_player = 84781397
    # offline_bga = BoardGameArenaScraper()
    # raw = '''{"status":1,"data":{"tables":[{"table_id":"67953988","game_name":"quoridor","game_id":"43","start":"1584979102","end":"1584979326","concede":"0","unranked":"0","normalend":"1","players":"85429074,84781397","player_names":"kimy711,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-10","elo_after":"1418","arena_win":null,"arena_after":"1.1500"},{"table_id":"67952662","game_name":"quoridor","game_id":"43","start":"1584978660","end":"1584979082","concede":"0","unranked":"0","normalend":"1","players":"85429074,84781397","player_names":"kimy711,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-11","elo_after":"1429","arena_win":null,"arena_after":"1.1500"},{"table_id":"67951262","game_name":"quoridor","game_id":"43","start":"1584978149","end":"1584978644","concede":"0","unranked":"0","normalend":"1","players":"85429074,84781397","player_names":"kimy711,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-12","elo_after":"1440","arena_win":null,"arena_after":"1.1500"},{"table_id":"67949743","game_name":"quoridor","game_id":"43","start":"1584977614","end":"1584978115","concede":"1","unranked":"0","normalend":"1","players":"84781397,85429074","player_names":"Mehrschad,kimy711","scores":"0,0","ranks":"1,2","elo_win":"30","elo_after":"1452","arena_win":null,"arena_after":"1.1500"},{"table_id":"67948267","game_name":"quoridor","game_id":"43","start":"1584977077","end":"1584977592","concede":"0","unranked":"0","normalend":"1","players":"85429074,84781397","player_names":"kimy711,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-11","elo_after":"1422","arena_win":null,"arena_after":"1.1500"},{"table_id":"67946990","game_name":"quoridor","game_id":"43","start":"1584976567","end":"1584977013","concede":"0","unranked":"0","normalend":"1","players":"85429074,84781397","player_names":"kimy711,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-11","elo_after":"1432","arena_win":null,"arena_after":"1.1500"},{"table_id":"67944981","game_name":"quoridor","game_id":"43","start":"1584975850","end":"1584976544","concede":"0","unranked":"0","normalend":"1","players":"85429074,84781397","player_names":"kimy711,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-19","elo_after":"1444","arena_win":null,"arena_after":"1.1500"},{"table_id":"67911877","game_name":"quoridor","game_id":"43","start":"1584961221","end":"1584961865","concede":"0","unranked":"0","normalend":"1","players":"83961560,84781397","player_names":"Syl20rrr,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-42","elo_after":"1463","arena_win":null,"arena_after":"1.1500"},{"table_id":"67910754","game_name":"quoridor","game_id":"43","start":"1584960759","end":"1584961181","concede":"0","unranked":"0","normalend":"1","players":"84781397,83961560","player_names":"Mehrschad,Syl20rrr","scores":"1,0","ranks":"1,2","elo_win":"20","elo_after":"1505","arena_win":null,"arena_after":"1.1500"},{"table_id":"67899669","game_name":"quoridor","game_id":"43","start":"1584953283","end":"1584953448","concede":"1","unranked":"0","normalend":"1","players":"84781397,85124665","player_names":"Mehrschad,elijo","scores":"0,0","ranks":"1,2","elo_win":"32","elo_after":"1468","arena_win":null,"arena_after":"1.1500"}],"stats":[]}}'''
    # print(offline_bga.parse_scraped_games_metadata(raw, player_id_scraped_player))

  