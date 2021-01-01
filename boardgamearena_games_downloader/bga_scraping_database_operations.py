

import random
import time
import datetime
import logging
from pathlib import Path
from collections import defaultdict

import sqlite3_operations

'''
https://www.sqlitetutorial.net/sqlite-python/creating-database/

SQLiteDatabaseBrowserPortable.exe to browse.
'''

PLAYER_STATUSES = ["TEST", "UP_TO_DATE", "TO_BE_SCRAPED", "TEST2", "BUSY_SCRAPING"] 

GAME_SCRAPE_STATUSES = ["BUSY_SCRAPING", "TO_BE_SCRAPED", "SCRAPED", ""]
OPERATION_STATUSES = ["TODO", "BUSY", "DONE"]

DATABASE_PATH = r"C:\Data\Generated_program_data\boardgamearena_quoridor_scraper"

DATATYPE_TO_SQL_DATATYPE= {
    int:"INTEGER",
    str:"TEXT",
}

game_metadata_by_player_columns = {

    "table_with_player_id":str,
    "table_id":int,
    "download_status":str,
    "player_1_id":int,
    "player_2_id":int,
    "player_1_name":str,
    "player_2_name":str,
    "time_start":int,
    "time_end":int,
    "concede":int,
    "unranked":int,
    "normalend":int,
    "player_1_score":int,
    "player_1_rank":int,
    "player_2_score":int,
    "player_2_rank":int,
    "elo_after":int,
    "elo_win":int,
    "player_id_scraped_player":int,
    "players_count":int,
}

games_table_columns = {
    "table_id":int,
    
    "player_1_id":int,
    "player_2_id":int,
    "player_1_name":str,
    "player_2_name":str,
    "moves_bga_notation":str,
    "moves_lode_notation":str,
    "thinking_times":str,
    "thinking_times":str,
    "total_time":str,
    "game_quality":str,
    "time_start":int,
    "time_end":int,
    "concede":int,
    "unranked":int,
    "normalend":int,
    "player_1_score":int,
    "player_2_score":int,
    "player_1_rank":int,
    "player_2_rank":int,
    "players_count":int,

    "thinking_times":str,
    "absolute_timestamps":str,
    "reflexion_time_delta":int,
    "reflexion_time_max":int,
    "starting_player":int,
    "non_starting_player":int,
    "elo_after_player_1":int,
    "elo_after_player_2":int,
    "elo_win_player_1":int,
    "elo_win_player_2":int,

    "download_status":str,
    "process_state":str,
}


# games_table_columns = {
#     "table_id":int,
#     "download_status":str,
#     "player_1_id":int,
#     "player_2_id":int,
#     "player_1_name":str,
#     "player_2_name":str,
#     "moves_bga_notation":str,
#     "moves_lode_notation":str,
#     "thinking_times":str,
#     "total_time":str,
#     "game_quality":str,
#     "time_start":int,
#     "time_end":int,
#     "concede":int,
#     "unranked":int,
#     "normalend":int,
#     "player_1_score":int,
#     "player_2_score":int,
#     "player_1_rank":int,
#     "player_2_rank":int,
#     "elo_after":int,
#     "elo_win":int,
#     "player_id_scraped_player":int,
#     "players_count":int,
# }

class BoardGameArenaDatabaseOperations():
    def __init__(self, db_path, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.logger.info("BoardGameArena scraper database operations. init.".format(
            ))
       
        self.db_path = db_path
        self.players_table_name = "players"
        self.games_table_name = "games"
        self.games_per_player_table_name = "games_per_player"

        self.db_connect(self.db_path)

        self.create_players_table()  # will only create if not exists
        self.create_games_table()
        self.create_game_metadata_by_player_table()

    def db_connect(self, db_path):
        self.db = sqlite3_operations.DatabaseSqlite3Actions( db_path, self.logger)

    def prepare_columns_data_for_sql(self, table_columns_dict, primary_key_column_name):

        columns = []
        for name,datatype in table_columns_dict.items():
            col = "{} {}".format(name, DATATYPE_TO_SQL_DATATYPE[datatype])
            
            if name == primary_key_column_name:
                col = "{} PRIMARY KEY".format(col)
            
            columns.append(col)
        
        sql_columns_string = "({})".format(
            ",".join(columns),
            )
        return sql_columns_string 

    def create_game_metadata_by_player_table(self):

        col_str = self.prepare_columns_data_for_sql(game_metadata_by_player_columns, "table_with_player_id")
         

        sql = """CREATE TABLE IF NOT EXISTS {} {};""".format(
            self.games_per_player_table_name,
            col_str,
            )

        self.db.execute_sql(sql)
        self.commit()

    def create_players_table(self):
        sql_create_player_table = """CREATE TABLE IF NOT EXISTS {} (
            player_id INTEGER PRIMARY KEY,
            player_name TEXT ,
            quoridor_games_played INTEGER,
            quoridor_games_won INTEGER,
            quoridor_games_lost INTEGER,
            ranking INTEGER,
            download_status TEXT,
            player_status TEXT
        );""".format(self.players_table_name)
        self.db.execute_sql(sql_create_player_table)
        self.commit()

    def commit(self):
        self.db.commit()

    def create_games_table(self):

        col_str = self.prepare_columns_data_for_sql(games_table_columns, "table_id")
         

        sql = """CREATE TABLE IF NOT EXISTS {} {};""".format(
            self.games_table_name,
            col_str,
            )

        self.db.execute_sql(sql)
        self.commit()

    def add_game(self, game_data):
        # game_data is a dict with all game data
        self.db.add_record(self.games_table_name, game_data, True)

    def get_game_metadata(self, id):
        sql = """SELECT * FROM {} WHERE {}=={};""".format(
            self.games_per_player_table_name,
            "table_id",
            id,
            )

        rows = self.db.execute_sql_return_rows(sql)

        game_meta_data = {}
        for row in rows:

            # convert to dict
            for i,column_name in enumerate(list(game_metadata_by_player_columns)):
                column_type_convert = game_metadata_by_player_columns[column_name]
                game_meta_data[column_name] = column_type_convert(row[i])

            if game_meta_data["player_id_scraped_player"] == game_meta_data["player_1_id"]:
                game_meta_data["elo_after_player_1"] = game_meta_data["elo_after"]
                game_meta_data["elo_win_player_1"] = game_meta_data["elo_win"]

            elif game_meta_data["player_id_scraped_player"] == game_meta_data["player_2_id"]:
                game_meta_data["elo_after_player_2"] = game_meta_data["elo_after"]
                game_meta_data["elo_win_player_2"] = game_meta_data["elo_win"]

            else:
                self.logger("should be player_1 or player_2.. but non found.")
                raise Exception 

        del game_meta_data["elo_win"]
        del game_meta_data["elo_after"]
        del game_meta_data["table_with_player_id"]
        del game_meta_data["player_id_scraped_player"]
        return game_meta_data

    def set_status_of_game_ids(self, ids, status="BUSY"):

        if status not in OPERATION_STATUSES:
            self.logger.error("Illegal status {}".format(status))
            return
        
        # set statuses as one sql transaction
        ids_str = [str(id) for id in ids]
        ids_formatted = ",".join(ids_str)

        sql = "UPDATE '{}' SET {} = '{}' WHERE  {} in ({})".format(
            self.games_per_player_table_name,
            "download_status",
            status,
            "table_id",
            ids_formatted,
            )

        self.logger.info(sql)

        self.db.execute_sql(sql)
        self.db.commit()    

    def games_set_status_from_status(self, find_status="BUSY", set_status="DONE"):
        # anomalous rows that are still at busy even when all process finished need to be reset
        table_ids = self.get_games_ids_by_status(None,find_status)
        self.set_status_of_game_ids(table_ids, set_status)

    def get_games_ids_by_status(self, count=None, status=None):
        # if count=None --> all
        # if status=None --> no status needed.

        if status not in OPERATION_STATUSES:
            self.logger.error("Illegal status {}".format(status))
            return

        sql = "SELECT {} FROM {} WHERE download_status = '{}'".format(
            "table_id",
            self.games_table_name,
            status,
            )
        rows = self.db.execute_sql_return_rows(sql,count)
        ids = [r[0] for r in rows]

        return ids

    def set_games_priority(self):
        
        # for every player number of games time elo ranking! 
        # player_1 average elo 
        # player_2 average elo
        # player_1 number of games
        # player_2 number of games
        # 
        # player_1_elo_with_games_count_multiplied
        # player_2_elo_with_games_count_multiplied

        # game_importance_from_elo_and_games_count
        
        # get players data

        # get game data --> player1 and player2

        # create game importance data

        # create sql to set game importance

        pass

    def set_status_of_player_ids(self, ids, status="BUSY"):

        if status not in OPERATION_STATUSES:
            self.logger.error("Illegal status {}".format(status))
            return
        
        # set statuses as one sql transaction
        ids_str = [str(id) for id in ids]
        ids_formatted = ",".join(ids_str)

        sql = "UPDATE '{}' SET {} = '{}' WHERE  {} in ({})".format(
            self.players_table_name,
            "processing_status",
            status,
            "player_id",
            ids_formatted,
            )
        # self.logger.info(sql)

        self.db.execute_sql(sql)
        self.db.commit()

    def repair_busy_status_to_todo(self):
        # anomalous rows that are still at busy even when all process finished need to be reset
        while True:
            player_ids = self.get_player_ids("BUSY_SCRAPING")

            if len(player_ids) == 0:
                return 
                
            for player_id in player_ids:
                self.update_player_status(player_id, "TO_BE_SCRAPED", False)
            self.db.commit()

    def normalize_player_to_player_id(self, player):
        # player can be given as int (for the id) or string (id as string or player_name)
        try:
            player_id = int(player)

        except Exception as e:
            player_id = self.get_player_id_from_name(player)
            if player_id is None:
                self.logger.error("Could not get player id from name ({})".format(
                    player,
                    ))
                return None 
        return player_id
                
    def get_player_id_from_name(self, player_name):
        sql_base = ''' SELECT "player_id" FROM players WHERE {} = "{}";'''.format(
            "player_name",
            player_name,
            )

        sql = sql_base

        rows = self.db.execute_sql_return_rows(sql)

        if len(rows)>1:
            self.logger.error("More than one id for name: {} ({})".format(
                player_name,
                rows,
                ))

        if len(rows)==0:
            self.logger.warning("Player {} not found in db. ".format(
                player_name,
                ))
            return None

        return rows[0][0]

    def get_player_ids(self, status=None, count=None):
        if status is not None:
            if status not in PLAYER_STATUSES:
                self.logger.error("Illegal status {}".format(status))
                return
            sql_player_status = '''WHERE player_status = "{}"'''.format(status)

        else:
            sql_player_status = ""

        if count is None:
            count = ""
        else:
            count = "LIMIT {}".format(count)

        sql_base = ''' SELECT * FROM players {} {};'''.format(
            sql_player_status,
            count,
            )

        sql = sql_base

        rows = self.db.execute_sql_return_rows(sql)

        players = {}
        for row in rows:
            players[row[0]] = {"name":row[1]}

        return players

    def update_player_status(self, player_id, player_status, commit):
        if player_status not in PLAYER_STATUSES:
            raise PlayerStatusNotFound
         
        sql = "UPDATE '{}' SET player_status = '{}' WHERE player_id = {}".format(
            self.players_table_name,
            player_status,
            player_id,
            )

        self.db.execute_sql(sql)
        if commit:
            self.commit()

    def add_player(self, player_id, player_name, player_status, commit):
        if player_status not in PLAYER_STATUSES:
            raise PlayerStatusNotFound
        
        sql_base = ''' INSERT OR IGNORE INTO {} (player_id, player_name,player_status)
                        VALUES ({},"{}","{}");'''.format(
            self.players_table_name,
            player_id,
            player_name,
            player_status,
            )

        sql = sql_base

        self.db.execute_sql(sql)

        if commit:
            self.commit()

    def update_players_from_games(self):
        players = self.get_players_from_games()
        for id,name in players.items():
            self.add_player( id, name, "TO_BE_SCRAPED", False)
        self.commit()

    

    def fill_in_player_data(self):
        # get players

        # avg_elo_games_count_mult
        # high_elo_games_count_mult


        # restriction = "WHERE games_played=100"
        restriction = ""

        # get player data
        sql = "SELECT player_id, games_played, average_elo, highest_elo FROM {} {}".format(
            self.players_table_name,
            restriction,
        )
        rows = self.db.execute_sql_return_rows(sql)

        player_data = defaultdict(dict)
        
        # process data
        for player_id, games_played, average_elo, highest_elo in rows:
            if games_played is None:
                games_played = 0
            if average_elo is None:
                average_elo = 0
            if highest_elo is None:
                highest_elo = 0

            player_data[player_id]["avg_elo_games_count_mult"] = games_played * average_elo
            player_data[player_id]["high_elo_games_count_mult"] = games_played * highest_elo

        self.db.add_column_to_existing_table("players","avg_elo_games_count_mult", "INT", "null")
        self.db.add_column_to_existing_table("players","high_elo_games_count_mult", "INT", "null")
        
        # write every player's stats
        number_of_players = len(list(player_data))
        for i, (player_id, data) in enumerate(player_data.items()):
            # add to table
            sql = "UPDATE '{}' SET avg_elo_games_count_mult={}, high_elo_games_count_mult={} WHERE player_id = {}".format(
            self.players_table_name,
            data["avg_elo_games_count_mult"],
            data["high_elo_games_count_mult"],
            player_id,
            )

            self.db.execute_sql(sql)
            if i%1000 == 0:
                self.logger.info("{} ({}/{})".format(
                    player_id,
                    i+1,
                    number_of_players,
                    ))
        self.commit()     

    def complete_player_data_from_games(self):

        # lowest timestamp
        # highest timestamp
        # highest elo
        # average elo
        # games played


        # restriction = "WHERE elo_win=47"
        restriction = ""

        # get games data
        sql = "SELECT player_1_id, player_2_id, time_start, player_id_scraped_player, elo_after FROM {} {}".format(
            self.games_table_name,
            restriction,
        )
        rows = self.db.execute_sql_return_rows(sql)

        player_data = defaultdict(dict)
        
        # process data
        for player_1, player_2, time_start, player_id_scraped_player, elo_after in rows:

            for player_id in (player_1, player_2):
               

                if not "games_played" in player_data[player_id]:
                    player_data[player_id]["games_played"] = 0

                player_data[player_id]["games_played"] += 1

                if not "lowest_timestamp" in player_data[player_id]:
                    player_data[player_id]["lowest_timestamp"] = 99999999999
                if player_data[player_id]["lowest_timestamp"] > time_start:
                    player_data[player_id]["lowest_timestamp"] = time_start
                    time_start_ISO = datetime.datetime.fromtimestamp(time_start).strftime("%Y.%m.%d-%H.%M.%S")
                    player_data[player_id]["lowest_timestamp_ISO"] = time_start_ISO

                if not "highest_timestamp" in player_data[player_id]:
                    player_data[player_id]["highest_timestamp"] = 0
                if player_data[player_id]["highest_timestamp"] < time_start:
                    player_data[player_id]["highest_timestamp"] = time_start
                    time_start_ISO = datetime.datetime.fromtimestamp(time_start).strftime("%Y.%m.%d-%H.%M.%S")
                    player_data[player_id]["highest_timestamp_ISO"] = time_start_ISO
                    
                if not "highest_elo" in player_data[player_id]:
                    player_data[player_id]["highest_elo"] = 0
                if not "average_elo" in player_data[player_id]:
                    player_data[player_id]["average_elo"] = 0
                

                if player_id == player_id_scraped_player:
                    if player_data[player_id]["highest_elo"] < elo_after:
                        player_data[player_id]["highest_elo"] = elo_after

                    average_elo = ((((player_data[player_id]["games_played"]-1) * player_data[player_id]["average_elo"]) + elo_after) / player_data[player_id]["games_played"])  # games_played is already updated.
                    player_data[player_id]["average_elo"] = average_elo

               
        # make sure columns exist
        self.db.add_column_to_existing_table("players","games_played", "INT", "null")
        self.db.add_column_to_existing_table("players","average_elo", "INT", "null")
        self.db.add_column_to_existing_table("players","highest_elo", "INT", "null")
        self.db.add_column_to_existing_table("players","highest_timestamp", "INT", "null")
        self.db.add_column_to_existing_table("players","lowest_timestamp", "INT", "null")
        self.db.add_column_to_existing_table("players","highest_timestamp_ISO", "TEXT", "null")
        self.db.add_column_to_existing_table("players","lowest_timestamp_ISO", "TEXT", "null")

        # write every player's stats
        number_of_players = len(list(player_data))
        for i, (player_id, data) in enumerate(player_data.items()):
            # add to table
            sql = "UPDATE '{}' SET games_played={}, average_elo={}, highest_elo={}, highest_timestamp={}, lowest_timestamp={}, highest_timestamp_ISO='{}', lowest_timestamp_ISO='{}' WHERE player_id = {}".format(
            self.players_table_name,
            data["games_played"],
            data["average_elo"],
            data["highest_elo"],
            data["highest_timestamp"],
            data["lowest_timestamp"],
            data["highest_timestamp_ISO"],
            data["lowest_timestamp_ISO"],
            player_id,
            )
            # if player_id == 9668513:
            #     # self.logger.info("FOUND PABLITOOOOO")
            #     # self.logger.info(player_data[player_id])
            #     self.logger.info(sql)

            self.db.execute_sql(sql)
            if i%1000 == 0:
                self.logger.info("{} ({}/{})".format(
                    player_id,
                    i+1,
                    number_of_players,
                    ))
        self.commit()     

    def elo_max_average_per_player(self):
        pass

    def get_game_ids_for_player_confrontations(self, player_id_1, player_id_2):
        # from raw scraped data
        sql = """SELECT table_id FROM {0} WHERE (player_1_id = {2} OR player_1_id = {1}) AND (player_2_id = {2} OR player_2_id = {1});""".format(
            "games_per_player",
            player_id_1,
            player_id_2,
            )
        
        rows = self.db.execute_sql_return_rows(sql)
        ids = [r[0] for r in rows]
        return ids
    
    # def get_game_ids_for_player(self, player_id):
    #     player_id = int(player_id)
    #     sql = """SELECT table_id FROM games WHERE player_1_id = {0} OR player_2_id = {0};""".format(player_id)
        
    #     rows = self.db.execute_sql_return_rows(sql)
    #     ids = [r[0] for r in rows]
    #     return ids
    
    def get_and_mark_game_ids_for_player(self, player_id, count=None, set_status="BUSY"):
        player_id = int(player_id)
        sql = """SELECT table_id FROM games_per_player WHERE (player_id_scraped_player = {0}) AND (download_status is null) LIMIT {1};""".format(
            player_id,
            count,
            )

        self.logger.info(sql)

        rows = self.db.execute_sql_return_rows(sql)

        if count is not None:
            ids = [r[0] for r in rows [:count]]
        else:
            ids = [r[0] for r in rows]
        
        self.logger.info("ids: {} , set status: {}".format(
            ids,
            set_status,
            ))

        self.set_status_of_game_ids(ids, set_status)

        return ids

    def max_elo_per_player(self):
        # check for elo at games (it's not perfect, but should do the trick)
        # add to player.
        pass

    def set_other_player_elo_per_game(self):
        # I should download this.... , but the alternative is to take the other players elo (or maybe the elo at the nearest closed table id !...)
        # YES! DOWNLOAD! Will be so much more straight forward!
        
        pass

    def generate_game_importance_score(self):
        # multiply elo player 1 with elo player 2
        #  
        pass

    def set_game_process_status(self, table_id):
        # update status

        pass
  
    def get_players_from_games(self):
        sql_base = ''' SELECT * FROM {};'''.format( 
            self.games_per_player_table_name,
            )

        sql = sql_base

        rows = self.db.execute_sql_return_rows(sql)

        players = {}
        for row in rows:
            # player id:name pair
            players[row[3]] = row[5]
            players[row[4]] = row[6]

        return players
    
    def add_game_metadata(self, table_id, metadata, commit):

        # check and prepare the data
        columns = []
        values = []

        table_columns_data = game_metadata_by_player_columns
        possible_column_names = table_columns_data.keys()
        for column,value in metadata.items():
            if column not in possible_column_names:
                raise UnexpectedColumnNameException

            if value is None:
                # reaction to error thrown. I presume things changed on website over time.....
                value = str(None)

            if table_columns_data[column] is str:
                values.append("\"{}\"".format(value))
                
            elif table_columns_data[column] is int:
                if value is None or value == "None":
                    value = "NULL"
                values.append(value)
                
            else:
                raise UnexpectedColumnTypeException

            columns.append(column)
        try:
            columns = ",".join(columns)
            values = ",".join(values)
        except Exception as e:
            self.logger.error("error converting {} to string. ({})".format(
                values,
                e,
                ))
            raise

        # sql command
        sql = ''' INSERT OR IGNORE INTO {} ({})
                        VALUES ({});'''.format(
            self.games_per_player_table_name,
            columns,
            values,
            )

        self.db.execute_sql(sql)

        if commit:
            self.commit()

    # def game_count_per_player_fast(self):
    #     # go over all games.
    #     # get player ids, add counter for both on a defaultdict

    #     sql = "SELECT player_1_id, player_2_id FROM {} ".format(
    #         self.games_table_name,
    #     )
    #     # sql = "SELECT player_1_id, player_2_id FROM {} WHERE elo_win=47 ".format(
    #     #     self.games_table_name,
    #     # )
        
    #     rows = self.db.execute_sql_return_rows(sql)
    #     games_per_player = defaultdict(int)

    #     for player_1, player_2 in rows:
    #         games_per_player[player_1] += 1
    #         games_per_player[player_2] += 1

    #     # make sure a column exists
    #     self.db.add_column_to_existing_table("players","games_played", "INT", "null")

    #     # write every player's stats
    #     number_of_players = len(list(games_per_player))
    #     for i, (player_id, games_played) in enumerate(games_per_player.items()):
    #         # add to table
    #         sql = "UPDATE '{}' SET games_played = '{}' WHERE player_id = {}".format(
    #         self.players_table_name,
    #         games_played,
    #         player_id,
    #         )

    #         self.db.execute_sql(sql)
    #         self.logger.info("{} ({}/{})".format(
    #             player_id,
    #             i+1,
    #             number_of_players,
    #             ))
    #     self.commit()


    # def games_count_per_player(self, count_per_call=4):
    #     # select all games for a player as player 1 and as player 2
    #     # make new column in players table
    #     # add games count to player.
    #     # self.db.add_column_to_existing_table("players","games_played", "INT", "null")
        
    #     timestamp = time.time()

    #     # reading and writing
    #     player_ids = self.get_player_ids(count=count_per_call, status="TODO", set_status_of_selected_rows="BUSY")

    #     time_delta_1 = time.time() - timestamp
    #     timestamp = time.time()

    #     # reading
    #     if len(player_ids) == 0:
    #         self.info.logger("No player ids returned. Done.")
    #         return False

    #     player_games_tuples = []
    #     for player_id in player_ids:
    #         game_ids= self.get_game_ids_for_player(player_id)
    #         games_played = len(game_ids)
    #         player_games_tuples.append((player_id, games_played))
    #         self.logger.info("Player {} player {} games".format(
    #             player_id,
    #             games_played,
    #             ))
        
    #     time_delta_2 = time.time() - timestamp
    #     timestamp = time.time()

    #     #writing results (combine to limit time spent writing (database is locked for other processes to read at that time. sqlite is settable for still being readable at that time though...))
    #     for player_id, games_played in player_games_tuples:
    #         # add to table
    #         sql = "UPDATE '{}' SET games_played = '{}' WHERE player_id = {}".format(
    #         self.players_table_name,
    #         games_played,
    #         player_id,
    #         )

    #         self.db.execute_sql(sql)


    #     time_delta_3 = time.time() - timestamp
    #     timestamp = time.time()
    #     # add to table

    #     # player_games_count_str = ""
    #     # for t in player_games_tuples:
    #     #     player_games_count_str += str(t)
    #     # player_games_tuples_str = [str(t) for t in player_games_tuples]
    #     # player_games_count_str = ",".join(player_games_tuples_str)

    #     # sql = "INSERT INTO {} (player_id, games_played) VALUES {} ON DUPLICATED KEYS UPDATE player_id=VALUES(player_id),games_played=VALUES(games_played);".format(
    #     # self.players_table_name,
    #     # player_games_count_str,
    #     # )
    #     # self.logger.info(sql)
    #     # self.db.execute_sql(sql)

    #     # self.logger.info("Player {} player {} games".format(
    #     #     player_id,
    #     #     games_played,
    #     #     ))
        
    #     self.set_status_of_player_ids(player_ids,"DONE")

    #     time_delta_4 = time.time() - timestamp
    #     timestamp = time.time()
        
    #     self.db.commit()
    #     self.logger.info("Counted games for {} players. Example player id processed: {}. {:.2f}s,{:.2f}s,{:.2f}s,{:.2f}s.".format(
    #         count_per_call,
    #         player_ids[0],
    #         time_delta_1,
    #         time_delta_2,
    #         time_delta_3,
    #         time_delta_4,
    #         ))

    #     return True

    # def add_sequences(self, sequences, status, commit=True):
    #     # all sequences are assumed to have the same lenght (aka for the same level)
    #     if len(sequences) == 0:
    #         return
        
    #     table_name = self.sequence_to_table_name(sequences[0])

    #     rows_data = []
    #     for sequence in sequences:
    #         seqstr = self.sequence_to_str(sequence)
    #         rows_data.append( "('{}','{}','{}')".format(seqstr, status,''))
            
    #     rowsdatastr = ",".join(rows_data)
                
    #     sql_base = ''' INSERT INTO {} (sequence, status, optional)
    #                    VALUES {} ;'''.format(table_name, rowsdatastr)

    #     sql = sql_base.format(table_name, )

    #     self.db.execute_sql(sql)

    #     if commit:
    #         self.db.commit()
    #         # print("commit")
        
    # def add_sequence(self, sequence, status, commit=True):
    #     # sequence is an array of tuples. with (piece_id, piece_orientation)

    #     # convert to string of list of ints.
       
    #     table_name = self.sequence_to_table_name(sequence)
    #     savestr = self.sequence_to_str(sequence)

    #     sql_base = ''' INSERT INTO {} (sequence, status, optional)
    #                    VALUES('{}','{}','{}');'''
    #     sql = sql_base.format(table_name, savestr, status,'')

    #     self.db.execute_sql(sql)

    #     if commit:
    #         self.db.commit()
      
    # # def change_statuses(self, sequences, status, commit=True):
    # #     for sequence in sequences:
    # #         self.change_status(sequence, status, False)

    # #     if commit:
    # #         self.db.commit()
    
    # def change_statuses(self, sequences, status, commit=True):

    #     if len(sequences) == 0:
    #         return 

    #     # all sequences should have the same length. So, 
    #     table_name = self.sequence_to_table_name(sequences[0])

    #     # table_name = self.level_to_table_name(level)

    #     conditions= []
    #     for sequence in sequences:
    #         seqstr = self.sequence_to_str(sequence)
    #         condition = "sequence = '{}'".format(seqstr)
    #         conditions.append(condition)
        
    #     conditionsstr = " OR ".join(conditions)

    #     sql = "UPDATE '{}' SET status = {} WHERE {}".format(table_name, status, conditionsstr)
    #     self.db.execute_sql(sql)
    #     if commit:
    #         self.db.commit()
                    
    # def change_status(self, sequence, status, commit=True):
    #     table_name = self.sequence_to_table_name(sequence)
    #     seqstr = self.sequence_to_str(sequence)

    #     sql = "UPDATE '{}' SET status = {} WHERE sequence = '{}'".format(table_name, status, seqstr)
    #     self.db.execute_sql(sql)
    #     if commit:
    #         self.db.commit()
           
    # def get_sequences(self, desired_status, level, count, mark_as_in_progress=False):
        
    #     table_name = self.level_to_table_name(level)
        
    #     with self.db.conn:
    #         sql = " SELECT * from '{}' where status = {} LIMIT {}".format(
    #                 table_name,
    #                 desired_status,
    #                 count,
    #                 )

    #         rows = self.db.execute_sql_return_rows(sql)
    #         sequences = []
    #         for row in rows:
    #             sequence = self.str_to_sequence(row[1])
    #             sequences.append(sequence)

    #         if mark_as_in_progress:
    #             self.change_statuses(sequences, TESTING_IN_PROGRESS, True)

    #         return sequences

    # def sequence_to_table_name(self, sequence):
    #     level= len(sequence)
    #     return self.level_to_table_name(level)

    # def level_to_table_name(self, level):
    #     return self.table_base_name.format(level)
        
    # def sequence_to_str(self, sequence):
    #     savestr = ""        
    #     for p,o in sequence:
    #         savestr += "{},{},".format(p,o)
    #     return savestr[:-1]  # delete last
    
    # def str_to_sequence(self, seqstr):
    #     # expect str like: 1,2,345,6,7,8  --> even length!! (not odd)
    #     elements = seqstr.split(",")
    #     seq = []
    #     for p,o in zip(elements[0::2], elements[1::2]):
    #         seq.append((int(p),int(o)))
    #     return seq

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
if __name__ == '__main__':
    
    logger = logging_setup(logging.INFO, Path(DATABASE_PATH,  r"logs", "bga_scraping_database_operations.log"), "SESSION" )

    # db_name = "bga_quoridor_data.db"
    # db_name = "TESTING_bga_quoridor_data.db"
    # db_name = "TESTING_bga_quoridor_data_test_player_game_table.db"
    db_name = "bga_quoridor_data.db"
    # db_name = "TESTING_bga_quoridor_data_bkpAfterBasicScraping_modified_20201120.db"


    
    db_path = Path( DATABASE_PATH,
        db_name,
        )
    
    db = BoardGameArenaDatabaseOperations(db_path, logger)

    # ids = db.get_and_mark_game_ids_for_player(84306079, 4, "BUSY")
    # db.set_status_of_game_ids(ids,"TODO")
    # db.games_set_status_from_status("BUSY", "TODO")

    # db.complete_player_data_from_games()
    # db.fill_in_player_data()
    # db.fill_in_games_data_from_player()
    # db.fill_in_games_data()

    exit() 
    # db.db.add_column_to_existing_table("players", "processing_status", "TEXT", "TODO")
    

    # continue_counting= True
    # while continue_counting:
    #     continue_counting = db.games_count_per_player(30)  # 19s for 100 records
    
    # print(db.get_games_for_player(2251))
    # print(db.get_games_for_player(85054430))

    # db.add_player("12345","lode","TEST",True)
    # print( list(db.get_player_ids("TEST",1))[0])
    # db.update_player_status(1233, "TEST2", True)
    # print(db.get_player_ids("TO_BE_SCRAPEDff",1))
    # db.update_players_from_games()