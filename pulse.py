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
def sine_gen(amp, step_size):
    sine_wave=[]
    for i in range(0,4095,+step_size):
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

    

# i2c = busio.I2C(board.SCL, board.SDA)
# dac = a.MCP4725(i2c, address=0x60)

# try:
#     while(True):
#         a = sine_gen(amp=amplitude, step_size=step_size)
        

# except KeyboardInterrupt:
#     print('End')