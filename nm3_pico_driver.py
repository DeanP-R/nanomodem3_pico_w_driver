#########################################################################################################
# Filename      : nm3_pico_driver.py                                                                    #
# Version       : 0.2.1                                                                                 #
# Description   : Driver for interfacing with the NanoModem V3.2 acoustic modem on Raspberry Pi Pico W. #
# Author        : Dean Rowlett                                                                          #
# Target        : Raspberry Pi Pico W with MicroPython                                                  #
# Interpreter   : MicroPython v1.22.1                                                                   #
# IDE           : Thonny 4.1.4                                                                          #
# Last Updated  : 11th March 2024                                                                       #
#########################################################################################################
from machine import UART, Pin
import time
from ucryptolib import aes
import hashlib
# Global debug flag
debug = False
TIMEOUT_SECONDS = 10
def debug_print(message):
    if debug:
        print(message)
        
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
                byte = self.uart.read()
                response.extend(byte)
                debug_print(f"Data Received: {response}")
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
            voltage_raw = int(response.split('V')[1])
            voltage = voltage_raw * 15 / 65536
            return int(addr), voltage
        if not response.startswith('#A'):
            raise Exception("Incorrect Response")
        
    def get_voltage(self, address):
        command = f"$V{address:03d}"
        debug_print(f"Voltage Command: {command}")
        self.send_command(command)
        
        # Wait for acknowledgment
        ack_received = False
        start_time = time.time()
        while not ack_received:
            response = self.read_response()
            if response:
                if response.startswith(f"$V{address:03d}"):
                    ack_received = True
                elif time.time() - start_time > TIMEOUT_SECONDS:
                    raise TimeoutError("Acknowledgment timeout")

        # Wait for the actual response
        start_time = time.time()
        while True:
            response = self.read_response()
            if response:
                if response.startswith(f"#B{address:03d}"):
                    raw_voltage = int(response.split("V")[1][:5])
                    voltage = raw_voltage*15/65536
                    return (voltage)
                elif time.time() - start_time > TIMEOUT_SECONDS:
                    raise TimeoutError("Response timeout")

    def query_modem(self):
        self.send_command('$?')
        
        # Wait for the actual response
        start_time = time.time()
        while True:
            response = self.read_response()
            if response:
                if response.startswith('#A'):
                    parts = response.split('V')
                    addr = int(parts[0][2:])
                    voltage_raw = int(parts[1])
                    voltage = voltage_raw * 15 / 65536
                    return addr, voltage
                elif time.time() - start_time > TIMEOUT_SECONDS:
                    raise TimeoutError("Response timeout")
            elif time.time() - start_time > TIMEOUT_SECONDS:
                raise TimeoutError("Response timeout")





        
    def ping(self, address):
        water = 1500    # 1500m/s in water
        air = 340       # 340m/s in air
        command = f"$P{address:03d}"
        self.send_command(command)
        
        # Wait for command acknowledgment
        ack = self.read_response()
        if ack is None or not ack.startswith('$P'):
            print("No acknowledgment received")
            return None
        
        # Wait for range response or timeout
        response = self.read_response()
        if response is None:
            debug_print(f"No range response received: {response}")
            return None

        if response.startswith('#R'):
            raw_distance = int(response.split("T")[1])
            sound_velocity = air 
            c = 0.00003125  # Conversion factor
            distance = raw_distance * sound_velocity * c
            return distance
        elif response.startswith('#TO'):
            debug_print(f"Timeout waiting for a response from the target modem: {response}")
            return None
        else:
            debug_print(f"Unexpected response: {response}")
            return None
        
    def send_unicast_message(self, address, message):
        message_length = len(message)
        command = f"$U{address:03d}{message_length:02d}{message}"
        self.send_command(command)
        debug_print(f"Sending Command: {command}")
        return self.read_response()
    
    def send_release_command(self, address):
        message_length = len("RELEASE")
        command = f"$U{address:03d}{message_length:02d}{"RELEASE"}"
        self.send_command(command)
        debug_print(f"Sending Command: {command}")
        return self.read_response()

    def send_lock_command(self, address):
        message_length = len("LOCK")
        command = f"$U{address:03d}{message_length:02d}{"LOCK"}"
        self.send_command(command)
        debug_print(f"Sending Command: {command}")
        return self.read_response()

