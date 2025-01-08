import numpy as np
import time
from smbus2 import SMBus
import pyaudio

#DAC_ADDRESS = 0x60

bus = SMBus(1)

freq = 1000
amp = 4096
offset = 4096
sampling_rate = 1000
duration = 20

t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

sine_wave = offset + amp * np.sin(2 * np.pi * freq * t)

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paFloat32, channels=1, rate=sampling_rate, output=True)

stream.write(sine_wave.astype(np.float32).tobytes())
stream.stop_stream()
stream.close()
p.terminate()
