#########################################################################################################
# Filename      : surface_main.py                                                                       #
# Version       : 0.1.0                                                                                 #
# Description   : Main program for handling communications for MEng Ropeless Fishing Gear Demonstrator. #
#                 Designed for the embedded system on water surface.Connects to user app through        #
#                 bluetooth. User can then send release commands to selected modem on sea floor.        #
#                 toggle magnet on.                                                                     #
# Author        : Ross Porteuous                                                                        #
# Target        : Raspberry Pi Pico W with MicroPython                                                  #
# Interpreter   : MicroPython v1.22.1                                                                   #
# IDE           : Thonny 4.1.4                                                                          #
# Last Updated  : 20th March 2024                                                                       #
#########################################################################################################

import sys
import aioble
import bluetooth
import machine
import uasyncio as asyncio
from micropython import const

# --- Modem imports ---
from nm3_pico_driver import NM3Driver
from servo import Servo

# Defined variables and constants
BLE_APPEARANCE = const(0x04)
ADV_INTERVAL_MS = 250_000

led = machine.Pin("LED", machine.Pin.OUT)
connection = None
connected = False

# Generic service declaration
generic_uuid = bluetooth.UUID("0daf39f8-ccac-4833-87bf-47ca19320abd")
generic_service = aioble.Service(generic_uuid)

# Trap service declaration
trap_uuid = bluetooth.UUID("3fefbcb1-e7b1-4d14-8252-135c94a4f0cf")
toggle_trap_uuid = bluetooth.UUID("aff35ec3-73fc-44dd-bd28-9da6c772cdc1")
trap_service = aioble.Service(trap_uuid)
toggle_characteristic = aioble.Characteristic(trap_service, toggle_trap_uuid, write=True, read=True, notify=True, capture=True)

# Registering services 
aioble.register_services(generic_service, trap_service)


async def status_task():
    """"Outputs status"""
    while True:
        if not connected:
            print("Not connected")
            await asyncio.sleep_ms(1000)
            continue
        await asyncio.sleep_ms(10)
        
        
async def receive_data(pico):
    """Receives data from mobile app"""
    print(f'Reading: {toggle_characteristic}')
    while True:
        data = await toggle_characteristic.written()
        
        if data:
            pico.send_unicast_message(data)
            
        await asyncio.sleep(1)
        

async def peripheral_task(pico):
    global connected, connection
    while True:
        connected = False
        async with await aioble.advertise(
            ADV_INTERVAL_MS,
            name="Modem",
            appearance=BLE_APPEARANCE,
            services=[generic_uuid]
        ) as connection:
            connected = True
            print(f"Connection from: {connection.device}")
            print(f"Connected: {connected}")
            
            await receive_data(pico)
            
            await connection.disconnected()
            print("Disconnected")
            


async def blink_task():
    """Blinks LED"""
    toggle = True
    while True:
        led.value(toggle)
        toggle = not toggle
        blink = 1000
        if connected:
            blink = 1000
        else:
            blink = 250
        await asyncio.sleep_ms(blink)
        
        
async def main():
    # --- Code from nanomodem main.py ---
    pico = NM3Driver()
    pico.connect()
    address, v = pico.get_address()
    print(f"Address: {address} Volts: {v}")
    ping = pico.ping(160)
    print(f"Distance to 115: {ping}")
    
    tasks = [
        asyncio.create_task(status_task()),
        asyncio.create_task(peripheral_task(pico)),
        asyncio.create_task(blink_task()),
    ]
    await asyncio.gather(*tasks)
    
    
asyncio.run(main())

        
        
        
        
        
        
        
        
