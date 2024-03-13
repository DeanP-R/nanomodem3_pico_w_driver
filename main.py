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
import machine
import utime

servo_pin = 26
servo_modem = 160
surface_modem = 169

pico = NM3Driver()
pico.connect()

servo = Servo(servo_pin)

# Function to process incoming responses
def process_response():
    response = pico.read_response().strip()  # Strip whitespace from response
    print(f"Response: '{response}'")
    if response == '#U07RELEASE':
        servo.move(180)
    elif response:  # Only attempt to lock if there's a non-empty response
        servo.move(90)

# Active phase: 9 hours
# Convert 9 hours into seconds for the loop
nine_hours_in_seconds = 9 * 60 * 60
start_time = utime.time()
while utime.time() - start_time < nine_hours_in_seconds:
    process_response()
    utime.sleep(1)  # Sleep 1 second between readings to reduce power consumption, not sure if this will effect functionality

# After the active phase, go into deep sleep for 15 hours
# 15 hours = 54,000,000 milliseconds
machine.deepsleep(54000000)
        
