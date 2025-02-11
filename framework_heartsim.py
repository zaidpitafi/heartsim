import numpy as np
import pandas as pd
import neurokit2 as nk
import time
from smbus2 import SMBus
import math
import numpy as np
import matplotlib.pyplot as plt
from datasim.ecg.ecg_simulate import *
from utils import write_influx
from mqtt_to_influxdb import *
from mqtt import *
from pulse import *
import argparse
import busio
import board
import adafruit_mcp4725 as a

influx = {'ip':'http://sensorserver.engr.uga.edu', 'db':'shake',
                  'user':'algtest', 'passw':'sensorweb711', 
                  'ssl':False}

table_name = 'Z'
data_name = 'value'

def main(args):
    
    hr = args.hr
    duration = args.duration
    freq = hr/60
    samples = args.sampling_rate  ## number of points from DAC 
    delay_req = 1/(samples)
    amplitude = args.amplitude  ### Strength of the Signal
    

    hb = int(freq * duration)

    ibi = args.ibi_interval
    unit = args.unit
    rr = args.rr

    i2c = busio.I2C(board.SCL, board.SDA)
    dac = a.MCP4725(i2c, address=0x60)

    if args.wave_type == 'sine':
        wave = sine_gen_with_rr_v2(amplitude, samples, duration, hr, rr)
    elif args.wave_type == 'ecg':
        wave= ecg_gen(amplitude,samples)
    elif args.wave_type == 'scg':
        wave= scg_gen(amplitude,samples)
    elif args.wave_type == 'hat':
        wave= mexhat_gen(amplitude,samples,duration,hr)
    elif args.wave_type == 'sym4':
        wave= sym4_gen(amplitude,samples,duration,hr)
    elif args.wave_type == 'db12':
        wave= db12_gen(amplitude,samples,duration,hr)

    # wave = rr_gen_ming(wave, rr)
    simulated_data = []
    diff = 0
    init_time = time.time()
    # init_time = epoch_to_datetime_est(init_time)
    k = 10
    try:
        while(k>0):
            wave= sine_gen_with_rr_v4(amplitude,samples,duration,hr,rr)
            # wave= mexhat_gen_with_rr(amplitude, samples, duration, hr, rr)
            start_time = time.time()
            print('Start time:', start_time)
            for i in range(0,len(wave)-1):
                val = int(wave[i])
                # print(wave[i])
                dac.raw_value = val
                delay = delay_req - 0.00041     # inherent delay of DAC is subtracted, 0.00041 
                time.sleep(delay)
            end_time = time.time()
            print('End time:', end_time)
            total_time = (end_time - start_time)
            diff = end_time - start_time
            
            total_cycles = hr
            frequ = total_cycles/total_time

            calc_hr = 60 * frequ
            # print("Actual Diff", diff)
            print(f"Calculated HR: {calc_hr:.2f} bpm")
            print('hr:', hr)
            
            #write_influx(influx= influx, unit=unit,table_name=table_name, data_name='value', data=wave, start_timestamp=start_time, fs = samples)
            simulated_data.append(list(wave)+[start_time]+[hr]+[rr])
            time.sleep(ibi)  ##IBI
            k -=1
            hr +=12
            
    except KeyboardInterrupt:
        print('End')
    simulated_data = np.asarray(simulated_data)
    np.save(f'wave_{args.wave_type}_rr_{args.rr}_time_{init_time}',simulated_data)
    print('Data Saved')


if __name__== '__main__':
    parser = argparse.ArgumentParser(description='Heartbeat Simulator', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--unit", type=str, help='BDot MAC address', default='12:02:12:02:12:02')
    parser.add_argument("--start", type=str, default=None, help='start time')
    parser.add_argument("--end", type=str, default=None, help='end time')        
    parser.add_argument('--wave_type', type=str, default='sine',
                        help='the input wave shape')       
    parser.add_argument('--hr', type=int, default='42',
                        help='the sampling rate of DAC board, divisible by 4096')                                
    parser.add_argument('--amplitude', type=int, default='2047', 
                        help='the strength of signal')
    parser.add_argument('--sampling_rate', type=int, default='410', 
                        help='the strength of signal')
    parser.add_argument('--rr', type=int, default=40, help='rr duration')
    parser.add_argument('--ibi_interval', type=float, default=0, help='rr duration')
    parser.add_argument('--duration', type=int, default=120, help='duration in seconds')

    args = parser.parse_args()
    main(args)
