# -*- coding: utf-8 -*-
"""
Created on Sun Feb 20 08:52:13 2022

@author: Alice
"""

import requests
import datetime
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import sys
import spotipy
import pandas as pd
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import raspberrypi.eeglibv2


with open('credentials.json', 'r') as f:
    cred = json.load(f)

ruri = r"https://www.google.com"

firebase_cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(firebase_cred)
db = firestore.client()

# %% Import playlist pickle
playlist_df = pd.read_pickle("playlist_df.pkl")

# %% generate tree
from scipy import spatial
valence_energy_pairs = list(playlist_df[['valence', 'energy']].itertuples(index=False, name=None))
k=1 # gets incremented to prevent same song from being played over and over again
tree = spatial.KDTree(valence_energy_pairs)

# %% PLAY MUSIC
scope = "streaming user-read-playback-state"
token = spotipy.util.prompt_for_user_token(cred['spotify_premium']['username'], scope,
                                           client_id=cred['spotify_premium']['client_id'],
                                           client_secret=cred['spotify_premium']['client_secret'],
                                           redirect_uri=ruri)
sp = spotipy.Spotify(auth=token)
device_id = sp.devices()['devices'][0]['id']

def get_song(valence_energy_coord, k=1):
    _, closest_index = tree.query(valence_energy_coord, k=[k])
    closest_index = closest_index[0]
    print(playlist_df.loc[closest_index, "name"])

    current_uri = playlist_df.loc[closest_index, 'uri']
    return current_uri

ki = 1
i = 0
uri_list = []
current_uri = get_song([0.5, 0.5]) # default setting
uri_list.append(current_uri)
sp.start_playback(device_id=device_id, uris=[current_uri])

while i<100:
    # if song is still playing
    if sp.current_playback()['is_playing']:
        time.sleep(i)
        i += 1
        print(i)
        pass
    else:
        print("song stopped")

        # get most recent biometric data
        data_ref = db.collection(u'biometric_data').order_by('TimeStamp', direction=firestore.Query.DESCENDING).limit(1)
        docs = data_ref.stream()

        df = pd.DataFrame()
        for doc in docs:
            latest_biodata = doc.to_dict()
            print("Getting latest data")

        # recalculate brainwaves
        recalculated_brainwaves = raspberrypi.eeglibv2.getbrainwaves(
            latest_biodata['eegraw'], latest_biodata['eegsamplerate'])
        # magic formula
        print(recalculated_brainwaves["arousal"], recalculated_brainwaves["valence"])
        arousal_coord = abs(recalculated_brainwaves["arousal"])+(latest_biodata['hr']/100)
        valence_coord = abs(recalculated_brainwaves["valence"])*10
        print(datetime.datetime.fromtimestamp(latest_biodata['TimeStamp']))
        print(f"arousal = {arousal_coord}, valence = {valence_coord}")
        coord = [arousal_coord, valence_coord]
        #coord = json.loads(input("Enter coords:"))
        #print(coord)

        while ki < 10:
            if get_song(coord, k=1) not in uri_list:
                ki = 1
                break
            else:
                ki += 1
                if get_song(coord, k=ki) not in uri_list:
                    break
        else:
            print("giving up, setting k to 1")
            ki = 1

        print(f"ki: {ki}")
        current_uri = get_song(coord, ki)
        uri_list.append(current_uri)
        sp.start_playback(device_id=device_id, uris=[current_uri])
