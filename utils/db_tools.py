import sqlite3
import pandas as pd


def db_copy_sqlite3_tables(db_in, db_out, tables):
    """
    Copy tables from one database to another
    :param db_in: full filename of the origin of tables 
    :type db_in: string
    :param db_out: full filename of the destination of tables
    :type db_in: string
    :param tables: list of tables to copy
    :type tables: list
    :return: status, 0: OK, 1: failure
    :rtype: int
    """
    
    status = 0
    try:
        conn_in = sqlite3.connect(db_in)
        conn_out = sqlite3.connect(db_out)
        for i in tables:
            df = pd.read_sql_query("SELECT * from {table:s}".format(table=i), conn_in)
            df.to_sql("{table:s}".format(table=i),conn_out, if_exists='replace', index = False)
        conn_in.close()
        conn_out.close()
    except Exception as e:
        print('Error copying tables:\n {error:s}'.format(error=e))
        status = 1
    return status