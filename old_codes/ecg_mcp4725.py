import numpy as np
import time
from smbus2 import SMBus
from adafruit_mcp4725 import MCP4725
import neurokit2 as nk
import busio, board

DAC_ADDRESS = 0x60
i2c = busio.I2C(board.SCL, board.SDA)
dac = MCP4725(i2c, address=0x60)
bus = SMBus(1)

freq = 3
amp = 2048
offset = 2048
sampling_rate = 1000
duration = 1

t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

sine_wave = offset + amp*nk.ecg_simulate(duration=10, heart_rate = 70)
sine_wave = (sine_wave - np.min(sine_wave))/ (np.max(sine_wave) - np.min(sine_wave)) * 4095
sine_wave = sine_wave.astype(int)


def write_dac(value):
    value = int(value) & 0xFF
    high_byte = (value >> 8) & 0xFF
    low_byte = value & 0xFF
    bus.write_i2c_block_data(DAC_ADDRESS, high_byte, [low_byte])

try:
    while True:
        for value in sine_wave:
            print(value)
            dac.value = value
            time.sleep(0.002)
    
except KeyboardInterrupt:
    print(freq)
    
