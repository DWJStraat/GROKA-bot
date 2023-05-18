import datetime
import random
import sys
import contextlib
import telebot
from fpdf import FPDF

from Tables import *
import functions as func

#TODO
# Dit kwartier
# Volgend kwartier
# Dit uur
# Volgend uur
# Mijn Straks fixen
# Nieuwe help pagina

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
                    "\nIn geval van nood:"
                    "\n - stuur /EHBOers om de EHBOers te zien en makkelijk "
                    "contact met ze op te nemen."
                    "\n - stuur /SOS als je echt in nood bent. Dit stuurt "
                    "een bericht naar de EHBOers."
                    "\n"
                    "\nDeze bot is geschreven door David Straat (Mang van de "
                    "Gidoerlog) voor het groepskamp van 2023. Voor vragen of "
                    "opmerkingen kan je contact met mij opnemen d.m.v. "
                    "/feedback."
                    "\n"
                    "\nHuidige versie: Stable Release 1.1.2"
                    )


@bot.message_handler(commands=['roosterhelp'])
def roosterhelp(message):
    message_handler(message.chat.id,
                    "Stuur /mijnnu om je rooster van nu op te vragen."
                    "\nStuur /mijnvandaag om je rooster van vandaag op te "
                    "vragen."
                    "\nStuur /mijnmorgen om je rooster van morgen op te "
                    "vragen."
                    "\nStuur /mijntotaalrooster om je totaalrooster op te "
                    "vragen."
                    "\n"
                    "\nStuur /nu om het rooster van een andere leiding op "
                    "te vragen."
                    "\nStuur /vandaag om het rooster van een andere leiding "
                    "op te vragen."
                    "\nStuur /morgen om het rooster van een andere leiding "
                    "op te vragen."
                    "\nStuur /totaalrooster om het totaalrooster van een andere"
                    "leiding op te vragen."
                    "\n Stuur /teamrooster om het rooster van een comissie op te "
                    "vragen."
                    "\n"
                    "\nStuur /speltakroosterhelp om hulp te krijgen met het "
                    "bekijken van speltakroosters."
                    "\n"
                    "\nDeze bot is geschreven door David Straat (Mang van de "
                    "Gidoerlog) voor het groepskamp van 2023. Voor vragen of "
                    "opmerkingen kan je contact met mij opnemen d.m.v. "
                    "/feedback."
                    )

@bot.message_handler(commands=['speltakroosterhelp'])
def speltakroosterhelp(message):
    bot.send_message(
        message.chat.id,
        "Stuur /mijnspeltakrooster om een verkort rooster van je speltak te "
        "bekijken."
        "\nStuur /speltakrooster om een verkort rooster van een andere speltak te "
        "bekijken."
        "\nStuur /mijnvolledigspeltakrooster om een volledig rooster van je speltak "
        "te bekijken."
        "\nStuur /volledigspeltakrooster om een volledig rooster van een andere "
        "speltak te bekijken."
        "\n"
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
                    "\nStuur /leiding om alle ingeschreven leiding te zien."
                    "\nStuur /groepen om alle ingeschreven groepen te zien."
                    "\nStuur /kaart om de kaart te zien."
                    "\nStuur /zwerverlied om de lyrics van het zwerverlied te krijgen."
                    "\n"
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
    entered_password = str(message.text)
    password = config['bot_password']
    if entered_password == password:
        register(message)
    else:
        message_handler(message.chat.id, "Wachtwoord incorrect.")

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
    naam = str(message.text)
    func_about(naam, message)

@bot.message_handler(commands=['zwerverlied','kamplied'])
def song(message):
    try:
        song = 'Refrein:\n' \
               'En de zon gaat schijnen\n'\
               'altijd zwerver geweest\n' \
               'Nu op kamp met zijn allen\n' \
               'Het is me een feest\n' \
               '\n' \
               'Couplet 1:\n' \
               'Wij staan met zijn allen\n' \
               'In Walrick paraat\n' \
               'Ruimtescouts worden we zijn heel kordaat\n' \
               '\n' \
               'Couplet 2:\n' \
               'We gaan onderzoeken\n' \
               'Een nieuw fenomeen\n' \
               'Zo\'n grote machine\n'\
               'Er is er maar één'
        message_handler(message.chat.id, song)
    except Exception as e:
        error_handler(e, message, command='song')

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

@bot.message_handler(commands=['ditkwartier'])
def dit_kwartier(message):
    try:
        if register_check(message):
            output = this_or_next_getter(True, True, True)
            message_handler(message.chat.id, output)
    except Exception as e:
        error_handler(e, message, command='dit_kwartier')

@bot.message_handler(commands=['volgendkwartier'])
def volgend_kwartier(message):
    try:
        if register_check(message):
            output = this_or_next_getter(False, True, True)
            message_handler(message.chat.id, output)
    except:
        error_handler(e, message, command='dit_kwartier')

@bot.message_handler(commands=['dituur'])
def dit_uur(message):
    try:
        if register_check(message):
            output = this_or_next_getter(True, False, True)
            message_handler(message.chat.id, output)
    except Exception as e:
        error_handler(e, message, command='dit_uur')

@bot.message_handler(commands=['volgenduur'])
def volgend_uur(message):
    try:        
        if register_check(message):
            output = this_or_next_getter(False, False, True)
            message_handler(message.chat.id, output)
    except Exception as e:
        error_handler(e, message, command='volgend_uur')


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
        registered = register_check(message)
        if registered:
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


@bot.message_handler(commands=['mijntotaalrooster'])
def mytotaalrooster(message):
    try:
        if register_check(message):
            telegram_id = message.from_user.id
            naam = Telegram().get_name(telegram_id)
            totaal_rooster = total_schedule(naam)
            message_handler(message.chat.id, totaal_rooster)
    except Exception as e:
        error_handler(e, message, command='mijntotaalrooster')


@bot.message_handler(commands=['totaalrooster'])
def totaalrooster(message):
    if register_check(message):
        message_handler(message.chat.id, "Van wie wil je het rooster zien?")
        bot.register_next_step_handler(message, totaalrooster2)


def totaalrooster2(message):
    try:
        naam = message.text
        totaal_rooster = total_schedule(naam)
        if message_handler(message.chat.id, totaal_rooster) is False:
            message_handler(message.chat.id, "Deze persoon is niet bekend in het systeem.")
    except Exception as e:
        error_handler(e, message, command='totaalrooster')

@bot.message_handler(commands=['teamrooster', 'commissierooster'])
def team_rooster(message):
    if register_check(message):
        message_handler(message.chat.id, "Van welk team wil je het rooster zien?")
        bot.register_next_step_handler(message, team_rooster2)

def team_rooster2 (message):
    try:
        team = message.text
        team_rooster = team_schedule(team)
        if message_handler(message.chat.id, team_rooster) is False:
            message_handler(message.chat.id, "Dit team is niet bekend in het systeem.")
    except Exception as e:
        error_handler(e, message, command='teamrooster')

@bot.message_handler(commands=['speltakroostervolledig', "volledigspeltakrooster"])
def speltak_rooster(message):
    if register_check(message):
        message_handler(message.chat.id, "Van welke speltak wil je het rooster zien?")
        bot.register_next_step_handler(message, speltak_rooster2)

def speltak_rooster2 (message, short=False):
    try:
        speltak = message.text
        speltak_rooster = speltak_schedule(speltak)
        if message_handler(message.chat.id, speltak_rooster) is False:
            message_handler(message.chat.id, "Deze speltak is niet bekend in het systeem.")
    except Exception as e:
        if short:
            command = 'kortspeltakrooster'
        else:
            command = 'speltakrooster'
        error_handler(e, message, command=command)

@bot.message_handler(commands=['mijnspeltakroostervolledig', 'mijnvolledigspeltakrooster','volledigmijnspeltakrooster'])
def myspeltak_rooster(message):
    try:
        speltak = Leiding(Telegram().get_name(message.from_user.id)).getTroop()
        speltak_rooster = speltak_schedule(speltak)
        message_handler(message.chat.id, speltak_rooster)
    except Exception as e:
        error_handler(e, message, command='mijnspeltakrooster')



@bot.message_handler(commands=['mijnspeltakrooster'])
def kort_myspeltak_rooster(message):
    try:
        speltak = Leiding(Telegram().get_name(message.from_user.id)).getTroop()
        speltak_rooster = speltak_schedule(speltak, short=True)
        message_handler(message.chat.id, speltak_rooster)
    except Exception as e:
        error_handler(e, message, command='mijnspeltakrooster')

@bot.message_handler(commands=['speltakrooster'])
def kort_speltak_rooster(message):
    if register_check(message):
        message_handler(message.chat.id, "Van welke speltak wil je het rooster zien?")
        bot.register_next_step_handler(message, kort_speltak_rooster2)

def kort_speltak_rooster2(message):
    try:
        speltak = message.text
        speltak_rooster = speltak_schedule(speltak, short=True)
        if message_handler(message.chat.id, speltak_rooster) is False:
            message_handler(message.chat.id, "Deze speltak is niet bekend in het systeem.")
    except Exception as e:
        error_handler(e, message, command='kortspeltakrooster')

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
@bot.message_handler(commands=['SOS', 'sos'])
def EHBOmsg(message):
    if register_check(message):
        message_handler(message.chat.id, "Wat is de boodschap? Geef hierin door waar je bent en wat er is gebeurd, of "
                                         "type 'stop' om te stoppen.")
        bot.register_next_step_handler(message, EHBOmsg2)


def EHBOmsg2(message):
    try:
        if message.text == "stop":
            message_handler(message.chat.id, "Je hebt het bericht niet verstuurd.")
            return
        logger(message, "EHBO", message.text)
        EHBOinput = message.text
        telegram_id = message.from_user.id
        EHBOmessage = f"[EHBO]\n" \
                      f"[{Telegram().get_name(telegram_id)}](tg://user?id={telegram_id}) " \
                      f"heeft het volgende bericht gestuurd: \n" \
                      f"{EHBOinput}"
        EHBO_id = Leader_Table().get_EHBO()
        print(EHBO_id)
        EHBO_names = [Leader_Table().get_name(i) for i in EHBO_id]
        mass_message(EHBOmessage, target_admin=True, target_ehbo=True)
        print("message sent")
        EHBO_name_string = ", ".join(EHBO_names)
        message_handler(message.chat.id, f"De EHBO-ers zijn {EHBO_name_string} en hebben een bericht gekregen.")
    except Exception as e:
        error_handler(e, message, command='SOS')


@bot.message_handler(commands=['EHBOers', 'ehboers'])
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
        message_handler(message.chat.id, f"De leiding is:\n=========\n{leader_list}")
    except Exception as e:
        error_handler(e, message, command='leiding')


@bot.message_handler(commands=['groepen'])
def groepen(message):
    try:
        if not register_check(message):
            return
        query = "SELECT DISTINCT Name FROM Troop ORDER BY Name"
        leaders = Leader_Table().execute(query)
        leader_list = [f"{leader[0]}\n" for leader in leaders]
        leader_list = "".join(leader_list)
        message_handler(message.chat.id, f"De groepen zijn:\n=========\n{leader_list}")
    except Exception as e:
        error_handler(e, message, command='groepen')

@bot.message_handler(commands=['kaart', 'plattegrond', 'map'])
def kaart(message):
    try:
        if not register_check(message):
            return
        map_path = config['map_path']
        bot.send_photo(message.chat.id, open(map_path, 'rb'))
    except Exception as e:
        error_handler(e, message, command='kaart')

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
                                         "//backup - Maak een backup van de database. "
                                         "SVP niet vaker dan 1 keer per dagdeel o.i.d. uitvoeren\n"
                                         "//pdftotaalrooster - Exporteert het totaal rooster van "
                                         "een leiding naar pdf\n"
                                         "/error - Gooit een error. Voor debuggen\n"
                                         "//error - Gooit een error die wordt gelogd. "
                                         "SVP niet zomaar gebruiken, Telegram stuurt dan namelijk "
                                         "een melding naar de beheerder."
                        )


@bot.message_handler(commands=['/announce'])
def announce(message):
    if Telegram().get_admin(message.from_user.id):
        message_handler(message.chat.id, "Wat is de boodschap? Schrijf 'stop' om te stoppen.")
        bot.register_next_step_handler(message, announce2)


def announce2(message):
    try:
        if Telegram().get_admin(message.from_user.id):
            if message.text == "stop":
                message_handler(message.chat.id, "De boodschap is niet verzonden.")
                return
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
        problem_list = Problems().get_problems()
        message_handler(message, problem_list)


@bot.message_handler(commands=['/backup'])
def backup(message):
    if Telegram().get_admin(message.from_user.id):
        try:
            default_server.execute("""INSERT INTO BU_Job (id, name, ActivityId, description, nLeaders, timestamp)
                SELECT t.id, t.name, t.ActivityId, t.description, t.nLeaders, NOW()
                FROM Job t;""", commit=True)
            default_server.execute("INSERT INTO BU_Schedule (id, LeaderId, jobId, StartTimeBlockId, EndTimeBlockId, \n"
                                   "Required, timestamp)\n"
                                   "SELECT t.id, t.LeaderId, t.jobId, t.StartTimeBlockId, t.EndTimeBlockId, t.Required,"
                                   " NOW()\n"
                                   "FROM Schedule t;", commit=True)
            logger(message, "Backup")
            message_handler(message.chat.id, "Backup gemaakt.")
        except Exception as e:
            error_handler(e, message)


@bot.message_handler(commands=['/pdftotaalrooster'])
def pdftotaalrooster(message):
    if Telegram().get_admin(message.from_user.id):
        message_handler(message.chat.id, 'Van wie wil je het totaalrooster exporteren naar een PDF?')
        bot.register_next_step_handler(message, pdftotaalrooster2)


def pdftotaalrooster2(message):
    try:
        if Telegram().get_admin(message.from_user.id):
            name = message.text
            if Leader_Table().check_name(name):
                schedule_pdf_generator(message, name)
            else:
                message_handler(message.chat.id, "Deze naam is niet gevonden.")
    except Exception as e:
        error_handler(e, message)

@bot.message_handler(commands=['/pdf_all'])
def pdf_all(message):
    if Telegram().get_admin(message.from_user.id):
        users = Leader_Table().get_name()
        schedule_pdf_generator(message, users)


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

@bot.message_handler(commands=["easter_help"])
def easter_help(message):
    easter_help_output = (
        "/haarlijn_jorik\n"
        "/pingelen\n"
    )
    message_handler(message.chat.id, easter_help_output)


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
    pinge_list = [
        "Commando pingelen",
        "Commando bol",
        "Commando plat",
        "Commando hol",
        "Pingelen",
        "Bol",
        "Plat",
        "Hol"
    ]
    commando = random.choice(pinge_list)
    message_handler(message.chat.id, commando)
    bot.register_next_step_handler(message, pingelen3, commando)


def pingelen3(message, commando):
    if commando == "Commando pingelen":
        output = "pingelen"
    elif commando == "Commando bol":
        output = "bol"
    elif commando == "Commando plat":
        output = "plat"
    elif commando == "Commando hol":
        output = "hol"
    else:
        output = "..."
    if message.text.lower() == output:
        message_handler(message.chat.id, "Goed gedaan!")
        pingelen(message)
    else:
        message_handler(message.chat.id, "Helaas, probeer het nog eens.")


@bot.message_handler(commands=["stress"])
def stress(message):
    message_handler(message.chat.id, "https://www.youtube.com/watch?v=logaMSPVV-E")


# Algemene functies

def schedule_pdf_generator(message, names):
    if type(names) != list :
        names = [names]
    message_handler(message.chat.id, "Het totaalrooster wordt gegenereerd...")
    pdf = FPDF()
    for name in names:
        output = total_schedule(name)
        output = output.replace(';', '\t')
        output = output.replace('-', ' - ')
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(40, 10, f'Totaalrooster van {name}')
        pdf.ln(10)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 5, output)
    pdf.output('totaalrooster.pdf', 'F')
    message_handler(message.chat.id, "Het totaalrooster is gegenereerd.")
    bot.send_document(message.chat.id, open('totaalrooster.pdf', 'rb'))

def total_schedule(naam):
    schedule_total = Table("VwBotTextScheduleTotal")
    user_schedule = schedule_total.query(f"SELECT Bottext FROM VwBotTextScheduleTotal WHERE Leader = '{naam}' "
                                         f"ORDER BY  Orderby, starttime")
    return "\n".join(i[0] for i in user_schedule)

def team_schedule(team):
    schedule = Table("VwBotTextScheduleTeamChiefLeader")
    schedule = schedule.query(f"SELECT Bottext FROM VwBotTextScheduleTeamChiefLeader WHERE Team = '{team}' "
                              f"ORDER BY  Orderby")
    output = ''
    for i in range(len(schedule)):
        try:
            output += schedule[i][0]
            output += '\n'
        except:
            pass
    return output

def speltak_schedule(speltak, short=False):
    database = "VwBotTextTroopSchedule"
    if short:
        database +="Short"
    schedule = Table(database)
    query = f"SELECT Bottext FROM {database} WHERE name = '{speltak}' order by Orderby"
    schedule = schedule.query(query)
    output = ''
    for i in range(len(schedule)):
        try:
            output += schedule[i][0]
            output += '\n'
        except:
            pass
    return output

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





def mass_message(message, target_admin=False, target_ehbo=False, target_everyone=False):
    telegram_ids = []
    if target_admin:
        with contextlib.suppress(Exception):
            admin_id = Leader_Table().get_admin()
            telegram_ids += admin_id
    if target_ehbo:
        with contextlib.suppress(Exception):
            EHBO_id = Leader_Table().get_EHBO()
            telegram_ids += EHBO_id
    if target_everyone:
        with contextlib.suppress(Exception):
            telegram_ids += Telegram().query("SELECT TelegramID FROM Telegram")
    telegram = []
    for i in telegram_ids:
        if i is not None:
            name = Leader_Table().get_name(i)
            try:
                tele_id = Leiding(name).getTelegram()
                telegram.append(tele_id)
            except Exception:
                telegram.append(None)
    print(telegram)
    for i in telegram:
        if i is not None:
            with contextlib.suppress(Exception):
                message_handler(int(i[0]), message, parse_mode="Markdown")
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
        user_name = message.from_user.first_name
        logger(message, f"!!!ERROR {command}!!!", str(e))
        admin_message = f"ERROR\n" \
                        f"User: [{user_name}](tg://user?id={user_id})\n" \
                        f"Command: {command}\n" \
                        f"Input: {message.text}\n" \
                        f"Error: \n" \
                        f"```{str(e)}```"
        mass_message(admin_message, target_admin=True)
        print(e)


def message_handler(message_object, content, parse_mode=None):
    if int(message_object) == message_object:
        telegram_id = message_object
    else:
        telegram_id = message_object.chat.id
    if content is None or content == "":
        return False
    if len(content) > 4096:
        message_list = [
            f"{content[i:i + 4096]}" for i in range(0, len(content), 4096)
        ]
    else:
        message_list = [content]
    for message in message_list:
        bot.send_message(telegram_id, message, parse_mode=parse_mode)


def register_check(message):
    try:
        if Telegram().get_name(message.from_user.id) is None:
            message_handler(message.chat.id, "Je bent nog niet geregistreerd. Gebruik /aanmelden.")
            return False
        else:
            return True
    except Exception:
        message_handler(message.chat.id, "Je bent nog niet geregistreerd. Gebruik /aanmelden.")
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

def func_about(naam, message):
    try:
        logger(message, 'over', naam)
        try:
            profile(naam, message)
        except IndexError:
            message_handler(message.chat.id, "Deze persoon is niet gevonden in de "
                                             "database, probeer het opnieuw.")
    except Exception as e:
        error_handler(e, message, command='over')

def this_or_next_getter(this = False, quarter = True, short=False):
    table = "VwBotTextSchedule"
    if this:
        table += "This"
    else:
        table += "Next"
    if quarter:
        table+="Quarter"
    else:
        table += "Hour"
    table_object = Table(table)
    column = "BotText"
    if short:
        column += "Verkort"
    query = f'SELECT {column} FROM {table}'
    output_list = table_object.query(query)
    output = ''
    for i in output_list:
        if output != '':
            output += '\n'
        output += i[0]
    return output



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
