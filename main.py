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
from nm3_pico_driver import NM3Driver
from servo import Servo

message = "Ocean Lab Test"
modem = 169

pico = NM3Driver()
pico.connect()
servo = Servo(27)

servo.move(180)
