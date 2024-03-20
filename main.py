#########################################################################################################
# Filename      : main.py                                                                               #
# Version       : 0.1.4                                                                                 #
# Description   : Main program for handling communications for MEng Ropeless Fishing Gear Demonstrator. #
#                 Designed for the embedded system on sea bed. Listens for Command and drives servo to  #
#                 toggle magnet on.                                                                     #
# Author        : Dean Rowlett                                                                          #
# Target        : Raspberry Pi Pico W with MicroPython                                                  #
# Interpreter   : MicroPython v1.22.1                                                                   #
# IDE           : Thonny 4.1.4                                                                          #
# Last Updated  : 20th March 2024                                                                       #
#########################################################################################################
from nm3_pico_driver import NM3Driver
from servo import Servo
import machine
import utime
import uasyncio as asyncio

# Configuration constants for hardware control and timing
SERVO_PIN = 26  # GPIO pin number to which the servo is connected
RELEASE_POSITION = 180  # Servo position for releasing the magnet
SET_POSITION = 90  # Servo position for setting the magnet
ACTIVE_PHASE_HOURS = 4  # Duration of the active phase in hours
DEEP_SLEEP_HOURS = 20  # Duration of deep sleep in hours

# Initialize NM3Driver for underwater communication
pico = NM3Driver()
pico.connect()

# Initialize the Servo object for controlling the magnet mechanism
servo = Servo(SERVO_PIN)

def process_response():
    """
    Reads and processes the incoming response from the NM3Driver.
    Checks for a specific command to toggle the magnet's state.
    """
    response = pico.read_response().strip()  # Strip whitespace from the response
    print(f"Response: '{response}'")
    if response == '#U07RELEASE':
        servo.move(RELEASE_POSITION)  # Move servo to release position
    elif response:  # Process non-empty responses only
        servo.move(SET_POSITION)  # Default servo position to set the magnet

async def go_to_sleep(sleep_duration_hours):
    """
    Initiates an asynchronous deep sleep task.

    :param sleep_duration_hours: Duration of the deep sleep in hours.
    """
    sleep_duration_ms = sleep_duration_hours * 3600000  # Convert hours to milliseconds
    await asyncio.sleep(sleep_duration_ms / 1000)  # Convert milliseconds to seconds for asyncio.sleep
    machine.deepsleep(sleep_duration_ms)  # Enter deep sleep for the specified duration

async def main():
    """
    Main function to run the program.
    Schedules the active phase and deep sleep based on user input.
    """
    start_hour = int(input("Enter the start hour for the 4-hour window (0-23): "))
    current_time = utime.localtime()
    current_seconds = current_time[3] * 3600 + current_time[4] * 60 + current_time[5]
    target_start_seconds = start_hour * 3600
    delay_seconds = target_start_seconds - current_seconds if current_seconds <= target_start_seconds else (24 * 3600 - current_seconds) + target_start_seconds
    
    print(f"Delaying for {delay_seconds} seconds until the start of the 4-hour window.")
    await asyncio.sleep(delay_seconds)  # Delay execution until the start of the 4-hour window

    # Compute the duration of the active phase in seconds
    nine_hours_in_seconds = ACTIVE_PHASE_HOURS * 60 * 60
    start_time = utime.time()
    while utime.time() - start_time < nine_hours_in_seconds:
        process_response()

    # Schedule asynchronous transition to deep sleep after the active phase
    asyncio.create_task(go_to_sleep(DEEP_SLEEP_HOURS))

# Execute the main function within an asyncio event loop
asyncio.run(main())
