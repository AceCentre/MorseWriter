#!/usr/bin/env pythone

# This is only needed for Python v2 but is harmless for Python v3.
#import sip
#sip.setapi('QVariant', 1)
import sys
import threading
import icons_rc
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Key, KeyCode
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QWidget, QApplication, QSystemTrayIcon, QGroupBox, QRadioButton, \
  QMessageBox, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QLineEdit, QGridLayout, QCheckBox, QPushButton, QAction, \
  QMenu
import json
import os
import configparser
import pressagio.callback
import pressagio
from enum import Enum
from collections import OrderedDict


from nava import play

lastkeydowntime = -1


pressagioconfig_file= os.path.join(os.path.dirname(os.path.realpath(__file__)), "morsewriter_pressagio.ini")
pressagioconfig = configparser.ConfigParser()
pressagioconfig.read(pressagioconfig_file)

mouse_controller = MouseController()
keyboard_controller = KeyboardController()

keystrokes_state = {}
disabled = False

currentX = 0
currentY = 0

pressingKey = False

layoutmanager = None
codeslayoutview = None
typestate = None

hm = None

configfile = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.json"))

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
        self.presage = pressagio.Pressagio(self, config)
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
            self.predictions = self.prsgio.predict()

        return self.predictions

class LayoutManager:
    def __init__(self, fn, actions):
        self.actions = actions
        with open(fn, "r") as f:
            data = json.load(f)
        self.layouts = {k: self._layout_import(v) for k, v in data['layouts'].items()}
        self.active = self.layouts.get(data['mainlayout'], None)
        self.mainlayout = self.active
        self.mainlayoutname = data['mainlayout']

    def _layout_import(self, layout):
        for item in layout['items']:
            action_name = item.get('action')
            if action_name in self.actions:
                action_class, *args = self.actions[action_name]
                item['_action'] = action_class(item, *args)  # Correct args based on action class constructor
            else:
                item['_action'] = None
        return OrderedDict((a['code'], a) for a in layout['items'])
    
    def set_active(self, layout):
        """Sets the active layout."""
        if layout in self.layouts:
            self.active = self.layouts[layout]
        else:
            raise ValueError("Layout not found: " + layout)


def moveMouse(x_delta, y_delta):
    current_pos = mouse_controller.position
    new_pos = (current_pos[0] + x_delta, current_pos[1] + y_delta)
    mouse_controller.position = new_pos

def clickMouse(button='left', action='click'):
    from pynput.mouse import Button
    btn = Button.left if button == 'left' else Button.right
    if action == 'click':
        mouse_controller.click(btn)
    elif action == 'press':
        mouse_controller.press(btn)
    elif action == 'release':
        mouse_controller.release(btn)


def PressKey(down, key):
    global pressingKey
    pressingKey = True
    if myConfig['debug']:
        print("presskey: ", key, "down" if down else "up")
    
    try:
        # Using pynput to press and release keys
        if down:
            keyboard_controller.press(key)
        else:
            keyboard_controller.release(key)
    finally:
        pressingKey = False

def TypeKey(key, keystroke_time=10):
    PressKey(True, key)
    # Delay between press and release
    time.sleep(keystroke_time / 1000)  # Convert milliseconds to seconds
    PressKey(False, key)
    if myConfig['debug']:
        print("typekey: ", key)

def endCharacter():
    if myConfig['debug']:
        print("End Character")
    global currentCharacter, hm, repeaton, repeatkey, currentX, currentY
    morse = "".join(map(str, currentCharacter))
    item = layoutmanager.active['items'].get(morse, None)
    action = None if item is None else item['_action']
    if myConfig['debug']:
        print("action: ", action)
    if action is not None:
        action.perform()
    currentCharacter = []
    codeslayoutview.reset()


def disableKeyUpDown(event):
    if pressingKey:
        updateKeyboardState(event)
        onKeyboardEvent(event)
        return True
    return False

def on_release(key):
    global lastkeydowntime, MyEvents, currentCharacter, endCharacterTimer, hm, disabled
    try:
        # Check if key has a char attribute
        if hasattr(key, 'char') and key.char:
            key_char = key.char
        else:
            # This covers cases like Key.space where key.char is None
            key_char = key.name
    except AttributeError:
        # Fallback if neither char nor name is present (unlikely)
        key_char = str(key)


def addDit():
    currentCharacter.append(MyEvents.DIT.value)
    if (myConfig['withsound']):
        # Original: winsound.Beep(int(myConfig['SoundDitFrequency']), int(myConfig['SoundDitDuration']))
        play("dit_sound.wav")  # assuming you have a 'dit_sound.wav' file
    codeslayoutview.Dit()

def addDah():
    currentCharacter.append(MyEvents.DAH.value)
    if (myConfig['withsound']):
        # Original: winsound.Beep(int(myConfig['SoundDahFrequency']), int(myConfig['SoundDahDuration']))
        play("dah_sound.wav")  # assuming you have a 'dah_sound.wav' file
    codeslayoutview.Dah()
    
def getPossibleCombos(currentCharacter):
    x = ""
    for i in currentCharacter:
        x += str(i)   
    possibleactions = []
    for action in normalmapping:
        if (len(action) >= len(x) and action[:len(x)] == x):
            possibleactions.append(action)
    print("possible: " + str(possibleactions))

def newConfig ():
    return {}

def saveConfig (configfile, config):
    data = dict()
    data.update(config)
    for name in ['keyone', 'keytwo', 'keythree']:
        if name in data:
            data[name] = data[name].name
    with open(configfile, "w") as f:
        f.write(json.dumps(data, indent=2))

def readConfig (configfile):
    with open(configfile, "r") as f:
        data = json.loads(f.read())
        for name in ['keyone', 'keytwo', 'keythree']:
            if name in data:
                data[name] = keystrokemap[data[name]]
        return data
    
class Action (object):
    def __init__ (self, item):
        self.item = item
    def getlabel (self):
        return self.item['label'] if 'label' in self.item else ""
    def perform (self):
        pass



class ActionLegacy (Action):

    def __init__(self, item, arg, label):
        super(ActionLegacy, self).__init__(item)  # Pass required parameters
        # Additional initialization for ActionLegacy
        self.arg = arg
        self.label = label
            
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
        if self.key in action_map:
            action_map[self.key]()
    
    def handleRepeatMode(self):
        global repeaton, myConfig
        if repeaton:
            if myConfig.get('debug', False):
                print("repeat OFF")
            repeaton = False
        else:
            if myConfig.get('debug', False):
                print("repeat ON")
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

class ChangeLayoutAction (Action):
    def perform (self):
        global typestate
        if 'target' not in self.item or self.item['target'] not in layoutmanager.layouts:
            raise AssertionError("target({}) not found".format(self.item.get('target', "")))
        # special case for `typing` target
        if self.item['target'] == 'typing':
            typestate = TypeState()
        else:
            typestate = None
        layoutmanager.set_active(layoutmanager.layouts[self.item['target']])
        codeslayoutview.changeLayoutSignal.emit()

class PredictionSelectLayoutAction (Action):
    def __init__(self, item, *args):
        pass  # handle initialization here; `args` can be ignored if not needed

    def getlabel (self):
        if typestate != None:
            target = self.item['target']
            predictions = typestate.getpredictions()
            if target >= 0 and target < len(predictions):
                return predictions[target]
        return ""
    def perform (self):
        if typestate != None:
            target = self.item['target']
            predictions = typestate.getpredictions()
            if target >= 0 and target < len(predictions):
                pred = predictions[target]
                plen = len(pred)
                print("PRED", predictions)
                if plen > 0:
                    stripsuffix = ""
                    for i in range(plen):
                        idx = len(typestate.text) - i
                        if idx == 0 or (idx > 0 and typestate.text[idx - 1] in [" ", "\n", "\t", "\r"]):
                            stripsuffix = typestate.text[idx:]
                            break
                    newchars = pred[len(stripsuffix):] + " "
                    typestate.text = typestate.text[:len(typestate.text)-len(stripsuffix)] + newchars
                    for char in newchars:
                        keys = tuple(filter(lambda a: a.character == char, keystrokes))
                        if len(keys) == 0:
                            break
                        if ord(keys[0].character) == 8 and len(typestate.text) == 0: # special case
                            continue
                        TypeKey(keys[0].keywin32)
                        

def initActions():
    global actions, keystrokes, keystrokemap
    # List of key definitions: (Key name, label, pynput key, character (if any)
    actions = {}
    key_data = {
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

    keystrokes = []
    action_counter = 0
    for name, (label, key_code, character, extra) in key_data.items():
        keystrokes.append(KeyStroke(name, label, key_code, character))
        actions[name] = (ActionLegacy, None, label)  # Adjust accordingly
        action_counter += 1

    actions.update({
        "CHANGELAYOUT": (ChangeLayoutAction,),
        "PREDICTION_SELECT": (PredictionSelectLayoutAction,)
    })
    keystrokemap = {stroke.name: stroke for stroke in keystrokes}

    # Optionally create an Enum for just referencing names
    #ActionsEnum = Enum('Actions', {name: i for i, name in enumerate(actions.keys())})



def Init():
    global MyEvents, currentCharacter, hm, repeaton, repeatkey, codeslayoutview, typestate
    MyEvents = Enum('DITDAH', [('DIT', 1), ('DAH', 2)])
    currentCharacter = []
    repeaton = False 
    repeatkey = None
    layoutmanager.set_active(layoutmanager.mainlayout)
    # special case for `typing` target
    if layoutmanager.mainlayoutname == 'typing':
        typestate = TypeState()
    else:
        typestate = None
    codeslayoutview = CodesLayoutViewWidget(layoutmanager.active)

def Go():
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    listener.join()


class Window(QDialog):
    def __init__(self):
        super(Window, self).__init__()

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

    def updateAudioProperties(self):
        if self.withSound.isChecked():
            self.iconComboBoxSoundDit.setEnabled(True)
            self.iconComboBoxSoundDah.setEnabled(True)
        else:
            self.iconComboBoxSoundDit.setEnabled(False)
            self.iconComboBoxSoundDah.setEnabled(False)

    def start (self, config):
        global myConfig
        myConfig = dict()
        myConfig.update(config)
        myConfig['fontsizescale'] = int(config['fontsizescale']) / 100.0
        Init()
        Go()

    def collectConfig (self):
        config = dict();
        config['keylen'] = 1 if self.keySelectionRadioOneKey.isChecked() else \
            2 if self.keySelectionRadioTwoKey.isChecked() else \
            3 if self.keySelectionRadioThreeKey.isChecked() else 1
        config['keyone'] = self.iconComboBoxKeyOne.itemData(self.iconComboBoxKeyOne.currentIndex())
        config['keytwo'] = self.iconComboBoxKeyTwo.itemData(self.iconComboBoxKeyTwo.currentIndex())
        config['keythree'] = self.iconComboBoxKeyThree.itemData(self.iconComboBoxKeyThree.currentIndex())
        config['maxDitTime'] = self.maxDitTimeEdit.text()
        config['minLetterPause'] = self.minLetterPauseEdit.text()
        config['withsound'] = self.withSound.isChecked() 
        config['SoundDit'] = self.iconComboBoxSoundDit.itemData(self.iconComboBoxSoundDit.currentIndex())
        config['SoundDah'] = self.iconComboBoxSoundDah.itemData(self.iconComboBoxSoundDah.currentIndex())
        config['debug'] = self.withDebug.isChecked()
        config['off'] = False
        config['fontsizescale'] = self.fontSizeScaleEdit.text()
        config['upperchars'] = self.upperCharsCheck.isChecked()
        config['autostart'] = self.autostartCheckbox.isChecked()
        config['winxaxis'] = "left" if self.keyWinPosXLeftRadio.isChecked() else "right"
        config['winyaxis'] = "top" if self.keyWinPosYTopRadio.isChecked() else "bottom"
        config['winposx'] = self.keyWinPosXEdit.text()
        config['winposy'] = self.keyWinPosYEdit.text()
        return config

    def goForIt(self):
        global myConfig
        if self.trayIcon.isVisible():
            QMessageBox.information(self, "MorseWriter", "The program will run in the system tray. To terminate the program, choose <b>Quit</b> in the context menu of the system tray entry.")
            self.hide()
        myConfig = self.collectConfig()
        myConfig['fontsizescale'] = int(myConfig['fontsizescale']) / 100.0
        if myConfig['debug']:
            print("Config: " + str(myConfig['keylen']) + " / " + str(myConfig['keyone']) + " / " + str(myConfig['keytwo']) + " / " + str(myConfig['keythree']) + " / " + str(myConfig['maxDitTime']) + " / " + str(myConfig['minLetterPause']))
        Init()
        Go()

    def closeEvent(self, event):
        app.quit
        sys.exit()
        
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
        self.iconComboBoxKeyOne = self.mkKeyStrokeComboBox(
            list(map(lambda a:(a,a),["SPACE", "ENTER", "ONE", "TWO", "Z", "X", "F8", "F9"])),
            myConfig.get('keyone', None), keystrokemap
        )
        self.iconComboBoxKeyTwo = self.mkKeyStrokeComboBox(
            list(map(lambda a:(a,a),["ENTER", "ONE", "TWO", "Z", "F8"])),
            myConfig.get('keytwo', None), keystrokemap
        )
        self.iconComboBoxKeyThree = self.mkKeyStrokeComboBox(
            [ ["Right Ctrl", "RCTRL"], ["Left Ctrl", "LCTRL"], ["Right Shift", "RSHIFT"],
              ["Left Shift", "LSHIFT"], ["Alt", "ALT"] ],
            myConfig.get('keythree', None), keystrokemap
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
            getattr(self, 'keySelectionRadio%sKey'%(name)).setChecked(myConfig.get('keylen', 1) == index)
        
        maxDitTimeLabel = QLabel("MaxDitTime (ms):")
        self.maxDitTimeEdit = QLineEdit(myConfig.get("maxDitTime", "350"))
        minLetterPauseLabel = QLabel("minLetterPause (ms):")
        self.minLetterPauseEdit = QLineEdit(myConfig.get("minLetterPause", "1000"))
        TimingsLayout = QGridLayout()
        TimingsLayout.addWidget(maxDitTimeLabel, 0, 0)
        TimingsLayout.addWidget(self.maxDitTimeEdit, 0, 1, 1, 4)
        TimingsLayout.addWidget(minLetterPauseLabel, 1, 0)
        TimingsLayout.addWidget(self.minLetterPauseEdit, 1, 1, 2, 4)
        TimingsLayout.setRowStretch(4, 1)
        inputSettingsLayout.addLayout(TimingsLayout)
        
        self.withDebug = QCheckBox("Debug On")
        self.withDebug.setChecked(myConfig.get("debug", False))
        inputSettingsLayout.addWidget(self.withDebug)
        
        self.withSound = QCheckBox("Audible beeps")
        self.withSound.setChecked(myConfig.get("withsound", True))
        inputSettingsLayout.addWidget(self.withSound)
        
        fontSizeScaleLabel = QLabel("FontSize (%):")
        self.fontSizeScaleEdit = QLineEdit(myConfig.get("fontsizescale", "100"))
        viewSettingSec = QGridLayout()
        viewSettingSec.addWidget(fontSizeScaleLabel, 0, 0)
        viewSettingSec.addWidget(self.fontSizeScaleEdit, 0, 1, 1, 2)
        self.upperCharsCheck = QCheckBox("Upper case chars")
        self.upperCharsCheck.setChecked(myConfig.get("upperchars", True))
        viewSettingSec.addWidget(self.upperCharsCheck, 0, 3)
        viewSettingSec.setRowStretch(4, 1)
        inputSettingsLayout.addLayout(viewSettingSec)

        self.iconComboBoxSoundDit = self.mkKeyStrokeComboBox([
                ["Dit Sound", "dit_sound.wav"],  # Ensure the path is correct
                ["Default", "dit_sound.wav"]  # Optional: default sound path
            ], myConfig.get('SoundDit', "dit_sound.wav"))
        
        self.iconComboBoxSoundDah = self.mkKeyStrokeComboBox([
            ["Dah Sound", "dah_sound.wav"],  # Ensure the path is correct
            ["Default", "dah_sound.wav"]  # Optional: default sound path
        ], myConfig.get('SoundDah', "dah_sound.wav"))

        DitSoundLabel = QLabel("Dit sound: ")
        DahSoundLabel = QLabel("Dah sound: ")
        SoundConfigLayout = QGridLayout()
        SoundConfigLayout.addWidget(DitSoundLabel, 0, 0)
        SoundConfigLayout.addWidget(self.iconComboBoxSoundDit, 0, 1, 1, 4)
        SoundConfigLayout.addWidget(DahSoundLabel, 1, 0)
        SoundConfigLayout.addWidget(self.iconComboBoxSoundDah, 1, 1, 1, 4)
        
        self.autostartCheckbox = QCheckBox("Auto-Start")
        self.autostartCheckbox.setChecked(myConfig.get("autostart", True))
        inputSettingsLayout.addWidget(self.autostartCheckbox)
        
        inputSettingsLayout.addLayout(SoundConfigLayout)
        
        
        inputRadioGroup = QGroupBox("Align window horizontally from")
        posAxisLayout = QHBoxLayout()
        self.keyWinPosXLeftRadio = QRadioButton("Left")
        self.keyWinPosXRightRadio = QRadioButton("Right")
        if myConfig.get("winxaxis", "left") == "left":
            self.keyWinPosXLeftRadio.setChecked(True)
        else:
            self.keyWinPosXRightRadio.setChecked(True)
        posAxisLayout.addWidget(self.keyWinPosXLeftRadio)
        posAxisLayout.addWidget(self.keyWinPosXRightRadio)
        self.keyWinPosXEdit = QLineEdit(myConfig.get("winposx", "10"))
        inputRadioGroup.setLayout(posAxisLayout)
        inputSettingsLayout.addWidget(inputRadioGroup)
        inputSettingsLayout.addWidget(self.keyWinPosXEdit)

        inputRadioGroup = QGroupBox("Align window vertically from")
        posAxisLayout = QHBoxLayout()
        self.keyWinPosYTopRadio = QRadioButton("Top")
        self.keyWinPosYBottomRadio = QRadioButton("Bottom")
        if myConfig.get("winyaxis", "top") == "top":
            self.keyWinPosYTopRadio.setChecked(True)
        else:
            self.keyWinPosYBottomRadio.setChecked(True)
        posAxisLayout.addWidget(self.keyWinPosYTopRadio)
        posAxisLayout.addWidget(self.keyWinPosYBottomRadio)
        self.keyWinPosYEdit = QLineEdit(myConfig.get("winposy", "10"))
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
        config = self.collectConfig()
        data = dict()
        data.update(config)
        saveConfig(configfile, data)
        
    def toggleOnOff(self):
        global myConfig
        if myConfig['off']:
            myConfig['off'] = False
        else:
            myConfig['off'] = True
    
    def stopIt (self):
        global hm, codeslayoutview
        if codeslayoutview is not None:
            codeslayoutview.hide()
            codeslayoutview = None
        # detect if it is running
        if hm is not None:
            hm.UnhookKeyboard()
            hm = None
        pythoncom.PumpMessages()
    
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


class CodeRepresentation(QWidget):
    def __init__(self, parent, code, item, c1):
        super(CodeRepresentation, self).__init__(None)       
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
        
    def item_label (self):
        return self.item['_action'].getlabel() if self.item['_action'] is not None else ""
    
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
        charfontsize = int(3.0 * myConfig['fontsizescale'])
        codefontsize = int(5.0 * myConfig['fontsizescale'])
        toggled = self.toggled
        self.character.setText("<font style='background-color:{bgcolor};color:{color};font-weight:bold;' size='{fontsize}'>{text}</font>"
                               .format(color='blue' if enabled else 'lightgrey', 
                                       text=(self.item_label().upper() if myConfig['upperchars'] else self.item_label()),
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
    
    def changeLayout (self):
        global codeslayoutview
        self.hide()
        if layoutmanager.active is not None:
            codeslayoutview = CodesLayoutViewWidget(layoutmanager.active)
        else:
            codeslayoutview = None
    
    def onFeedback (self):
        for keyname in ("ALT", "SHIFT", "CTRL"):
            coderep = self.keystroke_crs_map.get(keyname, None)
            if coderep is not None:
                coderep.toggled = getKeyStrokeState(keyname)['down']
                coderep.updateView()
        coderep = self.keystroke_crs_map.get("CAPSLOCK", None)
        if coderep is not None:
            key = coderep.item['_action'].key
            #state = unpack("H", pack("h", win32api.GetAsyncKeyState(key.keywin32)))[0]
            coderep.toggled = getKeyStrokeState("CAPSLOCK")["locked"]# (state & 1) == 1
            coderep.updateView()
         
    
    def __init__(self, layout):
        super(CodesLayoutViewWidget, self).__init__()
        self.feedbackSignal.connect(self.onFeedback)
        self.changeLayoutSignal.connect(self.changeLayout)
        self.hideSignal.connect(self.hide)
        self.showSignal.connect(self.show)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.vlayout = QVBoxLayout()
        hlayout = QHBoxLayout()
        hlayout.setContentsMargins(0, 0, 0, 0)
        self.vlayout.addLayout(hlayout)
        self.keystroke_crs_map = {}
        self.crs = {}
        x = 0
        perrow = layout['column_len']
        for code in layout['items']:
            x += 1
            item = layout['items'][code]
            if item.get('emptyspace', False) == False:
                coderep = CodeRepresentation(None, code, item, "Green")
                if isinstance(item['_action'], ActionKeyStroke):
                    self.keystroke_crs_map[item['_action'].key.name] = coderep
                #self.setStyleSheet("background: %s " % "green")
                self.crs[code] = coderep
                hlayout.addWidget(coderep)
            if (x > perrow):
                x = 0
                hlayout = QHBoxLayout()
                hlayout.setContentsMargins(0, 0, 0, 0)
                self.vlayout.addLayout(hlayout)
        self.setLayout(self.vlayout)
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        self.show()
        self.onFeedback()
        ssize = app.desktop().screenGeometry()
        size = self.frameSize()
        x = int(myConfig['winposx']) if myConfig['winxaxis'] == 'left' else\
            ssize.width() - size.width() - int(myConfig['winposx'])
        y = int(myConfig['winposy']) if myConfig['winyaxis'] == 'top' else\
            ssize.height() - size.height() - int(myConfig['winposy'])
        self.move(x, y)
    
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
    
if __name__ == '__main__':
    global layoutmanage, window, myConfig
    import sys
    initActions()
    try:
        myConfig = readConfig(configfile)
    except FileNotFoundError:
        myConfig = newConfig()
    layoutmanager = LayoutManager(os.path.join(os.path.dirname(os.path.realpath(__file__)), "layouts.json"), actions)
    if layoutmanager.active is None:
        raise AssertionError("layouts.json has no mainlayout")
    app = QApplication(sys.argv)

    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "MorseWriter", "I couldn't detect any system tray on this system.")
        sys.exit(1)

    QApplication.setQuitOnLastWindowClosed(False)

    window = Window()
    #code = CodeRepresentation(window, "A", "233232")
    #code.disable()
    #code.tickDitDah()
    #code.tickDitDah()
    if myConfig.get("autostart", False):
        window.start(myConfig)
    else:
        window.show()
    sys.exit(app.exec_())
