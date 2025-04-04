import numpy as np
import time
from smbus2 import SMBus
import math
import argparse
import busio
import board
import adafruit_mcp4725 as a
import struct
import time
import paho.mqtt.client as mqtt
import threading
from scipy import signal

from framework_heartsim import main

if __name__== '__main__':
    
    """
    option 1, HR 40, RR 8
    option 2, HR 64, RR 16
    option 3, HR 96, RR 24
    option 4, HR 128, RR 32
    option 5, HR 160, RR 40
    """
    parser = argparse.ArgumentParser(description='Heartbeat Simulator', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--minute', type=int, default=2, help='Length of Working (Unit: min), default=3')
    args = parser.parse_args()

    for option in range(1, 6):

        if option == 1:
            hr, rr, rr_step = 40, 8, 0.02
            max_amp, min_amp = 200, 0
            duty_circle = 0.5
            waveform = 'sine'
        elif option == 2:
            hr, rr, rr_step = 64, 16, 0.02
            max_amp, min_amp =  200, 0
            duty_circle = 0.5
            waveform = 'sine'
        elif option == 3:
            hr, rr, rr_step = 96, 24, 0.02
            max_amp, min_amp =  200, 0
            duty_circle = 0.5
            waveform = 'sine'   
        elif option == 4:
            hr, rr, rr_step = 128, 32, 0.02
            max_amp, min_amp =  200, 0
            duty_circle = 0.5
            waveform = 'sine'  
        elif option == 5:
            hr, rr, rr_step = 160, 40, 0.04
            max_amp, min_amp =  512, 0
            duty_circle = 0.05
            waveform = 'pulse'  
        
        # print(get_mac())
        main(hr, rr, rr_step, max_amp, min_amp, waveform, duty_circle, args.minute)
