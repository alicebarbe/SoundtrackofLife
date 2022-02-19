import time
import os
import math
import glob
import numpy as np
#import pyqtgraph as pg
#from pyqtgraph.Qt import QtGui
#from grove.adc import ADC
from scipy.signal import find_peaks
import RPi.GPIO as GPIO
import basichrv
import eeglib
import requests
import json
import sensors
import dataupload


# initialize temperature probe

#os.system('modprobe w1-gpio')
#os.system('modprobe w1-therm')
 
#base_dir = '/sys/bus/w1/devices/'
#device_folder = glob.glob(base_dir + '28*')[0]
#device_file = device_folder + '/w1_slave'

plotting = False

# initialize pin numbers
#ECG_A = 1
#GSR_A = 2
#EMG_A = 0

delay = 0.001
#temp_update = 20

#GPIO.setmode(GPIO.BCM)

#adc = ADC(address=0x08)

# initialize graph things
"""
if plotting:
    app = QtGui.QApplication([])
    win = pg.GraphicsWindow(title="ECG")  # creates a window
    p = win.addPlot(title="Realtime plot")  # creates empty space for the plot in the window
    curve = p.plot()
    windowWidth = 500  # width of the window displaying the curve
    x = np.linspace(0, 0, windowWidth)  # create array that will contain the relevant time series
    ptr = -windowWidth  # set first x position

def update(value):
    #Update live QT plot with new value
    global curve, ptr, x
    ptr += 1  # update x position for displaying the curve
    x[:-1] = x[1:]  # shift data in the temporal mean 1 sample left
    try:
        x[-1] = float(value)  # vector containing the instantaneous values
    except:
        x[-1] = 0
    curve.setData(x)  # set the curve with this data
    curve.setPos(ptr, 0)  # set x position in the graph to 0

    QtGui.QApplication.processEvents()  # you MUST process the plot now
"""

def ema_filtering(new_value, prev_value):
    # initialize EMA stuff
    ema_a = 0.1
    return (ema_a*new_value) + ((1-ema_a)*prev_value)

"""
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def gettemp():
    while True:
        print("Getting temperature...")
        lines = read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            print(temp_c)
            return temp_c
"""

def calculate_rr(ecg_data, time_elapsed):
    peaks, _ = find_peaks(ecg_data, height=2200, distance=80)
    rr_arr = np.diff(peaks)
    rr_arr = rr_arr * time_elapsed / len(ecg_data)
    print(f"Number of beats: {len(rr_arr)}")
    return rr_arr

def get_hrv(rr):
    #print(basichrv.gethrv(rr))
    tdf, oc = basichrv.gethrv(rr)
    reading = {}
    reading['ectopic'] = oc
    reading['hrstd'] = tdf['std_hr']
    print(tdf['std_hr'])
    reading['hr'] = tdf['mean_hr']
    reading['hrv'] = tdf['sdnn']

    return reading
        
def sensors_settle():
    print("Start settling")
    for i in range(5):
        ecg_reading = sensors.readAnalog(4)*2000
        #eeg_reading = adc.read_voltage(EMG_A)
        #gsr_reading = adc.read_voltage(GSR_A)
    print("Done settling")

def read_fast_data():
    #eeg_batch = []
    ecg_batch = []
    #gsr_batch = []
    batch_size = 3000
    i = 0
    
    start_time = time.time_ns()
    while 1:
        i = i + 1

        ecg_reading = sensors.readAnalog(4)*2000
        ecg_batch.append(ecg_reading)
        #print(ecg_reading)
        #eeg_reading = adc.read_voltage(EMG_A)
        #eeg_batch.append(eeg_reading)
        
        #gsr_reading = adc.read_voltage(GSR_A)
        #gsr_batch.append(gsr_reading)
        
        if i >=batch_size:
            end_time = time.time_ns()
            time_elapsed = end_time - start_time
            
            # process ECG data
            rr_arr = calculate_rr(ecg_batch, time_elapsed/1000000.0)
            hrv_dict = get_hrv(rr_arr)
            #print(hrv_dict)
            #np.savetxt(f'ecg_data_{start_time}_to_{end_time}.csv', np.array(ecg_batch), delimiter=",")
            
            # process EEG data
            #samplerate = len(eeg_batch) / (time_elapsed/1000000000.0)
            #brainwaves = eeglib.getbrainwaves(eeg_batch, samplerate)
            #print(brainwaves)
            #np.savetxt(f'eeg_data_{start_time}_to_{end_time}.csv', np.array(eeg_batch), delimiter=",")
            
            # process GSR data
            #gsr_avg = np.array(gsr_batch).mean()
            #print(gsr_avg)
            #np.savetxt(f'gsr_data_{start_time}_to_{end_time}.csv', np.array(gsr_batch), delimiter=",")
            
            # get temperature
            #temp_reading = gettemp()
            #print(temp_reading)
            #np.savetxt('temp_reading_{end_time}.csv', np.array([temp_reading]), delimiter=",")
            
            payload = {
                "hr": hrv_dict['hr'],
                "hrstd": hrv_dict['hrstd'],
                "hrv": hrv_dict['hrv'],
                "ectopic": hrv_dict['ectopic'],
              #  "alpha": brainwaves['alpha'],
              #  "beta": brainwaves['beta'],
              #  "delta": brainwaves['delta'],
              #  "gamma": brainwaves['gamma'],
              #  "theta": brainwaves['theta'],
              #  "temp": temp_reading,
              #  "gsr": gsr_avg
              }
           
            
            #response = requests.request("POST", url, headers=headers, data=payload)
            dataupload.upload_data(payload)
            #print(response.text)
            
            #print(f"Data saved.")
            #print(f"Start time {start_time}, end time {end_time}")
            ecg_batch = []
            #gsr_batch = []
            #eeg_batch = []
            i = 0
            start_time = time.time_ns()
            #exit()

print("Starting application")
sensors_settle()
read_fast_data()
