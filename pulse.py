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
import datetime
import pytz

def scg_gen(amp, step_size):
    scg = scg_simulate(length=step_size, duration=1)
    scg_n = amp + int((scg-np.min(scg))/(np.max(scg)-np.min(scg)) * amp)
    scg_n = np.tile(scg_n,10)
    return scg_n
def ecg_gen(amp, step_size):
    ecg = ecg_simulate(length=step_size, heart_rate = 80)
    ecg_n = amp + int((ecg-np.min(ecg))/(np.max(ecg)-np.min(ecg)) * amp)
    ecg_n = np.tile(ecg_n,10)
    return ecg_n

def sine_gen (amp, samples, hb, freq):
    frequency = freq       # Frequency in Hz
    amplitude = amp       # Amplitude of the sine wave
    sampling_rate = samples # Sampling rate in Hz
    duration = 1        # Duration in seconds
    # Generate the time axis
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

    # Generate the sine wave
    sine_wave = amplitude + (amplitude * np.sin(2 * np.pi * frequency * t))

    sine_wave = np.tile(sine_wave,hb)  
    return sine_wave

def sine_gen_with_rr (amp, samples, duration, freq, rr):
    freq_hr = freq       # Frequency in Hz
    freq_rr = rr/60
    hr_amp = amp       # Amplitude of the sine wave
    rr_amp = 0.2*hr_amp
    sampling_rate = samples # Sampling rate in Hz
    duration = duration        # Duration in seconds
    
    # Generate the time axis
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)


    # Generate the sine wave
    rr_wave = rr_amp + (rr_amp*np.sin(2 * np.pi * freq_rr * t))
    hr_wave = hr_amp + (hr_amp * np.sin(2 * np.pi * freq_hr * t))
    
    sine_wave = rr_wave + hr_wave
    return sine_wave

def sine_gen_old(amp, samples):
    sine_wave=[]
    step_size = int(4095/samples)
    for i in range(0,4095,step_size):
        val = amp + int(amp * (math.sin(2 * math.pi * i/4095)))
        sine_wave.append(val)    
    return sine_wave

def mexhat_gen(amp, step_size):
    points = step_size
    a = 4 ##width
    vec2 = signal.ricker(points, a)
    vec2 = np.tile(vec2,10)
    return vec2

def sym4_gen(amp,step_size):
    wavelet = pywt.Wavelet('sym4')
    phi, psi, x = wavelet.wavefun(level=10)
    psi = np.tile(psi,10)
    return psi

def rr_gen_ming(in_sig, respiratory_rate):
    print(len(in_sig))
    num_points = int(in_sig.shape[0])
    x_space = np.linspace(0,1,num_points)
    seg_fre = respiratory_rate / (60/1)
    seg_amp = max(in_sig)*0.1
    rr_component = seg_amp*np.sin(2*np.pi * seg_fre * x_space)
    in_sig += rr_component

    return in_sig

def rr_gen(rr, samples):
    fs = samples  # Sampling frequency in Hz
    duration = 1  # Signal duration in seconds
    f_resp = rr  # Respiration frequency in Hz (15 breaths per minute)

    # Time vector
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)

    # Respiration signal (sinusoidal)
    amplitude = 1.0  # Amplitude of the signal
    resp_signal = amplitude + (int(amplitude * np.sin(2 * np.pi * f_resp * t)))

    return resp_signal

def random_hr_gen(min,max):
    val = np.random(min,max)
    return val


def epoch_to_datetime_est(epoch_time):
    """Converts epoch time to datetime in EST."""
    
    # Convert epoch time to datetime (UTC)
    dt_utc = datetime.datetime.utcfromtimestamp(epoch_time)
    
    # Define EST timezone
    est_timezone = pytz.timezone('US/Eastern')
    
    # Localize the datetime to EST
    dt_est = dt_utc.replace(tzinfo=pytz.utc).astimezone(est_timezone)
    
    return dt_est
    
