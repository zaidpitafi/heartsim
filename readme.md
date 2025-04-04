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

- To Run the simulator code in 5 options testing mode, use the framework_heartsim_continous.py file

### Example Usage
`
python3 framework_simulator_continous.py 
`

## Usage

- To Run the simulator code in any option, use the framework_heartsim_flexible.py

### Example Usage
`
python3 framework_simulator_continous_flexible.py --hr 120 --rr 28

