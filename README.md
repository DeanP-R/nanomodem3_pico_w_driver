# MEng Ropeless Fishing Gear Demonstrator

## Overview
This repository contains the software for the MEng project focused on developing a ropeless fishing gear system. Designed for deployment in marine environments, the system utilizes Raspberry Pi Pico W units for both seabed and surface operations, facilitating underwater communication through acoustic modems and enabling user interaction via Bluetooth connectivity.

## Components
The project is divided into three main components:

1. **NM3 Pico Driver (`nm3_pico_driver.py`)**: A driver for interfacing with the NanoModem V3.2 acoustic modem on Raspberry Pi Pico W, allowing acoustic communication in underwater environments.

2. **Seabed Modem Program (`main.py`)**: The main application for the modem stationed on the seabed. It listens for commands from the surface to activate a servo mechanism that releases the fishing gear.

3. **Surface Modem Program (`surface_main.py`)**: The application for the surface-based Raspberry Pi Pico W. It connects to a user's phone via Bluetooth, allowing them to send commands to the seabed modem.

## Requirements
- Raspberry Pi Pico W
- MicroPython v1.22.1
- Thonny IDE 4.1.4 or compatible IDE
- NanoModem V3.2 acoustic modem
- Servo motor compatible with Raspberry Pi Pico W
- Bluetooth library for Raspberry Pi Pico W (for the surface unit)
## Custom App and Hardware

### Custom App
This project includes a proprietary mobile application designed for communicating with the surface unit. The app facilitates sending commands to release the fishing gear via the surface unit's Bluetooth interface.

### Custom PCB/Schematic
The hardware for this project is built on custom-designed PCBs that incorporate the MAX3232 chip for signal processing, essential for reliable underwater acoustic communication. While the system is intended for use with our specific hardware design, enthusiasts and researchers can create an identical setup. Schematics and PCB design files are available in the repository for those interested in replicating or extending the system.

## Setup and Deployment

### Hardware Setup
1. **Custom PCB Assembly**: Assemble the custom PCB incorporating the MAX3232 chip according to the provided schematics. This setup is required to match the signal protocol for the NanoModem V3.2.
2. **NanoModem V3.2 Connection**: Connect the NanoModem V3.2 to the Raspberry Pi Pico W following the NM3Driver configuration detailed in the schematic.
3. **Servo Motor Setup**: Attach the servo motor to the designated GPIO pin on the Pico W for the seabed unit as per the PCB design.
4. **Bluetooth Module Configuration**: Ensure the Bluetooth module is correctly set up on the surface unit Pico W, allowing for seamless communication with the mobile app.

### Software Installation
1. **MicroPython**: Flash MicroPython v1.22.1 onto the Raspberry Pi Pico W units.
2. **Script Upload**: Utilize Thonny IDE or a comparable tool to upload the `.py` files to the respective Pico W units—`main.py` for the seabed unit and `surface_main.py` for the surface unit.
3. **Configuration**: Adjust configuration constants in the scripts as necessary to match your hardware setup, ensuring proper operation of the devices.

### Operation Instructions
1. **Power Up**: Turn on both the seabed and surface Raspberry Pi Pico W units.
2. **App Connection**: Use a Bluetooth-enabled phone to connect to the surface unit via the proprietary mobile app designed for this system.
3. **Release Command**: Send a release command from the phone app to the surface unit. The surface unit will then acoustically relay the command to the seabed unit.
4. **Gear Release**: Upon receiving the command, the seabed unit's servo activates, toggling the magnet mechanism and releasing the fishing gear.

## Troubleshooting
- **Connection Verification**: Ensure all connections, including those on the custom PCB, are secure and that the hardware components are powered.
- **Bluetooth Connectivity**: Verify the Bluetooth connection between the phone and the surface unit is active and stable.
- **Acoustic Communication**: Check the acoustic link between the surface and seabed units for potential interference or obstructions that may impede signal transmission.

## Authors
- Dean Rowlett
- Ross Porteuous

## Note on Collaboration and Environmental Impact
We're actively seeking collaboration with veterinarians and environmental scientists to assess and mitigate any potential environmental impact of deploying this system in marine environments. Our goal is to ensure the system is both effective for its intended purpose and sustainable from an ecological perspective.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements
- Special thanks to the MEng project advisors and contributors.
- Raspberry Pi Foundation for the Raspberry Pi Pico W and MicroPython support.
