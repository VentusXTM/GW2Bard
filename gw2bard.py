# GW2Bard - Guild Wars 2 Music Player
import os
import subprocess
import time
import threading
from customtkinter import *
from tkinter import Listbox

# Settings location - use APPDATA for portability
SETTINGS_FOLDER = os.path.join(os.environ.get('APPDATA', os.path.dirname(__file__)), "GW2Bard")
SETTINGS_FILE = os.path.join(SETTINGS_FOLDER, "settings.txt")

DEFAULT_SONGS_FOLDER = os.path.join(os.path.dirname(__file__), "songs")
INSTRUMENTS = ["harp", "lute", "flute", "horn", "bell", "bass", "drum", "minstrel"]

# Translations
TRANSLATIONS = {
    "en": {
        "instrument": "Instrument:",
        "all": "All",
        "unclassified": "Unclassified",
        "now_playing": "Now Playing: -",
        "player": "Player",
        "options": "Options",
        "play": "Play",
        "pause": "Pause",
        "stop": "Stop",
        "refresh": "Refresh",
        "ready": "Ready",
        "finished": "Finished",
        "settings": "Settings",
        "start_delay": "Start delay (sec):",
        "songs_folder": "Songs folder:",
        "browse": "Browse",
        "apply": "Apply",
        "autohotkey": "AutoHotkey:",
        "save_settings": "Save Settings",
        "language": "Language:",
        "select_song": "Select a song first!",
        "starting_in": "Starting in {}s...",
        "autohotkey_notfound": "AutoHotkey not found!",
        "playing": "Playing...",
        "paused": "Paused",
        "stopped": "Stopped",
        "nothing_playing": "Nothing playing",
        "folder_applied": "Folder applied!",
        "settings_saved": "Settings saved!",
        "songs": "songs",
        "welcome": "Welcome to GW2Bard!",
        "welcome_desc": "Select your language and songs folder to get started.",
        "select_folder": "Please select your songs folder",
        "autohotkey_check": "AutoHotkey Required",
        "autohotkey_found": "Found: {}",
        "autohotkey_not_found": "AutoHotkey not found on this system",
        "autohotkey_path_label": "AutoHotkey path:",
        "download_ahk": "Download AutoHotkey",
        "browse_ahk": "Browse...",
    },
    "es": {
        "instrument": "Instrumento:",
        "all": "Todos",
        "unclassified": "Sin clasificar",
        "now_playing": "Reproduciendo: -",
        "player": "Reproductor",
        "options": "Opciones",
        "play": "Reproducir",
        "pause": "Pausar",
        "stop": "Detener",
        "refresh": "Actualizar",
        "ready": "Listo",
        "finished": "Finalizado",
        "settings": "Configuración",
        "start_delay": "Retraso inicial (seg):",
        "songs_folder": "Carpeta de canciones:",
        "browse": "Examinar",
        "apply": "Aplicar",
        "autohotkey": "AutoHotkey:",
        "save_settings": "Guardar",
        "language": "Idioma:",
        "select_song": "¡Selecciona una canción primero!",
        "starting_in": "Comenzando en {}s...",
        "autohotkey_notfound": "¡AutoHotkey no encontrado!",
        "playing": "Reproduciendo...",
        "paused": "Pausado",
        "stopped": "Detenido",
        "nothing_playing": "Nada reproduciendo",
        "folder_applied": "¡Carpeta aplicada!",
        "settings_saved": "¡Configuración guardada!",
        "songs": "canciones",
        "welcome": "¡Bienvenido a GW2Bard!",
        "welcome_desc": "Selecciona tu idioma y carpeta de canciones para comenzar.",
        "select_folder": "Por favor ubica tu carpeta de canciones",
        "autohotkey_check": "AutoHotkey Requerido",
        "autohotkey_found": "Encontrado: {}",
        "autohotkey_not_found": "AutoHotkey no encontrado en este sistema",
        "autohotkey_path_label": "Ruta de AutoHotkey:",
        "download_ahk": "Descargar AutoHotkey",
        "browse_ahk": "Examinar...",
    }
}

set_appearance_mode("dark")
set_default_color_theme("blue")

class GW2Bard(CTk):
    def __init__(self):
        super().__init__()
        self.title("GW2Bard")
        self.geometry("750x480")
        self.resizable(False, False)
        self.minsize(750, 480)
        
        self.current_process = None
        self.is_playing = False
        self.songs_folder = DEFAULT_SONGS_FOLDER
        self.start_delay = 0
        self.language = "en"
        self.first_run = True
        self.songs_data = []
        self.selected_path = ""
        self.ahk_path = ""
        self.ahk_path_v2 = ""
        self.ahk_path_v1 = ""
        
        self.load_settings()
        
        # First run wizard
        if self.first_run:
            self.show_wizard()
        else:
            self.create_widgets()
            self.check_and_create_folders()
            self.load_songs()
    
    def show_wizard(self):
        self.wizard_frame = CTkFrame(self, width=730, height=450)
        self.wizard_frame.place(x=10, y=10)
        
        CTkLabel(self.wizard_frame, text=self.t("welcome"), font=("Arial", 18, "bold")).place(x=365, y=20, anchor="center")
        CTkLabel(self.wizard_frame, text=self.t("welcome_desc"), font=("Arial", 11), text_color="gray").place(x=365, y=55, anchor="center")
        
        # Language
        CTkLabel(self.wizard_frame, text=self.t("language")).place(x=50, y=90)
        self.wizard_lang_var = StringVar(value="English")
        self.wizard_lang_dropdown = CTkOptionMenu(self.wizard_frame, values=["English", "Spanish"], variable=self.wizard_lang_var, command=self.on_wizard_lang_change, width=120)
        self.wizard_lang_dropdown.place(x=50, y=115)
        
        # Songs folder
        CTkLabel(self.wizard_frame, text=self.t("songs_folder")).place(x=50, y=155)
        self.wizard_folder_entry = CTkEntry(self.wizard_frame, width=480)
        self.wizard_folder_entry.insert(0, self.t("select_folder"))
        self.wizard_folder_entry.place(x=50, y=180)
        CTkButton(self.wizard_frame, text=self.t("browse"), command=self.wizard_browse_folder, width=80).place(x=540, y=178)
        
        # AutoHotkey v1.1 section (default)
        CTkLabel(self.wizard_frame, text="AutoHotkey v1.1 (default):", font=("Arial", 12, "bold")).place(x=50, y=225)
        
        all_ahk = self.find_all_ahk()
        v1_path = ""
        v2_path = ""
        for path, desc in all_ahk:
            if "v1" in desc and not v1_path:
                v1_path = path
            elif "v2" in desc and not v2_path:
                v2_path = path
        
        self.wizard_ahk1_entry = CTkEntry(self.wizard_frame, width=400)
        self.wizard_ahk1_entry.insert(0, v1_path)
        self.wizard_ahk1_entry.place(x=50, y=250)
        CTkButton(self.wizard_frame, text=self.t("browse_ahk"), command=self.wizard_browse_ahk1, width=80).place(x=460, y=248)
        
        # AutoHotkey v2 section (fallback)
        CTkLabel(self.wizard_frame, text="AutoHotkey v2 (fallback):", font=("Arial", 12, "bold")).place(x=50, y=285)
        
        self.wizard_ahk2_entry = CTkEntry(self.wizard_frame, width=400)
        self.wizard_ahk2_entry.insert(0, v2_path)
        self.wizard_ahk2_entry.place(x=50, y=310)
        CTkButton(self.wizard_frame, text=self.t("browse_ahk"), command=self.wizard_browse_ahk2, width=80).place(x=460, y=308)
        
        # Download buttons
        CTkButton(self.wizard_frame, text=self.t("download_ahk"), command=self.download_ahk, width=140).place(x=550, y=248)
        CTkButton(self.wizard_frame, text=self.t("download_ahk"), command=self.download_ahk_v1, width=140).place(x=550, y=308)
        
        CTkButton(self.wizard_frame, text=self.t("save_settings"), command=self.finish_wizard, width=150, height=35, font=("Arial", 12)).place(x=290, y=400)

    def on_wizard_lang_change(self, choice):
        self.language = "en" if choice == "English" else "es"
        # Store current values before rebuilding
        current_folder = self.wizard_folder_entry.get() if hasattr(self, 'wizard_folder_entry') else ""
        current_ahk2 = self.wizard_ahk2_entry.get() if hasattr(self, 'wizard_ahk2_entry') else ""
        current_ahk1 = self.wizard_ahk1_entry.get() if hasattr(self, 'wizard_ahk1_entry') else ""
        
        # Rebuild wizard UI
        for widget in self.wizard_frame.winfo_children():
            widget.destroy()
        
        CTkLabel(self.wizard_frame, text=self.t("welcome"), font=("Arial", 18, "bold")).place(x=365, y=20, anchor="center")
        CTkLabel(self.wizard_frame, text=self.t("welcome_desc"), font=("Arial", 11), text_color="gray").place(x=365, y=55, anchor="center")
        
        # Language
        CTkLabel(self.wizard_frame, text=self.t("language")).place(x=50, y=90)
        self.wizard_lang_var = StringVar(value=choice)
        self.wizard_lang_dropdown = CTkOptionMenu(self.wizard_frame, values=["English", "Spanish"], variable=self.wizard_lang_var, command=self.on_wizard_lang_change, width=120)
        self.wizard_lang_dropdown.place(x=50, y=115)
        
        # Songs folder
        CTkLabel(self.wizard_frame, text=self.t("songs_folder")).place(x=50, y=155)
        self.wizard_folder_entry = CTkEntry(self.wizard_frame, width=480)
        self.wizard_folder_entry.insert(0, current_folder if current_folder else self.t("select_folder"))
        self.wizard_folder_entry.place(x=50, y=180)
        CTkButton(self.wizard_frame, text=self.t("browse"), command=self.wizard_browse_folder, width=80).place(x=540, y=178)
        
        # AutoHotkey v1.1 section (default)
        CTkLabel(self.wizard_frame, text="AutoHotkey v1.1 (default):", font=("Arial", 12, "bold")).place(x=50, y=225)
        
        all_ahk = self.find_all_ahk()
        v1_path = current_ahk1
        v2_path = current_ahk2
        
        if not v1_path:
            for path, desc in all_ahk:
                if "v1" in desc and not v1_path:
                    v1_path = path
        
        self.wizard_ahk1_entry = CTkEntry(self.wizard_frame, width=400)
        self.wizard_ahk1_entry.insert(0, v1_path)
        self.wizard_ahk1_entry.place(x=50, y=250)
        CTkButton(self.wizard_frame, text=self.t("browse_ahk"), command=self.wizard_browse_ahk1, width=80).place(x=460, y=248)
        
        # AutoHotkey v2 section (fallback)
        CTkLabel(self.wizard_frame, text="AutoHotkey v2 (fallback):", font=("Arial", 12, "bold")).place(x=50, y=285)
        
        if not v2_path:
            for path, desc in all_ahk:
                if "v2" in desc and not v2_path:
                    v2_path = path
        
        self.wizard_ahk2_entry = CTkEntry(self.wizard_frame, width=400)
        self.wizard_ahk2_entry.insert(0, v2_path)
        self.wizard_ahk2_entry.place(x=50, y=310)
        CTkButton(self.wizard_frame, text=self.t("browse_ahk"), command=self.wizard_browse_ahk2, width=80).place(x=460, y=308)
        
        # Download buttons
        CTkButton(self.wizard_frame, text=self.t("download_ahk"), command=self.download_ahk, width=140).place(x=550, y=248)
        CTkButton(self.wizard_frame, text=self.t("download_ahk"), command=self.download_ahk_v1, width=140).place(x=550, y=308)
        
        CTkButton(self.wizard_frame, text=self.t("save_settings"), command=self.finish_wizard, width=150, height=35, font=("Arial", 12)).place(x=290, y=400)
    
    def wizard_browse_folder(self):
        from tkinter import filedialog
        folder = filedialog.askdirectory(initialdir=self.songs_folder)
        if folder:
            self.wizard_folder_entry.delete(0, "end")
            self.wizard_folder_entry.insert(0, folder)
    
    def wizard_browse_ahk(self):
        from tkinter import filedialog
        file = filedialog.askopenfilename(
            title="Select AutoHotkey executable",
            filetypes=[("Executable", "*.exe")],
            initialdir=r"C:\Program Files"
        )
        if file:
            self.wizard_ahk_entry.delete(0, "end")
            self.wizard_ahk_entry.insert(0, file)
    
    def wizard_browse_ahk2(self):
        from tkinter import filedialog
        file = filedialog.askopenfilename(
            title="Select AutoHotkey v2 executable",
            filetypes=[("Executable", "*.exe")],
            initialdir=r"C:\Program Files"
        )
        if file:
            self.wizard_ahk2_entry.delete(0, "end")
            self.wizard_ahk2_entry.insert(0, file)
    
    def wizard_browse_ahk1(self):
        from tkinter import filedialog
        file = filedialog.askopenfilename(
            title="Select AutoHotkey v1.1 executable",
            filetypes=[("Executable", "*.exe")],
            initialdir=r"C:\Program Files"
        )
        if file:
            self.wizard_ahk1_entry.delete(0, "end")
            self.wizard_ahk1_entry.insert(0, file)
    
    def download_ahk(self):
        import webbrowser
        webbrowser.open("https://www.autohotkey.com/download/")
    
    def download_ahk_v1(self):
        import webbrowser
        webbrowser.open("https://www.autohotkey.com/download/ahk-v1-setup.exe")
    
    def finish_wizard(self):
        self.songs_folder = self.wizard_folder_entry.get()
        # Save both v1 and v2 paths - v1 is default, v2 is fallback
        self.ahk_path_v1 = self.wizard_ahk1_entry.get()
        self.ahk_path_v2 = self.wizard_ahk2_entry.get()
        self.ahk_path = self.ahk_path_v1 or self.ahk_path_v2  # Default to v1
        self.first_run = False
        self.save_settings()
        
        self.wizard_frame.place_forget()
        
        self.create_widgets()
        self.check_and_create_folders()
        self.load_songs()
    
    def t(self, key):
        return TRANSLATIONS[self.language].get(key, key)

    def create_widgets(self):
        self.tabview = CTkTabview(self, width=730, height=460)
        self.tabview.place(x=10, y=10)
        
        # Player Tab
        self.tab_player = self.tabview.add(self.t("player"))
        
        self.instrument_label = CTkLabel(self.tab_player, text=self.t("instrument"))
        self.instrument_label.place(x=10, y=10)
        options = [self.t("all"), self.t("unclassified")] + INSTRUMENTS
        self.instrument_var = StringVar(value=self.t("all"))
        self.instrument_dropdown = CTkOptionMenu(self.tab_player, values=options, variable=self.instrument_var, command=self.on_instrument_change, width=150)
        self.instrument_dropdown.place(x=80, y=10)
        
        # Listbox con frame
        listbox_container = CTkFrame(self.tab_player, width=450, height=175)
        listbox_container.place(x=10, y=40)
        
        self.songs_listbox = Listbox(listbox_container, bg="#1a1a1a", fg="white", selectbackground="#3b8ed3", width=55, height=11, borderwidth=0, highlightthickness=0)
        self.songs_listbox.pack(side="left", fill="both", expand=True)
        self.songs_listbox.bind("<<ListboxSelect>>", self.on_song_select)
        self.songs_listbox.bind("<Double-Button-1>", lambda e: self.play())
        
        scrollbar = CTkScrollbar(listbox_container, command=self.songs_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        
        self.now_playing = CTkLabel(self.tab_player, text=self.t("now_playing"), font=("Arial", 12))
        self.now_playing.place(x=10, y=240)
        
        self.play_btn = CTkButton(self.tab_player, text=self.t("play"), command=self.play, width=70)
        self.play_btn.place(x=10, y=270)
        self.pause_btn = CTkButton(self.tab_player, text=self.t("pause"), command=self.pause, width=70)
        self.pause_btn.place(x=90, y=270)
        self.stop_btn = CTkButton(self.tab_player, text=self.t("stop"), command=self.stop, width=70)
        self.stop_btn.place(x=170, y=270)
        
        self.status = CTkLabel(self.tab_player, text=self.t("ready"), text_color="gray", font=("Arial", 10))
        self.status.place(x=10, y=310)
        
        self.refresh_btn = CTkButton(self.tab_player, text=self.t("refresh"), command=self.load_songs, width=80)
        self.refresh_btn.place(x=480, y=270)
        
        # Options Tab
        self.tab_options = self.tabview.add(self.t("options"))
        
        self.settings_label = CTkLabel(self.tab_options, text=self.t("settings"), font=("Arial", 14, "bold"))
        self.settings_label.place(x=200, y=10)
        
        # Language dropdown
        self.lang_label = CTkLabel(self.tab_options, text=self.t("language"))
        self.lang_label.place(x=10, y=50)
        self.lang_var = StringVar(value=self.language)
        self.lang_dropdown = CTkOptionMenu(self.tab_options, values=["English", "Spanish"], variable=self.lang_var, command=self.on_language_change, width=100)
        self.lang_dropdown.place(x=80, y=48)
        
        self.delay_label = CTkLabel(self.tab_options, text=self.t("start_delay"))
        self.delay_label.place(x=10, y=90)
        self.delay_entry = CTkEntry(self.tab_options, width=60)
        self.delay_entry.insert(0, str(self.start_delay))
        self.delay_entry.place(x=130, y=90)
        CTkButton(self.tab_options, text=self.t("apply"), command=self.apply_delay, width=50).place(x=200, y=88)
        
        self.folder_label = CTkLabel(self.tab_options, text=self.t("songs_folder"))
        self.folder_label.place(x=10, y=130)
        self.folder_entry = CTkEntry(self.tab_options, width=400)
        self.folder_entry.insert(0, self.songs_folder)
        self.folder_entry.place(x=10, y=155)
        
        CTkButton(self.tab_options, text=self.t("browse"), command=self.browse_folder, width=70).place(x=420, y=153)
        CTkButton(self.tab_options, text=self.t("apply"), command=self.apply_folder, width=70).place(x=500, y=153)
        
        # AutoHotkey v1.1 (default)
        self.ahk_label_v1 = CTkLabel(self.tab_options, text="AutoHotkey v1.1 (default):")
        self.ahk_label_v1.place(x=10, y=195)
        self.ahk_path_entry_v1 = CTkEntry(self.tab_options, width=350)
        default_v1 = self.ahk_path_v1 if (hasattr(self, 'ahk_path_v1') and self.ahk_path_v1) else ""
        if not default_v1:
            for path, desc in self.find_all_ahk():
                if "v1" in desc and not default_v1:
                    default_v1 = path
        self.ahk_path_entry_v1.insert(0, default_v1)
        self.ahk_path_entry_v1.place(x=10, y=220)
        
        # AutoHotkey v2 (fallback)
        self.ahk_label_v2 = CTkLabel(self.tab_options, text="AutoHotkey v2 (fallback):")
        self.ahk_label_v2.place(x=10, y=250)
        self.ahk_path_entry_v2 = CTkEntry(self.tab_options, width=350)
        default_v2 = self.ahk_path_v2 if (hasattr(self, 'ahk_path_v2') and self.ahk_path_v2) else ""
        if not default_v2:
            for path, desc in self.find_all_ahk():
                if "v2" in desc and not default_v2:
                    default_v2 = path
        self.ahk_path_entry_v2.insert(0, default_v2)
        self.ahk_path_entry_v2.place(x=10, y=275)
        
        self.save_btn = CTkButton(self.tab_options, text=self.t("save_settings"), command=self.save_settings, width=120, height=30)
        self.save_btn.place(x=230, y=310)

    def on_language_change(self, choice):
        self.language = "en" if choice == "English" else "es"
        
        # Update instrument dropdown
        self.instrument_dropdown.configure(values=[self.t("all"), self.t("unclassified")] + INSTRUMENTS)
        current = self.instrument_var.get()
        if current in ["All", "Todos"]:
            self.instrument_var.set(self.t("all"))
        elif current in ["Unclassified", "Sin clasificar"]:
            self.instrument_var.set(self.t("unclassified"))
        
        # Update tab names
        self.tabview.set(self.t("player"))
        self.tabview.set(self.t("options"))
        
        # Update player labels
        self.instrument_label.configure(text=self.t("instrument"))
        self.now_playing.configure(text=self.t("now_playing"))
        self.status.configure(text=self.t("ready"))
        
        # Update player buttons
        self.play_btn.configure(text=self.t("play"))
        self.pause_btn.configure(text=self.t("pause"))
        self.stop_btn.configure(text=self.t("stop"))
        self.refresh_btn.configure(text=self.t("refresh"))
        
        # Update options labels and buttons
        self.settings_label.configure(text=self.t("settings"))
        self.lang_label.configure(text=self.t("language"))
        self.delay_label.configure(text=self.t("start_delay"))
        self.folder_label.configure(text=self.t("songs_folder"))
        self.ahk_label.configure(text=self.t("autohotkey"))
        self.save_btn.configure(text=self.t("save_settings"))
        
        # Save language and reload songs
        self.save_settings()
        self.load_songs()

    def find_ahk_path(self):
        # Search for AutoHotkey v1 first (default), then v2 (fallback)
        # v1.1 is more compatible, v2 has compatibility issues
        search_paths = [
            # AutoHotkey v1.1 (default - more compatible)
            r"C:\Program Files\AutoHotkey\AutoHotkeyU64.exe",
            r"C:\Program Files\AutoHotkey\AutoHotkeyU32.exe",
            r"C:\Program Files\AutoHotkey\AutoHotkeyA32.exe",
            r"C:\Program Files (x86)\AutoHotkey\AutoHotkeyU64.exe",
            r"C:\Program Files (x86)\AutoHotkey\AutoHotkeyU32.exe",
            r"C:\Program Files (x86)\AutoHotkey\AutoHotkeyA32.exe",
            # AutoHotkey v2 (fallback) - including v2 subfolder
            r"C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe",
            r"C:\Program Files\AutoHotkey\v2\AutoHotkey32.exe",
            r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
            r"C:\Program Files\AutoHotkey\AutoHotkey64.exe",
            r"C:\Program Files (x86)\AutoHotkey\AutoHotkey64.exe",
            r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe",
        ]
        
        for path in search_paths:
            if os.path.exists(path):
                return path
        
        # Check if user has set a custom path in settings
        if hasattr(self, 'ahk_path') and self.ahk_path and os.path.exists(self.ahk_path):
            return self.ahk_path
        
        return ""
    
    def find_all_ahk(self):
        """Find all AutoHotkey executables (v1 and v2) - v1 listed first"""
        # v1.1 first (so it becomes default)
        v1_paths = [
            (r"C:\Program Files\AutoHotkey\AutoHotkeyU64.exe", "v1.1"),
            (r"C:\Program Files\AutoHotkey\AutoHotkeyU32.exe", "v1.1"),
            (r"C:\Program Files\AutoHotkey\AutoHotkeyA32.exe", "v1.1"),
            (r"C:\Program Files (x86)\AutoHotkey\AutoHotkeyU64.exe", "v1.1"),
            (r"C:\Program Files (x86)\AutoHotkey\AutoHotkeyU32.exe", "v1.1"),
            (r"C:\Program Files (x86)\AutoHotkey\AutoHotkeyA32.exe", "v1.1"),
        ]
        
        # v2 second (fallback) - including v2\ subfolder
        v2_paths = [
            # v2 subfolder
            (r"C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe", "v2"),
            (r"C:\Program Files\AutoHotkey\v2\AutoHotkey32.exe", "v2"),
            # v2 root (legacy install)
            (r"C:\Program Files\AutoHotkey\AutoHotkey.exe", "v2"),
            (r"C:\Program Files\AutoHotkey\AutoHotkey64.exe", "v2"),
            (r"C:\Program Files (x86)\AutoHotkey\AutoHotkey64.exe", "v2"),
            (r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe", "v2"),
        ]
        
        found = []
        for path, desc in v1_paths:
            if os.path.exists(path):
                found.append((path, desc))
        
        for path, desc in v2_paths:
            if os.path.exists(path):
                found.append((path, desc))
        
        return found

    def load_settings(self):
        # Ensure settings folder exists
        if not os.path.exists(SETTINGS_FOLDER):
            os.makedirs(SETTINGS_FOLDER)
        
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        if key == "songs_folder":
                            self.songs_folder = value
                        elif key == "start_delay":
                            self.start_delay = int(value)
                        elif key == "language":
                            self.language = value
                        elif key == "first_run":
                            self.first_run = value.lower() == "true"
                        elif key == "ahk_path":
                            self.ahk_path = value
                        elif key == "ahk_path_v2":
                            self.ahk_path_v2 = value
                        elif key == "ahk_path_v1":
                            self.ahk_path_v1 = value

    def save_settings(self):
        # Ensure settings folder exists
        if not os.path.exists(SETTINGS_FOLDER):
            os.makedirs(SETTINGS_FOLDER)
        
        # Update ahk_path from UI if entry exists
        if hasattr(self, 'ahk_path_entry'):
            self.ahk_path = self.ahk_path_entry.get()
        if hasattr(self, 'ahk_path_entry_v2'):
            self.ahk_path_v2 = self.ahk_path_entry_v2.get()
        if hasattr(self, 'ahk_path_entry_v1'):
            self.ahk_path_v1 = self.ahk_path_entry_v1.get()
        
        with open(SETTINGS_FILE, 'w') as f:
            f.write(f"songs_folder={self.songs_folder}\n")
            f.write(f"start_delay={self.start_delay}\n")
            f.write(f"language={self.language}\n")
            f.write(f"first_run={str(self.first_run).lower()}\n")
            if hasattr(self, 'ahk_path') and self.ahk_path:
                f.write(f"ahk_path={self.ahk_path}\n")
            if hasattr(self, 'ahk_path_v2') and self.ahk_path_v2:
                f.write(f"ahk_path_v2={self.ahk_path_v2}\n")
            if hasattr(self, 'ahk_path_v1') and self.ahk_path_v1:
                f.write(f"ahk_path_v1={self.ahk_path_v1}\n")
        if hasattr(self, 'status'):
            self.status.configure(text=self.t("settings_saved"))

    def check_and_create_folders(self):
        for inst in INSTRUMENTS:
            folder = os.path.join(self.songs_folder, inst)
            if not os.path.exists(folder):
                os.makedirs(folder)

    def load_songs(self):
        inst = self.instrument_var.get()
        self.songs_listbox.delete(0, "end")
        self.songs_data = []
        
        unclassified_label = self.t("unclassified")
        
        if inst == self.t("all"):
            for instrument in INSTRUMENTS:
                folder = os.path.join(self.songs_folder, instrument)
                if os.path.exists(folder):
                    for file in os.listdir(folder):
                        if file.endswith((".ahk", ".exe")):
                            full = os.path.join(folder, file)
                            self.songs_data.append((file, full, instrument))
            for file in os.listdir(self.songs_folder):
                if file.endswith((".ahk", ".exe")):
                    full = os.path.join(self.songs_folder, file)
                    if os.path.isfile(full):
                        self.songs_data.append((file, full, unclassified_label))
        elif inst == unclassified_label:
            for file in os.listdir(self.songs_folder):
                if file.endswith((".ahk", ".exe")):
                    full = os.path.join(self.songs_folder, file)
                    if os.path.isfile(full):
                        self.songs_data.append((file, full, "root"))
        else:
            folder = os.path.join(self.songs_folder, inst)
            if os.path.exists(folder):
                for file in os.listdir(folder):
                    if file.endswith((".ahk", ".exe")):
                        full = os.path.join(folder, file)
                        self.songs_data.append((file, full, inst))
        
        for file, path, cat in self.songs_data:
            display = file if cat in ["root", unclassified_label] else f"[{cat}] {file}"
            self.songs_listbox.insert("end", display)
        
        self.status.configure(text=f"{len(self.songs_data)} {self.t('songs')}")

    def on_instrument_change(self, choice):
        self.load_songs()

    def on_song_select(self, event):
        selection = self.songs_listbox.curselection()
        if selection:
            idx = selection[0]
            self.selected_path = self.songs_data[idx][1]
            self.now_playing.configure(text=f"Now: {self.songs_data[idx][0]}")

    def play(self):
        if not self.selected_path:
            self.status.configure(text=self.t("select_song"), text_color="orange")
            return
        
        try:
            delay = int(self.delay_entry.get())
        except:
            delay = 0
        
        # Countdown
        for i in range(delay, 0, -1):
            self.status.configure(text=self.t("starting_in").format(i))
            self.update()
            time.sleep(1)
        
        ext = os.path.splitext(self.selected_path)[1]
        
        if ext == ".exe":
            self.current_process = subprocess.Popen([self.selected_path])
        else:
            # Try v1.1 first (default), then v2 (fallback)
            ahk = self.ahk_path_entry_v1.get() if hasattr(self, 'ahk_path_entry_v1') else ""
            if not (ahk and os.path.exists(ahk)):
                ahk = self.ahk_path_entry_v2.get() if hasattr(self, 'ahk_path_entry_v2') else ""
            
            if ahk and os.path.exists(ahk):
                self.current_process = subprocess.Popen([ahk, self.selected_path])
            else:
                self.status.configure(text=self.t("autohotkey_notfound"), text_color="red")
                return
        
        self.is_playing = True
        self.now_playing.configure(text=f"Now: {os.path.basename(self.selected_path)}")
        self.status.configure(text=self.t("playing"))
        
        # Start thread to wait for song to end
        threading.Thread(target=self._wait_for_song, daemon=True).start()
    
    def _wait_for_song(self):
        if self.current_process:
            self.current_process.wait()
            self.is_playing = False
            self.current_process = None
            self.after(0, lambda: self.status.configure(text=self.t("finished")))
            self.after(0, lambda: self.now_playing.configure(text=self.t("now_playing")))

    def pause(self):
        if self.is_playing:
            self.status.configure(text=self.t("paused"))
            self.is_playing = False

    def stop(self):
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=2)
            except:
                try:
                    self.current_process.kill()
                except:
                    pass
            self.current_process = None
            self.is_playing = False
            self.status.configure(text=self.t("stopped"))
            self.now_playing.configure(text=self.t("now_playing"))
        else:
            self.status.configure(text=self.t("nothing_playing"))

    def browse_folder(self):
        from tkinter import filedialog
        folder = filedialog.askdirectory(initialdir=self.songs_folder)
        if folder:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)

    def apply_delay(self):
        try:
            self.start_delay = int(self.delay_entry.get())
            self.save_settings()
        except:
            pass
    
    def apply_folder(self):
        self.songs_folder = self.folder_entry.get()
        self.check_and_create_folders()
        self.load_songs()
        self.status.configure(text=self.t("folder_applied"))

if __name__ == "__main__":
    app = GW2Bard()
    app.mainloop()