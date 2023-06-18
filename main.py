import os
import json
import random
import time
import cv2
import numpy as np
import pyautogui
from PIL import Image
import pytesseract
import sys

if getattr(sys, 'frozen', False):
    # Running in a PyInstaller bundle
    pytesseract.pytesseract.tesseract_cmd = os.path.join(sys._MEIPASS, 'tesseract', 'tesseract.exe')
else:
    # Running in a normal Python environment
    pytesseract.pytesseract.tesseract_cmd = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tesseract', 'tesseract.exe')



if getattr(sys, 'frozen', False):
    # If it's bundled, add the directory containing the bundled .dll files to the PATH
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']
    # Also set the VLC_PLUGIN_PATH to point to the "plugins" directory
    os.environ['VLC_PLUGIN_PATH'] = os.path.join(sys._MEIPASS, 'plugins')
else:
    # If it's not bundled, add the directory containing the .dll files to the PATH
    # Assuming that the .dll files and "plugins" directory are in the same directory as the main.py file
    os.environ['PATH'] = os.path.dirname(os.path.realpath(__file__)) + ";" + os.environ['PATH']
    # Also set the VLC_PLUGIN_PATH to point to the "plugins" directory
    os.environ['VLC_PLUGIN_PATH'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'plugins')

import vlc
from yt_dlp import YoutubeDL
from collections import deque
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import queue
from datetime import datetime
import atexit


def run_gui(message_queue):
    root = tk.Tk()
    root.title("DiabloTunes")
    root.geometry("500x500")

    text_area = scrolledtext.ScrolledText(root, wrap = tk.WORD, width = 40, height = 10)
    text_area.pack()

    gui_state = tk.StringVar()
    gui_state.set("Diablo 4 zone name not detected, launch the game to start the playback")
    state_label = tk.Label(root, textvariable=gui_state, foreground="red")
    state_label.pack()

    def on_closing():
        # Cancel scheduled tasks before closing
        if root.after_id:
            root.after_cancel(root.after_id)

        # Destroy the root window to terminate the application
        root.destroy()
        os._exit(0)  # Use this instead of sys.exit()

    # Bind the on_closing function to the closing event of the root window
    root.protocol("WM_DELETE_WINDOW", on_closing)

    def print_log(message, type_of_message):  # define the print_log function inside the run_gui function
        print(message)  # print to console

        # Only print to text area if the message is a change in zone/act or a song start/stop
        if type_of_message in ['act_zone_change', 'song_start_stop']:
            text_area.insert(tk.END, f"{message}\n")  # print to text area in the GUI

    def change_volume(val):
        volume = int(val)  # convert the volume to integer
        player.audio_set_volume(volume)  # volume should be between 0 and 100 in vlc
        print_log(f"Volume set to {volume}", 'volume_change')

    separator_label = tk.Label(root, text="")
    separator_label.pack()

    volume_label = tk.Label(root, text="Volume")
    volume_label.pack()

    volume_scale = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, command=change_volume)
    volume_scale.set(100)  # Default volume level
    volume_scale.pack()

    def check_queue():
        while not message_queue.empty():
            message, message_type = message_queue.get()
            print(f"Message received: {message}, Message type: {message_type}") 
            if message_type == 'act_zone_change':
                # Extract zone
                zone = message.split(" (")[0]

                # Load act-zone hierarchy from json file
                with open("output.json", "r") as f:
                    act_zone_hierarchy = json.load(f)

                # Check if the location is a zone or an act
                if zone in [zone for zones in act_zone_hierarchy.values() for zone in zones]:
                    act = next((act for act, zones in act_zone_hierarchy.items() if zone in zones), None)
                    gui_state.set("Playback Active")
                else:
                    act = zone
                    zone = 'Open World'
                    gui_state.set("Playback Active")

                if not act:
                    print(f'Unable to find act for zone: {zone}. Please check your output.json file.')
                    return

                # Get the current time
                time_str = datetime.now().strftime("[%H:%M]")

                # Handle act and zone change here
                text_area.insert(tk.END, f"{time_str} Act: {act}, Zone: {zone}\n")
            elif message_type == 'song_started':
                print("Song started event received")  # Debugging line
                # Get the current time
                time_str = datetime.now().strftime("[%H:%M]")
                # Add the URL of the song to the log
                print_log(f"{time_str} Song URL: {message}", message_type)
                text_area.insert(tk.END, f"{time_str} {message}\n")
                root.update()  # Force GUI to update
        root.after_id = root.after(100, check_queue)  # Save the id of the scheduled task
        

    check_queue()

    root.mainloop()

def handle_zone_change(prev_act, prev_zone, current_act, current_zone):
    if prev_act != current_act or prev_zone != current_zone:
        message_queue.put((current_zone, 'act_zone_change'))  # send zone changes to GUI


# Load zone to act mapping from JSON file (only for non-town zoneNames)
with open('output.json', 'r') as file:
    act_to_zones = json.load(file)

zone_to_act = {}
for act, zones in act_to_zones.items():
    for zone in zones:
        zone_to_act[zone.lower()] = act # Handle case sensitivity

# actNames with youtube Urls
act_to_url = {
    'Dry Steppes': deque(random.sample(['https://www.youtube.com/watch?v=E2BBkgqU4LI', 'https://www.youtube.com/watch?v=h_CNmc7VZek', 'https://www.youtube.com/watch?v=LeX07fdBvCg', 'https://www.youtube.com/watch?v=sXhauazts10', 'https://www.youtube.com/watch?v=tXkw_0vR-k4','https://www.youtube.com/watch?v=cqVQtXmp0jY','https://www.youtube.com/watch?v=51Fp4XxT02s'], 7)),
    'Hawezar': deque(random.sample(['https://www.youtube.com/watch?v=CSM5_muJPUo', 'https://www.youtube.com/watch?v=N2uPl_IBPV8', 'https://www.youtube.com/watch?v=WgblauBtNcc'], 3)),
    'Fractured Peaks': deque(random.sample(['https://www.youtube.com/watch?v=tn2fgpaLcSU', 'https://www.youtube.com/watch?v=u70J2h3-oyA', 'https://www.youtube.com/watch?v=nlL1WalJhIg', 'https://www.youtube.com/watch?v=-Kpxi_SEIxQ'], 4)),
    'Scosglen': deque(random.sample(['https://www.youtube.com/watch?v=F1d4fN4A39M', 'https://www.youtube.com/watch?v=o4ZWBduA9OI','https://www.youtube.com/watch?v=OPviH4BNzJ4','https://www.youtube.com/watch?v=6I0_mEo3ptY', 'https://www.youtube.com/watch?v=dOTBudfi-KY'], 5)),
    'Kehjistan': deque(random.sample(['https://www.youtube.com/watch?v=E2BBkgqU4LI', 'https://www.youtube.com/watch?v=h_CNmc7VZek', 'https://www.youtube.com/watch?v=LeX07fdBvCg', 'https://www.youtube.com/watch?v=sXhauazts10', 'https://www.youtube.com/watch?v=tXkw_0vR-k4','https://www.youtube.com/watch?v=cqVQtXmp0jY','https://www.youtube.com/watch?v=51Fp4XxT02s'], 7)),
}


#zoneNames (only towns) with youtube Urls
song_associations = {
    "Kyovashad": {"url": "https://www.youtube.com/watch?v=IMg2K9PQK9E", "duration": 180},
    "Ked Bardu": {"url": "https://www.youtube.com/watch?v=skyz-5RWfx8", "duration": 200},
    "Cerrigar": {"url": "https://www.youtube.com/watch?v=egOksitsON8", "duration": 240},
    "Zarbinzet": {"url": "https://www.youtube.com/watch?v=gXtKzCuBiGg", "duration": 240},
    "Gea Kul": {"url": "https://www.youtube.com/watch?v=skyz-5RWfx8", "duration": 240},
}

currentAct = ""
prevAct = ""
currentZone = ""
prevZone = ""
current_video_url = ""

time_str = datetime.now().strftime("[%H:%M]")

Instance = vlc.Instance()
player = Instance.media_player_new()
was_playing = False
start_time = None
duration = None
is_fading = False
fade_length = 2  # You can adjust this to control the speed of the fade

test_mode = False

non_recognized_zone = False

def fade_in():
    global is_fading
    is_fading = True
    for i in range(101):
        player.audio_set_volume(i)
        time.sleep(fade_length / 100)
    is_fading = False

def fade_out():
    global is_fading
    is_fading = True
    for i in reversed(range(101)):
        player.audio_set_volume(i)
        time.sleep(fade_length / 100)
    is_fading = False

def stop_after_interval(interval):
    """Stops the player after the specified interval (in seconds)."""
    time.sleep(interval)
    if player.is_playing():
        print('Test mode: Stopping the song after {} seconds...'.format(interval))
        fade_out()
        player.stop()

def updateCurrentZone(zone_name):
    global currentZone, non_recognized_zone
    zone_name = zone_name.lower()  # Handle case sensitivity
    all_zones = list(song_associations.keys()) + list(zone_to_act.keys())
    for known_zone in all_zones:
        # Check if the recognized zone name contains the known zone name
        if known_zone.lower() in zone_name:  # Handle case sensitivity
            if known_zone in song_associations:
                currentZone = known_zone
            else:
                currentZone = zone_to_act[known_zone]  # Update currentZone to its corresponding act
            non_recognized_zone = False
            print(f"Zone matched: {currentZone}")
            return
    print(f"No match found for recognized zone name: {zone_name}")
    non_recognized_zone = True  # Set flag when in a non-recognized zone

def updateCurrentAct(zone_name):
    global currentAct
    act = zone_to_act.get(zone_name.lower(), None)  # Handle case sensitivity
    if act and act != currentAct:
        print(f"Act changed from {currentAct} to {act}")
        previousAct = currentAct
        currentAct = act
        return True, previousAct
    return False, currentAct

def getVideoUrlForZone():
    global currentZone, current_video_url
    if currentZone in song_associations:
        video_url = song_associations[currentZone]["url"]
        current_video_url = video_url  # Update the current video URL
        print(f"Playing URL for zone {currentZone}: {current_video_url}")
        return video_url
    else:
        act = currentZone  # Use currentZone as act for non-town zones
        if act and act in act_to_url and len(act_to_url[act]) > 0:
            video_url = act_to_url[act].popleft()  # Get the next URL from the deque
            act_to_url[act].append(video_url)  # Append the URL back to the deque
            current_video_url = video_url  # Update the current video URL
            print(f"Playing URL for act {act}: {current_video_url}")
            return video_url
    return ""

def getSongDurationForZone():
    return song_associations.get(currentZone, {}).get("duration", 0)

def play_youtube_video(video_url):
    global start_time, duration

    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        playurl = info_dict.get('url', None)

    Media = Instance.media_new(playurl)
    Media.get_mrl()
    player.set_media(Media)
    player.audio_set_volume(0)
    player.play()
    time.sleep(0.1)  # Add a small delay here

    threading.Thread(target=fade_in).start()

    # Add a message to the queue to print the URL to the log in the GUI thread
    message_queue.put((f"Playing URL: {video_url}", 'song_started'))

    start_time = time.time()
    duration = getSongDurationForZone()  
    print('Started streaming the audio from YouTube.')

    if test_mode:
        threading.Thread(target=stop_after_interval, args=(30,)).start()

def preprocess_image(image):
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, threshold = cv2.threshold(grayscale, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return threshold

def capture_screen_region():
    global prevZone
    screen_width, screen_height = pyautogui.size()
    region_width = int(screen_width * 0.22) 
    region_height = int(screen_height * 0.04)
    region_left = screen_width - region_width  
    region_top = 0  

    screenshot = pyautogui.screenshot(region=(region_left, region_top, region_width, region_height))
    image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    preprocessed_image = preprocess_image(image)
    raw_text = pytesseract.image_to_string(preprocessed_image)
    print('Raw Text:', raw_text)
    formatted_text = raw_text.split("(")[0].strip()  # split on "(" character
    updateCurrentZone(formatted_text)
    act_changed, prevAct = updateCurrentAct(formatted_text)

    handle_zone_change(prevAct, prevZone, currentAct, currentZone)
    
    if act_changed and not is_fading:
        print('Act has changed to a recognized act.')
        if player.is_playing():
            print('Fading out the current audio...')
            fade_out()
            player.stop()
            print('Starting to stream the audio for the new act...')
            video_url = get_next_song_in_playlist()
            if video_url:
                play_youtube_video(video_url)
                time.sleep(0)
                print('Fading in the audio for the new act...')
        prevZone = currentZone

def get_next_song_in_playlist():
    if currentZone not in song_associations:  # If it's not a town
        act = currentZone  # Use currentZone as act for non-town zones
        if act and act_to_url.get(act, []):
            # Pop song from the front of the queue
            video_url = act_to_url[act].popleft()
            # Put it at the end of the queue
            act_to_url[act].append(video_url)

            print(f"Playing next song for act {act}: {video_url}")
            return video_url
    return None

message_queue = queue.Queue()
threading.Thread(target=run_gui, args=(message_queue,)).start()

while True:
    print('Capturing the zone name from the screen...')
    capture_screen_region()
    video_url = getVideoUrlForZone()

    if video_url and (currentAct != prevAct):
        print('Act has changed.')
        if player.is_playing():
            fade_out()
            player.stop()

        print('Starting to stream the audio for the new act...')
        play_youtube_video(video_url)
        current_video_url = video_url
        was_playing = True
        prevAct = currentAct

    elif not player.is_playing():
        print(f'Song has ended. Checking player zone... Current Zone: {currentZone}, Current Act: {currentAct}, Previous Act: {prevAct}')
        if currentZone and currentAct == prevAct and currentZone in song_associations and not non_recognized_zone:
            print('Player is in the town. Playing town song...')
            play_youtube_video(video_url)
        else:
            print('Player has left the town or is in a non-recognized zone. Playing next song in the act...')
            video_url = get_next_song_in_playlist()  # Get the next song in the act's playlist
            if video_url:
                play_youtube_video(video_url)
    
    prevZone = currentZone

    time.sleep(3)
    print('Waiting for 1 seconds before capturing the screen again...')