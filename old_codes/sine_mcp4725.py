import numpy as np
import time
from smbus2 import SMBus
import adafruit_mcp4725

DAC_ADDRESS = 0x60

bus = SMBus(1)

freq = 3
amp = 2048
offset = 2048
sampling_rate = 1000
duration = 1

t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

sine_wave = offset + amp * np.sin(2 * np.pi * freq * t)

def write_dac(value):
    value = int(value) & 0xFF
    high_byte = (value >> 8) & 0xFF
    low_byte = value & 0xFF
    bus.write_i2c_block_data(DAC_ADDRESS, high_byte, [low_byte])

try:
    while True:
        start_time = time.time()
        for value in sine_wave:
            write_dac(value)
            time.sleep(max(0,(1/sampling_rate)- (time.time() - start_time)))
    
except KeyboardInterrupt:
    print(freq)
