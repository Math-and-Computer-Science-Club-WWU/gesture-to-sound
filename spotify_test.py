
import os
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

scope = (
    "user-read-playback-state "
    "user-modify-playback-state "
    "playlist-read-private "
    "playlist-read-collaborative"
)

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(scope=scope)
)

user = sp.current_user()
print("Connected to Spotify!")
print("Account:", user["display_name"])

playlists = sp.current_user_playlists(limit=50)

print("\nYour playlists:")
for playlist in playlists["items"]:
    print(playlist["name"], "-", playlist["external_urls"]["spotify"])
