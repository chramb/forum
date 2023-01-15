import sys

import psycopg2
from util.config import config


class Database:
    # def __init__(self):

    def connect(self):
        """
        Connect to database
        :return: database connection
        """
        try:
            params = config()
            print("Connecting to the Database...")
            conn = psycopg2.connect(**params)
            with conn.cursor() as crsr:
                print("Database Version: ", end="")
                crsr.execute("SELECT version()")
                print(crsr.fetchone()[0].split(',')[0])
        except psycopg2.OperationalError as err:
            print(err)
            sys.exit(1)

        return conn

    def cursor(self):
        try:
            params = config()
            print("Connecting to the Database...")
            conn = psycopg2.connect(**params)
            curr = conn.cursor()
        except psycopg2.OperationalError as err:
            print(err)
            sys.exit(1)

        return curr


global db, connection
db = Database()
connection = db.connect()