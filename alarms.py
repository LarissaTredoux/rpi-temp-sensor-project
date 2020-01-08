''' Checks for alarms and sends notifications if raised/cleared.

    Possible alarms:
    - Sensor down -> measurement on sensor is None
    - Temperature on sensor too high -> if it's above the threshold
    - Peer down (not currently implemented)

    Other failures:
    - Sometimes the sensor sends bad data causing incorrect measurements
      and possibly incorrect alarms
'''

from read_rpi_yaml import get_own_name, get_sensor_clear_thresholds, get_sensor_raise_thresholds
from read_rpi_yaml import set_sensor_raise_thresholds, set_sensor_clear_thresholds, get_sensor_alarms, get_alarm_names
from vastech_bot import telegram_bot_sendtext

yaml_file = "rpi2.yaml"
name = get_own_name(yaml_file)
sensor_up = [1, 1, 1, 1] # 1 = up, 0 = down
sensor_flags = [0, 0, 0, 0] # 0 = alarm cleared, 1 = alarm raised
sensor_thresholds_raise = get_sensor_raise_thresholds(yaml_file) # temperature at which to raise the alarm
sensor_thresholds_clear = get_sensor_clear_thresholds(yaml_file) # temperature at which to clear the alarm
all_alarms = get_sensor_alarms(yaml_file)
alarm_names = get_alarm_names(yaml_file)
over_temp_alarms = {}
sensor_down_alarms = {}


def alarm_check(temperatures):
    ''' Checks whether alarms need to be cleared, updated or raised '''
    global sensor_up, sensor_flags, sensor_thresholds_clear, sensor_thresholds_raise, name
    counter = 0
    for temp in temperatures:
        if temp is not None:
            if sensor_up[counter] == 0: # if sensor was down
                sensor_up[counter] = 1 # sensor is back up
                del sensor_down_alarms[counter]
                if sensor_down_alarms == {}: # if we have no more sensor down alarms
                    send_notification("clear", 1) # clear sensor down alarms
                else:
                    send_notification("update", 1) # update sensor down alarms

            if sensor_flags[counter] == 1: # alarm is raised for this sensor
                # check if sensor is below threshold
                if temp <= sensor_thresholds_clear[counter]:
                    sensor_flags[counter] = 0 # reset flag
                    del over_temp_alarms[counter] # remove from list of alarms
                    if over_temp_alarms == {}: # if we have no over temp alarms
                        send_notification("clear", 0) # clear over temp alarms
                    else:
                        send_notification("update", 0) # update over temp alarms
            else: # alarm is not raised for this sensor
                # check if sensor is above threshold
                if temp >= sensor_thresholds_raise[counter]:
                    sensor_flags[counter] = 1 # set flag
                    alarm = all_alarms[alarm_names[0] + str(counter)]
                    if over_temp_alarms == {}: # if this is the first alarm
                        over_temp_alarms[counter] = alarm # add alarm to over temp alarms
                        send_notification("raise", 0) # raise over temp alarm
                    else:
                        over_temp_alarms[counter] = alarm # add alarm to over temp alarms
                        send_notification("update", 0) # update over temp alarm
        else:
            if sensor_up[counter] == 1:
                sensor_up[counter] = 0 # sensor is down
                alarm = all_alarms[alarm_names[1] + str(counter)]
                if sensor_down_alarms == {}: # if this is the first alarm
                    sensor_down_alarms[counter] = alarm # add alarm to sensor down alarms
                    send_notification("raise", 1) # raise alarm
                else:
                    sensor_down_alarms[counter] = alarm # add alarm to sensor down alarms
                    send_notification("update", 1)

        counter += 1


def send_notification(alarm_action, alarm_type):
    ''' Sends notifications to say which alarm has been raised, updated or cleared '''
    global over_temp_alarms, sensor_down_alarms, name, alarm_names
    if alarm_action == "raise":
        a = "ALARM-RAISE: " + alarm_names[alarm_type] + " - " + name
        if alarm_type == 0: # alarm raise: over temp
            for alarm in over_temp_alarms.values():
                a += "\n"
                a += alarm
        elif alarm_type == 1: # alarm raise: sensor down
            for alarm in sensor_down_alarms.values():
                a += "\n"
                a += alarm
        telegram_bot_sendtext(a)
        print(a)
    elif alarm_action == "update": 
        b = "ALARM-UPDATE: " + alarm_names[alarm_type] + " - " + name
        if alarm_type == 0: # alarm update: over temp
            for alarm in over_temp_alarms.values():
                b += "\n"
                b += alarm
        elif alarm_type == 1: # alarm update: sensor down
            for alarm in sensor_down_alarms.values():
                b += "\n"
                b += alarm
        telegram_bot_sendtext(b)
        print(b)
    elif alarm_action == "clear":
        c = "ALARM-CLEAR: " + alarm_names[alarm_type] + " - " + name
        if alarm_type == 0: # alarm clear: over temp
            c += "\nAll sensors measured below threshold"
        elif alarm_type == 1: # alarm clear: sensor down
            c+= "\nAll sensors are up"
        telegram_bot_sendtext(c)
        print(c)

def set_thresholds(threshold, sensor, value):
    ''' Sets upper and lower temperature thresholds for sensors '''
    global sensor_thresholds_raise, sensor_thresholds_clear
    if threshold == "upper":
        sensor_thresholds_raise[sensor - 1] = value
        print(sensor_thresholds_raise)
        set_sensor_raise_thresholds(value, sensor, yaml_file)
    elif threshold == "lower":
        sensor_thresholds_clear[sensor - 1] = value
        print(sensor_thresholds_clear)
        set_sensor_clear_thresholds(value, sensor, yaml_file)

def get_alarms():
    ''' Returns a list of all alarms currently active '''
    active_alarms = {**over_temp_alarms, **sensor_down_alarms}
    return active_alarms
