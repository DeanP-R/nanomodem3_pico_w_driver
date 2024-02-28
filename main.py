#########################################################################################################
# Filename      : main.py                                                                               #
# Version       : 0.1.0                                                                                 #
# Description   : Main program for handling communications for MEng Ropeless Fishing Gear Demonstrator. #
# Author        : Dean Rowlett                                                                          #
# Target        : Raspberry Pi Pico W with MicroPython                                                  #
# Interpreter   : MicroPython v1.22.1                                                                   #
# IDE           : Thonny 4.1.4                                                                          #
# Last Updated  : 11th February 2024                                                                    #
#########################################################################################################
from nm3_pico_driver import NM3Driver
from servo import Servo
pico = NM3Driver()
pico.connect()
address, v = pico.get_address()
print(f"Address: {address} Volts: {v}")
ping = pico.ping(115)
print(f"Distance to 115: {ping}")
pico.send_unicast_message(115, "RELEASE")

servo = Servo(26)


while True:
    response = pico.read_response().strip()  # Strip whitespace from response
    print(f"Response: '{response}'")  
    if response == '#U07RELEASE':
        servo.move(180)
        print("Driving Servo to unlock")
    elif response:  # Only attempt to lock if there's a non-empty response
        servo.move(90)
        print("Driving Servo to lock")
    else:
        print("No response or awaiting further instructions")

        
