import json
from datetime import datetime

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
        self.connect()
        self.getCursor()

    def connect(self):
        self.connection = mariadb.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            port=self.port
        )

    def getCursor(self):
        self.cursor = self.connection.cursor()

    def closeCursor(self):
        self.cursor.close()
        self.getCursor()

    def execute(self, query):
        self.cursor.execute(query)

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
        self.server.execute(
            f"SELECT * FROM {self.name} WHERE {column} = '{value}';")
        values = self.server.cursor.fetchall()
        self.server.closeCursor()
        return values

    def query(self, query):
        self.server.execute(query)
        values = self.server.cursor.fetchall()
        self.server.closeCursor()
        return values

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

    def execute(self, query):
        self.server.execute(query)

    def commit(self):
        self.server.commit()

    def find_all(self, column):
        self.server.execute(
            f"SELECT {column} FROM {self.name};")
        values = self.server.cursor.fetchall()
        self.server.closeCursor()
        return [i[0] for i in values]


class Tijdblok(Table):
    def __init__(self):
        super().__init__("TimeBlock")
        self.dates = None
        self.days = None
        self.start_time = self.query('SELECT MIN(starttime) FROM TimeBlock;')[0][0]
        self.end_time = self.query('SELECT MAX(endtime) FROM TimeBlock;')[0][0]

    def get_day(self, date= None):
        if date is None:
            self.server.execute("SELECT * FROM TimeBlock;")
        else:
            self.server.execute(
                f"SELECT * FROM TimeBlock WHERE DATE(starttime) = '{date}';")
        value = list(self.server.cursor.fetchall())
        self.server.closeCursor()
        return value

    def get_today(self):
        return self.get_day(datetime.now().strftime("%Y-%m-%d"))

    def get_day_list(self):
        self.dates = []
        self.days = []
        self.server.execute(
            'SELECT DISTINCT DATE(starttime), '
            'DAYNAME(DATE(starttime)) '
            'FROM TimeBlock;'
        )
        for i in self.server.cursor.fetchall():
            self.days.append(i[1])
            self.dates.append(i[0])

    def get_start_time(self, timeblock):
        query = f'SELECT starttime from TimeBlock WHERE id = {timeblock};'
        return self.query(query)

    def get_end_time(self, timeblock):
        query = f'SELECT endtime from TimeBlock WHERE id = {timeblock};'
        return self.query(query)

class ShortTermSchedule(Table):
    def __init__(self, name):
        super().__init__(name)

    def get_schedule(self, name):
        bot_text = self.query(f"SELECT BotText FROM {self.name} WHERE Leader = '{name}'")
        entries = len(bot_text)
        if entries == 0:
            return "Geen rooster gevonden"
        elif entries == 1:
            return bot_text[0][0]
        else:
            output = ""
            for counter, i in enumerate(bot_text):
                output += i[0]
                if counter != entries - 1:
                    output += "\n----------------\n"
            return output

    def get_locations(self, name):
        locations = self.query(f"SELECT DISTINCT Location FROM {self.name} WHERE Leader = '{name}'")
        locationURLs = self.query(f"SELECT DISTINCT LocationURL FROM {self.name} WHERE Leader = '{name}'")
        return {i[0]: locationURLs[0][0] for i in locations}

