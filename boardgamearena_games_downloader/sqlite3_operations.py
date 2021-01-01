import logging
import random
import time

import sqlite3
from sqlite3 import Error

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

    def add_record(self, table_name, col_value_dict, commit=True):

        cols = []
        vals = []
        for col, val in col_value_dict.items():
            cols.append(col)
            if type(val) is str:
                vals.append(r'"{}"'.format(val))
            else:
                vals.append(str(val))

        print(",".join(cols))
        print(",".join(vals))
        sql = ''' INSERT OR IGNORE INTO {} ({})
                        VALUES ({});'''.format(
            table_name,
            ",".join(cols),
            ",".join(vals),
            )

        self.execute_sql(sql)

        if commit:
            self.commit()
    