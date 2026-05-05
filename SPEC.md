# GW2Bard - Guild Wars 2 Music Player

## Project Overview

Desktop application for playing .ahk and .exe music scripts in Guild Wars 2.

## Tech Stack

- **Language**: Python 3
- **GUI**: customtkinter
- **Global Hotkeys**: pynput
- **Target**: Windows, GW2 game window

## Features

| Feature | Description |
|---------|-------------|
| Song Browser | Grid showing .ahk/.exe files from folder |
| Categories | "Todos", "Sin clasificar", and by instrument (harp/lute/flute/horn/bell/bass/drum/minstrel) |
| Play/Pause/Stop | Execute scripts as processes |
| Auto-folder Creation | Creates instrument subfolders when applying new folder |
| Delay | Configurable start delay before playing |
| Global Hotkey | Custom hotkey to trigger play (e.g., F9) |
| Settings | Persisted to settings.txt |

## Project Structure

```
GW2Bard/
├── gw2bard.py       ← Main application
├── converter.py      ← JSON to AHK converter
├── settings.txt      ← Persisted settings
├── songs/            ← Default songs folder
│   └── harp/
└── SPEC.md
```

## Configuration

Settings are stored in `settings.txt`:
- `songs_folder`: Path to songs directory
- `play_hotkey`: Global hotkey for play
- `start_delay`: Delay in seconds before playing

## Usage

1. Run: `python gw2bard.py`
2. In Options tab, set your songs folder
3. Apply - creates instrument subfolders automatically
4. Select song from list
5. Click Play or use hotkey

## Custom Songs Folder

Users can set custom folder containing:
- Root level: .ahk/.exe files (shown as "Sin clasificar")
- Instrument subfolders: harp/, lute/, flute/, etc.

## Known Requirements

- Python 3.x
- customtkinter (`pip install customtkinter`)
- pynput for global hotkeys (`pip install pynput`)
- AutoHotkey installed for .ahk files