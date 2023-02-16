import mariadb
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from main import *

import telebot
import json

bot = telebot.TeleBot(json.load(open("config.json"))['telegram_token'])


@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.send_message(message.chat.id,
                     "Hallo, ik ben de rooster bot van de scouting voor "
                     "GROKA 2023. "
                     "\n"
                     "\nStuur /aanmelden om je te registreren."
                     "\nStuur /overmij om je profiel te bekijken."
                     "\nStuur /over om het profiel van iemand anders te "
                     "bekijken."
                     "\nStuur /mijnspeltak om je speltak te bekijken. (WIP)"
                     "\n"
                     "\nStuur /rooster om het rooster van een andere leiding "
                     "op te vragen."
                     "\nStuur /mijnrooster om je rooster op te vragen."
                     "\n"
                     "\nStuur /help of /start om dit bericht opnieuw te zien."
                     "\n"
                     "\nDeze bot is geschreven door David Straat (Mang van de "
                     "Gidoerlog) voor het groepskamp van 2023."
                     )


@bot.message_handler(commands=['overmij'])
def about_me(message):
    namenlijst = json.load(open("namenlijst.json"))
    telegram_user = message.from_user
    if str(telegram_user.id) in namenlijst:
        naam = namenlijst[str(telegram_user.id)]
        profile(naam, message)
    else:
        bot.send_message(message.chat.id,
                         "Je bent nog niet geregistreerd, stuur /register om "
                         "je te registreren.")


@bot.message_handler(commands=['over'])
def about(message):
    bot.send_message(message.chat.id, 'Over wie wil je informatie?')
    bot.register_next_step_handler(message, about2)


def about2(message):
    naam = message.text
    profile(naam, message)


@bot.message_handler(commands=['rooster'])
def rooster(message):
    text = "Wiens rooster wil je zien?"
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, dag)


def dag(message):
    naam = message.text
    text = "Welke dag?"
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, rooster2, naam)


def rooster2(message, naam):
    dag_keuze = message.text
    User = Leiding(naam)
    User.setDag(dag_keuze)
    try:
        rooster = User.getSchedule()
        if rooster == "":
            bot.send_message(message.chat.id, f"Je bent niet ingeroosterd op "
                                              f"{dag_keuze}")
        else:
            bot.send_message(message.chat.id, User.getSchedule(
                get_setting(message.from_user.id, 'rooster')))
    except Exception as e:
        bot.send_message(message.chat.id, f"Er is iets fout gegaan: {e}")

@bot.message_handler(commands=['mijnrooster'])
def mijnrooster(message):
    namenlijst = json.load(open("namenlijst.json"))
    telegram_user = message.from_user
    if str(telegram_user.id) in namenlijst:
        naam = get_setting(telegram_user.id, 'naam')
        bot.send_message(message.chat.id, "Welke dag?")
        bot.register_next_step_handler(message, rooster2, naam)
    else:
        bot.send_message(message.chat.id,
                         "Je bent nog niet geregistreerd, stuur /register om "
                         "je te registreren.")


@bot.message_handler(commands=['aanmelden'])
def register(message):
    bot.send_message(message.chat.id,
                     "Hallo leidings, wat is je volledige naam?")
    bot.register_next_step_handler(message, register2)


def register2(message):
    naam = message.text
    try:
        naam_sql = Table("User").query(f"SELECT name FROM User WHERE name = {naam}")
    except:
        naam_sql = None
    if naam_sql is not []:
        bot.send_message(message.chat.id,
                         f"Welkom, {naam}! Doe /overmij om je "
                         f"profiel te bekijken en te "
                         f"bevestigen dat alle informatie "
                         f"correct is.")
        telegram_user = message.from_user.id
        set_setting(telegram_user, 'naam', naam)
        set_setting(telegram_user, 'rooster', 0)
    else:
        bot.send_message(message.chat.id,
                         "Je naam staat niet in de database, neem contact op "
                         "met de beheerder.")


@bot.message_handler(commands=['mijnspeltak'])
# def mijnspeltak(message):
#     namenlijst = json.load(open("namenlijst.json"))
#     telegram_user = message.from_user
#     if str(telegram_user.id) in namenlijst:
#         naam = get_setting(telegram_user.id, 'naam')
#         User = Leiding(naam)
#         Groep = Speltak(User.speltak)
#         leiding_list = Groep.returnLeiding()
#         bot.send_message(message.chat.id,
#                          f"Je bent leiding van {Groep.naam}."
#                          f"\nDe leiding van jouw speltak is: "
#                          f"{leiding_list}")
#     else:
#         bot.send_message(message.chat.id,
#                          "Je bent nog niet geregistreerd, stuur /register om "
#                          "je te registreren.")


# Lookup Speltak

# @bot.message_handler(commands=['overspeltak'])
# def overspeltak(message):
#     bot.send_message(message.chat.id,
#                      "Welke speltak wil je zien?")
#     bot.register_next_step_handler(message, overspeltak2)


# def overspeltak2(message):
#     speltak = message.text
#     bot.send_message(message.chat.id,
#                      f"De leiding van de {speltak} is: "
#                      f"{', '.join([i[1] for i in Table('Leiding').values if i[2] == speltak])}")


@bot.message_handler(commands=['settings'])
def settings(message):
    bot.send_message(message.chat.id,
                     "Welke instelling wil je aanpassen?",
                     reply_markup=button_build(["Rooster"]))


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "Rooster":
        bot.send_message(call.message.chat.id, "Rooster Instellingen\nWil je "
                                               "zien met wie je ergens "
                                               "ingeroosterd staat?",
                         reply_markup=button_build(["Alleen leiding",
                                                    "Alleen leden",
                                                    "Leiding en leden",
                                                    "Geen"]))
    if call.data == "Alleen leiding":
        bot.send_message(call.message.chat.id, "Alleen leiding")
        set_setting(call.message.chat.id, 'rooster', 1)
    if call.data == "Alleen leden":
        bot.send_message(call.message.chat.id, "Alleen leden")
        set_setting(call.message.chat.id, 'rooster', 2)
    if call.data == "Leiding en leden":
        bot.send_message(call.message.chat.id, "Leiding en leden")
        set_setting(call.message.chat.id, 'rooster', 4)
    if call.data == "Geen":
        bot.send_message(call.message.chat.id, "Geen")
        set_setting(call.message.chat.id, 'rooster', 0)


# Algemene functies

def profile(naam, message):
    try:
        User = Leiding(naam)
        bot.send_message(message.chat.id, f"Naam: {User.naam}"
                                          f"\nSpeltak: (Tijdelijk niet mogelijk)"
                                          f"\nCommissie: {User.getCommissie()}")
    except mariadb.ProgrammingError:
        error_handler(mariadb.ProgrammingError, message)


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def button_build(buttons):
    list_of_settings = buttons
    button_list = [
        InlineKeyboardButton(each, callback_data=each)
        for each in list_of_settings
    ]
    return InlineKeyboardMarkup(build_menu(button_list, n_cols=1))


def set_setting(id, setting, value):
    namenlijst = json.load(open("namenlijst.json"))
    namenlijst[str(id)][setting] = value
    with open("namenlijst.json", "w") as f:
        json.dump(namenlijst, f)


def get_setting(id, setting):
    namenlijst = json.load(open("namenlijst.json"))
    try:
        return namenlijst[str(id)][setting]
    except (KeyError, TypeError):
        bot.send_message(id,
                         "Je bent nog niet geregistreerd, stuur /register om je te registreren.")


def error_handler(e, message):
    bot.send_message(message.chat.id,
                     "Er is iets fout gegaan, probeer het "
                     "opnieuw.\n\nAls het probleem zich blijft herhalen, "
                     "neem contact op met de beheerder.")
    print(e)

# Future fuzzy search - need to figure out how to implement it
# def name_picker(name):
#     user_table = Table('User')
#     try:
#         id = user_table.retrieve('name', name)[0][0]
#     except:
#         try:

bot.infinity_polling()
