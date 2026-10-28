Requirements
- Python 3.14 (the version used during development; compatibility may vary by package version)\
- A Spotify account with access to playback controls 
- A Spotify Developer application 
- A webcam

1. Clone the repository
git clone YOUR_REPOSITORY_URL
cd spotify-gesture-dj

2. Create a virtual environment
python -m venv .venv
Activate it on macOS:
source .venv/bin/activate

3. Install dependencies
python -m pip install -r requirements.txt

4. Configure Spotify credentials
Create a .env file in the project folder. Add your own Spotify Developer application credentials:
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
Replace the placeholder values with your own credentials. Never commit your .env file to GitHub.
In your Spotify Developer Dashboard, configure the redirect URI to match the value above.

5. Configure the playlist
In main.py, set PLAYLIST_URL to the Spotify playlist you want to control.

6. Set up the hand-tracking model
Make sure the MediaPipe Hand Landmarker model file, hand_landmarker.task, is available at the path expected by the program. If it is not included in the repository, obtain the model from the official MediaPipe documentation and place it in the project folder.

7. Run the project
Open Spotify, make sure a playback device is available, and run:
python main.py
Allow webcam access if macOS requests permission. Press q to close the hand-tracking window.

Security!
Credentials and authentication tokens must not be committed to GitHub. The .env file and Spotify authentication cache should remain private.

Future Improvements
- Improve gesture recognition and responsiveness. 
- Prevent repeated playlist restarts while holding the playback gesture. 
- Improve gesture feedback and error handling. 
- Add more customizable music controls.