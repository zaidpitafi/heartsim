#!/usr/bin/env python3
import json
import time
import math
import subprocess
import sys
import random
import webbrowser
import numpy as np
from datetime import datetime
from dateutil import tz
import pytz
import os, sys
from scipy import signal
from influxdb import InfluxDBClient
import operator
import copy
from collections import Counter
import pywt
from scipy.stats import norm
from scipy.special import softmax
import pandas as pd

import matplotlib.pyplot as plt
import re

# import tsfel
from pdb import set_trace as st
from scipy import signal


# list1: label; list2: prediction
def plot_2vectors(label, pred, name, mae=0):
    list1 = np.array(label)
    list2 = np.array(pred)
    if mae == 0: mae = calc_mae(list1, list2)
    sorted_id = sorted(range(len(list1)), key=lambda k: list1[k])

    plt.figure(figsize = (10,5))
    plt.clf()
    plt.text(0,np.min(list1),f'MAE={mae:.2f}')
    plt.scatter(np.arange(list2.shape[0]),list2[sorted_id],s = 1, alpha=0.5,label=f'{name} prediction', color='blue')
    plt.scatter(np.arange(list1.shape[0]),list1[sorted_id],s = 1, alpha=0.5,label=f'{name} label', color='red')
    # plt.ylim(0,50)

    plt.legend()
    plt.savefig(f'{name}.png')
    # print(f'Saved plot to {name}.png')
    plt.show()
    print(f'mae({name}): {mae:.2f}')

def plot_2times(list1, list2, name):
    plt.figure(figsize = (10,5))
    plt.clf()
    ylist1 = [1]*len(list1)    
    ylist2 = [2]*len(list2)  
    plt.scatter(list1, ylist1, s = 1, alpha=0.5, label=f'list1', color='blue')
    plt.scatter(list2, ylist2, s = 1, alpha=0.5, label=f'list2', color='red')

    plt.legend()
    plt.savefig(f'{name}.png')
    # print(f'Saved plot to {name}.png')
    plt.show()


def plot_save_result(result, name, savepath, verbose=False):
    if not os.path.exists(savepath):
        os.makedirs(savepath)
        print(f'Make dir {savepath}')
    gt = result[:,0]
    pred = result[:,1]

    mae = calc_mae(gt, pred)


    std = np.std(pred)
    plt.figure(figsize=(16,9))
    plt.text(0,np.min(pred),f'MAE={mae}')
    plt.plot(gt, 'r',  label=f'{name} gt', linewidth=1)
    # plt.plot(pred, 'b.', label='hr pred',alpha=0.3)
    plt.scatter(np.arange(pred.shape[0]),pred,s = 1, alpha=0.5,label=f'{name} pred')
    # plt.plot(pred+std, 'r--', label='std',alpha=0.3)
    # plt.plot(pred-std, 'r--', label='std',alpha=0.3)
    plt.legend()
    if verbose:
        print('show')
        plt.show()

    save_path = os.path.join(savepath, f'{name}.png')
    plt.savefig(save_path)
    print(f'Evaluation figure for {name} saved done!')
    print(f'Saved at: {save_path}')
    plt.close()


def calc_mae(gt, pred):
    return np.mean(abs(np.array(gt)-np.array(pred)))

def ensure_dir(file_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
        print(f'Make dir {file_path}')


def sort_by_trend(pred,gt):
    result = np.concatenate((np.array(gt),np.array(pred)),1)
    # st()
    result = result[np.argsort(result[:,0])]
    # st()
    return result

def z_score_normalize(data, mean, std):
   
    data = (data - mean)/std
    data_normalized = np.expand_dims(data, axis = -1)

    return data_normalized

# get_ipython().system(' pip install tsfel # installing TSFEL for feature extraction')
def str2bool(v):
  return v.lower() in ("true", "1", "https", "load")

def mac_to_int(mac):
    res = re.match('^((?:(?:[0-9a-f]{2}):){5}[0-9a-f]{2})$', mac.lower())
    if res is None:
        # print('invalid mac address, use 0 instead')
        return int(0)
    return int(res.group(0).replace(':', ''), 16)

def int_to_mac(macint):
    # if type(macint) != int:
    #     raise ValueError('invalid integer')
    newint = int(macint)
    return ':'.join(['{}{}'.format(a, b)
                     for a, b
                     in zip(*[iter('{:012x}'.format(newint))]*2)])

# This function converts the time string to epoch time xxx.xxx (second.ms).
# Example: time = "2020-08-13T02:03:00.200", zone = "UTC" or "America/New_York"
# If time = "2020-08-13T02:03:00.200Z" in UTC time, then call timestamp = local_time_epoch(time[:-1], "UTC"), which removes 'Z' in the string end
def local_time_epoch(time, zone):
    local_tz = pytz.timezone(zone)
    print('Getting time')
    print(time)
    try:
        localTime = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%f")
    except:
        localTime = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S")
    local_dt = local_tz.localize(localTime, is_dst=None)
    # utc_dt = local_dt.astimezone(pytz.utc)
    epoch = local_dt.timestamp()
    # print("epoch time:", epoch) # this is the epoch time in seconds, times 1000 will become epoch time in milliseconds
    # print(type(epoch)) # float
    return epoch

def influx_query_time_epoch(time, zone):
    local_tz = pytz.timezone(zone)
    try:
        localTime = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%fZ")
    except:
        localTime = datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
        
    local_dt = local_tz.localize(localTime, is_dst=None)
    # utc_dt = local_dt.astimezone(pytz.utc)
    epoch = local_dt.timestamp()
    # print("epoch time:", epoch) # this is the epoch time in seconds, times 1000 will become epoch time in milliseconds
    # print(type(epoch)) # float
    return epoch

# This function converts the epoch time xxx.xxx (second.ms) to time string.
# Example: time = "2020-08-13T02:03:00.200", zone = "UTC" or "America/New_York"
# If time = "2020-08-13T02:03:00.200Z" in UTC time, then call timestamp = local_time_epoch(time[:-1], "UTC"), which removes 'Z' in the string end
def epoch_time_local(epoch, zone):
    local_tz = pytz.timezone(zone)
    time = datetime.fromtimestamp(epoch).astimezone(local_tz).strftime("%Y-%m-%dT%H:%M:%S.%f")
    return time

# This function converts the grafana URL time to epoch time. For exmaple, given below URL
# https://sensorweb.us:3000/grafana/d/OSjxFKvGk/caretaker-vital-signs?orgId=1&var-mac=b8:27:eb:6c:6e:22&from=1612293741993&to=1612294445244
# 1612293741993 means epoch time 1612293741.993; 1612294445244 means epoch time 1612294445.244
def grafana_time_epoch(time):
    return time/1000

def influx_time_epoch(time):
    return time/10e8

def generate_waves(fs, fd, seconds):
    # fs = 10e3
    # N = 1e5
    N = fs * seconds
    amp = 2*np.sqrt(2)
    # fd = fs/20
    noise_power = 0.001 * fs / 2
    time = np.arange(N) / fs
    signal_ = amp*np.sin(2*np.pi*fd*time)
    # signal += amp*np.sin(2*np.pi*(fd*1.5)*time)
    signal_ += np.random.normal(scale=np.sqrt(noise_power), size=time.shape)
    return signal_, time

def select_with_gaussian_distribution(all_data, target_indexes): #label_indexes = [('S', -2)]):
    '''
    label_indexes is one below:
        [('H', -4)], [('R', -3)], [('S', -2)], [('D', -1)]
    '''
    data_name = target_indexes[0]
    index = target_indexes[1]

    data = all_data[:,index]
    values = list(set(data))
    num_sample = int(0.8*len(data))

    ### Gaussian Distibution
    mu = np.mean(data)
    sigma = np.std(data)
    n, bins = np.histogram(data, bins=len(values)-1, density=1)
    y = norm.pdf(bins, mu, sigma)

    ### calculate propability
    p_table = np.concatenate((np.array(values)[np.newaxis,:],y[np.newaxis,:]),0)
    p_list = []
    for each_ in data:
        index = np.where(p_table[0,:]==each_)[0][0]
        p_list.append(p_table[1,index])

    # import pdb; pdb.set_trace()
    p_arr = softmax(p_list)
    sample_index = np.random.choice(np.arange(data.shape[0]), size=num_sample, p=p_arr)
    result_data = all_data[sample_index]

    print(f"\nPerformed data selection with gaussian distribution on data_name: {data_name} with index: {index}\n")

    return result_data


def select_with_uniform_distribution(all_data, target_indexes): #label_indexes = [('S', -2)]):
    '''
    label_indexes is one below:
        [('H', -4)], [('R', -3)], [('S', -2)], [('D', -1)]
    '''
    data_name = target_indexes[0]
    index = target_indexes[1]
    data = all_data[:,index]
    minimum_num_sample = int(len(data)/len(list(set(data))))

    counter_result = Counter(data)
    dict_counter = dict(counter_result)
    result_dict = dict_counter.copy()

    # we keep them even if they have less than minimum
    # for item in dict_counter.items():
    #     if item[1] < minimum_num_sample:
    #         del result_dict[item[0]]

    keys = list(result_dict.keys())

    result_index_list = []
    for each_key in keys:
        result_index_list += list(np.random.choice(np.where(data == each_key)[0], size=minimum_num_sample))

    result_data = all_data[result_index_list]
    print(f"\nPerformed data selection with uniform distribution on data_name: {data_name} with index: {index}\n")

    return result_data

def label_index(label_name, labels_list = ['ID', 'Time', 'H', 'R', 'S', 'D']):
    # print(labels_list.index(label_name))
    return labels_list.index(label_name)-len(labels_list)  

def eval_data_stats(data_set_name, data_set, labels_list = ['ID', 'Time', 'H', 'R', 'S', 'D'], show=False ):

    num_labels = len(labels_list)

    print(f"{num_labels} labels are: {labels_list}")

    for label_name in labels_list: #[2:]:
        index = label_index (label_name, labels_list)

        target_ = data_set[:,index]
        target_pd = pd.DataFrame(target_,columns=[label_name])
        if show:
            # print(target_pd.describe())
            # print([ (i, list(target_).count(i)) for i in set(target_) ])
            # print(np.unique(target_, return_counts=True))
            # print(dict(pd.value_counts(target_)))

            plt.figure(f"{data_set_name} - distribution of {label_name}")
            nhist, bins, patches = plt.hist(target_,bins=30)
            # print(nhist)
            fig_name = f"{data_set_name}_{label_name}.png"
            plt.savefig(fig_name)
            print(f"save plot into {fig_name}")
            plt.show()

    try:
        id_index = label_index ('ID', labels_list)
        data_bed = data_set[:,id_index]
        counter_result = Counter(data_bed)
        result_dict = dict(counter_result)
        keys_list = list(result_dict.keys())
        for i in range(len(keys_list)):
            keys_list[i] = int_to_mac(keys_list[i])
        # print(f"\n{data_set_name} ID list: {keys_list}:")
    except:
        print('WARNING: ID label is not in the data set!')

    try:
        time_index = label_index ('Time', labels_list)
        time_min = epoch_time_local(min(data_set[:, time_index]), "America/New_York")
        time_max = epoch_time_local(max(data_set[:, time_index]), "America/New_York")

        data_time = data_set[:,time_index]
        truncated_data_time = get_truncated_epoch(data_time, 'day')
        counter_result = Counter(truncated_data_time)
        result_dict = dict(counter_result)
        keys_list = list(result_dict.keys())
        keys_list.sort()
        # random.shuffle(keys_list)
        for i in range(len(keys_list)):
            keys_list[i] = epoch_time_local(keys_list[i], "America/New_York")
        # print(f"\n{data_set_name} day list: {keys_list}:")
        print(f"time_min: {time_min}; time_max: {time_max}")
        # if show:
        #     plt.figure(figsize = (10,5))
        #     plt.figure(f"{data_set_name} - time distribution")
        #     # plt.plot(data_set[:, time_index])
        #     list2 = data_set[:, time_index]
        #     plt.scatter(np.arange(list2.shape[0]),list2,s = 1, alpha=0.5,label='time', color='blue')

        #     fig_name = f"{data_set_name}_time_distribution.png"
        #     plt.savefig(fig_name)
        #     print(f"save plot into {fig_name}")
        #     plt.show()
    except:
        print('WARNING: Time label is not in the data set!')

# This function write an array of data to influxdb. It assumes the sample interval is 1/fs.
# influx - the InfluxDB info including ip, db, user, pass. Example influx = {'ip': 'https://sensorweb.us', 'db': 'algtest', 'user':'test', 'passw':'sensorweb'}
# dataname - the dataname such as temperature, heartrate, etc
# timestamp - the epoch time (in second) of the first element in the data array, such as datetime.now().timestamp()
# fs - the sampling interval of readings in data

# unit - the unit location name tag
def write_influx(influx, unit, table_name, data_name, data, start_timestamp, fs):
    # print("epoch time:", timestamp)
    max_size = 100
    count = 0
    total = len(data)
    prefix_post  = "curl -k -POST \'"+ influx['ip']+":8086/write?db="+influx['db']+"\' -u "+ influx['user']+":"+ influx['passw']+" --data-binary \' "
    http_post = prefix_post
    for value in data:
        count += 1
        http_post += "\n" + table_name +",location=" + unit + " "
        http_post += data_name + "=" + str(value) + " " + str(int(start_timestamp*10e8))
        start_timestamp +=  1/fs
        if(count >= max_size):
            http_post += "\'  &"
            # print(http_post)
            # print("Write to influx: ", table_name, data_name, count)
            subprocess.call(http_post, shell=True)
            total = total - count
            count = 0
            http_post = prefix_post
    if count != 0:
        http_post += "\'  &"
        # print(http_post)
        # print("Write to influx: ", table_name, data_name, count, data)
        subprocess.call(http_post, shell=True)
    print('Done')

# This function read an array of data from influxdb.
# influx - the InfluxDB info including ip, db, user, pass. Example influx = {'ip': 'https://sensorweb.us', 'db': 'testdb', 'user':'test', 'passw':'sensorweb'}
# dataname - the dataname such as temperature, heartrate, etc
# start_timestamp, end_timestamp - the epoch time (in second) of the first element in the data array, such as datetime.now().timestamp()
# unit - the unit location name tag
def read_influx(influx, unit, table_name, data_name, start_timestamp, end_timestamp):
    if influx['ip'] == '127.0.0.1' or influx['ip'] == 'localhost':
        client = InfluxDBClient(influx['ip'], '8086', influx['user'], influx['passw'], influx['db'],  ssl=influx['ssl'])
    else:
        client = InfluxDBClient(influx['ip'].split('//')[1], '8086', influx['user'], influx['passw'], influx['db'],  ssl=influx['ssl'])

    # client = InfluxDBClient(influx['ip'].split('//')[1], '8086', influx['user'], influx['passw'], influx['db'],  ssl=True)
    query = 'SELECT "' + data_name + '" FROM "' + table_name + '" WHERE "location" = \''+unit+'\' AND time >= '+ str(int(start_timestamp*10e8))+' AND time < '+str(int(end_timestamp*10e8))
    # query = 'SELECT last("H") FROM "labelled" WHERE ("location" = \''+unit+'\')'

    # print(query)
    result = client.query(query)
    # print(result)

    points = list(result.get_points())
    values =  list(map(operator.itemgetter(data_name), points))
    times  =  list(map(operator.itemgetter('time'),  points))
    # print(times)
    # times = [local_time_epoch(item[:-1], "UTC") for item in times] # convert string time to epoch time
    # print(times)

    data = values #np.array(values)
    # print(data, times)
    return data, times



### example
# some_data = np.load('path/to/data.npy')
# result_ = extract_specific_bp(some_data, num_extraction=2, num_row=-2) ### -2 is SBP,  -1 is DBP in that data order.

def extract_specific_data(data, range_set, num_extraction, index_col):
    '''
    imports:
        import numpy as np
        import random
    args:
        data --- array like data
        num_extraction --- how many to extract
        index_col --- the index of target label located in array
    return:
        result --- array like data including targets
    '''
    if range_set == []:
        range_set = set(data[:,index_col])    ## get all target values
    print(len(range_set), range_set)

    # result = []
    i = 0
    for each_target in range_set:
        ### if there is not enough data for requesting, skip
        if len(np.where(data[:,index_col]==each_target)[0]) < num_extraction:
            print(f'For target {each_target}, there is only {len(np.where(data[:,index_col]==each_target)[0])} data, however, you request {num_extraction}. Skip!')
            continue

        ### randomly get indexs of request target
        # selection_index = random.sample(list(np.where(data[:,index_col]==each_target)[0]), num_extraction)
        # print("selection_index:", selection_index)
        ### append requested target to result
        # result.append(data[index,:])
        if i ==0:
            ### randomly get indexs of request target
            selection_index = random.sample(list(np.where(data[:,index_col]==each_target)[0]), num_extraction)
            # print("selection_index:", selection_index)

        else:
            selection_index = np.append(selection_index, random.sample(list(np.where(data[:,index_col]==each_target)[0]), num_extraction), axis=0)
        i += 1

    # print("final selection_index:", selection_index)
    result = data[selection_index,:]
    return np.array(result), selection_index

def load_data_files(file_list):
  for ind, data_file in enumerate(file_list):
    data_set = load_data_file(data_file)
    if ind == 0:
        total_set = data_set
    else:
        total_set = np.concatenate( (total_set, data_set), 0)
  return total_set

def load_data_file(data_file):
    if data_file.endswith('.csv'):
        data_set = pd.read_csv(data_file).to_numpy()
    elif data_file.endswith('.npy'):
        data_set = np.load(data_file)
    return data_set

# # This function only applied to old separated data and feature set
# def load_data_feature_files(file_list, num_labels=6, load_feature = True):

#     for ind, (data_file, feature_file) in enumerate(file_list):
#         data_set = np.load(data_file)    #bed H2
#         if load_feature:
#             features_set = load_features_data(feature_file)
#         else:
#             features_set = extract_features_data(data_set, data_file, with_windowed = False)
#         # features_set = extract_or_load_features_data(data_set, feature_file, load_feature) #.to_numpy()
#         print(data_set.shape, features_set.shape)
#         # features_set = extract_or_load_features_data(data_set, feature_file, load_feature).drop("Unnamed: 0", axis= 1).to_numpy()
#         features_labels = np.concatenate( (features_set, data_set[:, -num_labels:]), 1)
#         if ind == 0:
#             all_features_labels = features_labels
#         else:
#             all_features_labels = np.concatenate( (all_features_labels, features_labels), 0)
        
#         data_file_noext = os.path.splitext(data_file)[0]
#         npy_name = data_file_noext+"_feature_label.npy"
#         np.save(npy_name, all_features_labels)

#     # print_stats_distribution("Whole data set", data_set, [('H', -4), ('R', -3), ('S', -2), ('D', -1)])

#     return all_features_labels

def prepare_train_test_data(data_set, split_ratio, time_sorted, 
    target_indexes, target_distribution, target_range=[0,200], 
    num_labels=6, time_index=-5, id_index=-6, show = False):
    '''
    label_indexes is one below:
        [('H', -4)], [('R', -3)], [('S', -2)], [('D', -1)]
    '''
    # eval_data_stats("all original set", data_set, target_index, time_index )

    # target_index = target_indexes[2][1]
    # time_index = -5

    data_size = data_set.shape[0]
    # minimum_num_sample = int(data_size/len(target_range)/4)

    if time_sorted:
        sorted_indexes = np.argsort(data_set[:, time_index])
        data_set = data_set[sorted_indexes]
    else: # random shuffle
        np.random.shuffle(data_set) 

    print(data_set.shape)

    train_size = int(data_size*split_ratio)
    # test_size = data_size - train_size

    train_set = data_set[:train_size, :]
    test_set = data_set[train_size:, :]

    if target_distribution == "uniform":
        train_set = select_with_uniform_distribution(train_set, target_indexes)
        test_set = select_with_uniform_distribution(test_set, target_indexes)
    elif target_distribution == "gaussian":
        train_set = select_with_gaussian_distribution(train_set, target_indexes)
        test_set = select_with_gaussian_distribution(test_set, target_indexes)

    comb_data_set = np.concatenate((train_set, test_set), 0)
    # eval_data_stats("all data set", data_set, vital_indexes)
    if show:
        eval_data_stats(f"original set with {target_distribution}:", data_set)        
        eval_data_stats(f"train set with {target_distribution}:", train_set)
        eval_data_stats(f"test set with {target_distribution}:", test_set)
        eval_data_stats(f"recombined set with {target_distribution}:", comb_data_set)

    return train_set, test_set

def dummy_scg_data_set():
    rows, cols = (30, 6)
    time_index=-5
    # data_set = [[0]*cols]*rows
    # data_set[:,time_index] = np.random.randint(low=0, high=8, size=(rows, 1))

    data_set = np.random.randint(10, size=(rows, cols))
    print(data_set[:,time_index])
    return data_set

import copy
def get_truncated_epoch(input_epoch, interval="day"):
    if interval == "day":
        divider = 86400
    elif interval == "hour":
        divider = 3600
    elif interval == "10min":
        divider = 600
    elif interval == "minute":
        divider = 60
    elif interval == "second": #10 seconds
        divider = 10
    else:
        return input_epoch 

    out_epoch = np.zeros((input_epoch.shape[0],), dtype=int)
    for i in range(input_epoch.shape[0]):
        out_epoch[i] = input_epoch[i] - (input_epoch[i] % divider)
        # if i == 0:
        #     print(f"Truncated: {input_epoch[i]} => {out_epoch[i]}")
    return out_epoch

def get_train_index_list_by_time(data_time, no_overlap, split_ratio, debug=False):
    truncated_data_time = get_truncated_epoch(data_time, no_overlap)

    counter_result = Counter(truncated_data_time)
    dict_counter = dict(counter_result)
    result_dict = dict_counter.copy()

    keys_list = list(result_dict.keys())
    random.shuffle(keys_list)
    train_size = int(len(keys_list) * split_ratio)
    train_keys_list = keys_list[:train_size]

    if debug: print(f"keys_list: {keys_list}; train_keys_list: {train_keys_list}")

    train_index_list = []
    for each_key in train_keys_list:
        train_index_list += list(np.where(truncated_data_time == each_key)[0])
    return train_index_list

def get_train_index_list_by_sort(data_time, no_overlap, split_ratio, debug=False):
    truncated_data_time = get_truncated_epoch(data_time, interval="day")

    counter_result = Counter(truncated_data_time)
    dict_counter = dict(counter_result)
    result_dict = dict_counter.copy()

    keys_list = list(result_dict.keys())
    # random.shuffle(keys_list)
    # train_size = int(len(keys_list) * split_ratio)
    # train_keys_list = keys_list[:train_size]

    # if debug: print(f"keys_list: {keys_list}; train_keys_list: {train_keys_list}")

    train_index_list = []
    for each_key in keys_list:
        all_index_list = list(np.where(truncated_data_time == each_key)[0])
        # all_index_list = all_index_list[np.argsort(data_time[all_index_list])]
        train_size = int(len(all_index_list) * split_ratio)
        train_index_list += all_index_list[:train_size]
    return train_index_list

def get_train_index_list_by_bed(data_bed, no_overlap, split_ratio, debug=False):
#    train_keys_list = [mac_to_int("b8:27:eb:6c:6e:22"), mac_to_int("b8:27:eb:5b:35:37")] # H1 and H2
    train_keys_list = [mac_to_int("b8:27:eb:23:4b:2b"), mac_to_int("b8:27:eb:80:1c:cf")] # F1 and F2
    train_index_list = []
    for each_key in train_keys_list:
        train_index_list += list(np.where(data_bed == each_key)[0])
    return train_index_list


def prepare_train_test_data_no_overlap(data_name, data_set, split_ratio, no_overlap, 
    target_indexes, target_distribution, target_range=[0,200], 
    num_labels=6, time_index=-5, id_index=-6, show=True, debug=False):
    '''
    label_indexes is one below:
        [('H', -4)], [('R', -3)], [('S', -2)], [('D', -1)]
    '''
    # if debug:  data_set = dummy_scg_data_set() # for test correct split
    data_set = data_set[np.argsort(data_set[:,time_index])]
    data_size = data_set.shape[0]
    if no_overlap == "bed":
        train_index_list = get_train_index_list_by_bed(data_set[:,id_index], no_overlap, split_ratio)
    elif no_overlap == "sort":
        train_index_list = get_train_index_list_by_sort(data_set[:,time_index], no_overlap, split_ratio)
    else:
        train_index_list = get_train_index_list_by_time(data_set[:,time_index], no_overlap, split_ratio)
    # test_index_list = keys - train_index_list
    all_index_list = list(range(data_size))
    test_index_list = [x for x in all_index_list if x not in train_index_list]
    train_set = data_set[train_index_list]
    test_set = data_set[test_index_list]

    if debug: 
        print(f"train(size:{len(train_index_list)}): {train_index_list}: {train_set[:,time_index]}")
        print(f"test(size:{len(test_index_list)}): {test_index_list}: {test_set[:,time_index]}") 
    
    # comb_data_set = np.concatenate((train_set, test_set), 0)
    # eval_data_stats("all data set", data_set, vital_indexes)
    if show:
        eval_data_stats(f"{data_name}_all", data_set, show=True)        
        eval_data_stats(f"{data_name}_train", train_set, show=True)
        eval_data_stats(f"{data_name}_test", test_set, show=True)
        # eval_data_stats(f"{data_name}_recombine", comb_data_set, show)

        # eval_data_stats(f"original set with {target_distribution} of size({data_set.shape[0]}):", data_set)        
        # eval_data_stats(f"train set with {target_distribution} of size({train_set.shape[0]}):", train_set)
        # eval_data_stats(f"test set with {target_distribution} of size({test_set.shape[0]}):", test_set)
        # eval_data_stats(f"recombined set with {target_distribution} of size({comb_data_set.shape[0]}):", comb_data_set)

    return train_set, test_set


def prepare_train_test_data_v3(data_set, split_ratio, time_sorted, 
    target_indexes, target_distribution, target_range=[0,200], 
    num_labels=6, time_index=-5, id_index=-6, show = True):
    '''
    label_indexes is one below:
        [('H', -4)], [('R', -3)], [('S', -2)], [('D', -1)]
    '''
    orig_data_size = data_set.shape[0]
    # minimum_num_sample = int(data_size/len(target_range)/4)
    if target_distribution == "uniform":
        data_set = select_with_uniform_distribution(data_set, target_indexes)
    elif target_distribution == "gaussian":
        data_set = select_with_gaussian_distribution(data_set, target_indexes)

    data_size = data_set.shape[0]

    data = data_set[:,time_index]
    minimum_num_sample = int(len(data)/len(list(set(data)))*0.7)

    counter_result = Counter(data)
    dict_counter = dict(counter_result)
    result_dict = dict_counter.copy()

    # we keep them even if they have less than minimum
    # for item in dict_counter.items():
    #     if item[1] < minimum_num_sample:
    #         del result_dict[item[0]]

    keys = list(result_dict.keys())

    train_index_list = []
    for each_key in keys:
        train_index_list += list(np.random.choice(np.where(data == each_key)[0], size=minimum_num_sample))

    # test_index_list = keys - train_index_list
    all_index_list = list(range(data_size))
    # print(train_index_list)
    # print("***********************************************")

    test_index_list = [x for x in all_index_list if x not in train_index_list]
    # print(test_index_list)
    train_set = data_set[train_index_list]

    test_set = data_set[test_index_list]

    comb_data_set = np.concatenate((train_set, test_set), 0)
    # eval_data_stats("all data set", data_set, vital_indexes)
    if show:
        eval_data_stats(f"original set with {target_distribution} of size({orig_data_size}):", data_set)        
        eval_data_stats(f"train set with {target_distribution} of size({len(train_set)}):", train_set)
        eval_data_stats(f"test set with {target_distribution} of size({len(test_set)}):", test_set)
        eval_data_stats(f"recombined set with {target_distribution} of size({len(comb_data_set)}):", comb_data_set)

    return train_set, test_set


def standardize_data(X):
    X_mean = np.mean(X, axis = 1)
    X_mean = np.reshape(X_mean, (-1,1))
    X_std = np.std(X, axis = 1)
    X_std = np.reshape(X_std, (-1,1))
    X = (X - X_mean)/X_std
    return X


# def extract_features_data(data_set, data_file, with_windowed = True):

#     filename_noext = os.path.splitext(data_file)[0]
    
#     if with_windowed:
#         features_ready = windowed_feature_extraction(data_set, window_size = 200)
#         wstr = "_wd"
#     else:
#         features_ready = unwindowed_feature_extraction(data_set)
#         wstr = "_uw"

#     csv_name = filename_noext+ wstr+ "_feature.csv"
#     features_ready.to_csv(csv_name)
#     print("Save features into: ", csv_name)

#     features_ready = features_ready.to_numpy()
#     npy_name = filename_noext+ wstr+ "_feature.npy"
#     np.save(npy_name, features_ready)
#     print("Save features into: ", npy_name)

#     # if filename.endswith('.csv'):
#     #   features_ready.to_csv(filename)
#     # elif filename.endswith('.npy'):
#     #    np.save(filename, features_ready)

#     return features_ready

# def load_features_data(feature_file):
#     if feature_file.endswith('.csv'):
#         features_ready = pd.read_csv(feature_file).to_numpy()
#     elif feature_file.endswith('.npy'):
#         features_ready = np.load(feature_file)
#     return features_ready
# if __name__ == "__main__":

def J_peaks_detection(x, f):
    window_len = round(1/f * 100)
    start = 0
    J_peaks_index = []
    
    #get J peaks
    while start < len(x):
        end = start + window_len
        if start > 0:
            segmentation = x[start -1 : end]
        else:
            segmentation = x[start : end]
        # J_peak_index = np.argmax(segmentation) + start
        max_ids = argrelextrema(segmentation, np.greater)[0]
        for index in max_ids:
            if index == max_ids[0]:
                max_val = segmentation[index]
                J_peak_index = index + start
            elif max_val < segmentation[index]:
                max_val = segmentation[index]
                J_peak_index = index + start
        
        if len(max_ids) > 0 and x[J_peak_index] > 0:
            if len(J_peaks_index) == 0 or J_peak_index != J_peaks_index[-1]:
                J_peaks_index.append(J_peak_index)
        start = start + window_len//2
    
    return J_peaks_index

def kurtosis(data):
    x = data - np.mean(data)
    a = 0
    b = 0
    for i in range(len(x)):
        a += x[i] ** 4
        b += x[i] ** 2
    a = a/len(x)
    b = b/len(x)
    k = a/(b**2)
    return k

def wavelet_decomposition(data, wave, Fs = None, n_decomposition = None):
    a = data
    w = wave
    ca = []
    cd = []
    rec_a = []
    rec_d = []
    freq_range = []
    for i in range(n_decomposition):
        if i == 0:
            freq_range.append(Fs/2)
        freq_range.append(Fs/2/(2** (i+1)))
        (a, d) = pywt.dwt(a, w)
        ca.append(a)
        cd.append(d)

    for i, coeff in enumerate(ca):
        coeff_list = [coeff, None] + [None] * i
        rec = pywt.waverec(coeff_list, w)
        rec_a.append(rec)

    for i, coeff in enumerate(cd):
        coeff_list = [None, coeff] + [None] * i
        rec_d.append(pywt.waverec(coeff_list, w))
         
    return rec_a, rec_d

def zero_cross_rate(x):
    cnt  = 0
    x = standize(x)
    for i in range(1,len(x)):
        if x[i] > 0 and x[i-1] < 0:
            cnt += 1
        elif x[i] < 0 and x[i-1] > 0:
            cnt += 1
    return cnt

def standize(data):
    return (data - np.mean(data))/np.std(data)


#define high-order butterworth low-pass filter
def low_pass_filter(data, Fs, low, order, causal = False):
    b, a = signal.butter(order, low/(Fs * 0.5), 'low')
    if causal:
        filtered_data = signal.lfilter(b, a, data)
    else:
        filtered_data = signal.filtfilt(b, a, data)
    # filtered_data = signal.filtfilt(b, a, data, method = 'gust')
    return filtered_data

def high_pass_filter(data, Fs, high, order, causal = False):
    b, a = signal.butter(order, high/(Fs * 0.5), 'high')
    if causal:
        filtered_data = signal.lfilter(b, a, data)
    else:
        filtered_data = signal.filtfilt(b, a, data)
    # filtered_data = signal.filtfilt(b, a, data, method = 'gust')
    return filtered_data

def band_pass_filter(data, Fs, low, high, order, causal = False):
    b, a = signal.butter(order, [low/(Fs * 0.5), high/(Fs * 0.5)], 'bandpass')
    # perform band pass filter
    if causal:
        filtered_data = signal.lfilter(b, a, data)
    else:
        filtered_data = signal.filtfilt(b, a, data)
    return filtered_data

def ACF(x, lag):
    acf = []
    mean_x = np.mean(x)
    var = sum((x - mean_x) ** 2)
    for i in range(lag):
        if i == 0:
            lag_x = x
            original_x = x
        else:
            lag_x = x[i:]
            original_x = x[:-i]
        new_x = sum((lag_x - mean_x) * (original_x - mean_x))/var
        new_x = new_x/len(lag_x)
        acf.append(new_x)
    return np.array(acf)

def next_power_of_2(x):  
    return 1 if x == 0 else 2**(x - 1).bit_length()

def freq_com_select(Fs, low, high):
    n = 0
    valid_freq = Fs/2
    temp_f = valid_freq
    min_diff_high = abs(temp_f - high)
    min_diff_low = abs(temp_f - low)
    
    while(temp_f > low):
        temp_f = temp_f / 2
        n += 1
        diff_high = abs(temp_f - high)
        diff_low = abs(temp_f - low)
        if diff_high < min_diff_high:
            max_n = n
            min_diff_high = diff_high
        if diff_low < min_diff_low:
            min_n = n
            min_diff_low = diff_low
    return n, max_n, min_n

def remove_outliers(data):
    # Calculate Q1 (25th percentile) and Q3 (75th percentile)
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    
    # Calculate the Interquartile Range (IQR)
    IQR = Q3 - Q1
    
    # Define bounds for detecting outliers
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # Filter the data to remove outliers
    filtered_data = [x for x in data if lower_bound <= x <= upper_bound]
    
    return filtered_data


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
        packed_data += struct.pack("i", item)


    return packed_data


def write_mqtt(hrdata, rrdata, timestamp, fs):
    mac_addr="12:02:12:02:12:02"
    timestamp = int(timestamp * 1000000)
    hrdata = np.int32(hrdata)
    rrdata = np.int32(rrdata)
    Ts = int((1/fs) * 1000000)
    packed_data_1 = pack_beddot_data(mac_addr, timestamp, Ts, hrdata) # 10000 equates to fs=1/0.01=100
    packed_data_2 = pack_beddot_data(mac_addr, timestamp, Ts, rrdata)

    client = mqtt.Client()
    client.connect("sensorweb.us", 1883)
    mqtt_thread = threading.Thread(target=lambda: client.loop_forever())
    mqtt_thread.start()


    client.publish("/UGA/120212021202/hrlabel", packed_data_1, qos=1)
    client.publish("/UGA/120212021202/rrlabel", packed_data_2, qos=1)
    print('Published')
    return None

