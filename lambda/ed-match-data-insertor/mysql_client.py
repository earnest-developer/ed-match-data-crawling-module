#! python3
# sql_wrapper.py -- A wrapper class for the SQL connection

import logging
import mysql.connector
from mysql.connector import Error

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def create_connection(connection_string: str):
    """Creates a connection to the database"""

    connectionParams = dict(entry.split('=') for entry in connection_string.split(';'))
    connection = None
    try:
        connection = mysql.connector.connect(**connectionParams)
        logging.info("Connected to the database")
    except Error as e:
        logging.error(f"The error '{e}' occurred")

    return connection


def execute_query(connection, query, values):
    """Executes a query against the database in a fault tolerant way"""

    cursor = connection.cursor()
    try:
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
    except mysql.connector.Error as error:
        logging.error(f"Failed to insert into table {error}")
        pass
    finally:
        return cursor.rowcount
