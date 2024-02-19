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

    def get_voltage(self):
        self.send_command('$?')
        response = self.read_response()
        if response.startswith('#A'):
            raw_voltage = int(response.split("V")[1][:5])
            voltage = raw_voltage*15/65536
            return (voltage)
        if not response:
            raise Exception("No Response")
        if not response.startswith('#A'):
            raise Exception("Incorrect Response")
        
    def ping(self, address):
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
            print("No range response received")
            return None

        if response.startswith('#R'):
            raw_distance = int(response.split("T")[1])
            sound_velocity = 1500  # m/s in water
            c = 0.00003125  # Conversion factor
            distance = raw_distance * sound_velocity * c
            return distance
        elif response.startswith('#TO'):
            print("Timeout waiting for a response from the target modem")
            return None
        else:
            print("Unexpected response:", response)
            return None
        
    def send_unicast_message(self, address, message):
        message_length = len(message)
        command = f"$U{address:03d}{message_length:02d}{message}"
        self.send_command(command)
        return self.read_response()
        
import hashlib
from aes import AESModeOfOperationCTR
import os

class AESCipher:
    def __init__(self, passphrase):
        # Initialize the AESCipher instance with a passphrase.
        # This passphrase will be used to generate a unique AES key.
        
        # The AES key is generated in the `generate_aes_key` method and stored for future use.
        # A nonce (number used once) is also generated for use in the encryption/decryption process,
        # ensuring that the encryption is unique each time, even with the same key and plaintext.
        self.key = self.generate_aes_key(passphrase)
        self.nonce = os.urandom(8)  # Generates a random 8-byte nonce for AES CTR mode

    def generate_aes_key(self, passphrase):
        # Generate a 32-byte AES key from the given passphrase.
        # This is achieved by hashing the passphrase using SHA-256, which outputs a 32-byte hash.
        
        hasher = hashlib.sha256()  # Create a new SHA-256 hash object
        hasher.update(passphrase.encode('utf-8'))  # Hash the passphrase (after encoding it to bytes)
        return hasher.digest()  # Return the resulting 32-byte hash as the AES key

    def encrypt(self, plaintext):
        # Encrypt the given plaintext using AES in CTR (Counter) mode.
        # This mode requires a nonce, which we generated in the constructor.
        # The AES CTR mode is advantageous for several reasons, including allowing for stream encryption and not requiring padding.
        
        aes = AESModeOfOperationCTR(self.key, nonce=self.nonce)  # Initialize AES CTR mode with the key and nonce
        return aes.encrypt(plaintext)  # Encrypt and return the plaintext

    def decrypt(self, ciphertext):
        # Decrypt the given ciphertext using AES in CTR mode.
        # As with encryption, decryption requires the same key and nonce that were used for encryption.
        
        aes = AESModeOfOperationCTR(self.key, nonce=self.nonce)  # Initialize AES CTR mode with the key and nonce
        return aes.decrypt(ciphertext)  # Decrypt and return the ciphertext


#pico = NM3Driver()
#pico.connect()
#voltage = pico.get_voltage()
#print(f"Voltage: {voltage}")