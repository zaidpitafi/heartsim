import numpy as np
import time
from smbus2 import SMBus
import math
import argparse
import busio
import board
import adafruit_mcp4725 as a
import struct
import time
import paho.mqtt.client as mqtt
import threading
from scipy import signal
import netifaces
import random
import pywt

"""
************************ Used for Label Upload ************************
"""

def get_mac(interface='eth0'):
    return netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]['addr']

def pack_beddot_data(mac_addr, timestamp, data_interval, data):
    # First, convert the MAC address into byte sequence
    mac_bytes = bytes.fromhex(mac_addr.replace(':', ''))
    # Then, pack each data item sequentially
    packed_data = struct.pack("!BBBBBB", *mac_bytes)
    packed_data += struct.pack("H", len(data))  # data length
    packed_data += struct.pack("L", timestamp)  # timestamp
    packed_data += struct.pack("I", data_interval)  # data interval 

   # pack measurement data(Blood Oxygen)
    for item in data:
        packed_data += struct.pack("i", item)
    return packed_data

def write_mqtt(hrdata, rrdata, timestamp, fs):
    # mac_addr=get_mac()
    mac_addr = "12:12:12:12:12:12"
    timestamp = int(timestamp * 1000000)
    hrdata = np.int32(hrdata)
    rrdata = np.int32(rrdata)
    Ts = int((1/fs) * 1000000)
    packed_data_1 = pack_beddot_data(mac_addr, timestamp, Ts, hrdata) # 10000 equates to fs=1/0.01=100
    packed_data_2 = pack_beddot_data(mac_addr, timestamp, Ts, rrdata)

    client = mqtt.Client()
    # client.connect("yuantzg.com", 9183)
    client.connect("sensorweb.us", 1883)
    mqtt_thread = threading.Thread(target=lambda: client.loop_forever())
    mqtt_thread.start()

    mac_addr_str = mac_addr.replace(":", "")
    client.publish(f"/UGA/{mac_addr_str}/hrlabel", packed_data_1, qos=1)
    client.publish(f"/UGA/{mac_addr_str}/rrlabel", packed_data_2, qos=1)
    print('Published')
    return None


"""
************************ Used for Waveform Generation ************************
"""

def sym4_gen(min_amp,max_amp, samples, duration, hr):
    min_val = min_amp
    max_val = max_amp
    reps = int(duration*hr/60) 

    wavelet = pywt.Wavelet('sym4')
    phi, psi, x = wavelet.wavefun(level=3)
    
    phi = ((phi-np.min(phi))/(np.max(phi)-np.min(phi)) * max_amp)
    
    phi = np.tile(phi,reps)
    phi = signal.resample(phi, samples*duration)
    phi = abs(phi)
    return phi

def db12_gen(min_amp,max_amp, samples, duration, hr):
    min_val = min_amp
    max_val = max_amp

    reps = int(duration*hr/60) 
    wavelet = pywt.Wavelet('db12')
    phi, psi, x = wavelet.wavefun(level=3)
    
    phi = ((phi-np.min(phi))/(np.max(phi)-np.min(phi)) * max_amp)
    
    phi = np.tile(phi,reps)
    phi = signal.resample(phi, samples*duration)
    phi = abs(phi)
    return phi
    

def mexhat_gen_base(amp, samples, duration, hr):
    points = samples
    reps = int(duration*hr/60)
    a = 4 ##width default is 4
    
    vec2 = signal.ricker(100, a) 
    vec2 = ((vec2-np.min(vec2))/(np.max(vec2)-np.min(vec2)) * amp)
    vec2 = np.tile(vec2,reps)
    vec2 = signal.resample(vec2, samples*duration)
    vec2 = abs(vec2)
    return vec2


def mexhat_gen_with_rr(min_amp, max_amp, samples, duration, hr, rr, rr_step):

    wave = mexhat_gen_base(max_amp, samples, 1, 60)

    val = int(hr/rr)
    reps = int(rr/60*duration)
    scaling_factors = generate_increasing_amplitude_wave_array(val, rr_step)

    rsa = np.tile(wave, len(scaling_factors)) * np.repeat(scaling_factors, len(wave))

    # rsa_norm = ((rsa-np.min(rsa))/(np.max(rsa)-np.min(rsa)) * max_amp)

    wave_f = np.tile(rsa,reps)

    wave = signal.resample(wave_f,duration*samples)

    wave = min_amp + ((wave - np.min(wave)) / (np.max(wave) - np.min(wave))) * (max_amp - min_amp)
    wave = abs(wave)

    return wave

def chirp_wave(min_amp, max_amp, samples, duty_circle, duration, hr, rr, rr_step):
    wave = []
    wave = np.array(wave)
    hr = 40
    for i in range(21):
        wave_f = sine_gen_with_rr_irr_v2(min_amp, max_amp, samples, duty_circle, 10, hr, 16, rr_step)
        wave = np.concatenate((wave, wave_f))
        hr += 10
    return wave

"""
************************ Sine and Pulse Waveforms ************************
"""

def apply_amp(wave, max_amp, min_amp):
    return min_amp + ((wave - np.min(wave)) / (np.max(wave) - np.min(wave))) * (max_amp - min_amp)


def generate_increasing_amplitude_wave_array(i,step_size):
    # Create an array starting from 1.1, increasing by step up to length i
    step = step_size
    wave_array = np.arange(1, 1 + step * i, step)
    return wave_array

def pulse_base(samples, duty_cycle):
    f_hr = 0.5 / duty_cycle  # Sampling frequency in Hz
    t = np.linspace(0, 1, samples, endpoint=False)

    # Generate pulse waveform
    pulse_wave = (np.sin(2 * np.pi * f_hr * t) >= np.cos(np.pi * duty_cycle)).astype(int)[:int(samples * duty_cycle)]
    
    zeros = np.zeros(samples - int(samples * duty_cycle))
    wave = np.concatenate([pulse_wave, zeros])

    return wave


def pulse_gen_with_rr(min_val, max_val, samples, duty_circle, duration, hr, rr, rr_step):
    hr_num = int(duration * hr / 60)
    print(hr_num)

    hr_waves = [pulse_base(int(samples*60/hr), duty_circle) for _ in range(hr_num)]
    hr_waves_len = [len(wave) for wave in hr_waves]
    hr_waves = np.concatenate(hr_waves)
    hr_waves = signal.resample(hr_waves, samples*duration)
    print(f'len hr waves: {len(hr_waves)}')
    print(f'desried hr waves: {samples * duration}, actual hr waves: {len(hr_waves)}')
    if rr != 0: 
        rr_waves = generate_rr_wave(rr, samples, duration)
        print(f'len rr waves: {len(rr_waves)}')
        rr_waves_discrete = np.zeros_like(rr_waves)

        begin = 0
        end = hr_waves_len[0]
        for hr_wave_len in hr_waves_len:
            end = begin + hr_wave_len
            rr_waves_discrete[begin:end] = rr_waves[(2*begin + end) // 3]
            begin = end

        hr_waves = hr_waves * rr_waves_discrete
    # hr_waves = np.interp(np.linspace(0, len(hr_waves), samples * duration), np.arange(len(hr_waves)), hr_waves)
    wave = apply_amp(hr_waves, max_val, min_val)

    return wave


def sine_gen_with_rr_irr(min_amp, max_amp, samples, duty_circle, duration, hr, rr, rr_step, hrv=10):
    hr_num = int(duration * hr / 60) + 1
    rr_num = int(duration * rr / 60) + 1
    
    hr_waves = [sine_wave_base(samples, duty_circle, hrv) for _ in range(hr_num)]
    hr_waves_len = [len(wave) for wave in hr_waves]
    hr_waves = np.concatenate(hr_waves)
 
    if hr <140: val = val-1
    scaling_factors = generate_increasing_amplitude_wave_array(val, rr_step)
    rsa = np.tile(wave, len(scaling_factors)) * np.repeat(scaling_factors, len(wave))
    wave_f = np.tile(rsa,reps)

    new_length = duration*samples
    wave = np.interp(np.linspace(0, len(wave_f)-1, new_length), np.arange(len(wave_f)), wave_f)
    
    wave = apply_amp(wave, max_amp, min_amp)
    return wave


def sine_wave_base(samples, duty_cycle, hrv=None):
    f_hr = 0.5 / duty_cycle
    t = np.linspace(0, 1, samples, endpoint=False)
    sine_wave = np.sin(2 * np.pi * f_hr * t)[:int(samples * duty_cycle)]
    zeros = np.zeros(samples - int(samples * duty_cycle))
    wave = np.concatenate([sine_wave, zeros])
    if hrv:
        hrv_len = int(samples * random.uniform(-1 * hrv, hrv))
        if hrv_len > 0: 
            wave = np.concatenate([wave, np.zeros(hrv_len)])
        elif hrv_len < 0:
            wave = wave[:hrv_len]
    return wave




def sine_gen_with_rr_irr_v2(min_amp, max_amp, samples, duty_circle, duration, hr, rr, rr_step):
    hr_num = int(duration * hr / 60)
    print(hr_num)
    
    hr_waves = [sine_wave_base(int(samples*60/hr), duty_circle) for _ in range(hr_num)]
    hr_waves_len = [len(wave) for wave in hr_waves]
    hr_waves = np.concatenate(hr_waves)
    hr_waves = signal.resample(hr_waves, samples*duration)
    print(f'len hr waves: {len(hr_waves)}')
    print(f'desried hr waves: {samples * duration}, actual hr waves: {len(hr_waves)}')
    if rr != 0:
        rr_waves = generate_rr_wave(rr, samples, duration)
        print(f'len rr waves: {len(rr_waves)}')
        rr_waves_discrete = np.zeros_like(rr_waves)

        begin = 0
        end = hr_waves_len[0]
        for hr_wave_len in hr_waves_len:
            end = begin + hr_wave_len
            rr_waves_discrete[begin:end] = rr_waves[(2*begin + end) // 3]
            begin = end

        hr_waves = hr_waves * rr_waves_discrete
        # hr_waves = np.interp(np.linspace(0, len(hr_waves), samples * duration), np.arange(len(hr_waves)), hr_waves)
    wave = apply_amp(hr_waves, max_amp, min_amp)
    return wave


def generate_rr_wave(rr, samples, duration):
    t = np.linspace(0, duration, samples * duration, endpoint=False)
    rr_wave = signal.sawtooth(2 * np.pi * (rr/60) * t) 
    rr_wave = apply_amp(rr_wave, 1, 0.98)
    return rr_wave
    
