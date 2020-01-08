''' Prometheus client for measurement metrics from sensirion ek-h4 sensor '''
import time
import threading

from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY

from gettemps import get_temperature, get_humidity
from alarms import alarm_check

class CustomCollector(object):
    ''' Builds a custom collector for temperature and humidity metrics '''
    def collect(self):
        ''' Get metrics for temperature and humidity measurements '''

        temps = get_temperature()
        hums = get_humidity()

        yield GaugeMetricFamily('up', '1 if Rpi is up', value=1)

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


class UpdateTemps(threading.Thread):
    ''' Update values for temperature and humidity, and wait a bit'''
    def run(self):

        while True:
            get_humidity()
            temps = get_temperature()
            alarm_check(temps)
            time.sleep(10)


if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    thred1 = UpdateTemps()
    thred1.start()
    REGISTRY.register(CustomCollector())
