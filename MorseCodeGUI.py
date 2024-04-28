# Standard library imports
import configparser
import json
import logging
import os
import sys
import threading
import time
from collections import OrderedDict
from enum import Enum
from threading import Thread

# Third-party imports
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAction, QCheckBox, QComboBox, QDialog, QGridLayout,
                             QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
                             QPushButton, QRadioButton, QSystemTrayIcon, QVBoxLayout,
                             QWidget, QApplication, QMenu)
from nava import play
import keyboard
import mouse
# Local application/library specific imports
import pressagio.callback
import pressagio
import icons_rc  

# Configure basic logger
#logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='w',format='%(name)s - %(levelname)s - %(message)s')

# If you want to the console
logging.basicConfig(level=logging.DEBUG,format='%(name)s - %(levelname)s - %(message)s')
                    
lastkeydowntime = -1

pressagioconfig_file= os.path.join(os.path.dirname(os.path.realpath(__file__)), "res","morsewriter_pressagio.ini")
pressagioconfig = configparser.ConfigParser()
pressagioconfig.read(pressagioconfig_file)

keystrokes_state = {}
currentX = 0
currentY = 0
pressingKey = False
typestate = None

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


class ConfigManager:
    def __init__(self, config_file=None, default_config=DEFAULT_CONFIG):
        self.key_data = {
        "A": {'label': 'a', 'key_code': 'a', 'character': 'a', 'arg': None},
        "B": {'label': 'b', 'key_code': 'b', 'character': 'b', 'arg': None},
        "C": {'label': 'c', 'key_code': 'c', 'character': 'c', 'arg': None},
        "D": {'label': 'd', 'key_code': 'd', 'character': 'd', 'arg': None},
        "E": {'label': 'e', 'key_code': 'e', 'character': 'e', 'arg': None},
        "F": {'label': 'f', 'key_code': 'f', 'character': 'f', 'arg': None},
        "G": {'label': 'g', 'key_code': 'g', 'character': 'g', 'arg': None},
        "H": {'label': 'h', 'key_code': 'h', 'character': 'h', 'arg': None},
        "I": {'label': 'i', 'key_code': 'i', 'character': 'i', 'arg': None},
        "J": {'label': 'j', 'key_code': 'j', 'character': 'j', 'arg': None},
        "K": {'label': 'k', 'key_code': 'k', 'character': 'k', 'arg': None},
        "L": {'label': 'l', 'key_code': 'l', 'character': 'l', 'arg': None},
        "M": {'label': 'm', 'key_code': 'm', 'character': 'm', 'arg': None},
        "N": {'label': 'n', 'key_code': 'n', 'character': 'n', 'arg': None},
        "O": {'label': 'o', 'key_code': 'o', 'character': 'o', 'arg': None},
        "P": {'label': 'p', 'key_code': 'p', 'character': 'p', 'arg': None},
        "Q": {'label': 'q', 'key_code': 'q', 'character': 'q', 'arg': None},
        "R": {'label': 'r', 'key_code': 'r', 'character': 'r', 'arg': None},
        "S": {'label': 's', 'key_code': 's', 'character': 's', 'arg': None},
        "T": {'label': 't', 'key_code': 't', 'character': 't', 'arg': None},
        "U": {'label': 'u', 'key_code': 'u', 'character': 'u', 'arg': None},
        "V": {'label': 'v', 'key_code': 'v', 'character': 'v', 'arg': None},
        "W": {'label': 'w', 'key_code': 'w', 'character': 'w', 'arg': None},
        "X": {'label': 'x', 'key_code': 'x', 'character': 'x', 'arg': None},
        "Y": {'label': 'y', 'key_code': 'y', 'character': 'y', 'arg': None},
        "Z": {'label': 'z', 'key_code': 'z', 'character': 'z', 'arg': None},
        "ONE": {'label': '1', 'key_code': '1', 'character': '1', 'arg': None},
        "TWO": {'label': '2', 'key_code': '2', 'character': '2', 'arg': None},
        "THREE": {'label': '3', 'key_code': '3', 'character': '3', 'arg': None},
        "FOUR": {'label': '4', 'key_code': '4', 'character': '4', 'arg': None},
        "FIVE": {'label': '5', 'key_code': '5', 'character': '5', 'arg': None},
        "SIX": {'label': '6', 'key_code': '6', 'character': '6', 'arg': None},
        "SEVEN": {'label': '7', 'key_code': '7', 'character': '7', 'arg': None},
        "EIGHT": {'label': '8', 'key_code': '8', 'character': '8', 'arg': None},
        "NINE": {'label': '9', 'key_code': '9', 'character': '9', 'arg': None},
        "ZERO": {'label': '0', 'key_code': '0', 'character': '0', 'arg': None},
        "DOT": {'label': '.', 'key_code': '.', 'character': '.', 'arg': None},
        "COMMA": {'label': ',', 'key_code': ',', 'character': ',', 'arg': None},
        "QUESTION": {'label': '?', 'key_code': '/', 'character': '?', 'arg': None},
        "EXCLAMATION": {'label': '!', 'key_code': '1', 'character': '!', 'arg': None},
        "COLON": {'label': ':', 'key_code': ';', 'character': ':', 'arg': None},
        "SEMICOLON": {'label': ';', 'key_code': ';', 'character': ';', 'arg': None},
        "AT": {'label': '@', 'key_code': '2', 'character': '@', 'arg': None},
        "HASH": {'label': '#', 'key_code': '3', 'character': '#', 'arg': None},
        "DOLLAR": {'label': '$', 'key_code': '4', 'character': '$', 'arg': None},
        "PERCENT": {'label': '%', 'key_code': '5', 'character': '%', 'arg': None},
        "AMPERSAND": {'label': '&', 'key_code': '7', 'character': '&', 'arg': None},
        "STAR": {'label': '*', 'key_code': '*', 'character': '*', 'arg': None},
        "PLUS": {'label': '+', 'key_code': '=', 'character': '+', 'arg': None},
        "MINUS": {'label': '-', 'key_code': '-', 'character': '-', 'arg': None},
        "EQUALS": {'label': '=', 'key_code': '=', 'character': '=', 'arg': None},
        "FSLASH": {'label': '/', 'key_code': '/', 'character': '/', 'arg': None},
        "BSLASH": {'label': '\\', 'key_code': '\\', 'character': '\\', 'arg': None},
        "SINGLEQUOTE": {'label': "'", 'key_code': "'", 'character': "'", 'arg': None},
        "DOUBLEQUOTE": {'label': '"', 'key_code': '"', 'character': '"', 'arg': None},
        "OPENBRACKET": {'label': '(', 'key_code': '9', 'character': '(', 'arg': None},
        "CLOSEBRACKET": {'label': ')', 'key_code': '0', 'character': ')', 'arg': None},
        "LESSTHAN": {'label': '<', 'key_code': ',', 'character': '<', 'arg': None},
        "MORETHAN": {'label': '>', 'key_code': '.', 'character': '>', 'arg': None},
        "CIRCONFLEX": {'label': '^', 'key_code': '6', 'character': '^', 'arg': None},
        "ENTER": {'label': 'ENTER', 'key_code': 'Key.enter', 'character': '\n', 'arg': None},
        "SPACE": {'label': 'space', 'key_code': 'Key.space', 'character': ' ', 'arg': None},
        "BACKSPACE": {'label': 'bckspc', 'key_code': 'Key.backspace', 'character': '\x08', 'arg': None},
        "TAB": {'label': 'tab', 'key_code': 'Key.tab', 'character': '\t', 'arg': None},
        "PAGEUP": {'label': 'pageup', 'key_code': 'Key.page_up', 'character': None, 'arg': None},
        "PAGEDOWN": {'label': 'pagedwn', 'key_code': 'Key.page_down', 'character': None, 'arg': None},
        "LEFTARROW": {'label': 'left', 'key_code': 'Key.left', 'character': None, 'arg': None},
        "RIGHTARROW": {'label': 'right', 'key_code': 'Key.right', 'character': None, 'arg': None},
        "UPARROW": {'label': 'up', 'key_code': 'Key.up', 'character': None, 'arg': None},
        "DOWNARROW": {'label': 'down', 'key_code': 'Key.down', 'character': None, 'arg': None},
        "ESCAPE": {'label': 'esc', 'key_code': 'Key.esc', 'character': None, 'arg': None},
        "HOME": {'label': 'home', 'key_code': 'Key.home', 'character': None, 'arg': None},
        "END": {'label': 'end', 'key_code': 'Key.end', 'character': None, 'arg': None},
        "DELETE": {'label': 'del', 'key_code': 'Key.delete', 'character': None, 'arg': None},
        "SHIFT": {'label': 'shift', 'key_code': 'Key.shift', 'character': None, 'arg': None},
        "RSHIFT": {'label': 'rshift', 'key_code': 'Key.rshift', 'character': None, 'arg': None},
        "LSHIFT": {'label': 'lshift', 'key_code': 'Key.lshift', 'character': None, 'arg': None},
        "CTRL": {'label': 'ctrl', 'key_code': 'Key.ctrl', 'character': None, 'arg': None},
        "RCTRL": {'label': 'rctrl', 'key_code': 'Key.rctrl', 'character': None, 'arg': None},
        "LCTRL": {'label': 'lctrl', 'key_code': 'Key.lctrl', 'character': None, 'arg': None},
        "ALT": {'label': 'alt', 'key_code': 'Key.alt', 'character': None, 'arg': None},
        "WINDOWS": {'label': 'win', 'key_code': 'Key.cmd', 'character': None, 'arg': None},
        "CAPSLOCK": {'label': 'caps', 'key_code': 'Key.caps_lock', 'character': None, 'arg': None},
        "F1": {'label': 'F1', 'key_code': 'Key.f1', 'character': None, 'arg': None},
        "F2": {'label': 'F2', 'key_code': 'Key.f2', 'character': None, 'arg': None},
        "F3": {'label': 'F3', 'key_code': 'Key.f3', 'character': None, 'arg': None},
        "F4": {'label': 'F4', 'key_code': 'Key.f4', 'character': None, 'arg': None},
        "F5": {'label': 'F5', 'key_code': 'Key.f5', 'character': None, 'arg': None},
        "F6": {'label': 'F6', 'key_code': 'Key.f6', 'character': None, 'arg': None},
        "F7": {'label': 'F7', 'key_code': 'Key.f7', 'character': None, 'arg': None},
        "F8": {'label': 'F8', 'key_code': 'Key.f8', 'character': None, 'arg': None},
        "F9": {'label': 'F9', 'key_code': 'Key.f9', 'character': None, 'arg': None},
        "F10": {'label': 'F10', 'key_code': 'Key.f10', 'character': None, 'arg': None},
        "F11": {'label': 'F11', 'key_code': 'Key.f11', 'character': None, 'arg': None},
        "F12": {'label': 'F12', 'key_code': 'Key.f12', 'character': None, 'arg': None},
        "REPEATMODE": {'label': 'repeat', 'key_code': 'unknown', 'character': None, 'arg': 0},
        "SOUND": {'label': 'snd', 'key_code': 'unknown', 'character': None, 'arg': 8},
        "CODESET": {'label': 'code', 'key_code': 'unknown', 'character': None, 'arg': 9},
        "MOUSERIGHT5": {'label': 'ms right 5', 'key_code': 'unknown', 'character': None, 'arg': 2},
        "MOUSEUP5": {'label': 'ms up 5', 'key_code': 'unknown', 'character': None, 'arg': 3},
        "MOUSECLICKLEFT": {'label': 'ms clkleft', 'key_code': 'unknown', 'character': None, 'arg': 4},
        "MOUSEDBLCLICKLEFT": {'label': 'ms dblclkleft', 'key_code': 'unknown', 'character': None, 'arg': 5},
        "MOUSECLKHLDLEFT": {'label': 'ms hldleft', 'key_code': 'unknown', 'character': None, 'arg': 6},
        "MOUSEUPLEFT5": {'label': 'ms leftup 5', 'key_code': 'unknown', 'character': None, 'arg': 7},
        "MOUSEDOWNLEFT5": {'label': 'ms leftdown 5', 'key_code': 'unknown', 'character': None, 'arg': 8},
        "MOUSERELEASEHOLD": {'label': 'ms release', 'key_code': 'unknown', 'character': None, 'arg': 9},
        "MOUSELEFT5": {'label': 'ms left 5', 'key_code': 'unknown', 'character': None, 'arg': 0},
        "MOUSEDOWN5": {'label': 'ms down 5', 'key_code': 'unknown', 'character': None, 'arg': 1},
        "MOUSECLICKRIGHT": {'label': 'ms clkright', 'key_code': 'unknown', 'character': None, 'arg': 2},
        "MOUSEDBLCLICKRIGHT": {'label': 'ms dblclkright', 'key_code': 'unknown', 'character': None, 'arg': 3},
        "MOUSECLKHLDRIGHT": {'label': 'ms hldright', 'key_code': 'unknown', 'character': None, 'arg': 4},
        "MOUSEUPRIGHT5": {'label': 'ms rightup 5', 'key_code': 'unknown', 'character': None, 'arg': 5},
        "MOUSEDOWNRIGHT5": {'label': 'ms rightdown 5', 'key_code': 'unknown', 'character': None, 'arg': 6},
        "NORMALMODE": {'label': 'normal mode', 'key_code': 'unknown', 'character': None, 'arg': 7},
        "MOUSEUP40": {'label': 'ms up 40', 'key_code': 'unknown', 'character': None, 'arg': 8},
        "MOUSEUP250": {'label': 'ms up 250', 'key_code': 'unknown', 'character': None, 'arg': 9},
        "MOUSEDOWN40": {'label': 'ms down 40', 'key_code': 'unknown', 'character': None, 'arg': 0},
        "MOUSEDOWN250": {'label': 'ms down 250', 'key_code': 'unknown', 'character': None, 'arg': 1},
        "MOUSELEFT40": {'label': 'ms left 40', 'key_code': 'unknown', 'character': None, 'arg': 2},
        "MOUSELEFT250": {'label': 'ms left 250', 'key_code': 'unknown', 'character': None, 'arg': 3},
        "MOUSERIGHT40": {'label': 'ms right 40', 'key_code': 'unknown', 'character': None, 'arg': 4},
        "MOUSERIGHT250": {'label': 'ms right 250', 'key_code': 'unknown', 'character': None, 'arg': 5},
        "MOUSEUPLEFT40": {'label': 'ms leftup 40', 'key_code': 'unknown', 'character': None, 'arg': 6},
        "MOUSEUPLEFT250": {'label': 'ms leftup 250', 'key_code': 'unknown', 'character': None, 'arg': 7},
        "MOUSEDOWNLEFT40": {'label': 'ms leftdown 40', 'key_code': 'unknown', 'character': None, 'arg': 8},
        "MOUSEDOWNLEFT250": {'label': 'ms leftdown 250', 'key_code': 'unknown', 'character': None, 'arg': 9},
        "MOUSEUPRIGHT40": {'label': 'ms rightup 40', 'key_code': 'unknown', 'character': None, 'arg': 0},
        "MOUSEUPRIGHT250": {'label': 'ms rightup 250', 'key_code': 'unknown', 'character': None, 'arg': 1},
        "MOUSEDOWNRIGHT40": {'label': 'ms rightdown 40', 'key_code': 'unknown', 'character': None, 'arg': 2},
        "MOUSEDOWNRIGHT250": {'label': 'ms rightdown 250', 'key_code': 'unknown', 'character': None, 'arg': 3}
        }
        self.config_file = config_file
        self.default_config = default_config
        self.keystrokemap, self.keystrokes = self.initKeystrokeMap()
        self.config = self.read_config()
        self.actions = {}

    def initKeystrokeMap(self):
        keystrokemap = {}
        keystrokes = []
        for key, data in self.key_data.items():
            stroke = KeyStroke(key, data['label'], data['key_code'], data['character'])
            keystrokes.append(stroke)
            keystrokemap[key] = stroke
        return keystrokemap, keystrokes
    
    def read_config(self):
        if self.config_file and os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as file:
                    data = json.load(file)
                    self.update_keystrokes(data)
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
        
    def initActions(self, window):
        actions = {}
        
        # Set up actions for each key based on `key_data`
        for key, value in self.key_data.items():
            label = value['label']
            key_code = value['key_code']
            character = value['character']
            arg = value['arg']
    
            # Use the correct capturing of loop variables
            action_key = key.upper()
            actions[action_key] = lambda item, lbl=label, kc=key_code, char=character, a=arg: ActionKeyStroke(
                {'label': lbl, 'key_code': kc, 'character': char, 'arg': a}, kc)
        
        # Define special actions with correct lambda capturing
        actions["CHANGELAYOUT"] = lambda item, win=window: ChangeLayoutAction(item, win)
        actions["PREDICTION_SELECT"] = lambda item, win=window: PredictionSelectLayoutAction(
            item, get_predictions_func=win.getTypeStatePredictions)
        actions["KEYSTROKE"] = lambda item, kd=self.key_data: ActionKeyStroke(item, kd[item['action'].upper()])
    
        return actions
        
class TypeState(pressagio.callback.Callback):
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
        logging.debug(f"Updated TypeState text: {self.text}")
    def popchar (self):
        self.text = self.text[:-1]
        self.predictions = None
    def getpredictions(self):
        logging.debug("[TypeState] Fetching predictions for text: {}".format(self.text))
        if self.predictions is None:
            try:
                logging.debug("[TypeState] Predictions fetched: {}".format(self.predictions))
                self.predictions = self.presage.predict()
            except Exception as e:
                logging.error(f"[TypeState] Failed to generate predictions: {str(e)}")
                self.predictions = []
        return self.predictions


class KeyListenerThread(QThread):
    keyEvent = pyqtSignal(str, bool)  # Emit key name and press/release status

    def __init__(self, configured_keys):
        super().__init__()
        self.configured_keys = configured_keys  # keys in the 'keyboard' library format
        self.keep_running = True  # Control running of the loop

    def run(self):
        # Setup key hooks once, outside the loop
        for key in self.configured_keys:
            keyboard.on_press_key(key, self.on_press, suppress=True)
            keyboard.on_release_key(key, self.on_release, suppress=True)
        
        # Minimal loop to keep the thread alive
        while self.keep_running:
            time.sleep(0.1)  # Small sleep to avoid CPU overload

    def on_press(self, event):
        self.keyEvent.emit(event.name, True)

    def on_release(self, event):
        self.keyEvent.emit(event.name, False)

    def stop(self):
        self.keep_running = False  # Signal the loop to stop
        keyboard.unhook_all()  # Unhook all keys
        self.quit()  # Quit the thread's event loop if necessary
        self.wait()  # Wait for the thread to finish


class PressagioCallback(pressagio.callback.Callback):
    def __init__(self, buffer):
        super().__init__()
        self.buffer = buffer

    def past_stream(self):
        return self.buffer

    def future_stream(self):
        return ""
            
class LayoutManager:
    def __init__(self, layout_file):
        self.layout_file = layout_file
        self.layouts = {}
        self.active_layout_name = None
        self.main_layout_name = None
        self.load_layouts()

    def load_layouts(self):
        """Loads layout data from a JSON file without assigning actions."""
        try:
            with open(self.layout_file, "r") as f:
                data = json.load(f)
            self.layouts = {k: v for k, v in data['layouts'].items()}
            self.main_layout_name = data.get('mainlayout')
            self.active_layout_name = data.get('mainlayout')
            if self.active_layout_name not in self.layouts:
                raise ValueError("No valid main layout found in the layout file.")
        except FileNotFoundError:
            raise Exception(f"Layout file {self.layout_file} not found.")
        except json.JSONDecodeError:
            raise Exception("Error decoding JSON from the layout file.")

    def set_actions(self, actions):
        """Integrates actions with the layout items loaded from the layout file."""
        for layout_name, layout in self.layouts.items():
            if 'items' in layout:
                for item in layout['items']:
                    action_name = item.get('action')
                    if action_name in actions:
                        item['_action'] = actions[action_name](item)
                    else:
                        item['_action'] = None
                        logging.warning(f"No action found for {action_name} in layout {layout_name}")

    def set_active(self, layout_name):
        """Sets the active layout by name."""
        if layout_name in self.layouts:
            self.active_layout_name = layout_name
            logging.info(f"Active layout set to {layout_name}")
        else:
            raise ValueError("Specified layout does not exist.")

    def get_active_layout(self):
        """Returns the currently active layout."""
        if self.active_layout_name:
            return self.layouts[self.active_layout_name]
        else:
            raise ValueError("No active layout set.")

def moveMouse(x_delta, y_delta):
    current_pos = mouse.get_position
    new_pos = (current_pos[0] + x_delta, current_pos[1] + y_delta)
    mouse.move(new_pos)

def clickMouse(button='left', action='click'):
    btn = Button.left if button == 'left' else Button.right
    if action == 'click':
        mouse.click(btn)
    elif action == 'press':
        mouse.press(btn)
    elif action == 'release':
        mouse.release(btn)


def getPossibleCombos(currentCharacter):
    x = ""
    for i in currentCharacter:
        x += str(i)   
    possibleactions = []
    for action in normalmapping:
        if (len(action) >= len(x) and action[:len(x)] == x):
            possibleactions.append(action)
    logging.debug("possible: %s", str(possibleactions))


class Action (object):
    def __init__ (self, item):
        self.item = item
    def getlabel (self):
        return self.item.get('label', "")
    def perform (self):
        pass



class ActionLegacy (Action):

    def __init__(self, item, arg, label, key=None):
        super(ActionLegacy, self).__init__(item)  # Pass required parameters
        # Additional initialization for ActionLegacy
        self.arg = arg
        self.label = label
        self.key = key 
            
    def getlabel (self):
        return self.label
        

    def perform(self):
        action_map = {
            'MOUSEUP5': lambda: moveMouse(0, -5),
            'MOUSEDOWN5': lambda: moveMouse(0, 5),
            'MOUSELEFT5': lambda: moveMouse(-5, 0),
            'MOUSERIGHT5': lambda: moveMouse(5, 0),
            'MOUSEUPLEFT5': lambda: moveMouse(-5, -5),
            'MOUSEUPRIGHT5': lambda: moveMouse(5, -5),
            'MOUSEDOWNLEFT5': lambda: moveMouse(-5, 5),
            'MOUSEDOWNRIGHT5': lambda: moveMouse(5, 5),
            'MOUSEUP40': lambda: moveMouse(0, -40),
            'MOUSEDOWN40': lambda: moveMouse(0, 40),
            'MOUSELEFT40': lambda: moveMouse(-40, 0),
            'MOUSERIGHT40': lambda: moveMouse(40, 0),
            'MOUSEUPLEFT40': lambda: moveMouse(-40, -40),
            'MOUSEUPRIGHT40': lambda: moveMouse(40, -40),
            'MOUSEDOWNLEFT40': lambda: moveMouse(-40, 40),
            'MOUSEDOWNRIGHT40': lambda: moveMouse(40, 40),
            'MOUSEUP250': lambda: moveMouse(0, -250),
            'MOUSEDOWN250': lambda: moveMouse(0, 250),
            'MOUSELEFT250': lambda: moveMouse(-250, 0),
            'MOUSERIGHT250': lambda: moveMouse(250, 0),
            'MOUSEUPLEFT250': lambda: moveMouse(-250, -250),
            'MOUSEUPRIGHT250': lambda: moveMouse(250, -250),
            'MOUSEDOWNLEFT250': lambda: moveMouse(-250, 250),
            'MOUSEDOWNRIGHT250': lambda: moveMouse(250, 250),
            'MOUSECLICKLEFT': lambda: clickMouse(Button.left, 'click'),
            'MOUSECLICKRIGHT': lambda: clickMouse(Button.right, 'click'),
            'MOUSECLKHLDLEFT': lambda: clickMouse(Button.left, 'press'),
            'MOUSECLKHLDRIGHT': lambda: clickMouse(Button.right, 'press'),
            'MOUSERELEASEHOLD': lambda: clickMouse(Button.left, 'release'), # Assumes left button for example
            'REPEATMODE': self.handleRepeatMode
        }
    
        # Execute the mapped function based on self.key if exists
        if self.key and self.key in action_map:
            action_map[self.key]()
        else:
            logging.debug(f"[ActionLegacy-perform] No action defined for key: {self.key}")
    
    def handleRepeatMode(self):
        global repeaton
        if repeaton:
            if self.config.get('debug', False):
                logging.info("repeat OFF")
            repeaton = False
        else:
            if self.config.get('debug', False):
                logging.info("repeat ON")
            repeaton = True
    

class KeyStroke (object):
     def __init__(self, name, label, key, character):
        self.name = name
        self.label = label
        self.key = key
        self.character = character
        
class ActionKeyStroke(Action):
    def __init__(self, item, key, toggle_action=False):
        super(ActionKeyStroke, self).__init__(item)
        self.key = key  # Assuming 'key' contains both the key code and character information.
        self.label = item.get('label', item.get('action'))
        self.toggle_action = toggle_action

    @property
    def name(self):
        return self.key
    
    def getlabel(self):
        # Returns the label associated with this action, if any.
        return self.label

    def perform(self):
        logging.debug(f"[ActionKeyStroke] Key to press/release: {self.key}, type: {type(self.key)}")
        try:
            if self.toggle_action:
                current_state = get_keystroke_state(self.key)  # Ensure this function is properly defined.
                if current_state['down']:
                    keyboard.release(self.key)
                else:
                    keyboard.press(self.key)
            else:
                keyboard.press(self.key)
                keyboard.release(self.key)
                # Update typestate based on key action.
                if hasattr(self.key, 'character'):  # Ensure 'character' attribute exists.
                    if self.key.character == '\b':  # Assuming backspace is represented as '\b'.
                        typestate.popchar()
                    else:
                        typestate.pushchar(self.key.character)
        except Exception as e:
            logging.error(f"Error during key press/release: {e}")




class ChangeLayoutAction(Action):
    def __init__(self, item, window):
        super().__init__(item)
        self.window = window

    def perform(self):
        target_layout = self.item.get('target')
        if target_layout and target_layout in self.window.layoutManager.layouts:
            # Use the layout name to set the active layout
            self.window.layoutManager.set_active(target_layout)
        else:
            raise ValueError(f"Layout '{target_layout}' not found")

class PredictionSelectLayoutAction(Action):
    def __init__(self, item, get_predictions_func):
        super(PredictionSelectLayoutAction, self).__init__(item)
        self.get_predictions_func = get_predictions_func

    def getlabel(self):
        predictions = self.get_predictions_func()
        target = self.item.get('target', -1)
        if 0 <= target < len(predictions):
            return predictions[target]
        return ""

    def perform(self):
        if typestate is not None:
            target = self.item['target']
            predictions = typestate.getpredictions()
            if target >= 0 and target < len(predictions):
                pred = predictions[target]
                stripsuffix = ""
                for i in range(len(pred)):
                    idx = len(typestate.text) - i
                    if idx == 0 or (idx > 0 and typestate.text[idx - 1] in [" ", "\n", "\t", "\r"]):
                        stripsuffix = typestate.text[idx:]
                        break
                newchars = pred[len(stripsuffix):] + " "
                typestate.text = typestate.text[:len(typestate.text)-len(stripsuffix)] + newchars
                for char in newchars:
                    keyboard.press_and_release(char)  # This handles normal characters


class Window(QDialog):
    def __init__(self, layoutManager=None, configManager=None):
        super(Window, self).__init__()
        self.layoutManager = layoutManager
        self.configManager = configManager
        self.config = self.configManager.get_config()
        self.typestate = None 
        self.actions = {}
        self.keystrokes = []
        self.keystrokemap = {}
        logging.info(f"Window initialized with layout: {self.layoutManager.main_layout_name}")

        self.listenerThread = None
        self.currentCharacter = []
        self.lastKeyDownTime = None
        self.endCharacterTimer = None

    def load_default_config(self):
        return DEFAULT_CONFIG.copy()

    def init(self):
        self.currentCharacter = []
        self.repeaton = False 
        self.repeatkey = None
        logging.debug("Setting active layout to: %s", self.layoutManager.main_layout_name)
        self.layoutManager.set_active(self.layoutManager.main_layout_name)
        logging.debug("Active layout successfully set to: %s", self.layoutManager.active_layout_name)
        # Check for specific layout types that may require special handling
        if self.layoutManager.main_layout_name == 'typing':
            self.typestate = TypeState()  # Assuming TypeState is defined elsewhere
        else:
            self.typestate = None
        logging.debug(f"layout that is active is: {self.layoutManager.main_layout_name} ")
        self.codeslayoutview = CodesLayoutViewWidget(self.layoutManager.get_active_layout(), self.config)
        self.codeslayoutview.show()
       
    def postInit(self):
        # Initialize components that depend on actions being available
        self.actions = self.configManager.actions
        self.keystrokes = self.configManager.keystrokes
        self.keystrokemap = self.configManager.keystrokemap
        self.codeslayoutview = CodesLayoutViewWidget(self.layoutManager.get_active_layout(), self.config, self)
        self.createIconGroupBox()
        self.createActions()
        self.createTrayIcon()
        self.trayIcon.activated.connect(self.iconActivated)
        self.GOButton.clicked.connect(self.goForIt)
        self.SaveButton.clicked.connect(self.saveSettings)
        self.withSound.clicked.connect(self.updateAudioProperties)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.iconGroupBox)
        self.setLayout(mainLayout)
        self.setIcon()
        self.trayIcon.show()
        self.setWindowTitle("MorseWriter V2.1")
        self.resize(400, 300)

       
    def get_configured_keys(self):
        key_names = []
        if self.config.get('keylen', 1) >= 1:
            key_names.append(self.config.get('keyone', 'space'))  # Default to SPACE if not set
        if self.config.get('keylen', 1) >= 2:
            key_names.append(self.config.get('keytwo', 'enter'))  # Default to ENTER if not set
        if self.config.get('keylen', 1) == 3:
            key_names.append(self.config.get('keythree', 'right ctrl'))  # Default to RCTRL if not set
        return key_names
    
    
    def startKeyListener(self):
        key_names = self.get_configured_keys()  # this should return keys in the correct format already
        if not self.listenerThread:
            self.listenerThread = KeyListenerThread(configured_keys=key_names)
            self.listenerThread.keyEvent.connect(self.handle_key_event)
            self.listenerThread.start()
    
    def updateAudioProperties(self):
        if self.withSound.isChecked():
            self.iconComboBoxSoundDit.setEnabled(True)
            self.iconComboBoxSoundDah.setEnabled(True)
        else:
            self.iconComboBoxSoundDit.setEnabled(False)
            self.iconComboBoxSoundDah.setEnabled(False)
        
    def changeLayout(self, layout_name):
        # Check if the layout exists in the layoutManager by name
        if layout_name not in self.layoutManager.layouts:
            raise ValueError("Requested layout does not exist")
        
        # Use the layout name to set the active layout
        self.layoutManager.set_active(layout_name)
    
        # Retrieve the new layout object now that it's confirmed to exist and is active
        new_layout = self.layoutManager.layouts[layout_name]
    
        # Reinitialize the layout view widget
        if self.codeslayoutview:
            self.codeslayoutview.setParent(None)
            self.codeslayoutview.deleteLater()  # Properly delete the widget
        self.codeslayoutview = CodesLayoutViewWidget(new_layout, self.config, self)
        self.codeslayoutview.show()

    def getTypeStatePredictions(self):
        if self.typestate:
            return self.typestate.getpredictions()
        return []

    def collect_config(self):
        config = {
            'keylen': self.keySelectionRadioOneKey.isChecked() and 1 or \
                      self.keySelectionRadioTwoKey.isChecked() and 2 or 3,
            'keyone': self.iconComboBoxKeyOne.itemData(self.iconComboBoxKeyOne.currentIndex()),
            'keytwo': self.iconComboBoxKeyTwo.itemData(self.iconComboBoxKeyTwo.currentIndex()),
            'keythree': self.iconComboBoxKeyThree.itemData(self.iconComboBoxKeyThree.currentIndex()),
            'maxDitTime': float(self.maxDitTimeEdit.text()),
            'minLetterPause': float(self.minLetterPauseEdit.text()),
            'withsound': self.withSound.isChecked(),
            'SoundDit': self.iconComboBoxSoundDit.itemData(self.iconComboBoxSoundDit.currentIndex()),
            'SoundDah': self.iconComboBoxSoundDah.itemData(self.iconComboBoxSoundDah.currentIndex()),
            'debug': self.withDebug.isChecked(),
            'off': False,
            'fontsizescale': float(self.fontSizeScaleEdit.text()) / 100.0,
            'upperchars': self.upperCharsCheck.isChecked(),
            'autostart': self.autostartCheckbox.isChecked(),
            'winxaxis': "left" if self.keyWinPosXLeftRadio.isChecked() else "right",
            'winyaxis': "top" if self.keyWinPosYTopRadio.isChecked() else "bottom",
            'winposx': self.keyWinPosXEdit.text(),
            'winposy': self.keyWinPosYEdit.text()
        }
        return config

    def goForIt(self):
        if self.trayIcon.isVisible():
            QMessageBox.information(self, "MorseWriter",
                                    "The program will run in the system tray. To terminate the program, choose <b>Quit</b> in the context menu of the system tray entry.")
            self.hide()
        self.config = self.collect_config()
        self.init()  # Assume this initializes key listening etc
        self.startKeyListener()

    def closeEvent(self, event):
        self.stopIt()
        event.accept() 
        QApplication.instance().quit()
        
    def setIcon(self):
        icon = QIcon(':/morse-writer.ico')
        self.trayIcon.setIcon(icon)
        self.setWindowIcon(icon)

    def iconActivated(self, reason):
        #if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
        #     self.iconComboBox.setCurrentIndex((self.iconComboBox.currentIndex() + 1) % self.iconComboBox.count())
        if reason == QSystemTrayIcon.MiddleClick:
            self.showMessage()

    def showMessage(self):
        icon = QSystemTrayIcon.MessageIcon(self.typeComboBox.itemData(self.typeComboBox.currentIndex()))
        self.trayIcon.showMessage(self.titleEdit.text(), self.bodyEdit.toPlainText(), icon, self.durationSpinBox.value() * 1000)
        
    def mkKeyStrokeComboBox (self, items, currentkey, valuedict=None):
        box = QComboBox()
        for key, val in items:
            box.addItem(key, valuedict[val] if valuedict is not None else val)
        try:
            values = list(map(lambda a:valuedict[a[1]] if valuedict is not None else a[1], items))
            box.setCurrentIndex(values.index(currentkey))
        except ValueError:
            pass
        return box


    def createIconGroupBox(self):
        self.iconGroupBox = QGroupBox("Input Settings")
        
        self.keySelectionRadioOneKey = QRadioButton("One Key")
        self.keySelectionRadioTwoKey = QRadioButton("Two Key")
        self.keySelectionRadioThreeKey = QRadioButton("Three Key")
        
        inputSettingsLayout = QVBoxLayout()
        
        inputRadioGroup = QGroupBox("Number of keys")
        inputRadioButtonsLayout = QHBoxLayout()
        inputRadioButtonsLayout.addWidget(self.keySelectionRadioOneKey)
        inputRadioButtonsLayout.addWidget(self.keySelectionRadioTwoKey)
        inputRadioButtonsLayout.addWidget(self.keySelectionRadioThreeKey)
        inputRadioGroup.setLayout(inputRadioButtonsLayout)
        inputSettingsLayout.addWidget(inputRadioGroup)
        
        inputKeyComboBoxesLayout = QHBoxLayout()
         # Filter the keystrokes to only include those keys that are specified in morse_keys
        morse_keys = ["SPACE", "ENTER", "ONE", "TWO", "Z", "F8", "F9"]
        filtered_keystrokes = [(key, self.keystrokemap[key].label) for key in morse_keys if key in self.keystrokemap]

        
        # Set up the combo box for the first key using the filtered list
        self.iconComboBoxKeyOne = self.mkKeyStrokeComboBox(
            filtered_keystrokes,
            self.config.get('keyone')
        )
        
        # Repeat similar setup for other key selectors if necessary
        self.iconComboBoxKeyTwo = self.mkKeyStrokeComboBox(
            filtered_keystrokes,
            self.config.get('keytwo')
        )
        special_keys = ["RCTRL", "LCTRL", "RSHIFT", "LSHIFT", "ALT"]
        special_keystrokes = [(key, self.keystrokemap[key].label) for key in special_keys if key in self.keystrokemap]
    
        self.iconComboBoxKeyThree = self.mkKeyStrokeComboBox(
            special_keystrokes,
            self.config.get('keythree')
        )
        
        inputKeyComboBoxesLayout.addWidget(self.iconComboBoxKeyOne)
        inputKeyComboBoxesLayout.addWidget(self.iconComboBoxKeyTwo)
        inputKeyComboBoxesLayout.addWidget(self.iconComboBoxKeyThree)
        inputSettingsLayout.addLayout(inputKeyComboBoxesLayout)

        self.keySelectionRadioOneKey.toggled.connect(self.iconComboBoxKeyTwo.hide)
        self.keySelectionRadioOneKey.toggled.connect(self.iconComboBoxKeyThree.hide)
        self.keySelectionRadioTwoKey.toggled.connect(self.iconComboBoxKeyTwo.show)
        self.keySelectionRadioTwoKey.toggled.connect(self.iconComboBoxKeyThree.hide)
        self.keySelectionRadioThreeKey.toggled.connect(self.iconComboBoxKeyThree.show)
        self.keySelectionRadioThreeKey.toggled.connect(self.iconComboBoxKeyTwo.show)
        
        for index, name in [[1,'One'], [2,'Two'], [3,'Three']]: 
            getattr(self, 'keySelectionRadio%sKey'%(name)).setChecked(self.config.get('keylen', 1) == index)
        
        maxDitTimeLabel = QLabel("MaxDitTime (ms):")
        self.maxDitTimeEdit = QLineEdit(str(self.config.get("maxDitTime", "350")))
        minLetterPauseLabel = QLabel("minLetterPause (ms):")
        self.minLetterPauseEdit = QLineEdit(str(self.config.get("minLetterPause", "1000")))
        TimingsLayout = QGridLayout()
        TimingsLayout.addWidget(maxDitTimeLabel, 0, 0)
        TimingsLayout.addWidget(self.maxDitTimeEdit, 0, 1, 1, 4)
        TimingsLayout.addWidget(minLetterPauseLabel, 1, 0)
        TimingsLayout.addWidget(self.minLetterPauseEdit, 1, 1, 2, 4)
        TimingsLayout.setRowStretch(4, 1)
        inputSettingsLayout.addLayout(TimingsLayout)
        
        self.withDebug = QCheckBox("Debug On")
        self.withDebug.setChecked(self.config.get("debug", False))
        inputSettingsLayout.addWidget(self.withDebug)
        
        self.withSound = QCheckBox("Audible beeps")
        self.withSound.setChecked(self.config.get("withsound", True))
        inputSettingsLayout.addWidget(self.withSound)
        
        fontSizeScaleLabel = QLabel("FontSize (%):")
        self.fontSizeScaleEdit = QLineEdit(str(self.config.get("fontsizescale", "100")))
        viewSettingSec = QGridLayout()
        viewSettingSec.addWidget(fontSizeScaleLabel, 0, 0)
        viewSettingSec.addWidget(self.fontSizeScaleEdit, 0, 1, 1, 2)
        self.upperCharsCheck = QCheckBox("Upper case chars")
        self.upperCharsCheck.setChecked(self.config.get("upperchars", True))
        viewSettingSec.addWidget(self.upperCharsCheck, 0, 3)
        viewSettingSec.setRowStretch(4, 1)
        inputSettingsLayout.addLayout(viewSettingSec)

        self.iconComboBoxSoundDit = self.mkKeyStrokeComboBox([
                ["Dit Sound", "res/dit_sound.wav"],  # Ensure the path is correct
                ["Default", "res/dit_sound.wav"]  # Optional: default sound path
            ], self.config.get('SoundDit', "res/dit_sound.wav"))
        
        self.iconComboBoxSoundDah = self.mkKeyStrokeComboBox([
            ["Dah Sound", "res/dah_sound.wav"],  # Ensure the path is correct
            ["Default", "res/dah_sound.wav"]  # Optional: default sound path
        ], self.config.get('SoundDah', "res/dah_sound.wav"))

        DitSoundLabel = QLabel("Dit sound: ")
        DahSoundLabel = QLabel("Dah sound: ")
        SoundConfigLayout = QGridLayout()
        SoundConfigLayout.addWidget(DitSoundLabel, 0, 0)
        SoundConfigLayout.addWidget(self.iconComboBoxSoundDit, 0, 1, 1, 4)
        SoundConfigLayout.addWidget(DahSoundLabel, 1, 0)
        SoundConfigLayout.addWidget(self.iconComboBoxSoundDah, 1, 1, 1, 4)
        
        self.autostartCheckbox = QCheckBox("Auto-Start")
        self.autostartCheckbox.setChecked(self.config.get("autostart", True))
        inputSettingsLayout.addWidget(self.autostartCheckbox)
        
        inputSettingsLayout.addLayout(SoundConfigLayout)
        
        
        inputRadioGroup = QGroupBox("Align window horizontally from")
        posAxisLayout = QHBoxLayout()
        self.keyWinPosXLeftRadio = QRadioButton("Left")
        self.keyWinPosXRightRadio = QRadioButton("Right")
        if self.config.get("winxaxis", "left") == "left":
            self.keyWinPosXLeftRadio.setChecked(True)
        else:
            self.keyWinPosXRightRadio.setChecked(True)
        posAxisLayout.addWidget(self.keyWinPosXLeftRadio)
        posAxisLayout.addWidget(self.keyWinPosXRightRadio)
        self.keyWinPosXEdit = QLineEdit(self.config.get("winposx", "10"))
        inputRadioGroup.setLayout(posAxisLayout)
        inputSettingsLayout.addWidget(inputRadioGroup)
        inputSettingsLayout.addWidget(self.keyWinPosXEdit)

        inputRadioGroup = QGroupBox("Align window vertically from")
        posAxisLayout = QHBoxLayout()
        self.keyWinPosYTopRadio = QRadioButton("Top")
        self.keyWinPosYBottomRadio = QRadioButton("Bottom")
        if self.config.get("winyaxis", "top") == "top":
            self.keyWinPosYTopRadio.setChecked(True)
        else:
            self.keyWinPosYBottomRadio.setChecked(True)
        posAxisLayout.addWidget(self.keyWinPosYTopRadio)
        posAxisLayout.addWidget(self.keyWinPosYBottomRadio)
        self.keyWinPosYEdit = QLineEdit(self.config.get("winposy", "10"))
        inputRadioGroup.setLayout(posAxisLayout)
        inputSettingsLayout.addWidget(inputRadioGroup)
        inputSettingsLayout.addWidget(self.keyWinPosYEdit)
        
        self.SaveButton = QPushButton("Save Settings")
        self.GOButton = QPushButton("GO!")
        buttonsSec = QHBoxLayout()
        buttonsSec.addWidget(self.SaveButton)
        buttonsSec.addWidget(self.GOButton)
        inputSettingsLayout.addLayout(buttonsSec)
        
        self.iconGroupBox.setLayout(inputSettingsLayout)

    def saveSettings (self):
        config = self.collect_config()
        data = dict()
        data.update(config)
        saveConfig(configfile, data)
        
    def toggleOnOff(self):
        if self.config['off']:
            self.config['off'] = False
        else:
            self.config['off'] = True
    
    def stopIt(self):
        logging.debug("Stopping components...")
        if self.listenerThread is not None:
            self.listenerThread.stop()
            self.listenerThread.wait()
        if self.codeslayoutview is not None:
            self.codeslayoutview.hide()
            self.codeslayoutview = None
        logging.debug("All components stopped.")

    def backToSettings (self):
        self.showNormal()
        self.stopIt()
    
    def onOpenSettings (self):
        self.backToSettings()

    def createActions(self):
        self.onOffAction = QAction("OnOff", self, triggered=self.toggleOnOff)
        self.onOpenSettingsAction = QAction("Open Settings", self, triggered=self.onOpenSettings)
        self.quitAction = QAction("Quit", self, triggered=sys.exit)

    def createTrayIcon(self):
        self.trayIconMenu = QMenu(self)
        self.trayIconMenu.addAction(self.onOffAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.onOpenSettingsAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAction)
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)
        
    def handle_key_event(self, key, is_press):
        logging.debug(f"[handle_key_event] Event received: Key={key}, Pressed={is_press}")
        try:
            if is_press:
                self.on_press(key)
            else:
                self.on_release(key)
        except Exception as e:
            logging.warning(f"[handle_key_event] Error handling key event: {e}")
            

    def on_press(self, key):
        try:
            if self.lastKeyDownTime is None:  # Start timing the key press
                self.lastKeyDownTime = time.time()
            logging.debug(f"[on_press] Key pressed: {key}")
        except Exception as e:
            logging.warning(f"[on_press] Error on key press: {e}")
    
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
                logging.debug(f"[on_release] Key released: {key}, duration: {duration}ms")
        except Exception as e:
            logging.warning(f"[on_release] Error on key release: {e}")

    def addDit(self):
        self.currentCharacter.append(1)  # Assuming 1 represents Dit
        if self.config['withsound']:
            play("res/dit_sound.wav")   
        self.codeslayoutview.Dit()

    def addDah(self):
        self.currentCharacter.append(2)  # Assuming 2 represents Dah
        if self.config['withsound']:
            play("res/dah_sound.wav")
        self.codeslayoutview.Dah()

    def startEndCharacterTimer(self):
        if self.endCharacterTimer is not None:
            self.endCharacterTimer.stop()
        self.endCharacterTimer = QTimer()
        self.endCharacterTimer.setSingleShot(True)
        self.endCharacterTimer.timeout.connect(self.endCharacter)
        self.endCharacterTimer.start(int(self.config['minLetterPause']))

    def endCharacter(self):
        morse_code = "".join(map(str, self.currentCharacter)).upper()  # Convert to upper case to match action keys
    
        try:
            active_layout = self.layoutManager.get_active_layout()
            items = active_layout.get('items', [])
            item = next((item for item in items if item.get('code') == morse_code), None)
    
            if item and '_action' in item:
                action = item['_action']
                if action:
                    logging.debug(f"[endCharacter] Performing action for key: {action.key}, action type: {type(action)}")
                    action.perform()
                    logging.info(f"[endCharacter] Action performed for Morse code: {morse_code}")
                else:
                    logging.error(f"[endCharacter] Action defined but not executable for Morse code: {morse_code}")
            else:
                logging.error(f"[endCharacter] No action found for Morse code: {morse_code}")
        except Exception as e:
            logging.error(f"[endCharacter] Failed to perform action for Morse code: {morse_code}. Error: {str(e)}")
    
        self.currentCharacter = []



class CodeRepresentation(QWidget):
    def __init__(self, parent, code, item, c1, config):
        super(CodeRepresentation, self).__init__(None) 
        self.config = config
        #logging.debug("CodeRepresentation - Item: %s", item)
        #logging.debug("CodeRepresentation - Config: %s", config)
        vlayout = QVBoxLayout()
        self.item = item
        self.character = QLabel(self.item['_action'].getlabel())
        self.character.setGeometry(10, 10, 10, 10)
        self.character.setContentsMargins(0, 0, 0, 0)
        self.character.setAlignment(Qt.AlignTop)        
        self.codeline = QLabel() 
        self.codeline.setAlignment(Qt.AlignTop)
        self.codeline.setContentsMargins(0, 0, 0, 0)
        self.codeline.move(20, 30)
        self.code = self.codetocode(code)
        vlayout.setContentsMargins(5, 5, 5, 5)
        vlayout.addWidget(self.character)
        vlayout.addWidget(self.codeline)
        vlayout.setAlignment(self.character, Qt.AlignCenter)
        vlayout.setAlignment(self.codeline, Qt.AlignCenter)        
        self.setLayout(vlayout)
        self.setContentsMargins(0, 0, 0, 0)
     #   self.show()
        self.disabledchars = 0
        self.is_enabled = True
        self.character.setText(item['_action'].getlabel())
        self.toggled = False
        self.updateView()
        
    def item_label(self):
        action = self.item.get('_action')
        return action.getlabel() if action is not None else ""
    
    def codetocode(self, code):
        toReturn = code.replace('1', '.')
        toReturn = toReturn.replace('2', '-')
        return toReturn;
    
    def enable(self):
        self.is_enabled = True
        self.updateView()
        
    def disable(self):
        self.is_enabled = False
        self.updateView()
        
    def updateView (self):
        enabled = self.is_enabled
        codeselectrange = self.disabledchars if enabled  and self.disabledchars > 0 else 0
        self.character.setDisabled(not enabled)
        self.codeline.setDisabled(not enabled)
        charfontsize = int(3.0 * self.config['fontsizescale'])
        codefontsize = int(5.0 * self.config['fontsizescale'])
        toggled = self.toggled
        self.character.setText("<font style='background-color:{bgcolor};color:{color};font-weight:bold;' size='{fontsize}'>{text}</font>"
                               .format(color='blue' if enabled else 'lightgrey', 
                                       text=(self.item_label().upper() if self.config['upperchars'] else self.item_label()),
                                       fontsize=charfontsize, bgcolor="yellow" if toggled else "none"))
        self.codeline.setText("<font size='{fontsize}'><font color='green'>{selecttext}</font><font color='{color}'>{text}</font></font>"
                              .format(text=self.code[codeselectrange:], selecttext=self.code[:codeselectrange], 
                                      color='red' if enabled else 'lightgrey', fontsize=codefontsize))
        
        
    def enabled(self):
        return self.character.isEnabled()
    
    def reset(self):
        self.enable()
        self.disabledchars = -1
        self.tickDitDah()
    
    def Dit(self):
        logging.debug(f"[CodeRepresentation] Attempting Dit. Enabled: {self.is_enabled}, Disabled Chars: {self.disabledchars}, Code Length: {len(self.code)}")
        if (self.enabled()):
            if ((self.disabledchars < len(self.code)) and self.code[self.disabledchars] == '.'):
                self.tickDitDah()
                logging.debug("[CodeRepresentation] Dit successful.")
            else:
                self.disable()
                logging.debug("[CodeRepresentation] Dit failed - disabling.")

    def Dah(self):
        logging.debug(f"[CodeRepresentation] Attempting Dah. Enabled: {self.is_enabled}, Disabled Chars: {self.disabledchars}, Code Length: {len(self.code)}")
        if (self.enabled()):
            if ((self.disabledchars < len(self.code)) and self.code[self.disabledchars] == '-'):
                self.tickDitDah()
                logging.debug("[CodeRepresentation] Dah successful.")
            else:
                self.disable()
                logging.debug("[CodeRepresentation] Dah failed - disabling.")
    
    def tickDitDah(self):
        self.disabledchars += 1
        if (self.disabledchars > len(self.code)):
            self.is_enabled = False
        self.updateView()

class CodesLayoutViewWidget(QWidget):
    feedbackSignal = pyqtSignal()
    changeLayoutSignal = pyqtSignal()
    hideSignal = pyqtSignal()
    showSignal = pyqtSignal()
    
    
    def __init__(self, layout, config, parent=None):
        super(CodesLayoutViewWidget, self).__init__(parent)
        self.layout = layout
        self.config = config
        self.setupLayout(self.layout)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.adjustPosition()

    def onFeedback (self):
        for keyname in ("ALT", "SHIFT", "CTRL"):
            coderep = self.keystroke_crs_map.get(keyname, None)
            if coderep is not None:
                coderep.toggled = get_keystroke_state(keyname)['down']
                coderep.updateView()
        coderep = self.keystroke_crs_map.get("CAPSLOCK", None)
        if coderep is not None:
            key = coderep.item['_action'].key
            coderep.toggled = get_keystroke_state("CAPSLOCK")["locked"]# (state & 1) == 1
            coderep.updateView()
         

    def adjustPosition(self):
        #logging.debug("Current config: %s", self.config)
        ssize = QApplication.desktop().screenGeometry()
        size = self.frameSize()
        # Explicit conversion to int to ensure no float values slip through
        x = int(self.config['winposx'])
        y = int(self.config['winposy'])
    
        if self.config['winxaxis'] == 'left':
            x_position = x
        else:
            x_position = ssize.width() - size.width() - x
    
        if self.config['winyaxis'] == 'top':
            y_position = y
        else:
            y_position = ssize.height() - size.height() - y
    
        self.move(x_position, y_position)

    def setupLayout(self, layout):
        self.vlayout = QVBoxLayout()
        self.setLayout(self.vlayout)
        hlayout = QHBoxLayout()
        hlayout.setContentsMargins(0, 0, 0, 0)
        self.vlayout.addLayout(hlayout)
    
        self.keystroke_crs_map = {}
        self.crs = {}
        x = 0
        perrow = layout['column_len']
    
        for item in layout['items']:
            logging.debug(f"LAYOUT Item: {item}")
            if 'emptyspace' not in item or not item['emptyspace']:
                coderep = CodeRepresentation(None, item['code'], item, "Green", self.config)
                # Check if '_action' is an instance of ActionKeyStroke
                if isinstance(item['_action'], ActionKeyStroke):
                    # Use the .name property from ActionKeyStroke
                    label = item['_action'].label 
                    key_name = item['_action'].name
                    self.keystroke_crs_map[key_name] = coderep
                self.crs[item['code']] = coderep
                hlayout.addWidget(coderep)
            x += 1
            if x >= perrow:
                x = 0
                hlayout = QHBoxLayout()
                hlayout.setContentsMargins(0, 0, 0, 0)
                self.vlayout.addLayout(hlayout)

    
    def Dit(self):
        for item in self.crs.values():
            item.Dit()

    def Dah(self):
        for item in self.crs.values():
            item.Dah()
            
    def reset(self):
        for item in self.crs.values():
            item.reset()
            
    def closeEvent(self, event):
        window.backToSettings()
    
def get_keystroke_state(name):
    state = {
        "down": keyboard.is_pressed(name)
    }
    # Special case handling for CAPS LOCK which needs to check toggle state
    if name.lower() == "capslock":
        state["locked"] = keyboard.is_pressed('caps lock')
    return state


class CustomApplication(QApplication):
    def notify(self, receiver, event):
        #logging.debug(f"Event: {event.type()}, Receiver: {receiver.__class__.__name__}")
        return super().notify(receiver, event)


if __name__ == '__main__':
    app = CustomApplication(sys.argv)
    
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "MorseWriter", "I couldn't detect any system tray on this system.")
        sys.exit(1)
    
    QApplication.setQuitOnLastWindowClosed(False)

    # Initialize managers
    configmanager = ConfigManager(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.json"), default_config=DEFAULT_CONFIG)
    layoutmanager = LayoutManager(os.path.join(os.path.dirname(os.path.realpath(__file__)), "layouts.json"))

    # Create main window
    window = Window(layoutManager=layoutmanager, configManager=configmanager)

    # Now that we have the window, initialize actions that may require window reference
    actions = configmanager.initActions(window)
    layoutmanager.set_actions(actions)

    # Finish initializing the window if needed (after actions are available)
    window.postInit()

    # Show or hide the window based on the configuration
    if configmanager.config.get("autostart", False):
        window.hide()
    else:
        window.show()

    # Start the application event loop
    sys.exit(app.exec_())
