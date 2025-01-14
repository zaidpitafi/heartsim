import numpy as np
import pandas as pd
import neurokit2 as nk
import time
from smbus2 import SMBus
# import adafruit_mcp4725 as a
import math
# import board, busio
import numpy as np
import matplotlib.pyplot as plt
from datasim.ecg.ecg_simulate import *
from datasim.scg.scg_simulate import *
#from utils import write_influx
# from mqtt_to_influxdb import *
from mqtt import *
from scipy import signal
import pywt

sample_rate = 41

step_size = int(4095/41)

amplitude = 1024

def scg_gen(amp, step_size):
    scg = scg_simulate(length=step_size, duration=1)
    scg_n = amp + int((scg-np.min(scg))/(np.max(scg)-np.min(scg)) * amp)
    return scg
def ecg_gen(amp, step_size):
    ecg = ecg_simulate(length=step_size, heart_rate = 80)
    ecg_n = amp + int((ecg-np.min(ecg))/(np.max(ecg)-np.min(ecg)) * amp)
    return ecg_n

def sine_gen (amp, samples):
    frequency = 1       # Frequency in Hz
    amplitude = amp       # Amplitude of the sine wave
    sampling_rate = samples # Sampling rate in Hz
    duration = 1        # Duration in seconds
    # Generate the time axis
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

    # Generate the sine wave
    sine_wave = amplitude + (amplitude * np.sin(2 * np.pi * frequency * t))  
    return sine_wave

def sine_gen_old(amp, step_size):
    sine_wave=[]
    for i in range(0,4095,step_size):
        val = amp + int(amp * (math.sin(2 * math.pi * i/4095)))
        sine_wave.append(val)    
    return sine_wave

def mexhat_gen(amp, step_size):
    points = step_size
    a = 4 ##width
    vec2 = signal.ricker(points, a)
    return vec2

def sym4_gen(amp,step_size):
    wavelet = pywt.Wavelet('sym4')
    phi, psi, x = wavelet.wavefun(level=10)
    return psi

def rr_gen(in_sig, sample_rate, respiratory_rate):
    print(len(in_sig))
    num_points = 1 * sample_rate
    x_space = np.linspace(0,1,num_points)
    seg_fre = respiratory_rate / (60/1)
    seg_amp = max(in_sig)*0.10
    rr_component = seg_amp*np.sin(2*np.pi * seg_fre * x_space)
    in_sig += rr_component
    return in_sig

def random_hr_gen(min,max):
    val = np.random(min,max)
    return val
    

# i2c = busio.I2C(board.SCL, board.SDA)
# dac = a.MCP4725(i2c, address=0x60)

# try:
#     while(True):
#         a = sine_gen(amp=amplitude, step_size=step_size)
        

# except KeyboardInterrupt:
#     print('End')