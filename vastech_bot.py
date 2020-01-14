''' VASTech bot to report on server room temperatures
    bot_token = # Bot token '''

import logging
import requests
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters

import alarms
from sensor_detect import get_measurements
from read_rpi_yaml import get_chat_ids, get_own_name, get_sensor_names, get_sensor_measures

updater = Updater(token=# Bot token, use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

chat_ids = get_chat_ids()

def start(update, context):
    ''' Starts the bot. The response to the start command will contain the
        user's chat id, which should be added to the config file '''
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Hello. I will give you information about"
                             + " alarms that go off for the sensors. Your chat id is "
                             + str(update.effective_chat.id) + "; please add this to "
                             + "the config file so I can send you messages.")

def help_cmd(update, context):
    ''' Help message for the bot '''
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="I give information about sensors in the server rooms"
                             + " and send alerts when alarms go off. \n\n"
                             + "Type /start to get a message containing your chat id,"
                             + " which you need to add to the config file. \n"
                             + "Type /get_measurements to get the latest measurements"
                             + " from the sensors.\n"
                             + "Type /set_upper_threshold sensor_index new_threshold to change"
                             + " the alarm-raise threshold for a sensor. \n"
                             + "Type /set_lower_threshold sensor_index new_threshold to change"
                             + " the alarm-clear threshold for a sensor. \n"
                             + "Type /switch_off_server server_name to switch off"
                             + " a specific server. \n"
                             + "Type /get_active_alarms to get a list of all"
                             + " currently active alarms.")

def sendmsg(update, context):
    ''' Standard response to any unknown text message
        sent to the bot '''
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Hmm looks like there's nothing new to report right now. /help")

def telegram_bot_sendtext(bot_message):
    ''' Sends a message to the user if their chat id is known '''
    global chat_ids
    bot_token = '955626728:AAGNWD8dPJMszVhZRXvb69KVqMJTOVd7-eA'
    for chat_id in chat_ids:
        bot_chatID = str(chat_id)
        send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

        response = requests.get(send_text)

    return response.json()

def get_latest_measurements(update, context):
    ''' Returns latest temperature and humidity measurements '''
    sensors = get_sensor_names()
    name = get_own_name()
    sensor_measures = get_sensor_measures() 

    hums_measured = "MEASUREMENTS: Humidity - " + name +"\n"
    temps_measured = "MEASUREMENTS: Temperature - " + name +"\n"

    counter = 1
    for sensor in sensors:
        value = get_measurements(counter)
        if sensor_measures[counter - 1] == "humidity":
            hums_measured += (sensors[counter - 1] + ": " + str(value) + " %\n")
        elif sensor_measures[counter - 1] == "temperature":
            temps_measured += (sensors[counter - 1] + ": " + str(value) + " deg C\n")
        counter += 1

    message = ""

    for item in sensor_measures:
        if item == "temperature":
            message += (temps_measured + "\n")
            break
    for item in sensor_measures:
        if item == "humidity":
            message += (hums_measured + "\n")
            break
    print(message)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def set_upper_thresh(update, context):
    ''' Set upper threshold for a sensor.
        Format : /set_upper_threshold sensor_index new_threshold
        For sensor index see config file '''
    sensor = context.args[0]
    value = context.args[1]
    alarms.set_thresholds("upper", int(sensor), float(value))
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Upper threshold for Sensor" + sensor
                             + " updated to " + value + " deg C.")

def set_lower_thresh(update, context):
    ''' Set lower threshold for a sensor.
        Format: /set_lower_threshold sensor_index new_threshold
        For sensor index see config file '''
    sensor = context.args[0]
    value = context.args[1]
    alarms.set_thresholds("lower", int(sensor), float(value))
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Lower threshold for Sensor" + sensor
                             + " updated to " + value + " deg C.")

def switch_off(update, context):
    ''' Switches off the specified server.
        Format: /switch_off_server server_name '''
    server = context.args[0]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Server "
                             + server + " will be switched off.")

def get_active_alarms(update, context):
    ''' Returns a list of all alarms currently active '''
    active_alarms = alarms.get_alarms()
    msg = "ACTIVE ALARMS: "
    for alarm in active_alarms.values():
        msg += "\n"
        msg += alarm
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
help_handler = CommandHandler('help', help_cmd)
dispatcher.add_handler(help_handler)
get_measurements_handler = CommandHandler('get_measurements', get_latest_measurements)
dispatcher.add_handler(get_measurements_handler)
set_upper_thresh_handler = CommandHandler('set_upper_threshold', set_upper_thresh)
dispatcher.add_handler(set_upper_thresh_handler)
set_lower_thresh_handler = CommandHandler('set_lower_threshold', set_lower_thresh)
dispatcher.add_handler(set_lower_thresh_handler)
switch_off_handler = CommandHandler('switch_off_server', switch_off)
dispatcher.add_handler(switch_off_handler)
get_active_alarms_handler = CommandHandler('get_active_alarms', get_active_alarms)
dispatcher.add_handler(get_active_alarms_handler)
sendmsg_handler = MessageHandler(Filters.all, sendmsg)
dispatcher.add_handler(sendmsg_handler)

updater.start_polling()
