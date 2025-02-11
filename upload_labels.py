import numpy as np
import time
import math
import numpy as np
import matplotlib.pyplot as plt
from utils import *

influx = {'ip':'http://sensorserver.engr.uga.edu', 'db':'healthresult',
                  'user':'algtest', 'passw':'sensorweb711', 
                  'ssl':False}

table_name = 'vitals'
data_name = 'hrlabel'
unit = '74:4d:bd:8d:61:88'

data = np.load("wave_sine_rr_12_time_1739204684.2296906.npy")

vitals = data[:,-2].reshape(-1,1)
vitals = np.repeat(vitals, repeats=120, axis=1)

for i in range(vitals.shape[0]):
    write_influx(influx= influx, unit=unit,table_name=table_name, data_name=data_name, data=vitals[i,:], start_timestamp=data[i, -3], fs = 1)