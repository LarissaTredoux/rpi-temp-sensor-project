import yaml

def get_own_name():
    dictionary = get_dict()
    print(dictionary['name'])
    return dictionary['name']

def get_sensor_type():
    dictionary = get_dict()
    print(dictionary['sensor-type'])
    return dictionary['sensor-type']

def get_chat_ids():
    dictionary = get_dict()
    print(dictionary['chat-ids'])
    return dictionary['chat-ids']

def get_sensor_names():
    dictionary = get_dict()
    sensor_list = dictionary['sensors']
    sensors = []
    for sensor in sensor_list:
        sensors.append(sensor['name'])
    print(sensors)
    return sensors

def get_sensor_alarms():
    dictionary = get_dict()
    sensor_list = dictionary['sensors']
    alarms = {}
    counter = 1
    for sensor in sensor_list:
        alarm_messages = sensor['alarms']
        for message in alarm_messages:
            alarms[message['name'] + str(counter)] = "".join(message['message'])
        counter += 1
    print(alarms)
    return alarms

def get_sensor_raise_thresholds():
    dictionary = get_dict()
    sensor_list = dictionary['sensors']
    thresholds = []
    for sensor in sensor_list:
        thresholds.append(sensor['raise'])
    print(thresholds)
    return thresholds

def get_sensor_clear_thresholds():
    dictionary = get_dict()
    sensor_list = dictionary['sensors']
    thresholds = []
    for sensor in sensor_list:
        thresholds.append(sensor['clear'])
    print(thresholds)
    return thresholds

def get_alarm_names():
    dictionary = get_dict()
    sensor_list = dictionary['sensors']
    alarm_names = []
    for sensor in sensor_list:
        alarm_messages = sensor['alarms']
        for message in alarm_messages:
            if message['name'] not in alarm_names:
                alarm_names.append(message['name'])
    print(alarm_names)
    return alarm_names

def get_peers():
    dictionary = get_dict()
    peer_list = dictionary['peers']
    peers = {}
    for peer in peer_list:
        peers[peer['name']] = peer['ip']
    print(peers)
    return peers

def set_sensor_clear_thresholds(threshold, sensor_idx):
    dictionary = get_dict()
    sensor_list = dictionary['sensors']
    sensor_list[sensor_idx - 1]['clear'] = threshold
    dictionary['sensors'] = sensor_list

    with open("rpi1.yaml", 'w') as file:
        yaml.dump(dictionary, file)

def set_sensor_raise_thresholds(threshold, sensor_idx):
    dictionary = get_dict()
    sensor_list = dictionary['sensors']
    sensor_list[sensor_idx - 1]['raise'] = threshold
    sensor_list[sensor_idx - 1]['raise_str'] = str(threshold)
    sensor_list[sensor_idx - 1]['alarms'][0]['message'][2] = str(threshold)
    dictionary['sensors'] = sensor_list
    with open(r"rpi1.yaml", 'w') as file:
        yaml.dump(dictionary, file)

def get_dict():
    stream = open("rpi1.yaml", 'r')
    dictionary = yaml.load(stream, Loader=yaml.FullLoader)
    return dictionary
    