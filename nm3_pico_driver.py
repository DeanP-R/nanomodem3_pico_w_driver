#########################################################################################################
# Filename      : nm3_pico_driver.py                                                                    #
# Version       : 0.1.3                                                                                #
# Description   : Driver for interfacing with the NanoModem V3.2 acoustic modem on Raspberry Pi Pico W. #
# Author        : Dean Rowlett                                                                          #
# Target        : Raspberry Pi Pico W with MicroPython                                                  #
# Interpreter   : MicroPython v1.22.1                                                                   #
# IDE           : Thonny 4.1.4                                                                          #
# Last Updated  : 11th February 2024                                                                    #
#########################################################################################################
from machine import UART, Pin
import time
# Global debug flag
debug = True

def debug_print(message):
    if debug:
        print(message)
        
class NM3Driver:
    # Initialization with an optional cipher and encryption flag
    def __init__(self, uart_id=0, baudrate=9600, tx_pin=16, rx_pin=17, cipher=None, use_encryption=False):
        self.uart = UART(uart_id, baudrate=baudrate)
        self.cipher = cipher
        self.use_encryption = use_encryption
        debug_print(f"Initialized NM3Driver with encryption {'enabled' if use_encryption else 'disabled'}")


    def connect(self):
        self.uart.init(baudrate=9600, bits=8, parity=None, stop=1)

    def send_command(self, command):
        # Modified send_command method with debug_print for logging
        debug_print(f"Sending command: {command}")
        if self.use_encryption and self.cipher is not None:
            command = self.cipher.encrypt(command.encode('utf-8'))
            debug_print("Command encrypted")
        else:
            command = command.encode('utf-8')
        self.uart.write(b'$' + command + b'\r\n')
        debug_print("Command sent")

    def read_response(self, timeout=2):
        end_time = time.ticks_add(time.ticks_ms(), timeout * 1000)
        response = bytearray()
        while time.ticks_diff(end_time, time.ticks_ms()) > 0:
            if self.uart.any():
                response.extend(self.uart.read(1))
                if response.endswith(b'\r\n'):
                    break
        if self.use_encryption and self.cipher is not None:
            return self.cipher.decrypt(response[:-2]).decode()  # Exclude \r\n before decryption
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

    def get_voltage(self):
        self.send_command('$?')
        response = self.read_response()
        if response.startswith('#A'):
            raw_voltage = int(response.split("V")[1][:5])
            voltage = raw_voltage*15/65536
            return (voltage)
        if not response:
            raise Exception("No Response")
            debug_print(f"Response: {response}")
        if not response.startswith('#A'):
            debug_print(f"Response: {response}")
            raise Exception("Incorrect Response")
        
    def ping(self, address):
        command = f"$P{address:03d}"
        debug_print(f"Ping Comand: {command}")
        new_command = self.send_command(command)
        # Wait for command acknowledgment
        ack = self.read_response()
        if ack is None or not ack.startswith('$P'):
            debug_print("No acknowledgment received")
            return None
        
        # Wait for range response or timeout
        response = self.read_response()
        if response is None:
            debug_print("No range response received")
            return None

        if response.startswith('#R'):
            raw_distance = int(response.split("T")[1])
            sound_velocity = 340  # m/s in water 1500 m/s in air 340
            c = 0.00003125  # Conversion factor
            distance = raw_distance * sound_velocity * c
            return distance
        elif response.startswith('#TO'):
            debug_print("Timeout waiting for a response from the target modem")
            return None
        else:
            debug_print("Unexpected response:", response)
            return None
        
    def send_unicast_message(self, address, message):
        message_length = len(message)
        command = f"$U{address:03d}{message_length:02d}{message}"
        self.send_command(command)
        return self.read_response()
        
from ucryptolib import aes
import hashlib

# Modify AESCipher to handle padding correctly and ensure it fits the use case
class AESCipher:
    def __init__(self, passphrase, iv):
        self.key = self.generate_key(passphrase)
        self.iv = iv

    def generate_key(self, passphrase):
        hashed_passphrase = hashlib.sha256(passphrase.encode()).digest()
        return hashed_passphrase

    def encrypt(self, plaintext):
        debug_print(f"Encrypting plaintext: {plaintext}")
        cipher = aes(self.key, 2, self.iv)  # AES-256-CBC mode
        # Pad plaintext for encryption to make its length a multiple of 16 bytes
        padded_plaintext = plaintext + b'\0' * (16 - len(plaintext) % 16)
        ciphertext = cipher.encrypt(padded_plaintext)
        debug_print(f"Encrypt Cipher Length: {len(ciphertext)}")
        debug_print(f"Ciphertext: {ciphertext}")
        return ciphertext


    def decrypt(self, ciphertext):
        debug_print(f"Decrypting ciphertext: {ciphertext}")
        debug_print(f"Decrypt Cipher Length: {len(ciphertext)}")
        # Check if the ciphertext length is a multiple of 16
        if len(ciphertext) % 16 != 0:
            debug_print("Ciphertext block size is not a multiple of 16 bytes. Skipping decryption.")
            return ciphertext  # Optionally handle this case differently
        cipher = aes(self.key, 2, self.iv)
        decrypted_plaintext = cipher.decrypt(ciphertext)
        debug_print(f"Decrypted plaintext: {decrypted_plaintext}")
        return decrypted_plaintext.rstrip(b'\r\n\0')
