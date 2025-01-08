import struct
import time
import numpy as np
import paho.mqtt.client as mqtt
import threading


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
       print(item)
       packed_data += struct.pack("i", item)


   return packed_data

def data_mqtt(data):
    mac_addr="11:01:11:01:11:01"
    timestamp = int(time.time() * 1000000)
    data = [np.int32(data)] # spo2=95.2% 
    packed_data = pack_beddot_data(mac_addr, timestamp, 10000, data)


    client = mqtt.Client()
    client.connect("sensorweb.us", 1883)
    mqtt_thread = threading.Thread(target=lambda: client.loop_forever())
    mqtt_thread.start()

    client.publish("/UGA/110111011101/heartsim", packed_data, qos=1)