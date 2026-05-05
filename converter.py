# GW2Bard - Song Converter
# Converts JSON songs to AHK scripts

import json
import os
import shutil

SONGS_FOLDER = os.path.join(os.path.dirname(__file__), "songs")
KEYBINDINGS = {
    "note1": "1", "note2": "2", "note3": "3", "note4": "4",
    "note5": "5", "note6": "6", "note7": "7", "note8": "8",
    "octaveDown": "9", "octaveUp": "0"
}

def convert_json_to_ahk(json_path, output_path=None):
    """Convert JSON song to AHK script"""
    with open(json_path, 'r', encoding='utf-8') as f:
        song = json.load(f)
    
    title = song.get('title', 'Untitled')
    tempo = song.get('tempo', 120)
    notes = song.get('notes', [])
    
    beat_delay = 60000 // tempo  # ms per beat
    
    ahk_lines = [
        f"; GW2Bard - {title}",
        f"; Converted from JSON",
        f"#SingleInstance Force",
        f"#Requires AutoHotkey v2.0",
        "",
        f"#If WinActive(\"ahk_exe Gw2-64.exe\")",
        ""
    ]
    
    current_octave = 2  # Start at middle octave
    
    for note_data in notes:
        note_num = note_data.get('note', 1)
        target_octave = note_data.get('octave', 2)
        
        # Handle octave change
        if target_octave != current_octave:
            if target_octave > current_octave:
                for _ in range(target_octave - current_octave):
                    ahk_lines.append(f"Send, {KEYBINDINGS['octaveUp']}")
                    ahk_lines.append(f"Sleep, {beat_delay}")
            else:
                for _ in range(current_octave - target_octave):
                    ahk_lines.append(f"Send, {KEYBINDINGS['octaveDown']}")
                    ahk_lines.append(f"Sleep, {beat_delay}")
            current_octave = target_octave
        
        # Play note
        note_key = KEYBINDINGS.get(f"note{note_num}", str(note_num))
        ahk_lines.append(f"Send, {note_key}")
        ahk_lines.append(f"Sleep, {beat_delay}")
    
    ahk_lines.extend(["", "#If", "", "Esc::ExitApp"])
    
    # Write AHK file
    if output_path is None:
        output_path = json_path.replace('.json', '.ahk')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(ahk_lines))
    
    return output_path

def convert_all_songs():
    """Convert all JSON files to AHK in all instrument folders"""
    converted = []
    
    for instrument in os.listdir(SONGS_FOLDER):
        instrument_folder = os.path.join(SONGS_FOLDER, instrument)
        if not os.path.isdir(instrument_folder):
            continue
        
        for file in os.listdir(instrument_folder):
            if file.endswith('.json'):
                json_path = os.path.join(instrument_folder, file)
                try:
                    output = convert_json_to_ahk(json_path)
                    converted.append(output)
                    print(f"Converted: {file}")
                except Exception as e:
                    print(f"Error converting {file}: {e}")
    
    print(f"\nConverted {len(converted)} songs")
    return converted

if __name__ == "__main__":
    convert_all_songs()