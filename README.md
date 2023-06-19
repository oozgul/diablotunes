# DiabloTunes

**DISCLAIMER: APPLICATION DOES NOT READ ANY D4 FILES.**

a zone-aware python app that plays diablo 2 music while running diablo 4

<img src="https://i.imgur.com/BVLHPBi.png" alt="GUI screenshot" width="35%" />

**Instructions**
- Download the latest .zip file - https://github.com/oozgul/diablotunes/releases/download/executable/diablotunes_v05.zip
- Launch main.exe 
- Launch the game
- As soon as the zone names are visible on your screen the playback should start

Note: If you don't want to use the executable you need to download all dependencies and launch main.py on root folder

**Features**
- Application automatically recognizes your zone name in D4 and plays a track from d2 automatically.
- Application chooses a song based on your current zone, for example while in Kyovashad the application will play Harrogath music (Act 5 town in D2) as it's the geographical twin in D4. Same as applied for other acts as well.
- GUI window to show the current act/zone and current state of the player.

**How does it work?**
- Uses pyautogui to capture zone name while in-game (it only captures the portion where the zonename located in the screen)
- Uses pytessaract to convert zone name image to text
- Streams the d2 song audio via youtube audio stream using vlc library

**Known Issues/FAQ**
- If you start the application while you are in a dungeon the playback will only start when it recognizes an open world zone name or town name.
- Occassionally image to text logic would fail if there is too much background noise where your zone name is located. Try moving your character and eventually it will recognize the correct zone name.
- If it does not work still, create an issue in this repository.
