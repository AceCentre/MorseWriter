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
from pynput.keyboard import Controller as KeyboardController, Listener, Key, KeyCode
from pynput.mouse import Controller as MouseController, Button
from nava import play

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

mouse_controller = MouseController()
keyboard_controller = KeyboardController()
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
            "A": ('a', KeyCode.from_char('a'), 'a', None),
            "B": ('b', KeyCode.from_char('b'), 'b', None),
            "C": ('c', KeyCode.from_char('c'), 'c', None),
            "D": ('d', KeyCode.from_char('d'), 'd', None),
            "E": ('e', KeyCode.from_char('e'), 'e', None),
            "F": ('f', KeyCode.from_char('f'), 'f', None),
            "G": ('g', KeyCode.from_char('g'), 'g', None),
            "H": ('h', KeyCode.from_char('h'), 'h', None),
            "I": ('i', KeyCode.from_char('i'), 'i', None),
            "J": ('j', KeyCode.from_char('j'), 'j', None),
            "K": ('k', KeyCode.from_char('k'), 'k', None),
            "L": ('l', KeyCode.from_char('l'), 'l', None),
            "M": ('m', KeyCode.from_char('m'), 'm', None),
            "N": ('n', KeyCode.from_char('n'), 'n', None),
            "O": ('o', KeyCode.from_char('o'), 'o', None),
            "P": ('p', KeyCode.from_char('p'), 'p', None),
            "Q": ('q', KeyCode.from_char('q'), 'q', None),
            "R": ('r', KeyCode.from_char('r'), 'r', None),
            "S": ('s', KeyCode.from_char('s'), 's', None),
            "T": ('t', KeyCode.from_char('t'), 't', None),
            "U": ('u', KeyCode.from_char('u'), 'u', None),
            "V": ('v', KeyCode.from_char('v'), 'v', None),
            "W": ('w', KeyCode.from_char('w'), 'w', None),
            "X": ('x', KeyCode.from_char('x'), 'x', None),
            "Y": ('y', KeyCode.from_char('y'), 'y', None),
            "Z": ('z', KeyCode.from_char('z'), 'z', None),
            "ONE": ('1', KeyCode.from_char('1'), '1', None),
            "TWO": ('2', KeyCode.from_char('2'), '2', None),
            "THREE": ('3', KeyCode.from_char('3'), '3', None),
            "FOUR": ('4', KeyCode.from_char('4'), '4', None),
            "FIVE": ('5', KeyCode.from_char('5'), '5', None),
            "SIX": ('6', KeyCode.from_char('6'), '6', None),
            "SEVEN": ('7', KeyCode.from_char('7'), '7', None),
            "EIGHT": ('8', KeyCode.from_char('8'), '8', None),
            "NINE": ('9', KeyCode.from_char('9'), '9', None),
            "ZERO": ('0', KeyCode.from_char('0'), '0', None),
            "DOT": ('.', KeyCode.from_char('.'), '.', None),
            "COMMA": (',', KeyCode.from_char(','), ',', None),
            "QUESTION": ('?', KeyCode.from_char('/'), '?', None),
            "EXCLAMATION": ('!', KeyCode.from_char('1'), '!', None),
            "COLON": (':', KeyCode.from_char(';'), ':', None),
            "SEMICOLON": (';', KeyCode.from_char(';'), ';', None),
            "AT": ('@', KeyCode.from_char('2'), '@', None),
            "HASH": ('#', KeyCode.from_char('3'), '#', None),
            "DOLLAR": ('$', KeyCode.from_char('4'), '$', None),
            "PERCENT": ('%', KeyCode.from_char('5'), '%', None),
            "AMPERSAND": ('&', KeyCode.from_char('7'), '&', None),
            "STAR": ('*', KeyCode.from_char('*'), '*', None),
            "PLUS": ('+', KeyCode.from_char('='), '+', None),
            "MINUS": ('-', KeyCode.from_char('-'), '-', None),
            "EQUALS": ('=', KeyCode.from_char('='), '=', None),
            "FSLASH": ('/', KeyCode.from_char('/'), '/', None),
            "BSLASH": ('\\', KeyCode.from_char('\\'), '\\', None),
            "SINGLEQUOTE": ("'", KeyCode.from_char("'"), "'", None),
            "DOUBLEQUOTE": ('"', KeyCode.from_char('"'), '"', None),
            "OPENBRACKET": ('(', KeyCode.from_char('9'), '(', None),
            "CLOSEBRACKET": (')', KeyCode.from_char('0'), ')', None),
            "LESSTHAN": ('<', KeyCode.from_char(','), '<', None),
            "MORETHAN": ('>', KeyCode.from_char('.'), '>', None),
            "CIRCONFLEX": ('^', KeyCode.from_char('6'), '^', None),
            "ENTER": ('ENTER', KeyCode.from_char('Key.enter'), '\n', None),
            "SPACE": ('space', KeyCode.from_char('Key.space'), ' ', None),
            "BACKSPACE": ('bckspc', KeyCode.from_char('Key.backspace'), '\x08', None),
            "TAB": ('tab', KeyCode.from_char('Key.tab'), '\t', None),
            "PAGEUP": ('pageup', KeyCode.from_char('Key.page_up'), None, None),
            "PAGEDOWN": ('pagedwn', KeyCode.from_char('Key.page_down'), None, None),
            "LEFTARROW": ('left', KeyCode.from_char('Key.left'), None, None),
            "RIGHTARROW": ('right', KeyCode.from_char('Key.right'), None, None),
            "UPARROW": ('up', KeyCode.from_char('Key.up'), None, None),
            "DOWNARROW": ('down', KeyCode.from_char('Key.down'), None, None),
            "ESCAPE": ('esc', KeyCode.from_char('Key.esc'), None, None),
            "HOME": ('home', KeyCode.from_char('Key.home'), None, None),
            "END": ('end', KeyCode.from_char('Key.end'), None, None),
            "DELETE": ('del', KeyCode.from_char('Key.delete'), None, None),
            "SHIFT": ('shift', KeyCode.from_char('Key.shift'), None, None),
            "RSHIFT": ('rshift', KeyCode.from_char('Key.rshift'), None, None),
            "LSHIFT": ('lshift', KeyCode.from_char('Key.lshift'), None, None),
            "CTRL": ('ctrl', KeyCode.from_char('Key.ctrl'), None, None),
            "RCTRL": ('rctrl', KeyCode.from_char('Key.rctrl'), None, None),
            "LCTRL": ('lctrl', KeyCode.from_char('Key.lctrl'), None, None),
            "ALT": ('alt', KeyCode.from_char('Key.alt'), None, None),
            "WINDOWS": ('win', KeyCode.from_char('Key.cmd'), None, None),
            "CAPSLOCK": ('caps', KeyCode.from_char('Key.caps_lock'), None, None),
            "F1": ('F1', KeyCode.from_char('Key.f1'), None, None),
            "F2": ('F2', KeyCode.from_char('Key.f2'), None, None),
            "F3": ('F3', KeyCode.from_char('Key.f3'), None, None),
            "F4": ('F4', KeyCode.from_char('Key.f4'), None, None),
            "F5": ('F5', KeyCode.from_char('Key.f5'), None, None),
            "F6": ('F6', KeyCode.from_char('Key.f6'), None, None),
            "F7": ('F7', KeyCode.from_char('Key.f7'), None, None),
            "F8": ('F8', KeyCode.from_char('Key.f8'), None, None),
            "F9": ('F9', KeyCode.from_char('Key.f9'), None, None),
            "F10": ('F10', KeyCode.from_char('Key.f10'), None, None),
            "F11": ('F11', KeyCode.from_char('Key.f11'), None, None),
            "F12": ('F12', KeyCode.from_char('Key.f12'), None, None),
            "REPEATMODE": ('repeat', None, None, 0),
            "SOUND": ('snd', None, None, 8),
            "CODESET": ('code', None, None, 9),
            "MOUSERIGHT5": ('ms right 5', None, None, 2),
            "MOUSEUP5": ('ms up 5', None, None, 3),
            "MOUSECLICKLEFT": ('ms clkleft', None, None, 4),
            "MOUSEDBLCLICKLEFT": ('ms dblclkleft', None, None, 5),
            "MOUSECLKHLDLEFT": ('ms hldleft', None, None, 6),
            "MOUSEUPLEFT5": ('ms leftup 5', None, None, 7),
            "MOUSEDOWNLEFT5": ('ms leftdown 5', None, None, 8),
            "MOUSERELEASEHOLD": ('ms release', None, None, 9),
            "MOUSELEFT5": ('ms left 5', None, None, 0),
            "MOUSEDOWN5": ('ms down 5', None, None, 1),
            "MOUSECLICKRIGHT": ('ms clkright', None, None, 2),
            "MOUSEDBLCLICKRIGHT": ('ms dblclkright', None, None, 3),
            "MOUSECLKHLDRIGHT": ('ms hldright', None, None, 4),
            "MOUSEUPRIGHT5": ('ms rightup 5', None, None, 5),
            "MOUSEDOWNRIGHT5": ('ms rightdown 5', None, None, 6),
            "NORMALMODE": ('normal mode', None, None, 7),
            "MOUSEUP40": ('ms up 40', None, None, 8),
            "MOUSEUP250": ('ms up 250', None, None, 9),
            "MOUSEDOWN40": ('ms down 40', None, None, 0),
            "MOUSEDOWN250": ('ms down 250', None, None, 1),
            "MOUSELEFT40": ('ms left 40', None, None, 2),
            "MOUSELEFT250": ('ms left 250', None, None, 3),
            "MOUSERIGHT40": ('ms right 40', None, None, 4),
            "MOUSERIGHT250": ('ms right 250', None, None, 5),
            "MOUSEUPLEFT40": ('ms leftup 40', None, None, 6),
            "MOUSEUPLEFT250": ('ms leftup 250', None, None, 7),
            "MOUSEDOWNLEFT40": ('ms leftdown 40', None, None, 8),
            "MOUSEDOWNLEFT250": ('ms leftdown 250', None, None, 9),
            "MOUSEUPRIGHT40": ('ms rightup 40', None, None, 0),
            "MOUSEUPRIGHT250": ('ms rightup 250', None, None, 1),
            "MOUSEDOWNRIGHT40": ('ms rightdown 40', None, None, 2),
            "MOUSEDOWNRIGHT250": ('ms rightdown 250', None, None, 3)
        }
        self.config_file = config_file
        self.default_config = default_config
        self.keystrokemap, self.keystrokes = self.initKeystrokeMap()
        self.config = self.read_config()
        self.actions = {}

    def initKeystrokeMap(self):
        keystrokemap = {}
        keystrokes = []
        for key, (label, key_code, character, arg) in self.key_data.items():
            stroke = KeyStroke(key, label, key_code, character)
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
        for key, (label, key_code, character, arg) in self.key_data.items():
            # Pass current loop variables as default values to ensure correct capturing
            actions[key] = (lambda item, label=label, key_code=key_code, arg=arg: 
                            ActionLegacy(item=item, arg=arg, label=label, key=key_code))
    
        # Define special actions, making sure to correctly handle lambda capturing
        actions["CHANGELAYOUT"] = lambda item, window=window: ChangeLayoutAction(item, window)
        #actions["PREDICTION_SELECT"] = lambda item: PredictionSelectLayoutAction(item)
        actions["PREDICTION_SELECT"] = lambda item, window=window: PredictionSelectLayoutAction(
                item, get_predictions_func=window.getTypeStatePredictions)
        actions["KEYSTROKE"] = lambda item, key_data=self.key_data: ActionKeyStroke(item, key_data[item['action']])
    
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
        if self.predictions is None:
            try:
                self.predictions = self.presage.predict()
            except Exception as e:
                logging.error(f"Failed to generate predictions: {str(e)}")
                self.predictions = []
        return self.predictions


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
    current_pos = mouse_controller.position
    new_pos = (current_pos[0] + x_delta, current_pos[1] + y_delta)
    mouse_controller.position = new_pos

def clickMouse(button='left', action='click'):
    btn = Button.left if button == 'left' else Button.right
    if action == 'click':
        mouse_controller.click(btn)
    elif action == 'press':
        mouse_controller.press(btn)
    elif action == 'release':
        mouse_controller.release(btn)


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
            logging.debug(f"No action defined for key: {self.key}")
    
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
        self.key = get_pynput_key(key)  # Ensure this is a pynput compatible key
        self.toggle_action = toggle_action

    def perform(self):
        if self.toggle_action:
            current_state = getKeyStrokeState(self.key)  # Define this function based on your app's logic
            if current_state['down']:
                keyboard_controller.release(self.key)
            else:
                keyboard_controller.press(self.key)
        else:
            keyboard_controller.press(self.key)
            keyboard_controller.release(self.key)


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
                    # Use pynput to type characters instead of win32api
                    keyboard_controller.type(char)  # This handles normal characters


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
        morse_keys = ["SPACE", "ENTER", "ONE", "TWO", "Z", "X", "F8", "F9"]
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
        # Find the corresponding item based on morse_code using the refactored LayoutManager
        try:
            active_layout = self.layoutManager.get_active_layout()
            items = active_layout.get('items', [])
            item = next((item for item in items if item.get('code') == morse_code), None)
            
            if item and '_action' in item:
                action = item['_action']  # Ensure the action is retrieved correctly
                if action:  # Check if action is not None
                    action.perform()
                logging.info(f"Action performed for morse code: {morse_code}")
            else:
                logging.info(f"No action found for the given morse code: {morse_code}")
        except Exception as e:
            logging.error(f"Failed to perform action for morse code: {morse_code}. Error: {str(e)}")
    
        self.currentCharacter = []



class CodeRepresentation(QWidget):
    def __init__(self, parent, code, item, c1, config):
        super(CodeRepresentation, self).__init__(None) 
        self.config = config
        #logging.debug("CodeRepresentation - Item: %s", item)
        #logging.debug("CodeRepresentation - Config: %s", config)
        vlayout = QVBoxLayout()
        self.item = item
        self.character = QLabel()
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
        if (self.enabled()):
            if ((self.disabledchars < len(self.code)) and self.code[self.disabledchars] == '.'):
                self.tickDitDah()
            else:
                self.disable()

    def Dah(self):
        if (self.enabled()):
            if ((self.disabledchars < len(self.code)) and self.code[self.disabledchars] == '-'):
                self.tickDitDah()
            else:
                self.disable()
    
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
                coderep.toggled = getKeyStrokeState(keyname)['down']
                coderep.updateView()
        coderep = self.keystroke_crs_map.get("CAPSLOCK", None)
        if coderep is not None:
            key = coderep.item['_action'].key
            coderep.toggled = getKeyStrokeState("CAPSLOCK")["locked"]# (state & 1) == 1
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
                coderep = CodeRepresentation(None, item['code'], item, "Green",self.config)
                if isinstance(item['_action'], ActionKeyStroke):
                    self.keystroke_crs_map[item['_action'].key.name] = coderep
                self.crs[item['code']] = coderep
                hlayout.addWidget(coderep)
            x += 1
            if x > perrow:
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