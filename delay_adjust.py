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
import threading
from scipy import signal
from utils import pulse_gen_with_rr, sine_gen_with_rr_v4 

def main(hr, rr, rr_step, max_amp, min_amp, waveform, minute, duration=60, samples=410):
    freq = hr/60
    delay_req = 1/(samples)

    i2c = busio.I2C(board.SCL, board.SDA)
    dac = a.MCP4725(i2c, address=0x60)

    try:
        while(minute>0):
            if waveform == "sine":
                # wave = sine_gen_with_rr_v4(min_amp, max_amp, samples, duration, hr, rr, rr_step)
                wave = sine_gen_with_rr_v4(min_amp, max_amp, samples, 0.5, duration, hr, rr, rr_step)
            start_time = time.time()
            print('Start time:', start_time)
            for i in range(0,len(wave)-1):
                val = int(wave[i])
                dac.raw_value = val
                delay = delay_req - (0.00041 + 0.00025 + 0.000035)  
                time.sleep(delay)

            end_time = time.time()
            print('End time:', end_time)
            print('Time taken:', end_time - start_time)
            
            extra_time_per_iteration = (end_time - start_time - 60) / (60 * samples)
            print('Extra time per iteration:', extra_time_per_iteration)
            print('Delay should be:', 0.00041 + 0.00025 + 0.000035 + extra_time_per_iteration) 
            
            total_time = (end_time - start_time)
            
            total_cycles = hr/60 * duration
            frequ = total_cycles/total_time

            calc_hr = 60 * frequ
            print(f"Calculated HR: {calc_hr:.2f} bpm")
            print('hr:', hr, "rr:", rr)
            minute -=1
            
    except KeyboardInterrupt:
        print('End')


if __name__== '__main__':
    hr, rr, rr_step = 60, 10, 0.01
    max_amp, min_amp = 200, 0
    
    waveform = 'sine'

    
    main(hr, rr, rr_step, max_amp, min_amp, waveform, 3)
