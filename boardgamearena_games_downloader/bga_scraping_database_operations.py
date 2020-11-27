import sqlite3
from sqlite3 import Error

import random
import time
import datetime
import logging
from pathlib import Path
from collections import defaultdict

'''
https://www.sqlitetutorial.net/sqlite-python/creating-database/

SQLiteDatabaseBrowserPortable.exe to browse.
'''

PLAYER_STATUSES = ["TEST", "UP_TO_DATE", "TO_BE_SCRAPED", "TEST2", "BUSY_SCRAPING"] 

GAME_SCRAPE_STATUSES = ["BUSY_SCRAPING", "TO_BE_SCRAPED", "SCRAPED", ""]
OPERATION_STATUSES = ["TODO", "BUSY", "DONE"]

DATA_BASE_PATH = r"C:\Data\Generated_program_data\boardgamearena_quoridor_scraper"

games_table_columns = {
    "table_id":int,
    "download_status":str,
    "player_1_id":int,
    "player_2_id":int,
    "player_1_name":str,
    "player_2_name":str,
    "moves_bga_notation":str,
    "moves_lode_notation":str,
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
    "elo_after":int,
    "elo_win":int,
    "player_id_scraped_player":int,
    "players_count":int,
}


class DatabaseSqlite3Actions():
    def __init__(self, path,logger=None):
        self.logger = logger or logging.getLogger(__name__)
        
        self.conn = None
        self.create_connection(path)

    def create_connection(self, db_file):
        """ create a database connection to a SQLite database """
        try:
            self.conn = sqlite3.connect(db_file)
           
        except Error as e:
            self.logger.error("Error connecting database {}".format(e), exc_info = True)
    
    # def create_table(self, create_table_sql):
    #     """ create a table from the create_table_sql statement
    #     :param conn: Connection object
    #     :param create_table_sql: a CREATE TABLE statement
    #     :return:
    #     """
    #     try:
    #         c = self.get_cursor()
    #         c.execute(create_table_sql)
    #     except Error as e:
    #         print(e)

    def get_cursor(self):
        return self.conn.cursor()

    def execute_sql(self, sql, verbose=False, database_retries = 10):
        retry = database_retries

        while retry > 0:

            try:
                cur = self.get_cursor()
                cur.execute(sql)
                if retry  != database_retries:
                    self.logger.info("SQL success. after: {} retries".format(database_retries - retry))
                retry = 0
            except Exception as e:
                
                # sqlite3.OperationalError
                randomtime = random.randint(0,100)/100
                time.sleep(randomtime)
                retry -= 1
                self.logger.warning("Database error ({}) sql: {}, retries: {}".format(
                    e,
                    sql,
                    retry,
                    ))
        if verbose:
            max_chars = 1000
            self.logger.info("sql executed: {} (truncated to {} chars)".format(
                sql[:max_chars],
                max_chars,
                ))
        return cur

    def execute_sql_return_rows(self, sql, row_count=None, database_retries=10):
        # if row_count is None, return all fetched rows.
                    
        cur = self.execute_sql(sql,False,database_retries)
        data = cur.fetchall()
        if row_count is None:
            return data
        else:
            return data[:row_count]

    def commit(self):
        self.conn.commit()

    def get_all_records(self, tablename):
        sql = "SELECT * FROM {}".format(tablename)
        return self.execute_sql_return_rows(sql)

    def get_row_count(self, table_name):
        result = self.execute_sql("select count(*) from {}".format(table_name))
        row = result.fetchone()
        return row[0]

    def get_rows(self, table, limit=100):
        sql = "SELECT * FROM {} LIMIT {}".format(table, limit)
        cur = self.execute_sql(sql)
        data = cur.fetchall()
        return data

    def column_exists(self, table_name, column_name_to_test):

        table_info = self.get_table_info(table_name)

        for row in table_info:
            if column_name_to_test in row:
                return True

        return False

    def get_table_info(self, table_name):

        sql = "pragma table_info('{}')".format(
            table_name,
            )

        table_info = self.execute_sql_return_rows(sql)

        return table_info

    def add_column_to_existing_table(self, table_name, column_name, data_type, default_value):

        #  e.g. default_value = "null"

        if self.column_exists(table_name,column_name):
            self.logger.warning("{} in {} already exists. Will not add column".format(
                column_name,
                table_name,
            ))
            return 

        if data_type not in ["TEXT", "INT"]:
            logger.error("not yet added data type.")
            raise UnknownColumnTypeError 

        sql = "ALTER TABLE {} ADD COLUMN {} {} default {}".format(
            table_name,
            column_name,
            data_type,
            default_value,
            )
        try:
            self.execute_sql(sql,False,5)
        except Exception as e:
            self.logger.error("didn't add column work. {}".format(e,),exc_info=True)

class BoardGameArenaDatabaseOperations():
    def __init__(self, db_path, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.logger.info("BoardGameArena scraper database operations. init.".format(
            ))

        self.db_path = db_path
        self.players_table_name = "players"
        self.games_table_name = "games"

        self.db_connect(self.db_path)


        self.create_players_table()  # will only create if not exists
        self.create_games_table()

    def db_connect(self, db_path):
        self.db = DatabaseSqlite3Actions( db_path)
    
    # def row_count(self,level):
    #     table_name = self.level_to_table_name(level)
    #     return self.db.get_row_count(table_name)
        
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

    def get_player_ids(self, count=None, status=None, set_status_of_selected_rows=None):
        # if count=None --> all
        # if status=None --> no status needed.

        if status not in OPERATION_STATUSES:
            self.logger.error("Illegal status {}".format(status))
            return

        sql = "SELECT {} FROM {} WHERE processing_status = '{}'".format(
            "player_id",
            self.players_table_name,
            status,
            )
        # self.logger.info(sql)
        rows = self.db.execute_sql_return_rows(sql,count)
        ids = [r[0] for r in rows]
        # self.logger.info(ids)

        if set_status_of_selected_rows is not None:
            self.set_status_of_player_ids(ids,set_status_of_selected_rows)
        
        self.db.commit()
        return ids

        
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

    def players_recover_busy_status(self):
        # anomalous rows that are still at busy even when all process finished need to be reset
        player_ids = self.get_player_ids(None,"BUSY",None)
        self.set_status_of_player_ids(player_ids,"TODO")

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
                # print(table_id)
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

    def get_game_ids_for_player(self, player_id):
        player_id = int(player_id)
        sql = """SELECT table_id FROM games WHERE player_1_id = {0} OR player_2_id = {0};""".format(player_id)
        
        rows = self.db.execute_sql_return_rows(sql)
        ids = [r[0] for r in rows]
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

    def create_games_table(self):
        base_sql = """CREATE TABLE IF NOT EXISTS {} (
            table_id INTEGER PRIMARY KEY,
            download_status TEXT,
            player_1_id INTEGER ,
            player_2_id INTEGER ,
            player_1_name INTEGER,
            player_2_name INTEGER,
            moves_bga_notation TEXT,
            moves_lode_notation TEXT,
            thinking_times TEXT,
            total_time TEXT,
            game_quality TEXT,
            time_start INTEGER,
            time_end INTEGER,
            concede INTEGER,
            unranked INTEGER,
            normalend INTEGER,
            player_1_score INTEGER,
            player_2_score INTEGER,
            player_1_rank INTEGER,
            player_2_rank INTEGER,
            elo_after INTEGER,
            elo_win INTEGER,
            player_id_scraped_player INTEGER,
            players_count INTEGER

        );""".format(self.games_table_name)
        self.db.execute_sql(base_sql)
        self.commit()
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
    def get_players_from_games(self):
        sql_base = ''' SELECT * FROM games;'''.format( 
            )

        sql = sql_base

        rows = self.db.execute_sql_return_rows(sql)

        players = {}
        for row in rows:
            players[row[2]] = row[4]
            players[row[3]] = row[5]

        return players

    def get_players_by_status(self, status, quantity=None):
        if quantity is None:
            quantity = ""
        else:
            quantity = "LIMIT {}".format(quantity)

        sql_base = ''' SELECT * FROM players WHERE player_status = "{}" {};'''.format(
            status,
            quantity,
            )

        sql = sql_base

        rows = self.db.execute_sql_return_rows(sql)

        players = {}
        for row in rows:
            players[row[0]] = row[1]

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
        
        # check if player already exists
        

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

    def add_game_metadata(self, table_id, metadata, commit):

        # check and prepare the data
        columns = []
        values = []
        possible_column_names = games_table_columns.keys()
        for column,value in metadata.items():
            if column not in possible_column_names:
                raise UnexpectedColumnNameException

            if value is None:
                # reaction to error thrown. I presume things changed on website over time.....
                value = str(None)

            if games_table_columns[column] is str:
                values.append("\"{}\"".format(value))
                
            elif games_table_columns[column] is int:
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
            self.games_table_name,
            columns,
            values,
            )

        self.db.execute_sql(sql)

        if commit:
            self.commit()

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
if __name__ == '__main__':
    
    logger = logging_setup(logging.INFO, Path(DATA_BASE_PATH,  r"logs"), "SESSION" )

    # db_name = "bga_quoridor_data.db"
    db_name = "TESTING_bga_quoridor_data_bkpAfterBasicScraping_modified_20201120.db"


    
    db_path = Path( DATA_BASE_PATH,
        db_name,
        )

    db = BoardGameArenaDatabaseOperations(db_path, logger)

    # db.complete_player_data_from_games()
    # db.fill_in_player_data()
    # db.fill_in_games_data_from_player()
    db.fill_in_games_data()

    exit() 
    db.db.add_column_to_existing_table("players", "processing_status", "TEXT", "TODO")
    

    # continue_counting= True
    # while continue_counting:
    #     continue_counting = db.games_count_per_player(30)  # 19s for 100 records
    
    # print(db.get_games_for_player(2251))
    # print(db.get_games_for_player(85054430))

    # db.add_player("12345","lode","TEST",True)
    # print( list(db.get_players_by_status("TEST",1))[0])
    # db.update_player_status(1233, "TEST2", True)
    # print(db.get_players_by_status("TO_BE_SCRAPEDff",1))
    # db.update_players_from_games()