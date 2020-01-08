''' Prometheus client for measurement metrics from sensirion ek-h4 sensor '''
import time
import threading

from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY

#from gettemps import get_temperature, get_humidity
from get_internal_temps import read_internal_temp
from alarms import alarm_check
from read_rpi_yaml import get_sensor_type

class CustomCollector(object):
    ''' Builds a custom collector for temperature and humidity metrics '''
    def collect(self):
        ''' Get metrics for temperature and humidity measurements '''

        sensor_type = get_sensor_type("rpi2.yaml")
        yield GaugeMetricFamily('up', '1 if Rpi is up', value=1)

        if sensor_type == "sensirion ek-h4":
            temps = get_temperature()
            hums = get_humidity()
            
            c = CounterMetricFamily('sensor_temperature',
                                    'Temperature measured by each sensor', labels=['sensor'])
            counter = 1
            for t in temps:
                if t is not None:
                    c.add_metric([str(counter)], str(t))
                counter += 1
            yield c

            c2 = CounterMetricFamily('sensor_humidity',
                                    'Humidity measured by each sensor', labels=['sensor'])
            counter2 = 1
            for h in hums:
                if h is not None:
                    c2.add_metric([str(counter2)], str(h))
                counter2 += 1
            yield c2

        elif sensor_type == "internal":
            temp = read_internal_temp()
            c = CounterMetricFamily('sensor_temperature',
                                    'Temperature measured by each sensor', labels=['sensor'])
            if temp is not None:
                c.add_metric([str(1)], str(temp))


class UpdateTemps(threading.Thread):
    ''' Update values for temperature and humidity, and wait a bit'''
    def run(self):
        sensor_type = get_sensor_type("rpi2.yaml")
        while True:
            if sensor_type == "sensirion ek-h4":
                get_humidity()
                temps = get_temperature()
                alarm_check(temps)
            elif sensor_type == "internal":
                temp = read_internal_temp()
                temps = []
                temps.append(temp)
            alarm_check(temp)
            time.sleep(10)


if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    thred1 = UpdateTemps()
    thred1.start()
    REGISTRY.register(CustomCollector())
