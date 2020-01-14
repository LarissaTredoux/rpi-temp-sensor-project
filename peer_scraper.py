''' Author: Larissa Tredoux
    
    Contains a method that scrapes the prometheus
    client page for a Raspberry Pi to check if it is
    online '''
import urllib.request

def check_peer(target_url):
    ''' Scrapes the prometheus client for the Raspberry Pi
        and returns 1 if the target Raspberry Pi is online and
        returns 0 if it is not. '''
    try:
        data = urllib.request.urlopen(target_url)
        for line in data:
            if line == b'up 1.0\n':
                return 1
        return 0
    except (urllib.error.URLError, ConnectionResetError) as error:
        return 0
