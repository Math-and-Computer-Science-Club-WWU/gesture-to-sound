
from dotenv import load_dotenv
import spotipy
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


# Paste your Spotify playlist link here
PLAYLIST_URL = "https://open.spotify.com/playlist/3ZHL9IdjmSA4lFGt2L7xJW?si=8199fd0a9c944a3f"

# Extract the playlist ID from the URL
playlist_id = PLAYLIST_URL.split("playlist/")[1].split("?")[0]

# Check available playback devices
devices = sp.devices()["devices"]

if not devices:
    print("No Spotify devices found. Open Spotify and try again.")
else:
    device_id = next(
        (device["id"] for device in devices if device["is_active"]),
        devices[0]["id"]
    )

    # Start playing the playlist
    sp.start_playback(
        device_id=device_id,
        context_uri=f"spotify:playlist:{playlist_id}"
    )

    print("Your playlist is starting!")

    # Pause Spotify after starting playback
    # Uncomment this line later if you want to test pausing:
    # sp.pause_playback(device_id=device_id)
