
import cv2
import mediapipe as mp
import time
import subprocess
from pathlib import Path
import os
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

SOUND_FILE = Path(__file__).with_name("flick.wav")

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

PLAYLIST_URL = "https://open.spotify.com/playlist/3ZHL9IdjmSA4lFGt2L7xJW?si=ee136945edbe4a10"
playlist_id = PLAYLIST_URL.split("playlist/")[1].split("?")[0]
PLAYLIST_URI = f"spotify:playlist:{playlist_id}"


def play_playlist():
    devices = sp.devices()["devices"]

    if not devices:
        print("No Spotify device found. Open Spotify first.")
        return

    device_id = next(
        (d["id"] for d in devices if d["is_active"]),
        devices[0]["id"]
    )

    sp.start_playback(
        device_id=device_id,
        context_uri=PLAYLIST_URI
    )
    print("Frat flick detected: playing playlist!")



def pause_music():
    try:
        playback = sp.current_playback()

        if not playback or not playback.get("is_playing"):
            print("Spotify is not playing. Pause skipped.")
            return

        device = playback.get("device") or {}
        device_id = device.get("id")

        sp.pause_playback(device_id=device_id)
        print("Open palm detected: music paused!")

    except spotipy.exceptions.SpotifyException as error:
        print(f"Spotify could not pause playback: {error}")



def next_song():
    sp.next_track()
    print("Skip detected: next song!")


# Gesture tracking
swipe_start_x = None
swipe_start_time = None

swipe_window = 0.6

last_flick_time = 0
last_palm_time = 0
last_swipe_time = 0

gesture_cooldown = 1
swipe_threshold = 0.20


open_hand_start_x = None
open_hand_start_time = None
open_hand_action_done = False

open_hand_swipe_threshold = 0.1
open_hand_swipe_window = 1.0
open_hand_pause_delay = 1.0



def fingers_extended(hand):
    # Each fingertip is compared with its middle joint.
    # This first version works best when your palm faces the camera.
    index_up = hand[8].y < hand[6].y
    middle_up = hand[12].y < hand[10].y
    ring_up = hand[16].y < hand[14].y
    pinky_up = hand[20].y < hand[18].y

    # Thumb uses horizontal distance because it points sideways.
    thumb_out = abs(hand[4].x - hand[2].x) > 0.06

    return [thumb_out, index_up, middle_up, ring_up, pinky_up]


#These var tracks your fingers movement and prevent from the sound looping
previous_tip_y = None
previous_time = None
last_flick_time = 0
flick_cooldown = 1.5
#Makes the text stay longer
text_display_until = 0

#Hand conections, I am having trouble with mediapipe so we are making the lines ourselves
HAND_CONNECTIONS = [
    # Thumb
    (0, 1), (1, 2), (2, 3), (3, 4),

    # Index finger
    (0, 5), (5, 6), (6, 7), (7, 8),

    # Middle finger
    (5, 9), (9, 10), (10, 11), (11, 12),

    # Ring finger
    (9, 13), (13, 14), (14, 15), (15, 16),

    # Pinky
    (13, 17), (17, 18), (18, 19), (19, 20),

    # Palm
    (0, 17), (5, 9), (9, 13), (13, 17)
]

# Set up the webcam
cap = cv2.VideoCapture(1)

# Configure MediaPipe Tasks
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path="hand_landmarker.task"
    ),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=2
)

with HandLandmarker.create_from_options(options) as landmarker:
    start_time = time.monotonic()

    while cap.isOpened():
        success, frame = cap.read()

        if not success:
            break

        # Mirror the webcam image
        frame = cv2.flip(frame, 1)

        # Convert BGR (OpenCV) to RGB (MediaPipe)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Create a MediaPipe image
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # Video mode requires a timestamp in milliseconds
        timestamp_ms = int(
            (time.monotonic() - start_time) * 1000
        )

        result = landmarker.detect_for_video(
            mp_image, timestamp_ms
        )

        # Draw detected hand landmarks
        height, width, _ = frame.shape

        if result.hand_landmarks:
            for hand in result.hand_landmarks:
                points = []

                for landmark in hand:
                    x = int(landmark.x * width)
                    y = int(landmark.y * height)
                    points.append((x, y))

                # Draw landmark points
                for point in points:
                    cv2.circle(
                        frame, point, 5, (0, 255, 0), -1
                    )
                for a, b in HAND_CONNECTIONS:
                    cv2.line(
                        frame,
                        points[a],
                        points[b],
                        (255, 0, 0),
                        2
                    )

                # Detect which fingers are extended
                current_time = time.monotonic()
                fingers = fingers_extended(hand)

                thumb_up, index_up, middle_up, ring_up, pinky_up = fingers

                # Gesture 1: Your frat flick hand pose
                frat_pose = (
                    thumb_up
                    and index_up
                    and middle_up
                    and not ring_up
                    and not pinky_up
                )

                if frat_pose and current_time - last_flick_time > gesture_cooldown:
                    play_playlist()
                    last_flick_time = current_time

                    cv2.putText(
                        frame, "PLAYING PLAYLIST!",
                        (40, 80), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 255), 3
                    )

                # Gesture 2: Open palm pauses music
                open_hand = all(fingers)

                if (
                    open_hand
                    and current_time - last_palm_time > gesture_cooldown
                ):
                    pause_music()
                    last_palm_time = current_time

                    cv2.putText(
                        frame, "PAUSED",
                        (40, 80), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 255), 3
                    )


                # Gesture 3: Three fingers up skips the song
                three_fingers_up = (
                    index_up
                    and middle_up
                    and ring_up
                    and not thumb_up
                    and not pinky_up
                )

                if (
                    three_fingers_up
                    and current_time - last_swipe_time > gesture_cooldown
                ):
                    next_song()
                    last_swipe_time = current_time

                    cv2.putText(
                        frame,
                        "NEXT SONG!",
                        (40, 130),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 255),
                        3
                    )

        cv2.imshow("Hand Tracker", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
