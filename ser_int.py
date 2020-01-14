''' Serial interface between raspberry pi board and sensirion ek-h4 sensor '''

import time
import binascii
import threading
import serial

lock = threading.Lock()

def open_serial_port(port, baudrate):
    ''' Opens connection to the specified usb-port with specified baudrate'''
    ser = serial.Serial('/dev/' + port)  # open serial port
    ser.baudrate = baudrate
    return ser

def read(port):
    ''' Reads data from the port '''
    answer = []
    flg = 0
    for i in range(1024):  # data assumed to be less than 1024 words
        a = port.read(size=1)
        if a == '':
            break
        elif flg == 0 and a == b'~':
            flg = 1
        elif flg == 1 and a == b'~':
            break
        elif flg == 1:
            answer.append(str(binascii.hexlify(a))[2:-1])
        else:
            print(a)
    return answer

def write(port, command):
    ''' Writes a command to the port '''
    port.write(binascii.a2b_hex(command))

def ask(port, command):
    '''Read response to command and convert it to 16-bit integer.
    Returns : list of values
    '''
    global lock
    lock.acquire()
    write(port, command)
    time.sleep(0.1)
    a = read(port)
    lock.release()
    return a
    