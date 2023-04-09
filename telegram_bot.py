import contextlib
import datetime
import random
import sys

import regex as re
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from Tables import *

config = json.load(open("config.json"))

bot = telebot.TeleBot(config['telegram_token'])

schedule = Schedules_today()


@bot.message_handler(commands=['start', 'help'])
def start(message):
    message_handler(message.chat.id,
                     "Hallo, ik ben de rooster bot van de scouting voor "
                     "GROKA 2023. "
                     "\nDoe als eerste /aanmelden; pas als je aangemeld "
                     "ben kan je bij alle functies IVM privacy."
                     "\n"
                     "\nStuur /aanmelden om je te registreren. Hiervoor"
                     "heb je een wachtwoord nodig."
                     "\n"
                     "\nStuur /roosterhelp om hulp te krijgen met het "
                     "rooster."
                     "\nStuur /infohelp om hulp te krijgen met het "
                     "bekijken van profielen en speltakken"
                     "\n"
                     "\nStuur /help of /start om dit bericht opnieuw te zien."
                     "\n"
                     "\nDeze bot is geschreven door David Straat (Mang van de "
                     "Gidoerlog) voor het groepskamp van 2023. Voor vragen of "
                     "opmerkingen kan je contact met mij opnemen d.m.v. "
                     "/feedback."
                     )


@bot.message_handler(commands=['roosterhelp'])
def roosterhelp(message):
    message_handler(message.chat.id,
                     "Stuur /mijnnu om je rooster van nu op te vragen."
                     "\nStuur /mijnvandaag om je rooster van vandaag op te "
                     "vragen."
                     "\nStuur /mijnmorgen om je rooster van morgen op te "
                     "vragen."
                     "\n"
                     "\nStuur /nu om het rooster van een andere leiding op "
                     "te vragen."
                     "\nStuur /vandaag om het rooster van een andere leiding "
                     "op te vragen."
                     "\nStuur /morgen om het rooster van een andere leiding "
                     "op te vragen."
                     "\nDeze bot is geschreven door David Straat (Mang van de "
                     "Gidoerlog) voor het groepskamp van 2023. Voor vragen of "
                     "opmerkingen kan je contact met mij opnemen d.m.v. "
                     "/feedback."
                     )


@bot.message_handler(commands=['infohelp'])
def infohelp(message):
    message_handler(message.chat.id,
                     "Stuur /overmij om je profiel te bekijken."
                     "\nStuur /over om het profiel van iemand anders te "
                     "bekijken."
                     "\nStuur /mijnspeltak om je speltak te bekijken."
                     "\nStuur /speltak om een andere spelak te bekijken. "
                     "\nDeze bot is geschreven door David Straat (Mang van de "
                     "Gidoerlog) voor het groepskamp van 2023. Voor vragen of "
                     "opmerkingen kan je contact met mij opnemen d.m.v. "
                     "/feedback."
                     )


@bot.message_handler(commands=['aanmelden'])
def password(message):
    message_handler(message.chat.id, "Voer het wachtwoord in.")
    bot.register_next_step_handler(message, password2)


def password2(message):
    enteredpassword = str(message.text)
    correctpassword = config['bot_password']
    if enteredpassword == correctpassword:
        register(message)
    else:
        message_handler(message.chat.id, "Het wachtwoord is onjuist. Voer het commando opnieuw in of vraag hulp"
                                          "aan het planning team.")


def register(message):
    message_handler(message.chat.id,
                     "Hallo leidings, wat is je naam?")
    bot.register_next_step_handler(message, register2)


def register2(message):
    naam = str(message.text)
    logger(message, 'aanmelden', naam)
    try:
        try:
            naam_sql = Leader_Table().get_id(naam)
        except mariadb.Error:
            naam_sql = None
        if naam_sql is not None:
            telegram_id = str(message.from_user.id)
            Telegram_table = Telegram()
            Telegram_table.set_name(telegram_id, naam)
            message_handler(message.chat.id, f"Je bent geregistreerd! Welkom, {naam}")
        else:
            message_handler(message.chat.id, "Je naam is niet gevonden in de "
                                              "database, probeer het opnieuw.")
    except Exception as e:
        error_handler(e, message, command='aanmelden')


@bot.message_handler(commands=['overmij'])
def about_me(message):
    try:
        if register_check(message):
            telegram_user = message.from_user.id
            try:
                naam = Telegram().get_name(telegram_user)
                print(naam)
                profile(naam, message)
            except mariadb.Error:
                message_handler(message.chat.id, "Je bent nog niet geregistreerd, stuur /aanmelden om "
                                                  "je te registreren.")
    except Exception as e:
        error_handler(e, message, command='overmij')


@bot.message_handler(commands=['over'])
def about(message):
    if register_check(message):
        message_handler(message.chat.id, 'Over wie wil je informatie?')
        bot.register_next_step_handler(message, about2)


def about2(message):
    try:
        naam = message.text
        logger(message, 'over', naam)
        try:
            profile(naam, message)
        except IndexError:
            message_handler(message.chat.id, "Deze persoon is niet gevonden in de "
                                              "database, probeer het opnieuw.")
    except Exception as e:
        error_handler(e, message, command='over')


@bot.message_handler(commands=['mijnnu'])
def mynow(message):
    try:
        if register_check(message):
            telegram_id = message.from_user.id
            naam = Telegram().get_name(telegram_id)
            message_handler(message.chat.id, Schedules_now().get_schedule(naam))
    except Exception as e:
        error_handler(e, message, command='mijnnu')


# Rooster commands

@bot.message_handler(commands=['nu'])
def now(message):
    if register_check(message):
        message_handler(message.chat.id, "Over wie wil je het nu rooster zien?")
        bot.register_next_step_handler(message, now2)


def now2(message):
    try:
        naam = message.text
        logger(message, 'nu', naam)
        message_handler(message.chat.id, Schedules_now().get_schedule(naam))
    except Exception as e:
        error_handler(e, message, command='nu')


@bot.message_handler(commands=['mijnstraks'])
def mysoon(message):
    try:
        if register_check(message):
            telegram_id = message.from_user.id
            naam = Telegram().get_name(telegram_id)
            bot.message_handler(message.chat.id, Schedules_Next().get_schedule(naam))
    except Exception as e:
        error_handler(e, message, command='mijnstraks')


@bot.message_handler(commands=['straks'])
def soon(message):
    if register_check(message):
        message_handler(message.chat.id, "Over wie wil je het straks rooster zien?")
        bot.register_next_step_handler(message, soon2)


def soon2(message):
    try:
        logger(message, 'straks', message.text)
        if register_check(message):
            naam = message.text
            message_handler(message.chat.id, Schedules_Next().get_schedule(naam))
    except Exception as e:
        error_handler(e, message, command='straks')


@bot.message_handler(commands=['mijnrooster', 'mijnvandaag'])
def myrooster(message):
    try:
        if register_check(message):
            telegram_id = message.from_user.id
            naam = Telegram().get_name(telegram_id)
            message_handler(message.chat.id, Schedules_today().get_schedule(naam))
    except Exception as e:
        error_handler(e, message, command='mijnrooster')


@bot.message_handler(commands=['rooster', 'vandaag'])
def rooster(message):
    if register_check(message):
        message_handler(message.chat.id, "Over wie wil je het rooster zien?")
        bot.register_next_step_handler(message, rooster2)


def rooster2(message):
    try:
        naam = message.text
        message_handler(message.chat.id, Schedules_today().get_schedule(naam))
    except Exception as e:
        error_handler(e, message, command='rooster')


@bot.message_handler(commands=['mijnmorgen'])
def mymorgen(message):
    try:
        if register_check(message):
            telegram_id = message.from_user.id
            naam = Telegram().get_name(telegram_id)
            message_handler(message.chat.id, Schedules_tomorrow().get_schedule(naam))
    except Exception as e:
        error_handler(e, message, command='mijnmorgen')


@bot.message_handler(commands=['morgen'])
def morgen(message):
    if register_check(message):
        message_handler(message.chat.id, "Over wie wil je het morgen rooster zien?")
        bot.register_next_step_handler(message, morgen2)


def morgen2(message):
    try:
        naam = message.text
        message_handler(message.chat.id, Schedules_tomorrow().get_schedule(naam))
    except Exception as e:
        error_handler(e, message, command='morgen')


# Info commands

@bot.message_handler(commands=['mijnspeltak'])
def myspeltak(message):
    try:
        if not register_check(message):
            return
        telegram_id = message.from_user.id
        try:
            naam = Telegram().get_name(telegram_id)
            troopname = Leiding(naam).getTroop()
            output = TroopInfo(troopname)
            message_handler(message.chat.id, output)
        except mariadb.Error:
            message_handler(message.chat.id, "Je bent nog niet geregistreerd, stuur /aanmelden om "
                                              "je te registreren.")
    except Exception as e:
        error_handler(e, message, command='mijnspeltak')


@bot.message_handler(commands=['speltak'])
def speltak(message):
    if register_check(message):
        message_handler(message.chat.id, "Over welke speltak wil je informatie?")
        bot.register_next_step_handler(message, speltak2)


def speltak2(message):
    try:
        troopname = message.text
        try:
            output = TroopInfo(troopname)
            try:
                message_handler(message.chat.id, output)
            except Exception:
                message_handler(message.chat.id, "Deze speltak is niet gevonden")
        except mariadb.Error:
            message_handler(message.chat.id, "Deze speltak is niet gevonden in de database.")
    except Exception as e:
        error_handler(e, message, command='speltak')


@bot.message_handler(commands=['feedback'])
def feedback(message):
    message_handler(message.chat.id, "Bedankt dat je feedback wilt geven! Stuur een bericht naar "
                                      "[David Straat](tg://user?id=2059520607)",
                     parse_mode="Markdown")


# Noodgeval functies
@bot.message_handler(commands=['SOS','sos'])
def EHBOmsg(message):
    if register_check(message):
        message_handler(message.chat.id, "Wat is de boodschap? Geef hierin door waar je bent en wat er is gebeurd.")
        bot.register_next_step_handler(message, EHBOmsg2)


def EHBOmsg2(message):
    try:
        logger(message, "EHBO", message.text)
        EHBOinput = message.text
        telegram_id = message.from_user.id
        EHBOmessage = f"[EHBO]\n" \
                      f"[{Telegram().get_name(telegram_id)}](tg://user?id={telegram_id}) " \
                      f"heeft het volgende bericht gestuurd: \n" \
                      f"{EHBOinput}"
        EHBO_id = Leader_Table().get_EHBO()
        EHBO_names = [Leader_Table().get_name(i) for i in EHBO_id]
        EHBO_telegram = [Leiding(i).getTelegram() for i in EHBO_names]
        mass_message(EHBOmessage, admin = True, EHBO  = True)
        EHBO_name_string = ", ".join(EHBO_names)
        message_handler(message.chat.id, f"De EHBO-ers zijn {EHBO_name_string} en hebben een bericht gekregen.")
    except Exception as e:
        error_handler(e, message, command='SOS')


@bot.message_handler(commands=['EHBOers'])
def EHBOers(message):
    try:
        if not register_check(message):
            return
        EHBO_id = Leader_Table().get_EHBO()
        EHBO_names = [Leader_Table().get_name(i) for i in EHBO_id]
        EHBO_telegram = [Leiding(i).getTelegram() for i in EHBO_names]
        EHBO_list = []
        for i, n in enumerate(EHBO_names):
            telegram = EHBO_telegram[i]
            name = n
            if telegram is not None:
                EHBO_list.append(f"[{name}](tg://user?id={telegram})\n")
            else:
                EHBO_list.append(f"{name}\n")
        EHBO_list = "".join(EHBO_list)
        print(EHBO_list)
        message_handler(message.chat.id, f"De EHBO-ers zijn:\n{EHBO_list}", parse_mode="Markdown")
    except Exception as e:
        error_handler(e, message, command='EHBOers')

@bot.message_handler(commands=['leiding'])
def leiding(message):
    try:
        if not register_check(message):
            return
        query = "SELECT DISTINCT Bottext FROM VwBotTextLeaderInfo WHERE OrderBy = 1 ORDER BY Bottext"
        leaders = Leader_Table().execute(query)
        leader_list = [f"{leader[0]}\n" for leader in leaders]
        leader_list = "".join(leader_list)
        message_handler(message,f"De leiding is:\n=========\n{leader_list}")
    except Exception as e:
        error_handler(e, message, command='leiding')

# Admin commands

@bot.message_handler(commands=['/admin'])
def admin(message):
    if register_check(message):
        message_handler(message.chat.id, "Wat is het wachtwoord?")
        bot.register_next_step_handler(message, admin2)


def admin2(message):
    try:
        if message.text == config['bot_password_admin']:
            message_handler(message.chat.id, "Je bent nu ingelogd als admin.")
            Telegram().set_admin(message.from_user.id)
        else:
            message_handler(message.chat.id, "Het wachtwoord is onjuist.")
    except Exception as e:
        error_handler(e, message)


@bot.message_handler(commands=['/help'])
def admin_help(message):
    if Telegram().get_admin(message.from_user.id):
        message_handler(message.chat.id, "De volgende commando's zijn beschikbaar voor admins:\n"
                                          "//admin - Log in als admin\n"
                                          "//help - Toon deze lijst\n"
                                          "//announce - Stuur een bericht naar alle leden\n"
                                          "//test - Test of je admin bent\n"
                                          "//problems - Toon de problemen in de planning\n"
                         )


@bot.message_handler(commands=['/announce'])
def announce(message):
    if Telegram().get_admin(message.from_user.id):
        message_handler(message.chat.id, "Wat is de boodschap?")
        bot.register_next_step_handler(message, announce2)


def announce2(message):
    try:
        if Telegram().get_admin(message.from_user.id):
            message_handler(message.chat.id, "De boodschap is verzonden.")
            announcement = message.text
            user_id = message.from_user.id
            naam = Telegram().get_name(user_id)
            for i in Telegram().find_all('telegramid'):
                print(i)
                message_handler(i, f'Massabericht van [{naam}](tg://user?id={user_id}):', parse_mode='Markdown')
                message_handler(i, announcement)
    except Exception as e:
        error_handler(e, message)


@bot.message_handler(commands=['/test'])
def admin_test(message):
    if Telegram().get_admin(message.from_user.id):
        message_handler(message.chat.id, "Je bent ingelogd als admin.")


@bot.message_handler(commands=['/problems'])
def problems(message):
    if Telegram().get_admin(message.from_user.id):
        problems = Problems().get_problems()
        message_handler(message, problems)


@bot.message_handler(commands=['/schedule'])
def schedule(message):
    if Telegram().get_admin(message.from_user.id):
        message_handler(message.chat.id, "Van wie wil je het rooster inzien?")
        bot.register_next_step_handler(message, schedule2)


def schedule2(message):
    try:
        if Telegram().get_admin(message.from_user.id):
            name = message.text
            if Leader_Table().check_name(name):
                message_handler(message.chat.id, Leader_Table().get_schedule(name))
            else:
                message_handler(message.chat.id, "Deze naam is niet gevonden.")
    except Exception as e:
        error_handler(e, message)


@bot.message_handler(commands=['/backup'])
def backup(message):
    if Telegram().get_admin(message.from_user.id):
        try:
            default_server.execute("""INSERT INTO BU_Job (id, name, ActivityId, description, nLeaders, timestamp)
                SELECT t.id, t.name, t.ActivityId, t.description, t.nLeaders, NOW()
                FROM Job t;""")
            default_server.execute("INSERT INTO BU_Schedule (id, LeaderId, jobId, StartTimeBlockId, EndTimeBlockId, \n"
                                   "Required, timestamp)\n"
                                   "SELECT t.id, t.LeaderId, t.jobId, t.StartTimeBlockId, t.EndTimeBlockId, t.Required, NOW()\n"
                                   "FROM Schedule t;")
            logger(message, "Backup")
            message_handler(message.chat.id, "Backup gemaakt.")
        except Exception as e:
            error_handler(e, message)

# Debug commands

@bot.message_handler(commands=['error'])
# This version of the error doesn't log the error and thus doesn't send a message to everyone with Admin
def throw_error(message):
    message_handler(message.chat.id, "Dit is een testbericht voor de error-handler. (Dit is geen echte error.)\n "
                                      "Neem geen contact op met de ontwikkelaars.")
    string = ''
    try:
        string[1]
    except Exception as e:
        error_handler(e, message, do_not_log=True)

@bot.message_handler(commands=['/error'])
# This version of the error does log the error and thus sends a message to everyone with Admin
def admin_error(message):
    if Telegram().get_admin(message.from_user.id):
        message_handler(message.chat.id, "Dit is een testbericht voor de error-handler. (Dit is geen echte error.)\n "
                                          "Neem geen contact op met de ontwikkelaars.")
        string = ''
        try:
            string[1]
        except Exception as e:
            error_handler(e, message)

# Easter eggs

@bot.message_handler(commands=["haarlijn_jorik"])
def haarlijn(message):
    error_handler("ERROR 404:\nHairline not found", message, do_not_log=True)


@bot.message_handler(commands=["pingelen"])
def pingelen(message):
    message_handler(message.chat.id,
                     "Welkom bij Commando Pingelen. Als je een commando krijgt, volg het commando. Zo niet,"
                     "doe '...'")
    pingelen2(message)


def pingelen2(message):
    pingelen = [
        "Commando pingelen",
        "Commando bol",
        "Commando plat",
        "Commando hol"
        "Pingelen",
        "Bol",
        "Plat",
        "Hol"
    ]
    commando = random.choice(pingelen)
    message_handler(message.chat.id, commando)
    bot.register_next_step_handler(message, pingelen3, commando)


def pingelen3(message, commando):
    if commando == "Commando pingelen":
        output = "Pingelen"
    elif commando == "Commando bol":
        output = "Bol"
    elif commando == "Commando plat":
        output = "Plat"
    elif commando == "Commando hol":
        output = "Hol"
    else:
        output = "..."
    if message.text == output:
        message_handler(message.chat.id, "Goed gedaan!")
        pingelen(message)
    else:
        message_handler(message.chat.id, "Helaas, probeer het nog eens.")


@bot.message_handler(commands=["stress"])
def stress(message):
    message_handler(message.chat.id, "https://www.youtube.com/watch?v=logaMSPVV-E")


# Algemene functies

def profile(naam, message):
    try:
        User = Leiding(naam)
        telegrams = User.getTelegram()
        print(len(telegrams))
        if len(telegrams) > 1:
            print('multi')
            telegram_list = "".join(
                f"[{int(i)}](tg://user?id={int(i)})\n" for i in User.getTelegram()
            )

        elif len(telegrams) == 1:
            telegrams = int(telegrams[0])
            telegram_list = f"[{telegrams}](tg://user?id={telegrams})"
        else:
            telegram_list = "Niet gevonden"
        print(telegram_list)
        Output_list = Table('VwBotTextLeaderInfo').query(
            f"SELECT BotText FROM VwBotTextLeaderInfo WHERE Leader = '{naam}' ORDER BY OrderBy")
        for i in range(len(Output_list)):
            string = Output_list[i][0]
            if string is not tuple:
                Output_list[i] = string
        Output_list.append(f"Telegram:\n{telegram_list}")
        print(Output_list)
        output = "\n".join(Output_list)
        message_handler(message.chat.id, output,
                         parse_mode="Markdown"
                         )
    except mariadb.ProgrammingError:
        error_handler(mariadb.ProgrammingError, message)

def mass_message(message, admin = False, EHBO = False, everyone = False):
    id = []
    if admin:
        with contextlib.suppress(Exception):
            admin_id = Leader_Table().get_admin()
            id += admin_id
    if EHBO:
        with contextlib.suppress(Exception):
            EHBO_id = Leader_Table().get_EHBO()
            id += EHBO_id
    if everyone:
        with contextlib.suppress(Exception):
            id += Telegram().query("SELECT TelegramID FROM Telegram")
    names = [Leader_Table().get_name(i) for i in id]
    telegram = [Leiding(i).getTelegram() for i in names]
    for i in telegram:
        if i is not None:
            message_handler(i[0], message, parse_mode="Markdown")
            print(i)


# Safety Features

def error_handler(e, message, do_not_log=False, command=None):
    message_handler(message.chat.id,
                     f"Er is iets fout gegaan, probeer het "
                     f"opnieuw.\n\nAls het probleem zich blijft herhalen, "
                     f"neem contact op met de beheerder.\n"
                     f"De error is:\n--------\n```{str(e)}```\n--------", parse_mode='Markdown')
    if not do_not_log:
        user_id = message.from_user.id
        logger(message, f"!!!ERROR {command}!!!", str(e))
        admin_message = f"ERROR\n" \
                        f"User: {user_id}\n" \
                        f"Command: {command}\n" \
                        f"Input: {message.text}\n" \
                        f"Error: \n" \
                        f"```{str(e)}```"
        mass_message(admin_message, admin=True)
        print(e)

def message_handler(message_object, content, parse_mode = None):
    if int(message_object) == message_object:
        id = message_object
    else:
        id = message_object.chat.id
    if len(content) > 4096:
        message_list = [
            f"{content[i:i + 4096]}" for i in range(0, len(content), 4096)
        ]
    else:
        message_list = [content]
    for message in message_list:
        bot.send_message(id, message, parse_mode=parse_mode)

def register_check(message):
    try:
        Telegram().get_name(message.from_user.id)
        return True
    except mariadb.ProgrammingError:
        message_handler(message.chat.id, "Je bent nog niet geregistreerd.")
        return False


def admin_check(message):
    if Telegram().get_admin(message.from_user.id) is not None:
        return True
    message_handler(message.chat.id, "Je bent geen admin.")
    return False


def logger(message=None, command=None, input_string=None):
    if input_string is None:
        input_string = message.text
    datestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    telegram_id = "Server" if message is None else message.from_user.id
    command = command
    input_string = input_string or None
    with open('log.txt', 'a') as f:
        f.write(f'{datestamp};{telegram_id};{command};{input_string}\n')


import contextlib

print('Running')
try:
    with contextlib.suppress(Exception):
        bot.infinity_polling()
except KeyboardInterrupt:
    pass
finally:
    print('Shutting down')
    logger(None, "!!!EXIT!!!", "Shutting down")
    default_server.close()
    sys.exit(0)
