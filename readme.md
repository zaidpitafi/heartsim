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

- To Run the simulator use the framework_heartsim_continous.py file and specify option.
- Option 0 is for arbitrary HR and RR combination, in this case specify HR and RR
- Option 1 to 5 are for the standard HR and RR combinations

### Example Usage

- For Option 0

You can specify any combination of heart rate (HR) and respiration rate (RR). Example: 

`
python3 heartsim.py --option 0 --hr 96 --rr 16
`


- For Options 1-5

You can choose specific HR and RR combination by using different options. Example: 

`
python3 heartsim.py --option 1
`