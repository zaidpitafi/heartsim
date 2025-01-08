import numpy as np
import time
from smbus2 import SMBus
import adafruit_mcp4725 as a
import math
import board, busio

i2c = busio.I2C(board.SCL, board.SDA)

dac = a.MCP4725(i2c, address=0x60)
freq = 0.5
a = 2048
samples = 41

try:
    while True:
        start_time = time.time()
        for i in range(4095,0,-100):
            val = a + int(a * (math.sin(2 * math.pi * i/4095)))
            time.sleep(0.01)
            # print(val)
            dac.raw_value = val
        end_time = time.time()
        total_time = end_time - start_time
        actual_delay = total_time / samples
        print(f"Actual delay per sample: {actual_delay:.4f} seconds")
        print(f"Calculated frequency: {1 / (actual_delay * samples):.2f} Hz")
except KeyboardInterrupt:
    print(freq)
