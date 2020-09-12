''' Author: Larissa Tredoux

    Prometheus client for measurement metrics from sensirion ek-h4 sensor '''
import time
import threading

from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY

from sensor_detect import get_measurements
from alarms import alarm_check
from read_rpi_yaml import get_peers, get_own_name, get_sensor_names, get_sensor_measures
from peer_scraper import check_peer
from notification_bot import telegram_bot_sendtext

class CustomCollector(object):
    ''' Builds a custom collector for temperature and humidity metrics '''
    def collect(self):
        ''' Get metrics for temperature and humidity measurements '''

        sensors = get_sensor_names()
        sensor_measures = get_sensor_measures()

        yield GaugeMetricFamily('up', '1 if Rpi is up', value=1)

        temp_metric_fam = CounterMetricFamily('sensor_temperature',
                                    'Temperature measured by each sensor', labels=['sensor'])

        hum_metric_fam = CounterMetricFamily('sensor_humidity',
                                    'Humidity measured by each sensor', labels=['sensor'])

        sensor_num = 1
        for sensor in sensors:
            value = get_measurements(sensor_num)
            if value is not None:
                if sensor_measures[sensor_num - 1] == "humidity":
                    hum_metric_fam.add_metric([str(sensor_num)], str(value))
                elif sensor_measures[sensor_num - 1] == "temperature":
                    temp_metric_fam.add_metric([str(sensor_num)], str(value))
            sensor_num += 1

        for item in sensor_measures:
            if item == "temperature":
                yield temp_metric_fam
                break
        for item in sensor_measures:
            if item == "humidity":
                yield hum_metric_fam
                break


class UpdateTemps(threading.Thread):
    ''' Update values for temperature and humidity, and wait a bit'''
    def run(self):
        sensor_list = get_sensor_names()
        peer_dict = get_peers()
        while True:
            sensor_vals = []
            counter = 1
            for sensor_item in sensor_list:
                value = get_measurements(counter)
                sensor_vals.append(value)
            peer_states = []
            for peer_ip in peer_dict.values():
                online = check_peer('http://' + str(peer_ip)+ ':8000/')
                peer_states.append(online)
            alarm_check(sensor_vals, peer_states)
            time.sleep(10)


if __name__ == '__main__':
    # Start up the server to expose the metrics.
    name = get_own_name()
    sensor_names = get_sensor_names()
    start_http_server(8000)
    info = "INFO:\n" + "This device's name is: " + name + "\n"
    info += "The sensors connected to this device are:\n"
    for sensor_name in sensor_names:
        info += sensor_name
        info += "\n"
    telegram_bot_sendtext(info)
    thred1 = UpdateTemps()
    thred1.start()
    REGISTRY.register(CustomCollector())
