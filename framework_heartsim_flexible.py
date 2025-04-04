import numpy as np
import time
from smbus2 import SMBus
import argparse
import busio
import board
import adafruit_mcp4725 as a
import time
import paho.mqtt.client as mqtt
from utils import pulse_gen_with_rr, sine_gen_with_rr_v4, get_mac, sine_gen_with_rr_irr_v2, write_mqtt




def main(hr, rr, rr_step, max_amp, min_amp, waveform, duty_circle, minute, duration=180, samples=410):
    freq = hr/60
    delay_req = 1/(samples)

    i2c = busio.I2C(board.SCL, board.SDA)
    dac = a.MCP4725(i2c, address=0x60)

    try:
        while(minute>0):
            hr_array = np.repeat(hr, duration)
            rr_array = np.repeat(rr, duration)
            # if waveform == "pulse":
                # wave = pulse_gen_with_rr(min_amp, max_amp, samples, duty_circle, duration, hr, rr, rr_step)
            # elif waveform == "sine":
            wave = sine_gen_with_rr_irr_v2(min_amp, max_amp, samples, duty_circle, duration, hr, rr, rr_step)
            
            start_time = time.time()
            print('Start time:', start_time)
            for i in range(0,len(wave)-1):
                val = int(wave[i])
                dac.raw_value = val
                # delay = delay_req - 0.00041 - 0.00025   
                delay = delay_req - 0.00041 - 0.00025 - 0.000035
                time.sleep(delay)
 
            end_time = time.time()
            # print('End time:', end_time)
            
            ## Write Labels for 10s, each label after 1s

#            write_mqtt(hr_array, rr_array, start_time, 1)

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
#        write_mqtt(hr_array, rr_array, start_time, 1)
        print('End')


if __name__== '__main__':
    
    parser = argparse.ArgumentParser(description='Heartbeat Simulator', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--hr', type=int)
    parser.add_argument('--rr', type=int)
    parser.add_argument('--minute', type=int, default=1, help='Length of Working (Unit: min), default=3')
    args = parser.parse_args()


    rr_step = 0.04
    max_amp, min_amp =  200, 0
    duty_circle = 0.5
    waveform = 'sine'
#    waveform = 'pulse'

    print(get_mac())
    
    main(args.hr, args.rr, rr_step, max_amp, min_amp, waveform, duty_circle, args.minute)
