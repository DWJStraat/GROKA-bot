from main import *

Team = Table("Team", default_server)
Troop = Table("Troop", default_server)
Location = Table("Location", default_server)


class Schedules_now(ShortTermSchedule):
    def __init__(self):
        super().__init__("VwBotTextScheduleNow")


class Schedules_Next(ShortTermSchedule):
    def __init__(self):
        super().__init__("VwBotTextScheduleNext")


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


class Telegram(Table):
    def __init__(self):
        super().__init__("Telegram")

    def get_name(self, id):
        user_id = self.query(f'SELECT LeaderId FROM {self.name} WHERE telegramid = {id}')[0][0]
        return Leader().get_name(user_id)

    def get_id(self, name):
        try:
            user_id = Leader().get_id(name)
            return self.query(f'SELECT telegramid FROM {self.name} WHERE LeaderId = {user_id}')[0][0]
        except IndexError:
            return None

    def get_telegram(self, user_id):
        try:
            return self.query(f'SELECT telegramid FROM {self.name} WHERE LeaderId = {user_id}')[0][0]
        except IndexError:
            return None

    def set_name(self, telegram_id, naam):
        leader_id = int(Leader().get_id(naam))
        telegram_id = str(telegram_id)
        query = f"REPLACE INTO Telegram VALUES ({telegram_id}, {leader_id}, null)"
        self.execute(query)
        self.commit()

    def set_admin(self, telegram_id):
        query = f"UPDATE Telegram SET admin = 1 WHERE telegramid = {telegram_id}"
        self.execute(query)
        self.commit()

    def get_admin(self, telegram_id):
        query = f"SELECT admin FROM Telegram WHERE telegramid = {telegram_id}"
        return self.query(query)[0][0]


class Leader(Table):
    def __init__(self):
        super().__init__("Leader")

    def get_name(self, id = None):
        if id is not None:
            return self.query(f"SELECT name FROM {self.name} WHERE id = '{id}'")[0][0]
        result = self.query(f"SELECT name FROM {self.name}")
        for i in range(len(result)):
            result[i] = result[i][0]
        return result

    def get_id(self, name= None):
        if name is not None:
            return self.query(f"SELECT id FROM {self.name} WHERE name = '{name}'")[0][0]
        result = self.query(f"SELECT id FROM {self.name}")
        for i in range(len(result)):
            result[i] = result[i][0]
        return result
    def get_EHBO(self):
        EHBOers = self.query(f"SELECT id FROM {self.name} WHERE EHBO = 1")
        return [user[0] for user in EHBOers]


class Leiding(Table):
    def __init__(self, naam):
        super().__init__("Leader")
        self.naam = naam
        self.ik = self.retrieve(self.naam, "name")[0]
        self.id = self.ik[0]
        self.tijdblok = Tijdblok()

    def getCommissie(self):
        TeamId = self.find(self.id, "id", "TeamId")[0][0]
        return Team.find(TeamId, "id", "name")[0][0]

    def getTroop(self):
        TroopId = self.find(self.id, "id", "TroopId")[0][0]
        return Troop.find(TroopId, "Id", "Name")[0][0]

    def getPhone(self):
        phone_nr = self.find(self.id, "id", "phone_nr")[0][0]
        return "Geen telefoonnummer bekend" if phone_nr is None else phone_nr

    def getTelegram(self):
        try:
            return Telegram().get_id(self.naam)
        except AttributeError:
            return "Geen telegram account bekend"

    def get_EHBO(self):
        EHBO = self.find(self.id, "id", "EHBO")[0][0]
        return "Nee" if EHBO == 0 else "Ja"


class Speltak(Table):
    def __init__(self, name):
        super().__init__('Troop')
        self.speltak = name
        self.id = self.find(self.speltak, "Name", "Id")[0][0]

    def getLeiding(self):
        leidings = Leader().find(self.id, "TroopId", "name")
        return [i[0] for i in leidings]

    def getMembers(self):
        return self.find(self.id, "Id", "nYouthmembers")[0][0]


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
Availability().get_days()
