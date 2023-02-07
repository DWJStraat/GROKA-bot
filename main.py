import json
from datetime import datetime, timedelta

import mariadb

config = json.load(open("config.json"))



class Server:
    def __init__(self, config_path):
        config = json.load(open(config_path))
        self.host = config["host"]
        self.database = config["database"]
        self.user = config["user"]
        self.password = config["password"]
        self.port = config["port"]
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

    def execute(self, query):
        self.cursor.execute(query)

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()

default_server = Server("config.json")

class Table:
    def __init__(self, name, server_object=None):
        self.name = name
        self.server = server_object
        if self.server is None:
            self.server = default_server

    def retrieve(self, value, column):
        self.server.execute(
            f"SELECT * FROM {self.name} WHERE {column} = '{value}';")
        return self.server.cursor.fetchall()

    def query(self, query: object) -> object:
        self.server.execute(query)
        return self.server.cursor.fetchall()

    def find(self, value, column, return_column):
        self.server.execute(
            f"SELECT {return_column} FROM {self.name} WHERE {column} = '{value}';")
        return self.server.cursor.fetchall()

    def values(self):
        self.server.execute(f"SELECT * FROM {self.name};")
        return self.server.cursor.fetchall()


class Leiding:
    def __init__(self, naam, server_object=None):
        self.agenda_list = None
        self.start = None
        self.stop = None
        self.agenda = None
        self.naam = naam
        self.server = server_object
        if self.server is None:
            self.server = default_server
        self.ik = Table("User", self.server).retrieve(self.naam, "name")[0]
        self.id = self.ik[0]

        # self.commissie = Table("Team", self.server).retrieve(self.id, "id")[
        #     2]
        # self.speltak_lijst = Table("Speltakken", self.server)
        # self.speltak_id = None
        # self.speltak = None
        # self.getSpeltak()

    # def getSpeltak(self):
    #     for i in range(len(self.leiding.values)):
    #         if self.leiding.values[i][1] == self.naam:
    #             self.speltak_id = self.leiding.values[i][2]
    #             self.speltak = self.speltak_lijst.retrieve(self.speltak_id)

    # def load(self, column, table):
    #     table = Table(table, self.server)
    #     index = None
    #     for i in range(len(self.leiding.values)):
    #         if self.leiding.values[i][1] == self.naam:
    #             index = self.leiding.values[i][column]
    #     return table.find(index)

    def setDag(self, dag):
        dag = dag.lower()
        if dag == "donderdag":
            self.start = 1
            self.stop = 68
        elif dag == "vrijdag":
            self.start = 69
            self.stop = 138
        elif dag == "zaterdag":
            self.start = 139
            self.stop = 208
        elif dag == "zondag":
            self.start = 209
            self.stop = 250
        else:
            return False

    def getSchedule(self, setting=0):
        return schedule(self.id, self.server)

    def getCommissie(self):
        return Table("Team", self.server).find(self.id, "id", "name")[0][0]


# class Speltak:
#     def __init__(self, naam, server_object=None):
#         self.naam = naam
#         self.server = server_object
#         if self.server is None:
#             self.server = default_server
#         self.speltak = Table("Speltakken", self.server)
#         self.id = self.getID()
#         # self.leiding = self.getLeiding()
#
#     def getID(self):
#         self.speltak.retrieve(self.naam, "name")
#
#     # def getLeiding(self):
#     #     Leiding = Table("Leiding", self.server)
#     #     return [
#     #         Leiding.values[i][1]
#     #         for i in range(len(Leiding.values))
#     #         if Leiding.values[i][2] == self.id
#     #     ]
#
#     # def returnLeiding(self):
#     #     leiding_list = ''
#     #     for i in range(len(self.leiding)):
#     #         if not leiding_list:
#     #             leiding_list = (self.leiding[i])
#     #         else:
#     #             leiding_list += f', {self.leiding[i]}'
#     #     return leiding_list
#
#     def getSchedule(self):
#         entry = []
#         SpelKinderen = Table("SpelKinderen", self.server)
#         Taken = Table("Taken", self.server)
#         Taken_List = [
#             i[0]
#             for i in SpelKinderen.values
#             if i[2] == self.id
#         ]
#         Agenda = []
#         for i in Taken_List:
#             for j in Taken.values:
#                 if i == j[0]:
#                     start_time = datetime.strptime(j[2], "%H:%M").time()
#                     end_time = datetime.strptime(j[3], "%H:%M").time()
#                     entry = [start_time, end_time, j[1], j[0], '\t']
#             for j in SpelKinderen.values:
#                 if i == j[0]:
#                     naam = self.leiding.find(j[1])
#                     if entry[4] == '\t':
#                         entry[4] = f'{naam}'
#                     else:
#                         entry[4] += f', {naam}'
#             Agenda.append(entry)


def schedule_option(planning, reference, taak):
    entry = ''
    for j in planning.values:
        if taak == j[0]:
            naam = reference.find(j[1])
            if entry == '':
                entry = f'met {naam}'
            else:
                entry += f', {naam}'
    return entry


def schedule(id, server=default_server):
    print(id)
    schedule = Table("Schedule", server)
    query = f'SELECT DISTINCT jobId FROM Schedule WHERE userid = {id}'
    Taken_List = list(schedule.query(query))
    for i in Taken_List:
        Taken_List[Taken_List.index(i)] = jobBuilder(i[0], server)
    query = f'SELECT COUNT( DISTINCT jobId ) FROM Schedule WHERE userid = {id}'
    Taken_count = schedule.query(query)
    print(Taken_count)
    if Taken_count[0][0] > 1:
        schedule = schedule_builder_2d_list(Taken_List)
        return [
            f'Taak: {i[0]} (Activiteit: {i[1]}) {i[2]} - {i[3]}, locatie: {i[4]}'
            for i in schedule
        ]
    else:
        schedule = schedule_builder_list(Taken_List)
        return f'Taak: {schedule[0]} (Activiteit: {schedule[1]}) ' \
               f'{schedule[2]} - {schedule[3]}, locatie: {schedule[4]}'

def schedule_builder_2d_list(taken_list):
        '''
        This function takes a list of jobs and returns the schedule in list format

        :param taken_list: list of jobs

        :return: list containing schedule
        '''
        agenda = []
        print(taken_list)
        for i in taken_list:
            print(i)
            entry = [i[1], i[2]]
            start_day, start_time = timeConverter(i[3])
            entry.append(f'{start_day} {start_time}')
            stop_day, stop_time = timeConverter(i[4])
            entry.extend((f'{stop_time}', i[5]))
            agenda.append(entry)
        return agenda

def schedule_builder_list(taken_list):
    '''
    This function takes a list of jobs and returns the schedule in list format

    :param taken_list: list of jobs

    :return: list containing schedule
    '''
    try:
        entry = [taken_list[1], taken_list[2]]
    except IndexError:
        raise Exception('No schedule found')
    start_day, start_time = timeConverter(taken_list[3])
    entry.append(f'{start_day} {start_time}')
    stop_day, stop_time = timeConverter(taken_list[4])
    entry.extend((f'{stop_time}', taken_list[5]))
    return entry

def BlockToTime(time, start):
    """
    This function converts a timeblock to a time

    :param time: timeblock
    :param start: True if you want the start time, False if you want the end time

    :return: time in string format
    """
    TimeBlock = Table("TimeBlock", default_server)
    returnvalue = 'starttime' if start else 'endtime'
    return TimeBlock.find(time, "id", returnvalue)[0]

def timeConverter(time):
    days = {
        0: "Maandag",
        1: "Dinsdag",
        2: "Woensdag",
        3: "Donderdag",
        4: "Vrijdag",
        5: "Zaterdag",
        6: "Zondag"
    }
    day = days[time.weekday()]
    return day, time.strftime("%H:%M")

def jobBuilder(jobID, server):
    """
    This function builds a job from a jobID

    :param jobID: ID of the job
    :param server: server to connect to

    :return: job name, activity name, location, start time, stop time
    """
    job_name = Table("Job", server).retrieve(jobID, "id")[0][1]
    activityID = Table("Job", server).retrieve(jobID, "id")[0][2]
    activity_name = Table("Activity", server).retrieve(activityID, "id")[0][1]
    locationID = Table("Activity", server).retrieve(activityID, "id")[0][5]
    startTimeBlock = Table("Schedule", server).find(activityID, "id",
                                                    'timeBlockStart')[0][0]
    stopTimeBlock = Table("Schedule", server).find(activityID, "id",
                                                   'timeBlockEnd')[0][0]
    start_time = BlockToTime(startTimeBlock, True)
    stop_time = BlockToTime(stopTimeBlock, False)
    location = Table("Location", server).retrieve(locationID, "id")[0][1]

    return [startTimeBlock, job_name, activity_name, start_time[0], stop_time[0], location]

def timeToBlock(time):
    """
    This function converts a time to a timeblock

    :param time: time in string format

    :return: timeblock
    """
    TimeBlock = Table("TimeBlock", default_server)
    timeRounded = time + (datetime.min - time) % (timedelta(minutes=15))
    return TimeBlock.find(timeRounded, "endtime", "id")[0][0]