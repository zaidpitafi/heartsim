## Table of Contents
- [Installation](#installation)
- [Usage](#usage)

## Prerequisites
- Python 3.8 or higher

## Installation
- Controller Board: [Raspberry Pi 4 Model B Rev 1.4](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/)
- Motor [60VC003](https://www.smoothmotor.com/video/products-detail-3207327)
- DAC Board [MCP4725](https://www.microchip.com/en-us/product/mcp4725)
- Power Amplifier [OPA541](https://www.ti.com/lit/ds/symlink/opa541.pdf?ts=1736251871643&ref_url=https%253A%252F%252Fwww.mouser.cn%252F)
- Independent [Power Supply] (https://a.co/d/hWlwYX6) 

![Flow Chart](arch.png)
![Installation](pic.jpg)

## Usage

- To Run the simulator code, use the framework_heartsim.py file and provide following arguments
- --wave_type (type of wave to simulate e.g., sine, mexican hat, sym4, scg, ecg)
- --ibi_interval (in milliseconds)
- --hr
- --rr
- --amplitude (maximum is 2048, default is 1024)
- --duration (The duration of signal in seconds)

### Example Usage
'
python3 framework_simulator.py --wave_type='sine' --hr=80 --rr=12 --amplitude=2048 --duration=120

- The frequency of sine wave  is calculated by = 1/(sampling rate)
- The Heart Rate is found by multiplying frequency by 60 

