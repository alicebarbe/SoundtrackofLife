# -*- coding: utf-8 -*-
"""
Created on Sat Feb 19 20:23:11 2022

@author: Alice
"""
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd

cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# %%

data_ref = db.collection(u'biometric_data').order_by('TimeStamp', direction=firestore.Query.DESCENDING).limit(200)
docs = data_ref.stream()

df = pd.DataFrame()
for doc in docs:
    new_row = {'timestamp': doc.id, **doc.to_dict()}
    df = df.append(new_row, ignore_index=True)

# %% get brain sample

import raspberrypi.eeglib as eeglib
import numpy as np

eegraw = df['eegraw'][116]
samplerate = df['eegsamplerate'][116]
brainwaves = eeglib.getbrainwaves(eegraw, samplerate)

amplitude = np.array(eegraw)

fourierTransform = np.fft.fft(amplitude)/len(amplitude)           # Normalize amplitude
fourierTransform = fourierTransform[range(int(len(amplitude)/2))] # Exclude sampling frequency


tpCount     = len(amplitude)
values      = np.arange(int(tpCount/2))
timePeriod  = tpCount/samplerate
frequencies = values/timePeriod

# %% Look at brain
import matplotlib.pyplot as plt
plt.plot(frequencies[frequencies>0.1], abs(fourierTransform)[frequencies>0.1])

# %% Look at more brain
df[['alpha', 'beta', 'gamma', 'theta', 'delta']].plot()

# %% Look at heart values
plt.plot(df['HeartRateValues'][96])
