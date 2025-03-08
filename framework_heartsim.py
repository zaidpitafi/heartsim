import numpy as np
import pandas as pd
import neurokit2 as nk
import time
from smbus2 import SMBus
import math
import numpy as np
import matplotlib.pyplot as plt
from datasim.ecg.ecg_simulate import *
from utils import write_influx, write_mqtt
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
    delay_req = 1/(samples) ## 2 to avoid double counting
    min_amp = args.min_amp  ### Strength of the Signal
    max_amp = args.max_amp
    rr_step = args.rr_step

    ibi = args.ibi_interval
    unit = args.unit
    rr = args.rr

    i2c = busio.I2C(board.SCL, board.SDA)
    dac = a.MCP4725(i2c, address=0x60)

    if args.wave_type == 'sine':
        wave = sine_gen_with_rr_v4(min_amp, max_amp, samples, duration, hr, rr, rr_step)
    elif args.wave_type == 'ecg':
        wave= ecg_gen(max_amp,samples)
    elif args.wave_type == 'scg':
        wave= scg_gen(max_amp,samples)
    elif args.wave_type == 'hat':
        wave= mexhat_gen_with_rr(max_amp,samples,duration,hr)
    elif args.wave_type == 'sym4':
        wave= sym4_gen(max_amp,samples,duration,hr)
    elif args.wave_type == 'db12':
        wave= db12_gen(max_amp,samples,duration,hr)

    simulated_data = []

    hr_list = [40, 66, 80, 120, 160]
    rr_list = [8, 16, 24, 32, 40]
    k = 50
    fs = 1

    try:
        wave = sine_gen_with_rr_v4(min_amp, 4095, samples, 60, 126, 12, 0.15)
        while(k>0):
            # if hr>150:
            #     rr_step = 0.05

            #### Select Wave Here
            # wave = mexhat_gen_with_rr(min_amp, max_amp, samples, duration, hr, rr, rr_step)
            wave = pulse_gen_with_rr(min_amp, max_amp, samples, duration, hr, rr, rr_step)
            # wave = sine_gen_with_rr_v4(min_amp, max_amp, samples, duration, hr, rr, rr_step)
 
            start_time = time.time()
            print('Start time:', start_time)
            for i in range(0,len(wave)-1):

                val = int(wave[i])
                dac.raw_value = val
                delay = delay_req - 0.00041     # inherent delay of DAC is subtracted, 0.00041  
                time.sleep(delay)

            end_time = time.time()
            # print('End time:', end_time)
            
            ## Write Labels for 10s, each label after 1s
            hr_array = np.repeat(hr, args.duration)
            rr_array = np.repeat(rr, args.duration)
            write_mqtt(hr_array, rr_array, start_time, fs)


            final_time = time.time()
            print('Final time:', final_time)
            total_time = (end_time - start_time)
            
            total_cycles = hr/60 * duration
            frequ = total_cycles/total_time

            calc_hr = 60 * frequ
            print(f"Calculated HR: {calc_hr:.2f} bpm")
            print('hr:', hr, "rr:", rr)
            
            simulated_data.append(list(wave)+[start_time]+[calc_hr]+[rr])
            time.sleep(ibi)  ##IBI
            k -=1

            # hr +=12
            # if k<5:
            #     hr = hr_list[5-k]
            #     rr = rr_list[5-k]
            # rr +=4
            # rr_step += 0.08


            
    except KeyboardInterrupt:
        print('End')
    simulated_data = np.asarray(simulated_data)
    # np.save(f'wave_{args.wave_type}_rr_{args.rr}_step_{rr_step}_time_{init_time}',simulated_data)
    print('Data Saved')


if __name__== '__main__':
    parser = argparse.ArgumentParser(description='Heartbeat Simulator', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--unit", type=str, help='BDot MAC address to Post Labels', default='12:02:12:02:12:02')
    parser.add_argument("--start", type=str, default=None, help='start time')
    parser.add_argument("--end", type=str, default=None, help='end time')        
    parser.add_argument('--wave_type', type=str, default='mexhat',
                        help='the input wave shape')       
    parser.add_argument('--hr', type=int, default=160,
                        help='the desired Heart Rate')
    parser.add_argument('--rr', type=int, default=40, help='The desired Respiratory Rate')
    parser.add_argument('--rr_step', type=float, default=0.04, help='rr envelope step')
    parser.add_argument('--min_amp', type=int, default=0, 
                        help='the min strength of signal')                                
    parser.add_argument('--max_amp', type=int, default=512, 
                        help='the max strength of signal')
    parser.add_argument('--sampling_rate', type=int, default=410, 
                        help='the number of samples')
    parser.add_argument('--ibi_interval', type=float, default=0, help='inter beat interval')
    parser.add_argument('--duration', type=int, default=60, help='duration in seconds')

    args = parser.parse_args()
    main(args)
