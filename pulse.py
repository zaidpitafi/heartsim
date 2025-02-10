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
from scipy import signal

def sine_gen_with_rr_v2(amp, samples, duration, hr, rr):
    wave=[]
    f_hr = hr/60
    f_rr = rr/60
    amp_rr = amp*0.2
    for i in range(0,duration*samples):
        val_hr = amp + int(amp * (math.sin(2 * math.pi * f_hr * i/samples)))
        val_rr = amp_rr + int(amp_rr * (math.sin(2 * math.pi * f_rr * i/samples)))
        val = val_hr #+ val_rr
        wave.append(val)    
    
    return wave

def sym4_gen(amp,samples, duration, hr):
    reps = int(duration*hr/60) 

    wavelet = pywt.Wavelet('sym4')
    phi, psi, x = wavelet.wavefun(level=3)
    
    phi = ((phi-np.min(phi))/(np.max(phi)-np.min(phi)) * amp)
    
    phi = np.tile(phi,reps)
    phi = signal.resample(phi, samples*duration)
    phi = abs(phi)
    return phi

def db12_gen(amp,samples, duration, hr):
    reps = int(duration*hr/60) 

    wavelet = pywt.Wavelet('db12')
    phi, psi, x = wavelet.wavefun(level=3)
    
    phi = ((phi-np.min(phi))/(np.max(phi)-np.min(phi)) * amp)
    
    phi = np.tile(phi,reps)
    phi = signal.resample(phi, samples*duration)
    phi = abs(phi)
    return phi

def mexhat_gen(amp, samples, duration, hr):
    points = samples
    reps = int(duration*hr/60)
    a = 4 ##width
    vec2 = signal.ricker(100, a)
    vec2 = ((vec2-np.min(vec2))/(np.max(vec2)-np.min(vec2)) * amp)
    vec2 = np.tile(vec2,reps)
    vec2 = signal.resample(vec2, samples*duration)
    vec2 = abs(vec2)
    return vec2

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

def sine_gen_with_rr (amp, samples, duration, hr, rr):
    freq_hr = hr/60       # Frequency in Hz
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


def rr_gen_ming(in_sig, respiratory_rate):
    print(len(in_sig))
    num_points = int(in_sig.shape[0])
    x_space = np.linspace(0,1,num_points)
    seg_fre = respiratory_rate / (60/1)
    seg_amp = max(in_sig)*0.1
    rr_component = seg_amp*np.sin(2*np.pi * seg_fre * x_space)
    in_sig += rr_component

    return in_sig

def sine_gen_old(amp, samples, freq):
    sine_wave=[]
    for i in range(0,samples):
        val = amp + int(amp * (math.sin(2 * math.pi * i/4095)))
        sine_wave.append(val)    
    return sine_wave


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
    
def sine_gen_with_rr_v3(amp, samples, duration, hr, rr):
    f_rr = rr/60
    f_hr = hr/60
    sampling_rate = samples

    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

    sine_wave = np.sin(2 * np.pi * f_hr * t)

    breathing_effect = (np.sin(2 * np.pi * f_rr * t) + 1) / 2

    wave = sine_wave * breathing_effect
    wave = amp + amp*wave
    return wave



def generate_wave_array(i):
    # Generate the increasing part (from 0.1 to i/2 with step 0.1)
    step = 0.1
    half_length = int(i // 2)
    increasing_part = np.arange(step, (half_length + 1) * step, step)
    
    # Generate the decreasing part (reverse of the increasing part, excluding the last value)
    # decreasing_part = increasing_part[-2::-1]  # Skip the last element to avoid repetition
    decreasing_part = increasing_part[-2:]
    # Combine both parts
    wave_array = np.concatenate((increasing_part, decreasing_part))
    return wave_array

def generate_increasing_amplitude_wave_array(i):
    # Create an array starting from 1.1, increasing by 0.1 up to length i
    step = 0.2
    wave_array = np.arange(1, 1 + step * i, step)
    return wave_array

def sine_gen_with_rr_v4(amp, samples, duration, hr, rr):
    wave = sine_gen_with_rr_v3(amp, samples, 1, 60, rr)
    max_amp = 4094

    val = int(hr/rr)
    reps = int(rr/60*duration)
    scaling_factors = generate_increasing_amplitude_wave_array(val)

    rsa = np.tile(wave, len(scaling_factors)) * np.repeat(scaling_factors, len(wave))

    rsa_norm = ((rsa-np.min(rsa))/(np.max(rsa)-np.min(rsa)) * max_amp)

    wave_f = np.tile(rsa_norm,reps)

    wave = signal.resample(wave_f,duration*samples)
    wave = abs(wave)
    return wave