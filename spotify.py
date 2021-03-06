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
import time

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
playlist_df.to_pickle("playlist_df.pkl")

# %% plot values of library
import plotly.graph_objects as go
from plotly.offline import plot as htmlplot
import plotly.express as px

fig = px.scatter(playlist_df, x="valence", y="energy",
                 hover_data=['name'])


htmlplot(fig)
