import numpy as np
import time
from smbus2 import SMBus
import argparse
import busio
import board
import adafruit_mcp4725 as a
import time
import paho.mqtt.client as mqtt
from utils import pulse_gen_with_rr, sine_gen_with_rr_v4, get_mac, write_mqtt

def main(hr, rr, rr_step, max_amp, min_amp, waveform, duty_circle, minute, duration=60, samples=410):   
    samples = args.sampling_rate  ## number of points from DAC 
    delay_req = 1/(samples) ## 2 to avoid double counting
    min_amp = args.min_amp  ### Strength of the Signal
    max_amp = args.max_amp
    rr_step = args.rr_step
    rr = args.rr

    i2c = busio.I2C(board.SCL, board.SDA)
    dac = a.MCP4725(i2c, address=0x60)

    simulated_data = []
    
    try:
        while(minute>0):
            if waveform == "pulse":
                wave = pulse_gen_with_rr(min_amp, max_amp, samples, duty_circle, duration, hr, rr, rr_step)
            elif waveform == "sine":
                wave = sine_gen_with_rr_v4(min_amp, max_amp, samples, duty_circle, duration, hr, rr, rr_step)
 
            start_time = time.time()
            print('Start time:', start_time)

            for i in range(0,len(wave)-1):
                val = int(wave[i])
                dac.raw_value = val
                delay = delay_req - 0.00041 - 0.00025 - 0.000035
                time.sleep(delay)

            end_time = time.time()
            # print('End time:', end_time)
            
            ## Write Labels for 10s, each label after 1s
            hr_array = np.repeat(hr, args.duration)
            rr_array = np.repeat(rr, args.duration)
            write_mqtt(hr_array, rr_array, start_time, 1)

            final_time = time.time()
            print('Final time:', final_time)
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
    
    """
    option 1, HR 40, RR 8
    option 2, HR 64, RR 16
    option 3, HR 96, RR 24
    option 4, HR 128, RR 32
    option 5, HR 160, RR 40
    """
    parser = argparse.ArgumentParser(description='Heartbeat Simulator', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--option', type=int, default=1, help='Different HR and RR Combination')
    parser.add_argument('--minute', type=int, default=3, help='Length of Working (Unit: min), default=3')
    parser.add_argument('--hr', type=int, default=40, help='HR to enter')
    parser.add_argument('--rr', type=int, default=8, help='RR to enter')
    parser.add_argument('--rr_step', type=float, default=0.02, help='Resp Effect')
    parser.add_argument('--max_amp', type=int, default=200, help='Amplitude')
    parser.add_argument('--duty_circle', type=float, default=0.5, help='Duty Cycle of Wave (0 to 1)')
    parser.add_argument('--waveform', type=str, default='sine', help='Sine for HR < 140, pulse for >140')
    args = parser.parse_args()

    if args.option == 0:
        hr, rr, rr_step = args.hr, args.rr, args.rr_step
        max_amp, min_amp = args.max_amp, 0
        duty_circle = args.duty_circle
        waveform = args.waveform
    elif args.option == 1:
        hr, rr, rr_step = 40, 8, 0.02
        max_amp, min_amp = 200, 0
        duty_circle = 0.5
        waveform = 'sine'
    elif args.option == 2:
        hr, rr, rr_step = 64, 16, 0.02
        max_amp, min_amp =  200, 0
        duty_circle = 0.5
        waveform = 'sine'
    elif args.option == 3:
        hr, rr, rr_step = 96, 24, 0.02
        max_amp, min_amp =  200, 0
        duty_circle = 0.5
        waveform = 'sine'   
    elif args.option == 4:
        hr, rr, rr_step = 128, 32, 0.02
        max_amp, min_amp =  200, 0
        duty_circle = 0.5
        waveform = 'sine'  
    elif args.option == 5:
        hr, rr, rr_step = 160, 40, 0.04
        max_amp, min_amp =  512, 0
        duty_circle = 0.05
        waveform = 'pulse'
    
    main(hr, rr, rr_step, max_amp, min_amp, waveform, duty_circle, args.minute)
