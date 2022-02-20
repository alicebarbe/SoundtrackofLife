# SoundtrackofLife

## Emotion mapping
![image](https://user-images.githubusercontent.com/21221668/154844681-f943f53a-e098-4999-9706-8ccda046be41.png)

Seemo: A Computational Approach to See Emotions - Scientific Figure on ResearchGate. Available from: https://www.researchgate.net/figure/Core-emotions-established-in-the-circumplex-model_fig1_324664655 [accessed 20 Feb, 2022]

## Architecture "Diagram"
![image](https://user-images.githubusercontent.com/21221668/154844541-14d5661f-8922-4674-a01d-cad08132e8e6.png)

## top secret config file format and how to link to your spotify account
In `credentials.json`:
```
{
  "spotify": {
    "username": "[redacted]",
    "client_id": "[redacted]",
    "client_secret": "[redacted]"},
  "spotify_premium": {
    "username": "[redacted]",
    "client_id": "[redacted]",
    "client_secret": "[redacted]",
    "device_id": "[redacted]"
  },
}
```

The regular spotify account is used to get the library playlist data. A Spotify premium account is required to run the play_song file which plays the actual song on your device. Create a `client_id` and `client_secret` by creating an application on your Spotify for Developers dashboard. Be sure to set the redirect URI to `https://google.com`

`firebase_credentials.json` is provided when you create a Firebase database.

Use the `spotify.py` file to generate a pickle file storing all the songs in your library so you don't have to query through it again.
Use the `play_songs.py` file to actually play songs based on the latest biometric data in the database.
