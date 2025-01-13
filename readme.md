### The frequency of sine wave  is calculated by = 1/(samples per cycle x delay per sample)
### Currently we have 100 samples from DAC and a delay of 0.01s after each sample
### The Heart Rate is found by multiplying frequency by 60

## To Run the simulator code, use the framework_heartsim.py file and provide following arguments
### --wave_type (type of wave to simulate e.g., sine, mexican hat, sym4, scg, ecg)
### --ibi_interval (in milliseconds)
### --hr 
### --rr
### --amplitude (maximum is 2048, default is 1024)
