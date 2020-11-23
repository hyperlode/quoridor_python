import sqlite3
from sqlite3 import Error

import random
import time
from pathlib import Path

'''
https://www.sqlitetutorial.net/sqlite-python/creating-database/

SQLiteDatabaseBrowserPortable.exe to browse.
'''

PLAYER_STATUSSES = ["TEST", "UP_TO_DATE", "TO_BE_SCRAPED", "TEST2"]

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
    def __init__(self, path):
        self.conn = None
        self.create_connection(path)

    def create_connection(self, db_file):
        """ create a database connection to a SQLite database """
        try:
            self.conn = sqlite3.connect(db_file)
           
        except Error as e:
            print(e)
    
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

    def execute_sql(self, sql, verbose=False):
        DATABASE_RETRIES = 100
        retry = DATABASE_RETRIES

        while retry > 0:

            try:
                cur = self.get_cursor()
                cur.execute(sql)
                if retry  != DATABASE_RETRIES:
                    print("SQL success. after: {} retries".format(DATABASE_RETRIES - retry))
                retry = 0
            except Exception as e:
                print(sql)
                # sqlite3.OperationalError
                randomtime = random.randint(0,100)/100
                time.sleep(randomtime)
                retry -= 1
                print("database error: {}".format(e))
                print("database error, retries: {}".format(retry))
        if verbose:
            print("sql executed: {} (truncated to 100 chars)".format(sql[:100]))
        return cur

    def execute_sql_return_rows(self, sql):
        cur = self.execute_sql(sql)
        data = cur.fetchall()
        return data

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

class BoardGameArenaDatabaseOperations():
    def __init__(self, db_path):
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
        if player_status not in PLAYER_STATUSSES:
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
        if player_status not in PLAYER_STATUSSES:
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
        for k,v in metadata.items():
            if k not in possible_column_names:
                raise UnexpectedColumnNameException

            if games_table_columns[k] is str:
                values.append("\"{}\"".format(v))
                
            elif games_table_columns[k] is int:
                values.append(v)
                
            else:
                raise UnexpectedColumnTypeException

            columns.append(k)
        try:
            columns = ",".join(columns)
            values = ",".join(values)
        except:
            print(values)
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

if __name__ == '__main__':
    
    db_path = r"C:\Data\Generated_program_data\boardgamearena_quoridor_scraper\bga_quoridor_data.db".format()
    db = BoardGameArenaDatabaseOperations(db_path)

    # db.add_player("12345","lode","TEST",True)
    print( list(db.get_players_by_status("TEST",1))[0])
    db.update_player_status(1233, "TEST2", True)
    print(db.get_players_by_status("TO_BE_SCRAPEDff",1))
    # db.update_players_from_games()