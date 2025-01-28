import time
import math
import board
import busio
from adafruit_mcp4725 import MCP4725

# Initialize I2C and MCP4725 DAC
i2c = busio.I2C(board.SCL, board.SDA)
dac = MCP4725(i2c, address=0x60)

# DAC resolution (12-bit)
dac_resolution = 4096

# Sampling frequency (Hz)
fs = 1


# Main sine wave parameters
main_freq = 1  # Main sine wave frequency (Hz)

# Respiration sine wave parameters
respiration_freq = 0.25  # Respiration frequency (Hz)
respiration_depth = 0.5  # Amplitude modulation depth (0 to 1)

# Generate and output the signal
print("Generating sine wave with respiration effect... Press Ctrl+C to stop.")
start_time = time.time()

try:
    while True:
        # Calculate elapsed time
        elapsed_time = time.time() - start_time

        # Generate the main sine wave
        main_wave = math.sin(2 * math.pi * main_freq * elapsed_time)

        # Generate the respiration sine wave (used for amplitude modulation)
        respiration_wave = 0.5 * (1 + math.sin(2 * math.pi * respiration_freq * elapsed_time))

        # Apply modulation
        combined_wave = respiration_wave * main_wave

        # Normalize the combined wave to DAC range (0 to 4095)
        dac_value = int((combined_wave + 1) / 2 * (dac_resolution - 1))

        # Send value to DAC
        dac.raw_value = dac_value
        print(dac_value)

        # Wait for the next sample
        time.sleep(1 / fs)

except KeyboardInterrupt:
    print("\nSignal generation stopped.")
