#########################################################################################################
# Filename      : main.py                                                                               #
# Version       : 0.1.2                                                                                 #
# Description   : Main program for handling communications for MEng Ropeless Fishing Gear Demonstrator. #
#                 Designed for the embedded system on sea bed. Listens for Command and drives servo to  #
#                 toggle magnet on.                                                                     #
# Author        : Dean Rowlett                                                                          #
# Target        : Raspberry Pi Pico W with MicroPython                                                  #
# Interpreter   : MicroPython v1.22.1                                                                   #
# IDE           : Thonny 4.1.4                                                                          #
# Last Updated  : 13th March 2024                                                                       #
#########################################################################################################
from nm3_pico_driver import NM3Driver
from servo import Servo

servo_pin = 26
servo_modem = 160
surface_modem = 169

pico = NM3Driver()
pico.connect()

servo = Servo(servo_pin)


while True:

    response = pico.read_response().strip()  # Strip whitespace from response
    print(f"Response: '{response}'")  
    if response == '#U07RELEASE':
        servo.move(180)
    elif response:  # Only attempt to lock if there's a non-empty response
        servo.move(90)
    else:
        continue
        
