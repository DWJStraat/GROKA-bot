import random

import regex as re
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime

from Tables import *



config = json.load(open("config.json"))

bot = telebot.TeleBot(config['telegram_token'])

schedule = Schedules_today()


@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.send_message(message.chat.id,
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
    bot.send_message(message.chat.id,
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
    bot.send_message(message.chat.id,
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
    bot.send_message(message.chat.id, "Voer het wachtwoord in.")
    bot.register_next_step_handler(message, password2)


def password2(message):
    enteredpassword = str(message.text)
    correctpassword = config['bot_password']
    if enteredpassword == correctpassword:
        register(message)
    else:
        bot.send_message(message.chat.id, "Het wachtwoord is onjuist. Voer het commando opnieuw in of vraag hulp"
                                          "aan het planning team.")


def register(message):
    bot.send_message(message.chat.id,
                     "Hallo leidings, wat is je naam?")
    bot.register_next_step_handler(message, register2)


def register2(message):
    naam = str(message.text)
    logger(message, 'aanmelden', naam)
    try:
        try:
            naam_sql = Leader().get_id(naam)
        except mariadb.Error:
            naam_sql = None
        if naam_sql is not None:
            telegram_id = str(message.from_user.id)
            Telegram_table = Telegram()
            Telegram_table.set_name(telegram_id, naam)
            bot.send_message(message.chat.id, f"Je bent geregistreerd! Welkom, {naam}")
        else:
            bot.send_message(message.chat.id, "Je naam is niet gevonden in de "
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
                profile(naam, message)
            except mariadb.Error:
                bot.send_message(message.chat.id, "Je bent nog niet geregistreerd, stuur /aanmelden om "
                                                  "je te registreren.")
    except Exception as e:
        error_handler(e, message, command= 'overmij')


@bot.message_handler(commands=['over'])
def about(message):
    if register_check(message):
        bot.send_message(message.chat.id, 'Over wie wil je informatie?')
        bot.register_next_step_handler(message, about2)


def about2(message):
    try:
        naam = message.text
        logger(message, 'over', naam)
        profile(naam, message)
    except Exception as e:
        error_handler(e, message, command='over')


@bot.message_handler(commands=['mijnnu'])
def mynow(message):
    try:
        if register_check(message):
            telegram_id = message.from_user.id
            naam = Telegram().get_name(telegram_id)
            bot.send_message(message.chat.id, Schedules_now().get_schedule(naam))
    except Exception as e:
        error_handler(e, message, command='mijnnu')


# Rooster commands

@bot.message_handler(commands=['nu'])
def now(message):
    if register_check(message):
        bot.send_message(message.chat.id, "Over wie wil je het nu rooster zien?")
        bot.register_next_step_handler(message, now2)


def now2(message):
    try:
        naam = message.text
        logger(message, 'nu', naam)
        bot.send_message(message.chat.id, Schedules_now().get_schedule(naam))
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
        bot.send_message(message.chat.id, "Over wie wil je het straks rooster zien?")
        bot.register_next_step_handler(message, soon2)


def soon2(message):
    try:
        logger(message, 'straks', message.text)
        if register_check(message):
            naam = message.text
            bot.send_message(message.chat.id, Schedules_Next().get_schedule(naam))
    except Exception as e:
        error_handler(e, message,command='straks')


@bot.message_handler(commands=['mijnrooster', 'mijnvandaag'])
def myrooster(message):
    try:
        if register_check(message):
            telegram_id = message.from_user.id
            naam = Telegram().get_name(telegram_id)
            bot.send_message(message.chat.id, Schedules_today().get_schedule(naam))
    except Exception as e:
        error_handler(e, message, command='mijnrooster')


@bot.message_handler(commands=['rooster', 'vandaag'])
def rooster(message):
    if register_check(message):
        bot.send_message(message.chat.id, "Over wie wil je het rooster zien?")
        bot.register_next_step_handler(message, rooster2)


def rooster2(message):
    try:
        naam = message.text
        bot.send_message(message.chat.id, Schedules_today().get_schedule(naam))
    except Exception as e:
        error_handler(e, message, command='rooster')


@bot.message_handler(commands=['mijnmorgen'])
def mymorgen(message):
    try:
        if register_check(message):
            telegram_id = message.from_user.id
            naam = Telegram().get_name(telegram_id)
            bot.send_message(message.chat.id, Schedules_tomorrow().get_schedule(naam))
    except Exception as e:
        error_handler(e, message, command='mijnmorgen')


@bot.message_handler(commands=['morgen'])
def morgen(message):
    if register_check(message):
        bot.send_message(message.chat.id, "Over wie wil je het morgen rooster zien?")
        bot.register_next_step_handler(message, morgen2)


def morgen2(message):
    try:
        naam = message.text
        bot.send_message(message.chat.id, Schedules_tomorrow().get_schedule(naam))
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
            troop = Speltak(troopname)
            leden = troop.getMembers()
            leiding = troop.getLeiding()
            leiding.remove(naam)
            output = ''
            for i in leiding:
                if i == leiding[-1]:
                    output += 'en '
                output += f"{i}"
                if i != leiding[-1]:
                    output += ', '
            bot.send_message(message.chat.id, f"Je bent leiding van {troopname}, samen met {output}. Jullie hebben"
                                              f" {leden} leden."
                             )
        except mariadb.Error:
            bot.send_message(message.chat.id, "Je bent nog niet geregistreerd, stuur /aanmelden om "
                                              "je te registreren.")
    except Exception as e:
        error_handler(e, message, command='mijnspeltak')


@bot.message_handler(commands=['speltak'])
def speltak(message):
    if register_check(message):
        bot.send_message(message.chat.id, "Over welke speltak wil je informatie?")
        bot.register_next_step_handler(message, speltak2)


def speltak2(message):
    try:
        troopname = message.text
        try:
            leiding = Speltak(troopname).getLeiding()
            leden = Speltak(troopname).getMembers()
            output = ''
            for i in leiding:
                if i == leiding[-1]:
                    output += 'en '
                output += f"{i}"
                if i != leiding[-1]:
                    output += ', '
            bot.send_message(message.chat.id, f"De leiding van {troopname} zijn {output}. Zij hebben {leden} leden.")
        except mariadb.Error:
            bot.send_message(message.chat.id, "Deze speltak is niet gevonden in de database.")
    except Exception as e:
        error_handler(e, message, command='speltak')


@bot.message_handler(commands=['feedback'])
def feedback(message):
    bot.send_message(message.chat.id, "Bedankt dat je feedback wilt geven! Stuur een bericht naar "
                                      "[David Straat](tg://user?id=2059520607)",
                     parse_mode="Markdown")


# Noodgeval functies
@bot.message_handler(commands=['SOS'])
def EHBOmsg(message):
    if register_check(message):
        bot.send_message(message.chat.id, "Wat is de boodschap? Geef hierin door waar je bent en wat er is gebeurd.")
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
        EHBO_id = Leader().get_EHBO()
        EHBO_names = [Leader().get_name(i) for i in EHBO_id]
        EHBO_telegram = [Leiding(i).getTelegram() for i in EHBO_names]
        for i in EHBO_telegram:
            if i is not None:
                bot.send_message(i, EHBOmessage, parse_mode="Markdown")
        EHBO_name_string = ", ".join(EHBO_names)
        bot.send_message(message.chat.id, f"De EHBO-ers zijn {EHBO_name_string} en hebben een bericht gekregen.")
    except Exception as e:
        error_handler(e, message, command='SOS')


@bot.message_handler(commands=['EHBOers'])
def EHBOers(message):
    try:
        if not register_check(message):
            return
        EHBO_id = Leader().get_EHBO()
        EHBO_names = [Leader().get_name(i) for i in EHBO_id]
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
        bot.send_message(message.chat.id, f"De EHBO-ers zijn:\n{EHBO_list}", parse_mode="Markdown")
    except Exception as e:
        error_handler(e, message, command='EHBOers')


# Admin commands

@bot.message_handler(commands=['/admin'])
def admin(message):
    if register_check(message):
        bot.send_message(message.chat.id, "Wat is het wachtwoord?")
        bot.register_next_step_handler(message, admin2)


def admin2(message):
    try:
        if message.text == config['bot_password_admin']:
            bot.send_message(message.chat.id, "Je bent nu ingelogd als admin.")
            Telegram().set_admin(message.from_user.id)
        else:
            bot.send_message(message.chat.id, "Het wachtwoord is onjuist.")
    except Exception as e:
        error_handler(e, message)


@bot.message_handler(commands=['/help'])
def admin_help(message):
    if Telegram().get_admin(message.from_user.id):
        bot.send_message(message.chat.id, "De volgende commando's zijn beschikbaar voor admins:\n"
                                          "//admin - Log in als admin\n"
                                          "//help - Toon deze lijst\n"
                                          "//announce - Stuur een bericht naar alle leden\n"
                                          "//test - Test of je admin bent\n"
                                          "//problems - Toon de problemen in de planning\n"
                         )


@bot.message_handler(commands=['/announce'])
def announce(message):
    if Telegram().get_admin(message.from_user.id):
        bot.send_message(message.chat.id, "Wat is de boodschap?")
        bot.register_next_step_handler(message, announce2)


def announce2(message):
    try:
        if Telegram().get_admin(message.from_user.id):
            bot.send_message(message.chat.id, "De boodschap is verzonden.")
            announcement = message.text
            user_id = message.from_user.id
            naam = Telegram().get_name(user_id)
            for i in Telegram().find_all('telegramid'):
                print(i)
                bot.send_message(i, f'Massabericht van [{naam}](tg://user?id={user_id}):', parse_mode='Markdown')
                bot.send_message(i, announcement)
    except Exception as e:
        error_handler(e, message)


@bot.message_handler(commands=['/test'])
def admin_test(message):
    if Telegram().get_admin(message.from_user.id):
        bot.send_message(message.chat.id, "Je bent ingelogd als admin.")


@bot.message_handler(commands=['/problems'])
def problems(message):
    if Telegram().get_admin(message.from_user.id):
        bot.send_message(message.chat.id, Problems().get_problems())


@bot.message_handler(commands=['/schedule'])
def schedule(message):
    if Telegram().get_admin(message.from_user.id):
        bot.send_message(message.chat.id, "Van wie wil je het rooster inzien?")
        bot.register_next_step_handler(message, schedule2)


def schedule2(message):
    try:
        if Telegram().get_admin(message.from_user.id):
            name = message.text
            if Leader().check_name(name):
                bot.send_message(message.chat.id, Leader().get_schedule(name))
            else:
                bot.send_message(message.chat.id, "Deze naam is niet gevonden.")
    except Exception as e:
        error_handler(e, message)


@bot.message_handler(commands=['error'])
def throw_error(message):
    bot.send_message(message.chat.id, "Dit is een testbericht voor de error-handler. (Dit is geen echte error.)\n "
                                      "Neem geen contact op met de ontwikkelaars.")
    string = ''
    try:
        string[1]
    except Exception as e:
        error_handler(e, message)

# Eastereggs

@bot.message_handler(commands=["haarlijn_jorik"])
def haarlijn(message):
    error_handler("ERROR 404:\nHairline not found", message, do_not_log=True)


@bot.message_handler(commands=["pingelen"])
def pingelen(message):
    bot.send_message(message.chat.id, "Welkom bij Commando Pingelen. Als je een commando krijgt, volg het commando. Zo niet,"
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
    bot.send_message(message.chat.id, commando)
    bot.register_next_step_handler(message, pingelen3, commando)

def pingelen3 (message, commando):
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
        bot.send_message(message.chat.id, "Goed gedaan!")
        pingelen(message)
    else:
        bot.send_message(message.chat.id, "Helaas, probeer het nog eens.")

@bot.message_handler(commands=["stress"])
def stress(message):
    bot.send_message(message.chat.id, "https://www.youtube.com/watch?v=logaMSPVV-E")



# Algemene functies

def profile(naam, message):
    try:
        User = Leiding(naam)
        telegrams = User.getTelegram()
        if telegrams is list:
            telegram_list = "".join(
                f"[{i}](tg://user?id={i})\n" for i in User.getTelegram()
            )
        elif telegrams is str or int:
            telegram_list = f"[{telegrams}](tg://user?id={telegrams})"
        else:
            telegram_list = "Niet gevonden"
        print(telegram_list)
        bot.send_message(message.chat.id, f"Naam: {User.naam}"
                                          f"\nSpeltak: {User.getTroop()}"
                                          f"\nCommissie: {User.getCommissie()}"
                                          f"\nTelefoonnummer: {User.getPhone()}"
                                          f"\nTelegram: {telegram_list}",
                         parse_mode="Markdown"
                         )
    except mariadb.ProgrammingError:
        error_handler(mariadb.ProgrammingError, message)


def button_build(names, values):
    return [
        [InlineKeyboardButton(text=names, url=values)]
        for _ in range(len(values))
    ]


def location_buttons(location_dictionary):
    location = list(location_dictionary.keys())
    location_urls = list(location_dictionary.values())
    return button_build(location, location_urls)


def schedule_now(name):
    output = Schedules_now().get_schedule(name)
    return re.sub(r'(?<=[.,])(?=[^\s])', r' ', output)


def schedule_next(name):
    output = Schedules_Next().get_schedule(name)
    return re.sub(r'(?<=[.,])(?=[^\s])', r' ', output)


def now_function(naam, message):
    location_dict = Tijdblok().get_locations(naam)
    location = list(location_dict.keys())
    location_urls = list(location_dict.values())
    inline_keyboard = [
        [InlineKeyboardButton(text=location[i], url=location_urls[i])]
        for i in range(len(location))
    ]
    bot.send_message(message.chat.id, schedule_now(naam), reply_markup=InlineKeyboardMarkup(inline_keyboard))


def soon_function(naam, message):
    location_dict = Schedules_Next().get_locations(naam)
    location = list(location_dict.keys())
    location_urls = list(location_dict.values())
    inline_keyboard = [
        [InlineKeyboardButton(text=location[i], url=location_urls[i])]
        for i in range(len(location))
    ]
    bot.send_message(message.chat.id, schedule_next(naam), reply_markup=InlineKeyboardMarkup(inline_keyboard))


# Safety Features

def error_handler(e, message, do_not_log=False, command = None):
    bot.send_message(message.chat.id,
                     f"Er is iets fout gegaan, probeer het "
                     f"opnieuw.\n\nAls het probleem zich blijft herhalen, "
                     f"neem contact op met de beheerder.\n"
                     f"De error is:\n--------\n```{str(e)}```\n--------", parse_mode='Markdown')
    if not do_not_log:
        logger(message, f"!!!ERROR{command}!!!", str(e))
    print(e)


def register_check(message):
    try:
        Telegram().get_name(message.from_user.id)
        return True
    except mariadb.ProgrammingError:
        bot.send_message(message.chat.id, "Je bent nog niet geregistreerd.")
        return False


def admin_check(message):
    if Telegram().get_admin(message.from_user.id) is not None:
        return True
    bot.send_message(message.chat.id, "Je bent geen admin.")
    return False


def logger(message, command, input_string=None):
    if input_string is None:
        input_string = message.text
    datestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    telegram_id = message.from_user.id
    command = command
    input_string = input_string or None
    with open('log.txt', 'a') as f:
        f.write(f'{datestamp};{telegram_id};{command};{input_string}\n')


print('Running')
bot.infinity_polling()
