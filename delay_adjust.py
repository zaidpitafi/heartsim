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



"""
************************ Used for Waveform Generation ************************
"""


def generate_increasing_amplitude_wave_array(i,step_size):
    # Create an array starting from 1.1, increasing by step up to length i
    step = step_size
    wave_array = np.arange(1, 1 + step * i, step)
    return wave_array


def pulse_base(min_val, max_val, samples, duration):
    fs = samples  # Sampling frequency in Hz
    t = np.linspace(0, duration, fs, endpoint=False)  # 1 second duration
    duty_cycle = 0.05  # 50% duty cycle
    f_hr = 1
    amp =1
    # Generate pulse waveform
    pulse_wave = (np.sin(2 * np.pi * f_hr * t) >= np.cos(np.pi * duty_cycle)).astype(int)
    pulse_wave= ((pulse_wave-np.min(pulse_wave))/(np.max(pulse_wave)-np.min(pulse_wave)) * amp)
    
    pulse_wave = signal.resample(pulse_wave,duration*samples)
    pulse_wave= min_val + ((pulse_wave - np.min(pulse_wave)) / (np.max(pulse_wave) - np.min(pulse_wave))) * (max_val - min_val)
    pulse_wave = abs(pulse_wave)
    return pulse_wave


def pulse_gen_with_rr(min_val, max_val, samples, duration, hr, rr, rr_step):
    wave_a = pulse_base(min_val, max_val, samples, 1)

    val = int(np.round(hr/rr))
    reps = int(np.round(rr/60*duration))

    ## For RR effect
    if hr < 120: val = val-1
    scaling_factors = generate_increasing_amplitude_wave_array(val, rr_step)
    rsa = np.tile(wave_a, len(scaling_factors)) * np.repeat(scaling_factors, len(wave_a))
    wave_f = np.tile(rsa,reps)

    # Without RR effect
    # reps = int(hr)
    # wave_f = np.tile(wave_a, reps)

    new_length = duration*samples
    wave = np.interp(np.linspace(0, len(wave_f)-1, new_length), np.arange(len(wave_f)), wave_f)
    wave = min_val + ((wave - np.min(wave)) / (np.max(wave) - np.min(wave))) * (max_val - min_val)
    wave = abs(wave)
    return wave


def sine_gen_with_rr_dc(amp, samples, duty_cycle):

    f_hr = 1
    duration = 1
    sampling_rate = samples
    phase = 0

    val = int(duty_cycle*samples)
    rem = samples - val
    zer_array = np.zeros(rem)
  
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    sine_wave = np.sin(2 * np.pi * f_hr * t - phase)
    wave = sine_wave

    # wave = signal.resample(wave, val)
    # wave = np.concatenate((zer_array, wave),axis=0)
    wave = np.where(wave < 0, 0, wave)

    return wave


def sine_gen_with_rr_v4(min_amp, max_amp, samples, duration, hr, rr, rr_step):
    min_val = min_amp
    max_val = max_amp

    duty_cycle = 0.75

    ## Select base sine wave - with or without Duty Cycle
    wave = sine_gen_with_rr_dc(max_val, samples, duty_cycle)

    ### For RR effect uncomment this
    val = int(np.round(hr/rr))
    reps = int(np.round(rr/60*duration))
    if hr <140: val = val-1
    scaling_factors = generate_increasing_amplitude_wave_array(val, rr_step)
    rsa = np.tile(wave, len(scaling_factors)) * np.repeat(scaling_factors, len(wave))
    wave_f = np.tile(rsa,reps)

    ### For RR effect comment this
    # reps = int(hr)
    # wave_f = np.tile(wave, reps)

    ## Resample to intended duration
    new_length = duration*samples
    wave = np.interp(np.linspace(0, len(wave_f)-1, new_length), np.arange(len(wave_f)), wave_f)
    
    ## Select Normalization
    wave = min_val + ((wave - np.min(wave)) / (np.max(wave) - np.min(wave))) * (max_val - min_val)
    
    wave = abs(wave)
    return wave


def main(hr, rr, rr_step, max_amp, min_amp, waveform, minute, duration=60, samples=410):
    freq = hr/60
    delay_req = 1/(samples)

    i2c = busio.I2C(board.SCL, board.SDA)
    dac = a.MCP4725(i2c, address=0x60)

    try:
        while(minute>0):
            if waveform == "pulse":
                wave = pulse_gen_with_rr(min_amp, max_amp, samples, duration, hr, rr, rr_step)
            elif waveform == "sine":
                wave = sine_gen_with_rr_v4(min_amp, max_amp, samples, duration, hr, rr, rr_step)
            
            start_time = time.time()
            print('Start time:', start_time)
            for i in range(0,len(wave)-1):
                val = int(wave[i])
                dac.raw_value = val
                delay = delay_req - (0.00041 - 0.00025 - 0.000035)  
                time.sleep(delay)

            end_time = time.time()
            print('End time:', end_time)
            print('Time taken:', end_time - start_time)
            
            extra_time_per_iteration = (end_time - start_time - 60) / (60 * samples)
            print('Extra time per iteration:', extra_time_per_iteration)
            print('Delay should be:', 0.00041 + 0.00025 + 0.000035 + extra_time_per_iteration) 
            
            ## Write Labels for 10s, each label after 1s
            hr_array = np.repeat(hr, duration)
            rr_array = np.repeat(rr, duration)

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
    hr, rr, rr_step = 60, 10, 0.01
    max_amp, min_amp = 200, 0
    waveform = 'sine'

    
    print(f"the mac address is: {get_mac()}")
    main(hr, rr, rr_step, max_amp, min_amp, waveform, 3)