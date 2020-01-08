''' VASTech bot to report on server room temperatures '''

import logging
import requests
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters

import alarms
from gettemps import get_temperature, get_humidity
from read_rpi1_yaml import get_chat_ids, get_own_name, get_sensor_names


updater = Updater(token='955626728:AAGNWD8dPJMszVhZRXvb69KVqMJTOVd7-eA', use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

chat_ids = get_chat_ids()

def start(update, context):
    ''' Starts the bot. The response to the start command will contain the
        user's chat id, which should be added to the config file '''
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Hello. I will give you information about"
                             + " alarms that go off for the sensors. Your chat id is "
                             + str(update.effective_chat.id) + "; please add this to "
                             + "the config file so I can send you messages.")

def sendmsg(update, context):
    ''' Standard response to any unknown text message
        sent to the bot '''
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Hmm looks like there's nothing new to report right now.")

def telegram_bot_sendtext(bot_message):
    ''' Sends a message to the user if their chat id is known '''
    global chat_ids
    bot_token = '955626728:AAGNWD8dPJMszVhZRXvb69KVqMJTOVd7-eA'
    for chat_id in chat_ids:
        bot_chatID = str(chat_id)
        send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

        response = requests.get(send_text)

    return response.json()

def get_measurements(update, context):
    ''' Returns latest temperature and humidity measurements '''
    temps = get_temperature()
    hums = get_humidity()
    sensors = get_sensor_names()
    name = get_own_name()
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="MEASUREMENTS: Temperature - " + name +"\n" 
                             + sensors[0] + ": " + str(temps[0]) + " deg C\n"
                             + sensors[1] + ": " + str(temps[1]) + " deg C\n"
                             + sensors[2] + ": " + str(temps[2]) + " deg C\n"
                             + sensors[3] + ": " + str(temps[3]) + " deg C\n" 
                             + "\nMEASUREMENTS: Humidity - " + name + ": \n"
                             + sensors[0] + ": " + str(hums[0]) + " %\n" 
                             + sensors[1] + ": " + str(hums[1]) + " %\n" 
                             + sensors[2] + ": " + str(hums[2]) + " %\n" 
                             + sensors[3] + ": " + str(hums[3]) + " %")

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
get_measurements_handler = CommandHandler('get_measurements', get_measurements)
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
