import sys
import logging
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from pynput.keyboard import Listener, Key, KeyCode
import time
import json
import configparser
import os
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
    keyEvent = pyqtSignal(str, bool)

    def __init__(self, configured_keys):
        super().__init__()
        self.configured_keys = configured_keys
        self.listener = None

    def run(self):
        try:
            self.listener = Listener(on_press=self.on_press, on_release=self.on_release)
            self.listener.start()
            self.listener.join()
        except Exception as e:
            logging.error(f"Listener failed: {e}")

    def stop(self):
        if self.listener:
            self.listener.stop()

    def on_press(self, key):
        try:
            if any(key == k for k in self.configured_keys):
                key_description = self.get_key_description(key)
                self.keyEvent.emit(key_description, True)
        except Exception as e:
            logging.error(f"Error processing key press: {e}")

    def on_release(self, key):
        try:
            if any(key == k for k in self.configured_keys):
                key_description = self.get_key_description(key)
                self.keyEvent.emit(key_description, False)
        except Exception as e:
            logging.error(f"Error processing key release: {e}")

    def get_key_description(self, key):
        if hasattr(key, 'char') and key.char:
            return key.char
        elif hasattr(key, 'name'):
            return key.name
        return 'Unknown key'


class MainWindow(QMainWindow):
    def __init__(self, configManager):
        super().__init__()
        self.setWindowTitle("Qt with Pynput")
        self.lastKeyDownTime = None
        self.resize(300, 200)
        self.configManager = configManager
        self.config = self.configManager.get_config()
        self.endCharacterTimer = None
        self.init()
        self.listenerThread = None 
        self.startKeyListener()

    def init(self):
        self.currentCharacter = []
        self.repeaton = False 
        self.repeatkey = None
        self.typestate = TypeState()
        
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
        pynputKeys = {
            "SPACE": Key.space, "ENTER": Key.enter,
            "ONE": KeyCode.from_char('1'), "TWO": KeyCode.from_char('2'),
            "Z": KeyCode.from_char('z'), "X": KeyCode.from_char('x'),
            "F8": Key.f8, "F9": Key.f9,
            "RCTRL": Key.ctrl_r, "LCTRL": Key.ctrl_l,
            "RSHIFT": Key.shift_r, "LSHIFT": Key.shift_l,
            "LALT": Key.alt_l
        }
        logging.debug(f"Available keys in pynputKeys: {list(pynputKeys.keys())}")  # Print available keys

        try:
            key_names = self.get_configured_keys()  # Retrieve configured key names
            logging.debug(f"Configured key names: {key_names}")
            configured_keys = [pynputKeys[key.upper()] for key in key_names if key.upper() in pynputKeys]
            logging.debug(f"Configured pynput keys: {configured_keys}")
    
            if not configured_keys:  # If no valid keys are configured, log and avoid starting the thread
                logging.warning("No valid keys configured for KeyListenerThread.")
                return
    
            if not self.listenerThread:
                self.listenerThread = KeyListenerThread(configured_keys=configured_keys)
                self.listenerThread.keyEvent.connect(self.handle_key_event)
                self.listenerThread.start()
            logging.debug("KeyListenerThread started successfully.")
        except Exception as e:
            logging.critical(f"Failed to start KeyListenerThread due to error: {str(e)}")
            logging.critical(f"Problematic keys: {[key for key in key_names if key.upper() not in pynputKeys]}")

    def handle_key_event(self, key, is_press):
        logging.debug(f"Event received: Key={key}, Pressed={is_press}")
        try:
            if is_press:
                self.on_press(key)
            else:
                self.on_release(key)
        except Exception as e:
            logging.warning(f"Error handling key event: {e}")
            

    def on_press(self, key):
        try:
            if self.lastKeyDownTime is None:  # Start timing the key press
                self.lastKeyDownTime = time.time()
            logging.debug(f"Key pressed: {key}")
        except Exception as e:
            logging.warning(f"Error on key press: {e}")
    
    def on_release(self, key):
        try:
            if self.lastKeyDownTime is not None:
                duration = (time.time() - self.lastKeyDownTime) * 1000  # Duration in milliseconds
                self.lastKeyDownTime = None
                maxDitTime = float(self.config.get('maxDitTime', 350))  # Safely access config
                if duration < maxDitTime:
                    self.addDit()
                else:
                    self.addDah()
                self.startEndCharacterTimer()
                logging.debug(f"Key released: {key}, duration: {duration}ms")
        except Exception as e:
            logging.warning(f"Error on key release: {e}")
            
    def addDit(self):
        self.currentCharacter.append(1)  # Assuming 1 represents Dit
        if self.config['withsound']:
            play("res/dit_sound.wav")

    def addDah(self):
        self.currentCharacter.append(2)  # Assuming 2 represents Dah
        if self.config['withsound']:
            play("res/dah_sound.wav")

    def startEndCharacterTimer(self):
        if self.endCharacterTimer is not None:
            self.endCharacterTimer.stop()
        self.endCharacterTimer = QTimer()
        self.endCharacterTimer.setSingleShot(True)
        self.endCharacterTimer.timeout.connect(self.endCharacter)
        self.endCharacterTimer.start(int(self.config['minLetterPause']))

    def endCharacter(self):
        morse_code = "".join(map(str, self.currentCharacter))
        # Find the corresponding item based on morse_code
        #This is now different.. 
        print(morse_code)

            
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    configmanager = ConfigManager(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.json"), default_config=DEFAULT_CONFIG)
    app = QApplication(sys.argv)
    window = MainWindow(configManager=configmanager)
    window.show()
    sys.exit(app.exec_())
