#########################################################################################################
# Filename      : main.py                                                                               #
# Version       : 0.0.1                                                                                 #
# Description   : Main program for handling communications for MEng Ropeless Fishing Gear Demonstrator. #
# Author        : Dean Rowlett                                                                          #
# Target        : Raspberry Pi Pico W with MicroPython                                                  #
# Interpreter   : MicroPython v1.22.1                                                                   #
# IDE           : Thonny 4.1.4                                                                          #
# Last Updated  : 11th February 2024                                                                    #
#########################################################################################################
"""
from nm3_pico_driver import NM3Driver
message = "Ocean Lab Test"
modem = 169

pico = NM3Driver()
pico.connect()
#addr = pico.get_address()
#print(f"Address: {addr}")

voltage = pico.get_voltage()
print(f"Voltage: {voltage}")
distance = str(pico.ping(modem))

print(f"Distance to modem 169: {distance}")
send_test = pico.send_unicast_message(modem, distance)
print(f"Sending message: {message}. To modem: {modem}. Returning: {send_test}.")
"""
class Servo:
    def __init__(self, MIN_DUTY=300000, MAX_DUTY=2300000, pin=27, freq=50):
        self.pwm = machine.PWM(machine.Pin(pin))
        self.pwm.freq(freq)
        self.MIN_DUTY = MIN_DUTY
        self.MAX_DUTY = MAX_DUTY
        
    def rotateDeg(self, deg):
        if deg < 0:
            deg = 0
        elif deg > 180:
            deg = 180
        duty_ns = int(self.MAX_DUTY - deg * (self.MAX_DUTY-self.MIN_DUTY)/180)
        self.pwm.duty_ns(duty_ns)

servo = Servo()
servo.rotateDeg(90)