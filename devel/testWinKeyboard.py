import sys
import time
import json
import configparser
import os
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import keyboard
from nava import play


# Local application/library specific imports
import pressagio.callback
import pressagio
import icons_rc  

pressagioconfig_file= os.path.join(os.path.dirname(os.path.realpath(__file__)), "res","morsewriter_pressagio.ini")
pressagioconfig = configparser.ConfigParser()
pressagioconfig.read(pressagioconfig_file)

# If configfile file is lost.. 
DEFAULT_CONFIG = {
  "keylen": 1,
  "keyone": "SPACE",
  "keytwo": "ENTER",
  "keythree": "RCTRL",
  "maxDitTime": 350,  # It's better to store numbers as numbers, not strings
  "minLetterPause": 1000,
  "withsound": True,
  "SoundDit": "res/dit_sound.wav",
  "SoundDah": "res/dah_sound.wav",
  "debug": True,
  "off": False,
  "fontsizescale": 100,
  "upperchars": True,
  "autostart": False,
  "winxaxis": "left",
  "winyaxis": "top",
  "winposx": 10,
  "winposy": 10
}

class PressagioCallback(pressagio.callback.Callback):
    def __init__(self, buffer):
        super().__init__()
        self.buffer = buffer

    def past_stream(self):
        return self.buffer

    def future_stream(self):
        return ""
        
class TypeState (pressagio.callback.Callback):
    def __init__ (self):
        self.text = ""
        self.predictions = None
        self.presage = pressagio.Pressagio(self, pressagioconfig)
    def past_stream (self):
        return self.text
    def future_stream (self):
        return self.text
    def pushchar (self, char):
        self.text += char
        self.predictions = None
    def popchar (self):
        self.text = self.text[:-1]
        self.predictions = None
    def getpredictions (self):
        if self.predictions == None:
            self.predictions = self.presage.predict()


        return self.predictions

class ConfigManager:
    def __init__(self, config_file=None, default_config=DEFAULT_CONFIG):
        self.config_file = config_file
        self.default_config = default_config
        self.config = self.read_config()
        self.actions = {}

    def read_config(self):
        if self.config_file and os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as file:
                    data = json.load(file)
                    self.convert_types(data)
                    return data
            except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
                logging.warning(f"Error loading configuration: {e}")
        return self.default_config.copy()
        

    def update_keystrokes(self, data):
        for key in ['keyone', 'keytwo', 'keythree']:
            if key in data and data[key] in self.keystrokemap:
                data[key] = self.keystrokemap[data[key]]

    def convert_types(self, data):
        if 'maxDitTime' in data:
            data['maxDitTime'] = float(data['maxDitTime'])
        if 'minLetterPause' in data:
            data['minLetterPause'] = float(data['minLetterPause'])
        if 'fontsizescale' in data:
            data['fontsizescale'] = int(data['fontsizescale'])

    def save_config(self):
        try:
            with open(self.config_file, "w") as file:
                json.dump(self.config, file, indent=4)
        except Exception as e:
            logging.warning(f"Error saving configuration: {e}")

    def get_config(self):
        return self.config
        

class KeyListenerThread(QThread):
    keyEvent = pyqtSignal(str, bool)  # Signal emitting key name and whether it's pressed or released

    def __init__(self, configured_keys):
        super().__init__()
        self.configured_keys = configured_keys

    def run(self):
        # Use the keyboard library to hook to the specified keys
        for key in self.configured_keys:
            keyboard.on_press_key(key, lambda e: self.keyEvent.emit(e.name, True))
            keyboard.on_release_key(key, lambda e: self.keyEvent.emit(e.name, False))
        self.exec_()  # Start the Qt event loop to keep the thread running

    def stop(self):
        keyboard.unhook_all()  # Unhooks all keys when the thread is stopped

class MainWindow(QMainWindow):
    def __init__(self, configManager):
        super().__init__()
        self.setWindowTitle("Qt with Keyboard Library")
        self.resize(300, 200)
        self.configManager = configManager
        self.config = self.configManager.get_config()
        self.endCharacterTimer = None
        self.init()
        self.listenerThread = None 
        self.startKeyListener()

    def init(self):
        self.currentCharacter = []
        self.typestate = pressagio.Pressagio(pressagio.callback.Callback(), pressagioconfig)
        self.lastKeyDownTime = None

    def get_configured_keys(self):
        key_names = []
        if self.config.get('keylen', 1) >= 1:
            key_names.append(self.config.get('keyone', 'SPACE'))  # Default to SPACE if not set
        if self.config.get('keylen', 1) >= 2:
            key_names.append(self.config.get('keytwo', 'ENTER'))  # Default to ENTER if not set
        if self.config.get('keylen', 1) == 3:
            key_names.append(self.config.get('keythree', 'RCTRL'))  # Default to RCTRL if not set
        return key_names

    def startKeyListener(self):
        key_names = self.get_configured_keys()
        if not self.listenerThread:
            self.listenerThread = KeyListenerThread(configured_keys=key_names)
            self.listenerThread.keyEvent.connect(self.handle_key_event)
            self.listenerThread.start()

    def handle_key_event(self, key, is_press):
        if is_press:
            self.on_press(key)
        else:
            self.on_release(key)

    def on_press(self, key):
        self.lastKeyDownTime = time.time()

    def on_release(self, key):
        duration = (time.time() - self.lastKeyDownTime) * 1000  # Duration in milliseconds
        maxDitTime = self.config.get('maxDitTime', 350)
        if duration < maxDitTime:
            self.addDit()
        else:
            self.addDah()
        self.startEndCharacterTimer()

    def addDit(self):
        self.currentCharacter.append(".")
        if self.config['withsound']:
            play(self.config['SoundDit'])

    def addDah(self):
        self.currentCharacter.append("-")
        if self.config['withsound']:
            play(self.config['SoundDah'])

    def startEndCharacterTimer(self):
        if self.endCharacterTimer is not None:
            self.endCharacterTimer.stop()
        self.endCharacterTimer = QTimer()
        self.endCharacterTimer.setSingleShot(True)
        self.endCharacterTimer.timeout.connect(self.endCharacter)
        self.endCharacterTimer.start(int(self.config['minLetterPause']))

    def endCharacter(self):
        morse_code = "".join(self.currentCharacter)
        print(morse_code)  # Process Morse code here
        self.currentCharacter = []

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    configmanager = ConfigManager(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.json"), default_config=DEFAULT_CONFIG)
    app = QApplication(sys.argv)
    window = MainWindow(configManager=configmanager)
    window.show()
    sys.exit(app.exec_())
