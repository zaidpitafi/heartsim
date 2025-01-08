import numpy as np
import pandas as pd
import neurokit2 as nk
import time
from smbus2 import SMBus
import adafruit_mcp4725 as a
import math
import board, busio

ecg = nk.ecg_simulate(duration=1, sampling_rate= 4096, heart_rate = 80)
ecg_n = (ecg-np.min(ecg))/(np.max(ecg)-np.min(ecg)) * 256
ecg_n = ecg_n.astype(int)

i2c = busio.I2C(board.SCL, board.SDA)

dac = a.MCP4725(i2c, address=0x60)
freq = 2

try:
    while True:
        for i in range(2048,-2048,-5):
            if ecg_n[i]>1000:
                print(ecg_n[i])
            dac.raw_value = ecg_n[i]
        time.sleep(0.0)
    
except KeyboardInterrupt:
    print(freq)
