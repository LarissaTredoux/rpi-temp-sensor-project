from gpiozero import CPUTemperature

def read_internal_temp():
    cpu = CPUTemperature()
    print(cpu.temperature)
    return cpu.temperature

read_internal_temp()