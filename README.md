# GW2Bard - Guild Wars 2 Music Player

A desktop application to play custom music in Guild Wars 2 using AutoHotkey scripts.

## Features

- Play/Pause/Stop controls for GW2 music scripts
- Support for all GW2 instruments: Harp, Lute, Flute, Horn, Bell, Bass, Drum, Minstrel
- Start delay countdown before playback
- First-run wizard for initial setup
- English/Spanish language support
- Auto-detection of AutoHotkey installation

## Requirements

### Python Version

- **Python 3.13+**
- CustomTkInter library

### Install Dependencies

```bash
pip install customtkinter
```

### Required for Scripts

- [AutoHotkey](https://www.autohotkey.com/) v2.0+ - Required to run `.ahk` music scripts
- **Recommended:** AutoHotkey v1.1 (for maximum compatibility with existing scripts)

## Usage

### Running from Source

```bash
python gw2bard.py
```

### Running Compiled (.exe)

Download GW2Bard.exe from Releases and run directly - no Python required.

## Configuration

Settings are saved in `settings.txt`:
- Songs folder location
- Start delay (seconds)
- Language preference

## First Run

On first launch, a wizard will guide you through:
1. Language selection (English/Spanish)
2. Songs folder location

## License

MIT License