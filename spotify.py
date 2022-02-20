# -*- coding: utf-8 -*-
"""
Created on Sat Feb 19 12:11:06 2022

@author: Alice
"""

import requests
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import sys
import spotipy
import pandas as pd

with open('credentials.json', 'r') as f:
    cred = json.load(f)

scope = "user-library-read"

ruri = r"https://www.google.com"

token = spotipy.util.prompt_for_user_token(cred['spotify']['username'], scope,
                                           client_id=cred['spotify']['client_id'],
                                           client_secret=cred['spotify']['client_secret'],
                                           redirect_uri=ruri)

def get_library_tracks(sp):
    results = sp.current_user_saved_tracks(limit=50)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def get_playlist_df(token):
    playlist_df = pd.DataFrame(columns=['uri', 'name', 'artist', 'energy', 'valence'])

    if token:
        sp = spotipy.Spotify(auth=token)
        #results = sp.current_user_saved_tracks(limit=50)
        results = get_library_tracks(sp)
        results = [result['track'] for result in results]

        i = 0
        for track in results:
            track_uri = track["uri"]
            track_name = track['name']
            track_artist = track['artists'][0]['name']
            energy = sp.audio_features(track_uri)[0]['energy']
            valence = sp.audio_features(track_uri)[0]['valence']
            playlist_df = playlist_df.append({'uri': track_uri,
                                              'name': track_name,
                                              'artist': track_artist,
                                              'energy': energy,
                                              'valence': valence}, ignore_index=True)
            print(f"{i}: {track_name} - {track_artist}")
            i += 1
    else:
        print("Can't get token for", cred['spotify']['username'])

    return playlist_df

playlist_df = get_playlist_df(token)
# %%
playlist_df.to_pickle("playlist_df1.pkl")
# %%
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
    print(playlist_df.loc[closest_index, :])

    current_uri = playlist_df.loc[closest_index, 'uri']
    return current_uri

ki = 1
i = 0
import time
uri_list = []
current_uri = get_song([0.2, 0.2])
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
        coord = json.loads(input("Enter coords:"))
        print(coord)

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


# %% plot values of library
import plotly.graph_objects as go
from plotly.offline import plot as htmlplot
import plotly.express as px

fig = px.scatter(playlist_df, x="valence", y="energy",
                 hover_data=['name'])


htmlplot(fig)
