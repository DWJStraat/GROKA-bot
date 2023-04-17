import json
from datetime import datetime
import time
import mariadb

config = json.load(open("config.json"))


class Server:
    """
    This class is meant to access the database.
    """

    def __init__(self, config_path):
        config_json = json.load(open(config_path))
        self.host = config_json["host"]
        self.database = config_json["database"]
        self.user = config_json["user"]
        self.password = config_json["password"]
        self.port = config_json["port"]
        self.connection = None
        self.cursor = None


    def connect(self):
        try:
            self.connection = mariadb.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
        except mariadb.OperationalError as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            print('Attempting to reconnect in 5 seconds...')
            time.sleep(5)
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")

    def getCursor(self):
        try:
            self.cursor = self.connection.cursor()
        except Exception:
            self.connect()
            self.getCursor()

    def closeCursor(self):
        self.cursor.close()
        self.getCursor()

    def execute(self, query, commit=False):
        self.connect()
        self.getCursor()
        try:
            self.cursor.execute(query)
            if commit:
                self.connection.commit()
            try:
                value = self.cursor.fetchall()
            except mariadb.ProgrammingError:
                value = None
            self.cursor.close()
            self.close()
        except Exception as e:
            self.cursor.close()
            self.close()
            print(f"Error: {e}\nQuery: {query}")
            raise e
        return value

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()


default_server = Server("config.json")


class Table:
    """
    This class is meant to access a table in the database.
    """

    def __init__(self, name, server_object=None):
        self.name = name
        self.server = server_object
        if self.server is None:
            self.server = default_server

    def retrieve(self, value, column):
        return self.server.execute(
            f"SELECT * FROM {self.name} WHERE {column} = '{value}';")


    def query(self, query):
        return self.server.execute(query)

    def find(self, value, column, return_column):
        self.server.execute(
            f"SELECT {return_column} FROM {self.name} WHERE {column} = '{value}';")
        values = self.server.cursor.fetchall()
        self.server.closeCursor()
        return values

    def values(self):
        self.server.execute(f"SELECT * FROM {self.name};")
        values = self.server.cursor.fetchall()
        self.server.closeCursor()
        return values

    def like(self, value, column):
        self.server.execute(
            f"SELECT * FROM {self.name} WHERE {column} LIKE '%{value}%';")
        values = self.server.cursor.fetchall()
        self.server.closeCursor()
        return values

    def soundsLike(self, value, column):
        self.server.execute(
            f"SELECT * FROM {self.name} WHERE STRCMP({column},'{value}');")
        values = self.server.cursor.fetchall()
        self.server.closeCursor()
        return values

    def execute(self, query, commit=False):
        return self.server.execute(query, commit)

    def commit(self):
        self.server.commit()

    def find_all(self, column):
        self.server.execute(
            f"SELECT {column} FROM {self.name};")
        values = self.server.cursor.fetchall()
        self.server.closeCursor()
        return [i[0] for i in values]




