''' Interfaces with a rpi yaml config file '''
import yaml

yaml_file = "rpi.yaml"

def get_own_name():
    ''' Returns the name of the RPi that owns
        the yaml file '''
    dictionary = get_dict()
    return dictionary['name']

def get_sensor_type():
    ''' Returns the sensor type for the RPi
        that owns the yaml file '''
    dictionary = get_dict()
    return dictionary['sensor-type']

def get_chat_ids():
    ''' Returns a list of at ids for all the users that need to
        receive messages from the telegram bot '''
    dictionary = get_dict()
    return dictionary['chat-ids']

def get_sensor_names():
    ''' Returns the names of the sensors that are
        connected to the RPi that owns the yaml file '''
    dictionary = get_dict()
    sensor_list = dictionary['sensors']
    sensors = []
    for sensor in sensor_list:
        sensors.append(sensor['name'])
    return sensors

def get_sensor_measures():
    ''' Returns a list of what is measured by each
        sensor '''
    dictionary = get_dict()
    sensor_list = dictionary['sensors']
    measurements = []
    for sensor in sensor_list:
        measurements.append(sensor['measures'])
    return measurements

def get_sensor_alarms():
    ''' Returns a dictionary of names (key) and messages
        (value) for alarms that can go off for the
        sensors connected to the RPi that owns the yaml file '''
    dictionary = get_dict()
    sensor_list = dictionary['sensors']
    alarms = {}
    counter = 1
    for sensor in sensor_list:
        alarm_messages = sensor['alarms']
        for message in alarm_messages:
            alarms[message['name'] + str(counter)] = "".join(message['message'])
        counter += 1
    return alarms

def get_sensor_raise_thresholds():
    ''' Returns a list of the upper thresholds for the sensors
        connected to the RPi that owns the yaml file '''
    dictionary = get_dict()
    sensor_list = dictionary['sensors']
    thresholds = []
    for sensor in sensor_list:
        thresholds.append(sensor['raise'])
    return thresholds

def get_sensor_clear_thresholds():
    ''' Returns a list of the lower thresholds for the sensors
        connected to the RPi that owns the yaml file '''
    dictionary = get_dict()
    sensor_list = dictionary['sensors']
    thresholds = []
    for sensor in sensor_list:
        thresholds.append(sensor['clear'])
    return thresholds

def get_alarm_names():
    ''' Returns a list of names of the possible alarms that
        can go off for the sensors connected to the RPi
        that owns the yaml file '''
    dictionary = get_dict()
    sensor_list = dictionary['sensors']
    alarm_names = []
    for sensor in sensor_list:
        alarm_messages = sensor['alarms']
        for message in alarm_messages:
            if message['name'] not in alarm_names:
                alarm_names.append(message['name'])
    return alarm_names

def get_peers():
    ''' Returns a dictionary of peers (name - key and ip - value) that the
        Pi that owns the yaml file needs to check up on '''
    dictionary = get_dict()
    peer_list = dictionary['peers']
    peers = {}
    for peer in peer_list:
        peers[peer['name']] = peer['ip']
    return peers

def get_peer_alarms():
    ''' Returns a dictionary containing the name (key)
        and message (value) for each alarm that could
        go off for a peer of the RPi '''
    dictionary = get_dict()
    peer_list = dictionary['peers']
    alarms = {}
    counter = 1
    for peer in peer_list:
        alarm_messages = peer['alarm']
        for message in alarm_messages:
            alarms[message['name'] + str(counter)] = "".join(message['message'])
        counter += 1
    return alarms

def get_peer_alarm_names():
    ''' Returns a list of names of the possible alarms that
        can go off for the peers checked by the RPi
        that owns the yaml file '''
    dictionary = get_dict()
    peer_list = dictionary['peers']
    alarm_names = []
    for peer in peer_list:
        alarm_messages = peer['alarm']
        for message in alarm_messages:
            if message['name'] not in alarm_names:
                alarm_names.append(message['name'])
    return alarm_names

def get_shutdown_list():
    ''' Returns a list of dictionaries containing shutdown
        details for servers (ip, user and password)'''
    dictionary = get_dict()
    shutdown_list = dictionary['shutdown-list']
    return shutdown_list

def set_sensor_clear_thresholds(threshold, sensor_idx):
    ''' Sets the upper threshold for a specified sensor '''
    global yaml_file
    dictionary = get_dict()
    sensor_list = dictionary['sensors']
    sensor_list[sensor_idx]['clear'] = threshold
    dictionary['sensors'] = sensor_list

    with open(yaml_file, 'w') as file:
        yaml.dump(dictionary, file)

def set_sensor_raise_thresholds(threshold, sensor_idx):
    ''' Sets the lower threshold for a specified sensor '''
    global yaml_file
    dictionary = get_dict()
    sensor_list = dictionary['sensors']
    sensor_list[sensor_idx]['raise'] = threshold
    sensor_list[sensor_idx]['raise_str'] = str(threshold)
    sensor_list[sensor_idx]['alarms'][0]['message'][2] = str(threshold)
    dictionary['sensors'] = sensor_list
    with open(yaml_file, 'w') as file:
        yaml.dump(dictionary, file)


def get_dict():
    ''' Returns the contents of the yaml file as a dictionary '''
    global yaml_file
    stream = open(yaml_file, 'r')
    dictionary = yaml.load(stream, Loader=yaml.FullLoader)
    return dictionary
