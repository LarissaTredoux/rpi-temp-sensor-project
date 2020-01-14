''' Interfaces with DHT-11 sensor '''
import Adafruit_DHT

def read_dht_temp_hum():
    ''' Returns a list containing temperature and humidity
        values read from the DHT-11 sensor '''
    humidity, temperature = Adafruit_DHT.read_retry(11, 4)

    report = []
    report.append(temperature)
    report.append(humidity)

    return report
