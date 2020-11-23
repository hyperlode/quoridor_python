import sqlite3
from sqlite3 import Error

import haley_puzzle_create_multithreading_task as haley_puzzle_attempts


'''
https://www.sqlitetutorial.net/sqlite-python/creating-database/
'''


create_attempts_table = """CREATE TABLE IF NOT EXISTS attempts (
    id int ,
	sequence text PRIMARY KEY,
	is_tested integer,
    is_solution integer,
    seconds_epoch_requested integer,
    requester text
);"""

#id int NOT NULL AUTO_INCREMENT,

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    
def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def add_attempt(conn, attempt_string, manual_id=None):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO attempts(id, sequence, is_tested, is_solution, seconds_epoch_requested, requester)
              VALUES(? ,?,?,?,?,?) '''
    cur = conn.cursor()

    if manual_id is not None:
        data = (manual_id, attempt_string,0,0,0,'')
    else:
        data = (attempt_string,0,0,0,'')
    cur.execute(sql, data)
    return cur

def commit(conn):
    conn.commit()

def get_all_records(conn, table):
    sql = "SELECT * FROM {}".format(table)
    cur = execute_sql(conn, sql)
    data = cur.fetchall()
    return data

def get_row_count(conn, table_name):
    result = execute_sql(conn, "select count(*) from {}".format(table_name))
    row = result.fetchone()
    return row[0]

def get_rows(conn, table, limit=100):
    sql = "SELECT * FROM {} LIMIT {}".format(table, limit)
    cur = execute_sql(conn, sql)
    data = cur.fetchall()
    return data

def execute_sql(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    return cur

def execute_sql_return_rows(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    return data

def setup_haley_puzzle_attempts_no_boards():
    conn = create_connection(r"D:\Temp\puzzle_haley\attempts_no_boards.db")
   
    # all used pieces indeces
    used_pieces = [1,2,3,4,5,6,7,8,9,10,11]

    # create tables
    if conn is None:
        print("Error! cannot create the database connection.")
        raise Error
    create_table(conn, create_attempts_table)

    attemps_iterator = haley_puzzle_attempts.PermutationAsString(used_pieces)
    
    for i, sequence in enumerate(attemps_iterator):
        try:
            add_attempt(conn, sequence, i)
        except sqlite3.IntegrityError:
           
            pass
            
    commit(conn)

    # records = get_all_records(conn, "attempts")
    
def setup_haley_puzzle_attempts():
     # conn = create_connection(r"C:\temp\haley_puzzle\pythonsqlite.db")
    conn = create_connection(r"D:\Temp\puzzle_haley\attempts.db")

   
    # all used pieces indeces
    used_pieces = [1,2,3,4,5,6,7,8,9,10,11]

    # board indeces 
    boards = ['a','b','c','d','e']
            
    # create tables
    if conn is None:
        print("Error! cannot create the database connection.")
        raise Error
    create_table(conn, create_attempts_table)
    
    # sql_set_auto_increment = "UPDATE SQLITE_SEQUENCE SET seq = 0 WHERE name = 'attempts'"
    # sql_set_auto_increment = "UPDATE sqlite_sequence SET seq = 666 WHERE name = 'attempts';"
    # execute_sql(conn, sql_set_auto_increment)


    # INSERT INTO sqlite_sequence (name,seq) SELECT '<table>', <n> WHERE NOT EXISTS 
    #         (SELECT changes() AS change FROM sqlite_sequence WHERE NOT EXISTS SELECT name from sqlite_sequence WHERE name = 'table');

    # add_attempt(conn, "test", 666)


    attemps_iterator = haley_puzzle_attempts.PermutationAsString(used_pieces, boards)
    
    

    # for i in range(110):
    #     try:
    #         add_attempt(conn, next(attemps_iterator), i)
    #     except sqlite3.IntegrityError:
           
    #         pass
    for i, sequence in enumerate(attemps_iterator):
        try:
            add_attempt(conn, sequence, i)
        except sqlite3.IntegrityError:
           
            pass
            
    commit(conn)

    records = get_all_records(conn, "attempts")
    # for r in records[:110]:
    #     print(r)

def get_untested_sequences(conn, count = 1000, print_result=False):

    result = execute_sql_return_rows(conn, " SELECT * from 'attempts' where is_tested != 1 and is_tested != 666 LIMIT {}".format(count))
    sequences = []
    if print_result:
        print(result)
    id_of_first_row = result[0][0]
    for row in result:
        sequences.append( [int(i) for i in row[1].split(",")])
    
    set_sequences_as_tested(conn, sequences, tested_value=666)
    
    return id_of_first_row, sequences

def set_sequences_as_tested(conn, sequences, tested_value=1):
    # expect sequence as array of ints. (will convert to string)
    # print(sequences)
    sequences_str = [",".join(str(el) for el in seq) for seq in sequences]
    
    # print(sequences_str)
    for seq in sequences_str:
        sql_statement = "UPDATE attempts SET is_tested = {} WHERE sequence = '{}'".format(tested_value, seq)
        # print(sql_statement)
        result = execute_sql_return_rows(conn, sql_statement )
    commit(conn)

# def get_incomplete_level(conn):

def get_rows_by_level(conn, level, status, limit):
    # result = execute_sql_return_rows(conn, " SELECT * from 'attempts' where is_tested != 1 and is_tested != 666 LIMIT {}".format(count))
    # sequences = []
    # if print_result:
    #     print(result)
    # id_of_first_row = result[0][0]
    # for row in result:
    #     sequences.append( [int(i) for i in row[1].split(",")])
    
    # set_sequences_as_tested(conn, sequences, tested_value=666)
    
    # return id_of_first_row, sequences
    pass

if __name__ == '__main__':
   # conn = create_connection(r"C:\temp\haley_puzzle\pythonsqlite.db")
    conn = create_connection(r"D:\Temp\puzzle_haley\attempts_no_boards.db")

    # setup_haley_puzzle_attempts_no_boards()
  
    # result = get_row_count(conn, "attempts")
    # result = get_rows(conn, "attempts")
    # winner: '7,2,3,11,8,1,10,6,4,9,5'
   
    # s = get_untested_sequences(conn, count = 10)

    # set_sequences_as_tested(conn, s)

    id_f, s = get_untested_sequences(conn, count = 10, print_result=True)
    print(s)
    print(id_f)

    # result = execute_sql_return_rows(conn, "UPDATE attempts SET is_solution = 1 WHERE sequence = '7,2,3,11,8,1,10,6,4,9,5'")
    # commit(conn)
    # print(result)


