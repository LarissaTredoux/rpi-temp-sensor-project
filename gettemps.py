''' Functions to fetch the temperature and humidity from the sensirion ek-h4 sensor '''
from serint import open_serial_port, ask


SERIAL_PORT = "ttyUSB0"
BAUDRATE = 115200

ser = open_serial_port(SERIAL_PORT, BAUDRATE)

def get_temperature():
    ''' Fetches and parses the temperature value from the sensirion ek-h4 sensor '''
    ret = ask(ser, r"7e4700b87e")
    values = []
    for j in range(4):
        if ret[2 + 2 * j] == "7f" and ret[2 + 2 * j + 1] == "ff":
            values.append(None)
        else:
            values.append(cal_ret(ret[2 + 2 * j] + ret[2 + 2 * j + 1]))
    print(values)
    return values

def get_humidity():
    ''' Fetches and parses humidity values from sensirion ek-h4 sensor '''
    ret = ask(ser, r"7e4600b97e")
    print(ret)
    values = []
    for j in range(4):
        if ret[2 + 2 * j] == "7f" and ret[2 + 2 * j + 1] == "ff":
            values.append(None)
        else:
            values.append(cal_ret(ret[2 + 2 * j] + ret[2 + 2 * j + 1]))
    print(values)
    return values

def cal_ret(value):
    ''' Parses hex value from serial comms '''
    bits = 16
    value = int(value, 16)
    # compute the 2's compliment of int value
    if (value & (1 << (bits - 1))) != 0:  # if sign bit is set, e.g., 8bit: 128-255
        value = value - (1 << bits)  # compute negative value
    return float(value) / 100.0  # return positive value as is
