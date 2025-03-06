import numpy as np
import time
import math
import numpy as np
import matplotlib.pyplot as plt
from utils import *

influx = {'ip':'https://sensorserver.engr.uga.edu', 'db':'healthresult',
                  'user':'algtest', 'passw':'sensorweb711', 
                  'ssl':False}

table_name = 'vitals'
data_name = 'hrlabel'
unit = '74:4d:bd:8d:61:88'
data_name2 = 'rrlabel'

data = np.load("wave_mexhat_rr_36_step_0.15_time_1741114764.npy")

vitals = data[:,-2].reshape(-1,1)
vitals = np.repeat(vitals, repeats=120, axis=1)

vitals_2 = data[:,-1].reshape(-1,1)
vitals_2 = np.repeat(vitals_2, repeats=120, axis=1)

for i in range(vitals.shape[0]):
    write_influx(influx= influx, unit=unit,table_name=table_name, data_name=data_name, data=vitals[i,:], start_timestamp=data[i, -3], fs = 1)
    write_influx(influx= influx, unit=unit,table_name=table_name, data_name=data_name2, data=vitals_2[i,:], start_timestamp=data[i, -3], fs = 1)