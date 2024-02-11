#########################################################################################################
# Filename      : nm3_pico_driver.py                                                                    #
# Version       : 0.1.0                                                                                 #
# Description   : Driver for interfacing with the NanoModem V3.2 acoustic modem on Raspberry Pi Pico W. #
# Author        : Dean Rowlett                                                                          #
# Target        : Raspberry Pi Pico W with MicroPython                                                  #
# Interpreter   : MicroPython v1.22.1                                                                   #
# IDE           : Thonny 4.1.4                                                                          #
# Last Updated  : 11th February 2024                                                                    #
#########################################################################################################
from machine import UART, Pin
import time

class NM3Driver:
    def __init__(self, uart_id=0, baudrate=9600, tx_pin=16, rx_pin=17):
        self.uart = UART(uart_id, baudrate=baudrate)

    def connect(self):
        # Specify TX and RX pins during connection
        self.uart.init(baudrate=9600, bits=8, parity=None, stop=1, tx=Pin(16), rx=Pin(17))

    def send_command(self, command):
        self.uart.write(command.encode('utf-8'))

    def read_response(self, timeout=2):
        end_time = time.ticks_add(time.ticks_ms(), timeout * 1000)
        response = bytearray()
        while time.ticks_diff(end_time, time.ticks_ms()) > 0:
            if self.uart.any():
                byte = self.uart.read(1)
                response.extend(byte)
                if response.endswith(b'\r\n'):  # End of message
                    break
        return response.decode()

    def get_address(self):
        self.send_command('$?')
        response = self.read_response()
        if not response:
            raise Exception("No Response")
        if response.startswith('#A'):
            addr = response.split('V')[0][2:]
            return int(addr)
        if not response.startswith('#A'):
            raise Exception("Incorrect Response")


pico = NM3Driver()
pico.connect()
addr = pico.get_address()
print(f"Address: {addr}")
