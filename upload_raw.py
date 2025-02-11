import numpy as np
import time
import math
import numpy as np
import matplotlib.pyplot as plt
from utils import *

influx = {'ip':'https://sensorserver.engr.uga.edu', 'db':'shake',
                  'user':'algtest', 'passw':'sensorweb711', 
                  'ssl':True}

table_name = 'Z'
data_name = 'value'
unit = '12:02:12:02:12:02'

data = np.load("wave_sine_rr_40_time_1739217846.5581903.npy")

raw_data = data[:, :-3]

for i in range(data.shape[0]):
    write_influx(influx= influx, unit=unit,table_name=table_name, data_name=data_name, data=raw_data[i,:], start_timestamp=data[i, -3], fs = 410)

print ('Data Uploaded')