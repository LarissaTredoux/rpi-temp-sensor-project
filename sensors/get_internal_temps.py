''' Contains a method to read the internal (CPU)
    temperature of a Raspberry Pi '''
from gpiozero import CPUTemperature

def read_internal_temp():
    ''' Returns the CPU temperature of the
        Raspberry Pi '''
    cpu = CPUTemperature()
    return cpu.temperature
