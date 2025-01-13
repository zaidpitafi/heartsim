import numpy as np
import pandas as pd
import neurokit2 as nk
import time
from smbus2 import SMBus
import math
import numpy as np
import matplotlib.pyplot as plt
from datasim.ecg.ecg_simulate import *
#from utils import write_influx
# from mqtt_to_influxdb import *
from mqtt import *
from pulse import *
import argparse

def main(args):
    
    heart_rate = args.hr
    freq = heart_rate/60
    sample_rate = 41  ## number of points from DAC 
    delay_req = 1/(freq*sample_rate)

    amplitude = args.amplitude  ### Strength of the Signal

    ibi = args.ibi_interval

    # i2c = busio.I2C(board.SCL, board.SDA)
    # dac = a.MCP4725(i2c, address=0x60)

    if args.wave_type == 'sine':
        wave = sine_gen(amplitude,sample_rate)
    elif args.wave_type == 'ecg':
        wave= ecg_gen(amplitude,sample_rate)
    elif args.wave_type == 'scg':
        wave= scg_gen(amplitude,sample_rate)
    elif args.wave_type == 'hat':
        wave= mexhat_gen(amplitude,sample_rate)
    elif args.wave_type == 'sym4':
        wave= sym4_gen(amplitude,sample_rate)

    try:
        while(True):
            start_time = time.time()
            for i in range(0,41):
                print(wave[i])
                # dac.raw_value = int(wave[i])
                time.sleep(delay_req)
            end_time = time.time()
            total_time = end_time - start_time
            actual_delay = total_time / sample_rate
            print(f"Calculated frequency: {1 / (actual_delay * sample_rate):.2f} Hz")

            time.sleep(ibi)  ##IBI
    except KeyboardInterrupt:
        print('End')


if __name__== '__main__':
    parser = argparse.ArgumentParser(description='Heartbeat Simulator', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--unit", type=str, help='BDot MAC address', default='11:01:11:01:11:01')
    parser.add_argument("--start", type=str, default=None, help='start time')
    parser.add_argument("--end", type=str, default=None, help='end time')        
    parser.add_argument('--wave_type', type=str, default='scg',
                        help='the input wave shape')       
    parser.add_argument('--hr', type=int, default='100',
                        help='the sampling rate of DAC board, divisible by 4096')                                
    parser.add_argument('--amplitude', type=int, default='1024', 
                        help='the strength of signal')
    parser.add_argument('--rr', type=int, default=10, help='rr duration')
    parser.add_argument('--ibi_interval', type=int, default=0, help='rr duration')

    args = parser.parse_args()
    main(args)