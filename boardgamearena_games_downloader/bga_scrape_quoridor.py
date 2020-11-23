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
import bga_scraping_database_operations
import traceback
import logging
from pathlib import Path

# https://github.com/tpq/bga/blob/master/py/bga.py

class BoardGameArenaScraper:
    
    # Initialize a Game object from the html "logs" of a BGA game
    def __init__(self, email=None, password=None, db_path=None, logger=None):

        self.logger = logger or logging.getLogger(__name__)
        self.logger.info("BoardGameArenaScraper Logging init.  ".format(
        ))
        
        if db_path is not None:
            self.db = bga_scraping_database_operations.BoardGameArenaDatabaseOperations(db_path,logger)
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

    def get_full_game(self, tableID):
        
        tableID = str(tableID)
        
        # Define parameters to access to Board Game Arena
       
       
        url_game = "http://en.boardgamearena.com/gamereview?table=" + tableID
        url_log = "http://en.boardgamearena.com/archive/archive/logs.html"
        prm_log = {"table": tableID, "translated": "true"}
            
        # Generate the log files
        r = self.session.get(url_game)
        if r.status_code != 200:
             self.logger.error("Error trying to load the gamereview page!", exc_info=True)
        
        # Retrieve the log files
        r = self.session.get(url_log, params = prm_log)
        if r.status_code != 200:
            self.logger.error("Error trying to load the log file!", exc_info=True)
        log = r.text

        return log     
       
    def scrape_player_games_metadata(self, player_id):

        # IMPORTANT: the number of games downloaded is less than shown on the player's webpage. This is because abandoned games are not included in the downloaded data.
        # also: 4 player games are also existing. We will not study those, but the table_id is included, and we save the number of players. Just to make sure they are obvious.

        self.logger.info("-----scrape player {} -------".format(player_id))
        start_t = time.time()
        previous_t = start_t

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
            scrapee_data = self.db.get_players_by_status("TO_BE_SCRAPED",1)

            if len(scrapee_data) == 0:
                self.logger.info("No more players to be scraped in table 'players'")
                return 

            # get a player to be scraped
            scrapee_player_id = list(scrapee_data.keys())[0]

            # scrape his games
            self.scrape_player_games_metadata(scrapee_player_id)

    def scrape_all_players_and_keep_updating_players(self):
        while True:
            # do all players
            self.scrape_all_players_to_be_scraped_metadata()
            
            # save all new players
            self.db.update_players_from_games()

            # check if there are players to be scraped
            if len(self.db.get_players_by_status("TO_BE_SCRAPED",1)) == 0:
                self.logger.info("All up to date.")
                return

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
        logger = logging.getLogger(__name__)
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

        log_path = Path(log_path, "sSense_communicator_log.txt")

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
    
    logger = logging_setup(logging.INFO, Path(r"C:\Data\Generated_program_data\boardgamearena_quoridor_scraper\logs"), "SESSION" )

    # player_id_scraped_player = 84781397
    # offline_bga = BoardGameArenaScraper()
    # raw = '''{"status":1,"data":{"tables":[{"table_id":"67953988","game_name":"quoridor","game_id":"43","start":"1584979102","end":"1584979326","concede":"0","unranked":"0","normalend":"1","players":"85429074,84781397","player_names":"kimy711,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-10","elo_after":"1418","arena_win":null,"arena_after":"1.1500"},{"table_id":"67952662","game_name":"quoridor","game_id":"43","start":"1584978660","end":"1584979082","concede":"0","unranked":"0","normalend":"1","players":"85429074,84781397","player_names":"kimy711,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-11","elo_after":"1429","arena_win":null,"arena_after":"1.1500"},{"table_id":"67951262","game_name":"quoridor","game_id":"43","start":"1584978149","end":"1584978644","concede":"0","unranked":"0","normalend":"1","players":"85429074,84781397","player_names":"kimy711,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-12","elo_after":"1440","arena_win":null,"arena_after":"1.1500"},{"table_id":"67949743","game_name":"quoridor","game_id":"43","start":"1584977614","end":"1584978115","concede":"1","unranked":"0","normalend":"1","players":"84781397,85429074","player_names":"Mehrschad,kimy711","scores":"0,0","ranks":"1,2","elo_win":"30","elo_after":"1452","arena_win":null,"arena_after":"1.1500"},{"table_id":"67948267","game_name":"quoridor","game_id":"43","start":"1584977077","end":"1584977592","concede":"0","unranked":"0","normalend":"1","players":"85429074,84781397","player_names":"kimy711,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-11","elo_after":"1422","arena_win":null,"arena_after":"1.1500"},{"table_id":"67946990","game_name":"quoridor","game_id":"43","start":"1584976567","end":"1584977013","concede":"0","unranked":"0","normalend":"1","players":"85429074,84781397","player_names":"kimy711,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-11","elo_after":"1432","arena_win":null,"arena_after":"1.1500"},{"table_id":"67944981","game_name":"quoridor","game_id":"43","start":"1584975850","end":"1584976544","concede":"0","unranked":"0","normalend":"1","players":"85429074,84781397","player_names":"kimy711,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-19","elo_after":"1444","arena_win":null,"arena_after":"1.1500"},{"table_id":"67911877","game_name":"quoridor","game_id":"43","start":"1584961221","end":"1584961865","concede":"0","unranked":"0","normalend":"1","players":"83961560,84781397","player_names":"Syl20rrr,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-42","elo_after":"1463","arena_win":null,"arena_after":"1.1500"},{"table_id":"67910754","game_name":"quoridor","game_id":"43","start":"1584960759","end":"1584961181","concede":"0","unranked":"0","normalend":"1","players":"84781397,83961560","player_names":"Mehrschad,Syl20rrr","scores":"1,0","ranks":"1,2","elo_win":"20","elo_after":"1505","arena_win":null,"arena_after":"1.1500"},{"table_id":"67899669","game_name":"quoridor","game_id":"43","start":"1584953283","end":"1584953448","concede":"1","unranked":"0","normalend":"1","players":"84781397,85124665","player_names":"Mehrschad,elijo","scores":"0,0","ranks":"1,2","elo_win":"32","elo_after":"1468","arena_win":null,"arena_after":"1.1500"}],"stats":[]}}'''
    # print(offline_bga.parse_scraped_games_metadata(raw, player_id_scraped_player))
    # exit()
    try:
        # init (log in )
        bga = BoardGameArenaScraper("sun"+"setonalo"+"nelybea" + "ch"+"@"+"gma" + "il.com", "w8"+  "w" + "oo" + "rd", r"C:\Data\Generated_program_data\boardgamearena_quoridor_scraper\bga_quoridor_data.db")
        bga.scrape_all_players_and_keep_updating_players()

    except Exception as e:
        logger.error("Error in main thread during scraping. {} ".format(e), exc_info=True)
    
    finally:
        bga.close()