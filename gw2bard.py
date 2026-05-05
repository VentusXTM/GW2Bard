# GW2Bard - Guild Wars 2 Music Player
import os
import subprocess
import time
import threading
from customtkinter import *
from tkinter import Listbox

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
    }
}

set_appearance_mode("dark")
set_default_color_theme("blue")

class GW2Bard(CTk):
    def __init__(self):
        super().__init__()
        self.title("GW2Bard")
        self.geometry("600x400")
        self.resizable(False, False)
        
        self.current_process = None
        self.is_playing = False
        self.songs_folder = DEFAULT_SONGS_FOLDER
        self.start_delay = 0
        self.language = "en"
        self.first_run = True
        self.songs_data = []
        self.selected_path = ""
        
        self.load_settings()
        
        # First run wizard
        if self.first_run:
            self.show_wizard()
        else:
            self.create_widgets()
            self.check_and_create_folders()
            self.load_songs()
    
    def show_wizard(self):
        self.wizard_frame = CTkFrame(self, width=580, height=380)
        self.wizard_frame.place(x=10, y=10)
        
        CTkLabel(self.wizard_frame, text=self.t("welcome"), font=("Arial", 18, "bold")).place(x=290, y=30, anchor="center")
        CTkLabel(self.wizard_frame, text=self.t("welcome_desc"), font=("Arial", 11), text_color="gray").place(x=290, y=70, anchor="center")
        
        CTkLabel(self.wizard_frame, text=self.t("language")).place(x=50, y=120)
        self.wizard_lang_var = StringVar(value="English")
        self.wizard_lang_dropdown = CTkOptionMenu(self.wizard_frame, values=["English", "Spanish"], variable=self.wizard_lang_var, command=self.on_wizard_lang_change, width=120)
        self.wizard_lang_dropdown.place(x=50, y=145)
        
        CTkLabel(self.wizard_frame, text=self.t("songs_folder")).place(x=50, y=190)
        self.wizard_folder_entry = CTkEntry(self.wizard_frame, width=400)
        self.wizard_folder_entry.insert(0, self.t("select_folder"))
        self.wizard_folder_entry.place(x=50, y=215)
        CTkButton(self.wizard_frame, text=self.t("browse"), command=self.wizard_browse_folder, width=70).place(x=460, y=213)
        
        CTkButton(self.wizard_frame, text=self.t("save_settings"), command=self.finish_wizard, width=150, height=35, font=("Arial", 12)).place(x=215, y=290)
    
    def on_wizard_lang_change(self, choice):
        self.language = "en" if choice == "English" else "es"
        # Rebuild wizard UI
        for widget in self.wizard_frame.winfo_children():
            widget.destroy()
        
        CTkLabel(self.wizard_frame, text=self.t("welcome"), font=("Arial", 18, "bold")).place(x=290, y=30, anchor="center")
        CTkLabel(self.wizard_frame, text=self.t("welcome_desc"), font=("Arial", 11), text_color="gray").place(x=290, y=70, anchor="center")
        
        CTkLabel(self.wizard_frame, text=self.t("language")).place(x=50, y=120)
        self.wizard_lang_var = StringVar(value=choice)
        self.wizard_lang_dropdown = CTkOptionMenu(self.wizard_frame, values=["English", "Spanish"], variable=self.wizard_lang_var, command=self.on_wizard_lang_change, width=120)
        self.wizard_lang_dropdown.place(x=50, y=145)
        
        CTkLabel(self.wizard_frame, text=self.t("songs_folder")).place(x=50, y=190)
        self.wizard_folder_entry = CTkEntry(self.wizard_frame, width=400)
        self.wizard_folder_entry.insert(0, self.t("select_folder"))
        self.wizard_folder_entry.place(x=50, y=215)
        CTkButton(self.wizard_frame, text=self.t("browse"), command=self.wizard_browse_folder, width=70).place(x=460, y=213)
        
        CTkButton(self.wizard_frame, text=self.t("save_settings"), command=self.finish_wizard, width=150, height=35, font=("Arial", 12)).place(x=215, y=290)
    
    def wizard_browse_folder(self):
        from tkinter import filedialog
        folder = filedialog.askdirectory(initialdir=self.songs_folder)
        if folder:
            self.wizard_folder_entry.delete(0, "end")
            self.wizard_folder_entry.insert(0, folder)
    
    def finish_wizard(self):
        self.songs_folder = self.wizard_folder_entry.get()
        self.first_run = False
        self.save_settings()
        
        self.wizard_frame.place_forget()
        
        self.create_widgets()
        self.check_and_create_folders()
        self.load_songs()
    
    def t(self, key):
        return TRANSLATIONS[self.language].get(key, key)

    def create_widgets(self):
        self.tabview = CTkTabview(self, width=580, height=380)
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
        
        self.ahk_label = CTkLabel(self.tab_options, text=self.t("autohotkey"))
        self.ahk_label.place(x=10, y=195)
        self.ahk_path_entry = CTkEntry(self.tab_options, width=450)
        self.ahk_path_entry.insert(0, self.find_ahk_path())
        self.ahk_path_entry.place(x=10, y=220)
        
        self.save_btn = CTkButton(self.tab_options, text=self.t("save_settings"), command=self.save_settings, width=120, height=30)
        self.save_btn.place(x=230, y=260)

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
        paths = [r"C:\Program Files\AutoHotkey\AutoHotkey.exe", r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe"]
        for path in paths:
            if os.path.exists(path):
                return path
        return ""

    def load_settings(self):
        settings_file = os.path.join(os.path.dirname(__file__), "settings.txt")
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
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

    def save_settings(self):
        settings_file = os.path.join(os.path.dirname(__file__), "settings.txt")
        with open(settings_file, 'w') as f:
            f.write(f"songs_folder={self.songs_folder}\n")
            f.write(f"start_delay={self.start_delay}\n")
            f.write(f"language={self.language}\n")
            f.write(f"first_run={str(self.first_run).lower()}\n")
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
            ahk = self.ahk_path_entry.get()
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