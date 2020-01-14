''' Author: Larissa Tredoux

    Contains all sensor-specific methods necessary '''

from read_rpi_yaml import get_sensor_type, get_sensor_measures
from sensors.get_internal_temps import read_internal_temp
from sensors.get_sensirion_temps import get_humidity, get_temperature
from sensors.get_dht_temps import read_dht_temp_hum

def get_measurements(sensor_idx):
    ''' Checks which sensor is being used and returns
        measurement from that sensor '''
    sensor_type = get_sensor_type()
    sensor_measures = get_sensor_measures()
    sensor_idx = sensor_idx - 1 # aligning index
    if sensor_type == "internal":
        if sensor_measures[sensor_idx] == "temperature":
            temp = read_internal_temp()
            return temp
        return None
    if sensor_type == "sensirion ek-h4":
        if sensor_measures[sensor_idx] == "temperature":
            temps = get_temperature()
            return temps[sensor_idx]
        if sensor_measures[sensor_idx] == "humidity":
            hums = get_humidity()
            return hums[sensor_idx]
        return None
    if sensor_type == "dht-11":
        temp_hum = read_dht_temp_hum()
        if sensor_measures[sensor_idx] == "temperature":
            return temp_hum[0]
        if sensor_measures[sensor_idx] == "humidity":
            return temp_hum[1]
        return None
    return None

