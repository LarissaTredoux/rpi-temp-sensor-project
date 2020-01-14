''' Author: Larissa Tredoux

    Checks for alarms and sends notifications if raised/cleared.

    Possible alarms:
    - Sensor down -> measurement on sensor is None
    - Measurement on sensor too high -> if it's above the threshold
    - Peer down 

    Other failures:
    - Sometimes the sensor sends bad data causing incorrect measurements
      and possibly incorrect alarms
    - Wifi connection fails (GSM)
    - Power failure
'''

from read_rpi_yaml import get_own_name, get_sensor_clear_thresholds, get_sensor_raise_thresholds, get_peer_alarms, get_peer_alarm_names
from read_rpi_yaml import set_sensor_raise_thresholds, set_sensor_clear_thresholds, get_sensor_alarms, get_alarm_names
import vastech_bot

oob_count = [0, 0, 0, 0] # value from 0 to 10 - number of consecutive out of bounds
oob_state = [0, 0, 0, 0] # 0 if in bounds, 1 if out of bounds
name = get_own_name()
peer_states_prev = [1, 1] # 1 = up, 0 = down
sensor_states_prev = [1, 1, 1, 1] # 1 = up, 0 = down
sensor_flags = [0, 0, 0, 0] # 0 = alarm cleared, 1 = alarm raised
sensor_thresholds_raise = get_sensor_raise_thresholds() # temperature at which to raise the alarm
sensor_thresholds_clear = get_sensor_clear_thresholds() # temperature at which to clear the alarm
all_alarms = get_sensor_alarms()
alarm_names = get_alarm_names()
all_peer_alarms = get_peer_alarms()
peer_alarm_names = get_peer_alarm_names()
over_thresh_alarms = {}
sensor_down_alarms = {}
peer_alarms = {}
oob_alarms = {}


def alarm_check(sensor_values, peer_states_curr):
    ''' Checks whether alarms need to be cleared, updated or raised '''
    global sensor_up, sensor_flags, sensor_thresholds_clear, sensor_thresholds_raise, name, peer_states_prev

    if peer_states_prev != peer_states_curr: # change in peer states since last check
        peer_idx = 0
        for peer in peer_states_curr:
            if peer_states_curr[peer_idx] == 0 and peer_states_prev[peer_idx] != 0: # peer is down
                alarm_message = all_peer_alarms[peer_alarm_names[0] + str(peer_idx + 1)]
                if peer_alarms == {}: # if this is the first alarm
                    peer_alarms[peer_idx] = alarm_message # add alarm to sensor down alarms
                    send_notification("raise", 3) # raise alarm
                else:
                    peer_alarms[peer_idx] = alarm_message # add alarm to peer down alarms
                    send_notification("update", 3)
            elif peer_states_curr[peer_idx] == 1 and peer_states_prev[peer_idx] != 1: # peer is up
                del peer_alarms[peer_idx]
                if peer_alarms == {}: # if we have no more peer down alarms
                    send_notification("clear", 3) # clear peer down alarms
                else:
                    send_notification("update", 3) # update peer down alarms
            peer_idx += 1
        peer_states_prev = peer_states_curr

    sensor_idx = 0
    for sensor_value in sensor_values:
        if (sensor_value is not None) and (sensor_value <= 100) and (sensor_value >= 0):
            if oob_count[sensor_idx] >= 10:
                send_notification("clear", 2)
            oob_state[sensor_idx] = 0
            oob_count[sensor_idx] = 0
            if sensor_states_prev[sensor_idx] == 0: # if sensor was down
                sensor_states_prev[sensor_idx] = 1 # sensor is back up
                del sensor_down_alarms[sensor_idx]
                if sensor_down_alarms == {}: # if we have no more sensor down alarms
                    send_notification("clear", 1) # clear sensor down alarms
                else:
                    send_notification("update", 1) # update sensor down alarms

            # check if sensor has gone below threshold
            elif sensor_flags[sensor_idx] == 1 and sensor_value <= sensor_thresholds_clear[sensor_idx]: 
                # check if sensor is below threshold
                sensor_flags[sensor_idx] = 0 # reset flag
                del over_thresh_alarms[sensor_idx] # remove from list of alarms
                if over_thresh_alarms == {}: # if we have no over threshold alarms
                    send_notification("clear", 0) # clear over threshold alarms
                else:
                    send_notification("update", 0) # update over threshold alarms
            # check if sensor has gone above threshold
            elif sensor_flags[sensor_idx] != 1 and sensor_value >= sensor_thresholds_raise[sensor_idx]:
                sensor_flags[sensor_idx] = 1 # set flag
                alarm_message = all_alarms[alarm_names[0] + str(sensor_idx + 1)]
                if over_thresh_alarms == {}: # if this is the first alarm
                    over_thresh_alarms[sensor_idx] = alarm_message # add alarm to over threshold alarms
                    send_notification("raise", 0) # raise over temp alarm
                else:
                    over_thresh_alarms[sensor_idx] = alarm_message # add alarm to over threshold alarms
                    send_notification("update", 0) # update over threshold alarm
        
        elif ((sensor_value >= 100) or (sensor_value <= 0)) and oob_count[sensor_idx] < 10:
            oob_count[sensor_idx] += 1
            if oob_state[sensor_idx] == 0: # more than once consecutively
                oob_state[sensor_idx] = 1
            elif oob_count[sensor_idx] >= 10:
                if oob_alarms == {}: # if this is the first alarm
                    oob_alarms[sensor_idx] = alarm_message # add alarm to over threshold alarms
                    send_notification("raise", 2) # raise out of bounds alarm
                else:
                    oob_alarms[sensor_idx] = alarm_message # add alarm to over threshold alarms
                    send_notification("update", 2) # update out of bounds alarm
        
        else:
            if sensor_states_prev[sensor_idx] == 1:
                sensor_states_prev[sensor_idx] = 0 # sensor is down
                alarm = all_alarms[alarm_names[1] + str(sensor_idx + 1)]
                if sensor_down_alarms == {}: # if this is the first alarm
                    sensor_down_alarms[sensor_idx] = alarm # add alarm to sensor down alarms
                    send_notification("raise", 1) # raise alarm
                else:
                    sensor_down_alarms[sensor_idx] = alarm # add alarm to sensor down alarms
                    send_notification("update", 1)

        sensor_idx += 1


def send_notification(alarm_action, alarm_type):
    ''' Sends notifications to say which alarm has been raised, updated or cleared '''
    global over_temp_alarms, sensor_down_alarms, name, alarm_names, peer_alarm_names

    for peer_name in peer_alarm_names:
        alarm_names.append(peer_name)

    if alarm_action == "raise":
        raise_message = "ALARM-RAISE:\n[HOST]: " + name + "\n[TYPE]: " +  alarm_names[alarm_type]
        if alarm_type == 0: # alarm raise: over threshold
            for alarm in over_thresh_alarms.values():
                raise_message += "\n"
                raise_message += alarm
        elif alarm_type == 1: # alarm raise: sensor down
            for alarm in sensor_down_alarms.values():
                raise_message += "\n"
                raise_message += alarm
        elif alarm_type == 2: # alarm raise: out of bounds
            for alarm in oob_alarms.values():
                raise_message += "\n"
                raise_message += alarm
        elif alarm_type == 3: # alarm raise: peer down
            for alarm in peer_alarms.values():
                raise_message += "\n"
                raise_message += alarm
        vastech_bot.telegram_bot_sendtext(raise_message)
    elif alarm_action == "update":
        update_message = "ALARM-UPDATE:\n[HOST]: " + name + "\n[TYPE]: " +  alarm_names[alarm_type]
        if alarm_type == 0: # alarm update: over threshold
            for alarm in over_thresh_alarms.values():
                update_message += "\n"
                update_message += alarm
        elif alarm_type == 1: # alarm update: sensor down
            for alarm in sensor_down_alarms.values():
                update_message += "\n"
                update_message += alarm
        elif alarm_type == 2: # alarm update: out of bounds
            for alarm in oob_alarms.values():
                raise_message += "\n"
                raise_message += alarm
        elif alarm_type == 3: # alarm update: peer down
            for alarm in peer_alarms.values():
                update_message += "\n"
                update_message += alarm
        vastech_bot.telegram_bot_sendtext(update_message)
    elif alarm_action == "clear":
        clear_message = "ALARM-CLEAR:\n[HOST]: " + name + "\n[TYPE]: " +  alarm_names[alarm_type]
        if alarm_type == 0: # alarm clear: over threshold
            clear_message += "\nAll sensors measured below threshold"
        elif alarm_type == 1: # alarm clear: sensor down
            clear_message += "\nAll sensors are up"
        elif alarm_type == 2: # alarm clear: out of bounds
            clear_message += "\nAll sensors are within bounds"
        elif alarm_type == 3: # alarm clear: peer downs
            clear_message += "\nAll peers are up"
        vastech_bot.telegram_bot_sendtext(clear_message)


def set_thresholds(threshold, sensor, value):
    ''' Sets upper and lower temperature thresholds for sensors '''
    global sensor_thresholds_raise, sensor_thresholds_clear, all_alarms
    sensor = sensor - 1 # aligning index
    if threshold == "upper":
        sensor_thresholds_raise[sensor] = value
        set_sensor_raise_thresholds(value, sensor)
    elif threshold == "lower":
        sensor_thresholds_clear[sensor] = value
        set_sensor_clear_thresholds(value, sensor)
    all_alarms = get_sensor_alarms()


def get_alarms():
    ''' Returns a list of all alarms currently active '''
    active_alarms = {**over_thresh_alarms, **sensor_down_alarms, **peer_alarms, **oob_alarms}
    return active_alarms
