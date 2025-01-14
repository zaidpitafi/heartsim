import numpy as np
import pandas as pd
import neurokit2 as nk
import time
from smbus2 import SMBus
import adafruit_mcp4725 as a
import math
import board, busio
import numpy as np
import matplotlib.pyplot as plt
from datasim.ecg.ecg_simulate import *
#from utils import write_influx
# from mqtt_to_influxdb import *
from mqtt import *


sample_rate = 41

step_size = int(4095/41)

amplitude = 1024

influx = {'ip': 'https://sensorserver.engr.uga.edu', 'db': 'shake', 'user':'algtest', 'passw':'sensorweb711'}

def ecg_gen(amp, step_size):
    ecg = ecg_simulate(duration=1, sampling_rate= 41, heart_rate = 80)
    ecg_n = amp + ((ecg-np.min(ecg))/(np.max(ecg)-np.min(ecg)) * amp)
    for i in range(0,41):
        print(ecg_n[i])
        dac.raw_value = int(ecg_n[i])
        time.sleep(0.01)
    return ecg_n


def sine_gen(amp, step_size):
    sine_wave=[]
    for i in range(0,4095,+step_size):
        val = amp + int(amp * (math.sin(2 * math.pi * i/4095)))
        time.sleep(0.01)
        # print(val)
        dac.raw_value = val
        data_mqtt(val)
        sine_wave.append(val)
    
    return sine_wave

    

i2c = busio.I2C(board.SCL, board.SDA)
dac = a.MCP4725(i2c, address=0x60)

try:
    while(True):
        a = sine_gen(amp=amplitude, step_size=step_size)
        

except KeyboardInterrupt:
    print('End')