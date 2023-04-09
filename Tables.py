from main import *

Location = Table("Location", default_server)



class Telegram(Table):
    def __init__(self):
        super().__init__("Telegram")

    def get_name(self, id):
        user_id = self.query(f'SELECT LeaderId FROM {self.name} WHERE telegramid = {id}')[0][0]
        return Leader_Table().get_name(user_id)

    def get_id(self, name):
        try:
            user_id = Leader_Table().get_id(name)
            ids = self.query(f'SELECT telegramid FROM {self.name} WHERE LeaderId = {user_id}')
            output = [i[0] for i in ids]
            return output
        except IndexError:
            return None

    def get_telegram(self, user_id):
        try:
            return self.query(f'SELECT telegramid FROM {self.name} WHERE LeaderId = {user_id}')[0][0]
        except IndexError:
            return None

    def set_name(self, telegram_id, naam):
        leader_id = int(Leader_Table().get_id(naam))
        telegram_id = str(telegram_id)
        query = f"REPLACE INTO Telegram VALUES ({telegram_id}, {leader_id}, null)"
        self.execute(query, commit=True)

    def set_admin(self, telegram_id):
        query = f"UPDATE Telegram SET admin = 1 WHERE telegramid = {telegram_id}"
        self.execute(query, commit= True)
    def get_admin(self, telegram_id):
        query = f"SELECT admin FROM Telegram WHERE telegramid = {telegram_id}"
        return self.query(query)[0][0]





class Problems(Table):
    def __init__(self):
        super().__init__("VwProblems")

    def get_problems(self):
        problems = self.query(f"SELECT problem from {self.name}")
        output = ""
        for problem in problems:
            output += problem[0]
            if problem != problems[-1]:
                output += "\n"
        return output


class Availability(Table):
    def __init__(self):
        super().__init__("VwAvailability")

    def get_days(self):
        days = self.query(f"SELECT day from {self.name}")
        output = ""
        for day in days:
            output += day[0]
            if day != days[-1]:
                output += "\n"
        return output


class Team(Table):
    def __init__(self):
        super().__init__("Team")


class Leader_Table(Table):
    def __init__(self):
        super().__init__("Leader")

    def get_name(self, id=None):
        if id is not None:
            return self.query(f"SELECT name FROM {self.name} WHERE id = '{id}'")[0][0]
        result = self.query(f"SELECT name FROM {self.name}")
        for i in range(len(result)):
            result[i] = result[i][0]
        return result

    def get_id(self, name=None):
        if name is not None:
            try:
                return self.execute(f"SELECT id FROM {self.name} WHERE name = '{name}'")[0][0]
            except IndexError:
                print("Invalid Error")
                return None
        result = self.query(f"SELECT id FROM {self.name}")
        for i in range(len(result)):
            result[i] = result[i][0]
        return result

    def get_EHBO(self):
        EHBOers = self.query(f"SELECT id FROM {self.name} WHERE EHBO_team = 1")
        return [user[0] for user in EHBOers]

    def get_admin(self):
        admins = self.query(f"SELECT id FROM {self.name} WHERE admin = 1")
        return [user[0] for user in admins]

    def check_name(self, name):
        name = self.query(f"SELECT name FROM {self.name} WHERE name = '{name}'")
        return len(name) == 1


class Leiding(Table):
    def __init__(self, naam):
        super().__init__("Leader")
        self.naam = naam
        self.ik = self.retrieve(self.naam, "name")[0]
        self.id = self.ik[0]
        self.tijdblok = Tijdblok()

    def getCommissie(self):
        TeamId = self.find(self.id, "id", "TeamId")[0][0]
        return Team().find(TeamId, "id", "name")[0][0]

    def getTroop(self):
        TroopId = self.execute(f"SELECT TroopId FROM Leader WHERE id = {self.id}")[0][0]
        speltak = self.execute(f"SELECT Name FROM Troop WHERE id = {TroopId}")[0][0]
        return speltak

    def getPhone(self):
        phone_nr = self.find(self.id, "id", "phone_nr")[0][0]
        return "Geen telefoonnummer bekend" if phone_nr is None else phone_nr

    def getTelegram(self):
        try:
            return Telegram().get_id(self.naam)
        except AttributeError:
            return "Geen telegram account bekend"
        except IndexError:
            return None

    def get_EHBO(self):
        EHBO = self.find(self.id, "id", "EHBO")[0][0]
        return "Nee" if EHBO == 0 else "Ja"

    def get_schedule(self):
        results = Schedule().query(f'SELECT * FROM VwScheduleNames WHERE Leaders = "{self.naam}"')



class Speltak(Table):
    def __init__(self, name= None):
        super().__init__('Troop')
        self.speltak = name
        self.id = self.find(self.speltak, "Name", "Id")

    def getLeiding(self):
        leidings = Leader_Table().find(self.id, "TroopId", "name")
        return [i[0] for i in leidings]

    def getMembers(self):
        return self.find(self.id, "Id", "nYouthmembers")[0][0]


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


class Schedules_now(ShortTermSchedule):
    def __init__(self):
        super().__init__("VwBotTextScheduleNow")


class Schedules_Next(ShortTermSchedule):
    def __init__(self):
        super().__init__("VwBotTextScheduleNext")


class Schedule(Table):
    def __init__(self):
        super().__init__("VwScheduleNames")

class Schedules_tomorrow(Table):
    def __init__(self):
        super().__init__("VwBotTextScheduleTomorrow")

    def get_schedule(self, name):
        bot_text = self.query(f"SELECT BotText FROM {self.name} WHERE Leader = '{name}'")
        entries = len(bot_text)
        if entries == 0:
            return "Geen rooster gevonden"
        elif entries == 1:
            return bot_text[0][0]


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



    def get_locations(self, name):
        locations = self.query(f"SELECT DISTINCT Location FROM {self.name} WHERE Leader = '{name}'")
        locationURLs = self.query(f"SELECT DISTINCT LocationURL FROM {self.name} WHERE Leader = '{name}'")
        return {i[0]: locationURLs[0][0] for i in locations}


class Schedules_today(Table):
    def __init__(self):
        super().__init__("VwBotTextScheduleToday")

    def get_schedule(self, name):
        bot_text = self.query(f"SELECT BotText FROM {self.name} WHERE Leader = '{name}'")
        entries = len(bot_text)
        if entries == 0:
            return "Geen rooster gevonden"
        elif entries == 1:
            return bot_text[0][0]

def TroopInfo(name):
    table = Table('VwBotTextTroopInfo')
    contents = table.query(f"SELECT BotText FROM VwBotTextTroopInfo WHERE Troop = '{name}' ORDER BY OrderBy")
    output_list = [i[0] for i in contents]
    return "\n".join(output_list)

