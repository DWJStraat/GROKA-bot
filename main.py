from datetime import datetime

import pyodbc

default_server = pyodbc.connect(
    "Driver={SQL Server Native Client 11.0};"
    "Server=localhost;"
    "Database=master;"
    "Trusted_Connection=yes;"
)


class Table:
    def __init__(self, name, server_object=None):
        self.name = name
        self.server = server_object
        if self.server is None:
            self.server = default_server
        self.cursor = self.server.cursor()
        self.values = self.get()

    def get(self):
        self.cursor.execute(f"SELECT * FROM {self.name}")
        return self.cursor.fetchall()

    def find(self, index):
        for i in range(len(self.values)):
            if self.values[i][0] == index:
                return self.values[i][1]


class Leiding:
    def __init__(self, naam, server_object=None):
        self.agenda_list = None
        self.dag_id = None
        self.dag = None
        self.agenda = None
        self.naam = naam
        self.server = server_object
        if self.server is None:
            self.server = default_server
        self.leiding = Table("Leiding", self.server)
        self.id = self.getID()
        self.Commissie = self.load(3, "Comissie")
        self.speltak_lijst = Table("Speltakken", self.server)
        self.speltak_id = None
        self.speltak = None
        self.getSpeltak()

    def getSpeltak(self):
        for i in range(len(self.leiding.values)):
            if self.leiding.values[i][1] == self.naam:
                self.speltak_id = self.leiding.values[i][2]
                self.speltak = Table("Speltakken", self.server).find(
                    self.speltak_id)

    def getNaam(self):
        return self.naam

    def getID(self):
        for i in range(len(self.leiding.values)):
            if self.leiding.values[i][1] == self.naam:
                return self.leiding.values[i][0]

    def load(self, column, table):
        table = Table(table, self.server)
        index = None
        for i in range(len(self.leiding.values)):
            if self.leiding.values[i][1] == self.naam:
                index = self.leiding.values[i][column]
        return table.find(index)

    def setDag(self, dag):
        dag = dag.lower()
        self.dag = dag
        dag_table = Table("Dagen", self.server)
        on_list = False
        for i in range(len(dag_table.values)):
            if dag_table.values[i][1] == dag:
                self.dag_id = dag_table.values[i][0]
                on_list = True
        if not on_list:
            print('ERROR, dag niet gevonden')

    def getSchedule(self, setting=0):
        return schedule(setting, self.server, self.dag_id,
                        self.id, True)


class Speltak:
    def __init__(self, naam, server_object=None):
        self.naam = naam
        self.server = server_object
        if self.server is None:
            self.server = default_server
        self.speltak = Table("Speltakken", self.server)
        self.id = self.getID()
        self.leiding = self.getLeiding()

    def getID(self):
        for i in range(len(self.speltak.values)):
            if self.speltak.values[i][1] == self.naam:
                return self.speltak.values[i][0]

    def getLeiding(self):
        Leiding = Table("Leiding", self.server)
        return [
            Leiding.values[i][1]
            for i in range(len(Leiding.values))
            if Leiding.values[i][2] == self.id
        ]

    def returnLeiding(self):
        leiding_list = ''
        for i in range(len(self.leiding)):
            if not leiding_list:
                leiding_list = (self.leiding[i])
            else:
                leiding_list += f', {self.leiding[i]}'
        return leiding_list

    def getSchedule(self):
        entry = []
        SpelKinderen = Table("SpelKinderen", self.server)
        Taken = Table("Taken", self.server)
        Taken_List = [
            i[0]
            for i in SpelKinderen.values
            if i[2] == self.id
        ]
        Agenda = []
        for i in Taken_List:
            for j in Taken.values:
                if i == j[0]:
                    start_time = datetime.strptime(j[2], "%H:%M").time()
                    end_time = datetime.strptime(j[3], "%H:%M").time()
                    entry = [start_time, end_time, j[1], j[0], '\t']
            for j in SpelKinderen.values:
                if i == j[0]:
                    naam = self.leiding.find(j[1])
                    if entry[4] == '\t':
                        entry[4] = f'{naam}'
                    else:
                        entry[4] += f', {naam}'
            Agenda.append(entry)

def schedule_option(planning, reference, taak):
    entry = ''
    for j in planning.values:
        if taak == j[0]:
            naam = reference.find(j[1])
            if entry == '':
                entry= f'met {naam}'
            else:
                entry += f', {naam}'
    return entry

def agenda_builder(server, Taken_List, Taken, kinderen, leiding, setting):
    Agenda = []
    entry = []
    TakenLeiding = Table("TakenLeiding", server)
    SpelKinderen = Table("SpelKinderen", server)
    for taak in Taken_List:
        for j in Taken.values:
            if taak == j[0]:
                start_time = datetime.strptime(j[2], "%H:%M").time()
                end_time = datetime.strptime(j[3], "%H:%M").time()
                speltakken = ''
                leidinglijst = ''
                if kinderen:
                    speltakken = schedule_option(SpelKinderen, Table("Speltakken", server), taak)
                    if speltakken == '-1':
                        speltakken = 'voor alle kinderen'
                    if setting == 4:
                        speltakken = f'en {speltakken}'
                if leiding:
                    leidinglijst = schedule_option(TakenLeiding, Table("Leiding", server), taak)
                    if leiding == '-1':
                        leiding = 'voor alle leiding'
                entry = [start_time, end_time, j[1], j[0], leidinglijst, speltakken]
        Agenda.append(entry)
    Agenda.sort()
    return Agenda

def schedule(setting=0, server=default_server, dag_id=0, id=0,
             leidingrooster=False):
    leiding = setting in [1, 4]
    kinderen = setting in [2, 4]

    Taken = Table("Taken", server)
    if leidingrooster:
        main_rooster = Table("Takenleiding", server)
    else:
        main_rooster = Table("SpelKinderen", server)
    Taken_List = [
        i[0]
        for i in main_rooster.values
        if i[2] == dag_id and i[1] == id
    ]
    Agenda = agenda_builder(server, Taken_List, Taken, kinderen, leiding, setting)
    for i in range(len(Agenda)):
        Agenda[
            i] = f'{str(Agenda[i][0])[:-3]} - {str(Agenda[i][1])[:-3]}: {Agenda[i][2]} ' \
                 f'{Agenda[i][4]} {Agenda[i][5]}'
    return '\n'.join(Agenda)



def main():
    Welp = Speltak("Gidoerlog")
    print(f'Naam: \t\t{Welp.naam}')
    print(f'Leiding: \t{Welp.returnLeiding()}')


main()
