#!/usr/bin/env pythone

# This is only needed for Python v2 but is harmless for Python v3.
#import sip
#sip.setapi('QVariant', 1)
import sys
import threading
import winsound
import icons_rc
from pynput import keyboard
import json
import os
from presagectypes import Presage, PresageCallback

lastkeydowntime = -1

presageconfig = os.path.join(os.path.dirname(os.path.realpath(__file__)), "res", "presage.xml")
presagedll = os.path.join(os.path.dirname(os.path.realpath(__file__)), "libpresage-1.dll")

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

class TypeState (PresageCallback):
    def __init__ (self):
        self.text = ""
        self.predictions = None
        self.presage = Presage(self, config=presageconfig, dllfile=presagedll)
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

class LayoutManager (object):
    def __init__ (self, fn, actions):
        self.actions = actions
        data_str = ""
        with open(fn, "r") as f:
            data = json.loads("".join(chunk for chunk in iter(f.read, '')))
            self.layouts = dict(map(lambda a:(a[0],self._layout_import(a[1])), data['layouts'].items()))
            self.active = self.layouts.get(data['mainlayout'], None)
            self.mainlayout = self.active
            self.mainlayoutname = data['mainlayout']
            
    def _layout_import (self, layout):
        for item in layout['items']:
            actioninitdata =  self.actions.__members__.get(item.get('action', None), None)
            action = None
            if actioninitdata is not None:
                action = actioninitdata.value[0](item, *actioninitdata.value[1:])
            item['_action'] = action
        layout['items'] = OrderedDict(map(lambda a: (a['code'], a), layout['items']))
        return layout
        
    def set_active (self, layout):
        self.active = layout


def PressKey(down, key):
    global pressingKey
    pressingKey = True
    if myConfig['debug']:
        print("presskey: ",key, "down" if down else "up")
    # win32api.MAPVK_VK_TO_VSC = 0, one may need to pass this as second argument `win32api.MapVirtualKey(key, 0)`
    win32api.keybd_event(key, win32api.MapVirtualKey(key, 0), (not down) * win32con.KEYEVENTF_KEYUP)
    pressingKey = False

def TypeKey(key, keystroke_time=10):
    PressKey(True, key)
    PressKey(False, key)
    if myConfig['debug']:
        print("typekey, ", key)

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
    # save cursor position for after each action, MOUSEMODE has been removed!!
    currentX, currentY = win32api.GetCursorPos()
    hm.KeyDown = OnKeyboardEventDown
    hm.KeyUp = OnKeyboardEventUp
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
        if key.char:
            key_char = key.char
        else:
            key_char = key.name
    except AttributeError:
        key_char = key.name

    # Your existing logic for handling key up events goes here
    # You will need to adapt the logic from using PyHook3 to using the key information from pynput
    # Example adaptation:
    # if key_char == 'your_key_of_interest':
    #     # Perform actions


def addDit():
    currentCharacter.append(MyEvents.DIT.value)
    if (myConfig['withsound']):
        #winsound.Beep(int(myConfig['SoundDitFrequency']), int(myConfig['SoundDitDuration']))
        winsound.MessageBeep(myConfig.get('SoundDit', -1))
        #winsound.Beep(440, 33)
    #combos = getPossibleCombos(currentCharacter)
    codeslayoutview.Dit()

def addDah():
    currentCharacter.append(MyEvents.DAH.value)
    if (myConfig['withsound']):
        #winsound.Beep(int(myConfig['SoundDitFrequency']), int(myConfig['SoundDitDuration']))
        winsound.MessageBeep(myConfig.get('SoundDah', -1))
        #winsound.Beep(440, 100)
    #combos = getPossibleCombos(currentCharacter)
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
    def __init__ (self, item, key, label):
        super(ActionLegacy, self).__init__(item)
        self.key = key
        self.label = label
    def getlabel (self):
        return self.label
    def perform (self):
        global repeaton, repeatkey
        key = self.key
        if (key == actions.MOUSEUP5.value[1]):
            currentY += -5
            moveMouse()
        elif (key == actions.MOUSEDOWN5.value[1]):
            currentY += 5
            moveMouse()
        elif (key == actions.MOUSELEFT5.value[1]):
            currentX += -5
            moveMouse()
        elif (key == actions.MOUSERIGHT5.value[1]):
            currentX += 5
            moveMouse()
        elif (key == actions.MOUSEUPLEFT5.value[1]):
            currentX += -5
            currentY += -5
            moveMouse()
        elif (key == actions.MOUSEUPRIGHT5.value[1]):
            currentX += 5
            currentY += -5
            moveMouse()
        elif (key == actions.MOUSEDOWNLEFT5.value[1]):
            currentX += -5
            currentY += 5
            moveMouse()
        elif (key == actions.MOUSEDOWNRIGHT5.value[1]):
            currentX += 5
            currentY += 5
            moveMouse()
        elif (key == actions.MOUSEUP40.value[1]):
            currentY += -40
            moveMouse()
        elif (key == actions.MOUSEDOWN40.value[1]):
            currentY += 40
            moveMouse()
        elif (key == actions.MOUSELEFT40.value[1]):
            currentX += -40
            moveMouse()
        elif (key == actions.MOUSERIGHT40.value[1]):
            currentX += 40
            moveMouse()
        elif (key == actions.MOUSEUPLEFT40.value[1]):
            currentX += -40
            currentY += -40
            moveMouse()
        elif (key == actions.MOUSEUPRIGHT40.value[1]):
            currentX += 40
            currentY += -40
            moveMouse()
        elif (key == actions.MOUSEDOWNLEFT40.value[1]):
            currentX += -40
            currentY += 40
            moveMouse()
        elif (key == actions.MOUSEDOWNRIGHT40.value[1]):
            currentX += 40
            currentY += 40
            moveMouse()
        elif (key == actions.MOUSEUP250.value[1]):
            currentY += -250
            moveMouse()
        elif (key == actions.MOUSEDOWN250.value[1]):
            currentY += 250
            moveMouse()
        elif (key == actions.MOUSELEFT250.value[1]):
            currentX += -250
            moveMouse()
        elif (key == actions.MOUSERIGHT250.value[1]):
            currentX += 250
            moveMouse()
        elif (key == actions.MOUSEUPLEFT250.value[1]):
            currentX += -250
            currentY += -250
            moveMouse()
        elif (key == actions.MOUSEUPRIGHT250.value[1]):
            currentX += 250
            currentY += -250
            moveMouse()
        elif (key == actions.MOUSEDOWNLEFT250.value[1]):
            currentX += -250
            currentY += 250
            moveMouse()
        elif (key == actions.MOUSEDOWNRIGHT250.value[1]):
            currentX += 250
            currentY += 250
            moveMouse()
        elif (key == actions.MOUSECLICKLEFT.value[1]):
            leftClickMouse()
        elif (key == actions.MOUSECLICKRIGHT.value[1]):
            rightClickMouse()
        elif (key == actions.MOUSECLKHLDLEFT.value[1]):
            leftMouseDown()
        elif (key == actions.MOUSECLKHLDRIGHT.value[1]):
            rightMouseDown()
        elif (key == actions.MOUSERELEASEHOLD.value[1]):
            releaseMouseDown()
        elif (key == actions.REPEATMODE.value[1]):
            if (repeaton == True):
                if myConfig['debug']:
                    print("repeat OFF")
                    repeaton = False
                    repeatkey = None
                else:
                    if myConfig['debug']:
                        print("repeat ON")
                    repeaton = True 


class KeyStroke (object):
    def __init__ (self, name, label, keywin32, character):
        self.name = name
        self.label = label
        self.keywin32 = keywin32
        self.character = character
        
class ActionKeyStroke (Action):
    def __init__ (self, item, key, toggle_action=False):
        super(ActionKeyStroke, self).__init__(item)
        self.key = key
        self.toggle_action = toggle_action 
    def getlabel (self):
        return self.key.label
    def perform (self):
        key = self.key.keywin32
        if self.toggle_action:
            isdown = getKeyStrokeState(self.key.name)["down"]
            if isdown:
                PressKey(False, key)
            else:
                PressKey(True, key)
        else:
            if (repeaton):
                if (repeatkey == None):
                    repeatkey = key
                else:
                    if myConfig['debug']:
                        print("repeat code: ", repeatkey, " + ", key)
                    PressKey(True, repeatkey)
                    TypeKey(key)
                    PressKey(False, repeatkey)
            else:
                if myConfig['debug']:
                    print("code found: ", key)
                #win32api.VkKeyScan('1')
                TypeKey(key)
                if typestate != None:
                    if self.key.name == "BACKSPACE":
                        typestate.popchar()
                    elif self.key.character != None:
                        typestate.pushchar(self.key.character)


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
    keystrokesdata = list(map(lambda a: (KeyStroke(*a[:4]), a[4:]), (
        ("A", "a", win32api.VkKeyScan("a"), "a"), ("B", "b", win32api.VkKeyScan("b"), "b"), ("C", "c", win32api.VkKeyScan("c"), "c"), ("D", "d", win32api.VkKeyScan("d"), "d"), 
        ("E", "e", win32api.VkKeyScan("e"), "e"), ("F", "f", win32api.VkKeyScan("f"), "f"), ("G", "g", win32api.VkKeyScan("g"), "g"), ("H", "h", win32api.VkKeyScan("h"), "h"), 
        ("I", "i", win32api.VkKeyScan("i"), "i"), ("J", "j", win32api.VkKeyScan("j"), "j"), ("K", "k", win32api.VkKeyScan("k"), "k"), ("L", "l", win32api.VkKeyScan("l"), "l"), 
        ("M", "m", win32api.VkKeyScan("m"), "m"), ("N", "n", win32api.VkKeyScan("n"), "n"), ("O", "o", win32api.VkKeyScan("o"), "o"), ("P", "p", win32api.VkKeyScan("p"), "p"), 
        ("Q", "q", win32api.VkKeyScan("q"), "q"), ("R", "r", win32api.VkKeyScan("r"), "r"), ("S", "s", win32api.VkKeyScan("s"), "s"), ("T", "t", win32api.VkKeyScan("t"), "t"),
        ("U", "u", win32api.VkKeyScan("u"), "u"), ("V", "v", win32api.VkKeyScan("v"), "v"), ("W", "w", win32api.VkKeyScan("w"), "w"), ("X", "x", win32api.VkKeyScan("x"), "x"), 
        ("Y", "y", win32api.VkKeyScan("y"), "y"), ("Z", "z", win32api.VkKeyScan("z"), "z"), ("ONE", "1", win32api.VkKeyScan("1"), "1"), ("TWO", "2", win32api.VkKeyScan("2"), "2"), 
        ("THREE", "3", win32api.VkKeyScan("3"), "3"), ("FOUR", "4", win32api.VkKeyScan("4"), "4"), ("FIVE", "5", win32api.VkKeyScan("5"), "5"), 
        ("SIX", "6", win32api.VkKeyScan("6"), "6"), 
        ("SEVEN", "7", win32api.VkKeyScan("7"), "7"), ("EIGHT", "8", win32api.VkKeyScan("8"), "8"), ("NINE", "9", win32api.VkKeyScan("9"), "9"), 
        ("ZERO", "0", win32api.VkKeyScan("0"), "0"), ("DOT", ".", win32api.VkKeyScan("."), "."), ("COMMA", ",", win32api.VkKeyScan(","), ","), 
        ("QUESTION", "?", win32api.VkKeyScan("?"), "?"), ("EXCLAMATION", "!", win32api.VkKeyScan("!"), "!"), ("COLON", ":", win32api.VkKeyScan(":"), ":"), 
        ("SEMICOLON", ";", win32api.VkKeyScan(";"), ";"), ("AT", "@", win32api.VkKeyScan("@"), "@"), ("BASH", "#", win32api.VkKeyScan("#"), "#"),
        ("DOLLAR", "$", win32api.VkKeyScan("$"), "$"), ("PERCENT", "%", win32api.VkKeyScan("%"), "%"), ("AMPERSAND", "&", win32api.VkKeyScan("&"), "&"), 
        ("STAR", "*", win32con.VK_MULTIPLY, "*"), ("PLUS", "+", win32con.VK_ADD, "+"), ("MINUS", "-", win32con.VK_SUBTRACT, "-"), 
        ("EQUALS", "=", win32api.VkKeyScan("="), "="), ("FSLASH", "/", win32api.VkKeyScan("/"), "/"), ("BSLASH", "\\", win32api.VkKeyScan("\\"), "\\"), 
        ("SINGLEQUOTE", "\'", win32api.VkKeyScan("\'"), "\'"), ("DOUBLEQUOTE", "\"", win32api.VkKeyScan("\""), "\""), ("OPENBRACKET", "(", win32api.VkKeyScan("("), "("), 
        ("CLOSEBRACKET", ")", win32api.VkKeyScan(")"), ")"), ("LESSTHAN", "<", win32api.VkKeyScan("<"), "<"), ("MORETHAN", ">", win32api.VkKeyScan(">"), ">"), 
        ("CIRCONFLEX", "^", win32api.VkKeyScan("^"), "^"), ("ENTER", "ENTER", win32con.VK_RETURN, "\n"), ("SPACE", "space", win32con.VK_SPACE, " "),
        ("BACKSPACE", "bckspc", win32con.VK_BACK, chr(8)), ("TAB", "tab", win32con.VK_TAB, "\t"), ("TABLEFT", "tab", win32con.VK_TAB, "\t"), 
        ("UNDERSCORE", "_", win32api.VkKeyScan("_"), "_"), ("PAGEUP", "pageup", win32con.VK_PRIOR, None), ("PAGEDOWN", "pagedwn", win32con.VK_NEXT, None), 
        ("LEFTARROW", "left", win32con.VK_LEFT, None), ("RIGHTARROW", "right", win32con.VK_RIGHT, "right"),
        ("UPARROW", "up", win32con.VK_UP, "up"), ("DOWNARROW", "down", win32con.VK_DOWN, "down"), ("ESCAPE", "esc", win32con.VK_ESCAPE, "esc"), ("HOME", "home", win32con.VK_HOME, "home"), 
        ("END", "end", win32con.VK_END, None), ("INSERT", "insert", win32con.VK_INSERT, None), ("DELETE", "del", win32con.VK_DELETE, None), 
        ("STARTMENU", "start", win32con.VK_MENU, None), ("SHIFT", "shift", win32con.VK_SHIFT, None, True), ("ALT", "alt", win32con.VK_MENU, None, True),
        ("CTRL", "ctrl", win32con.VK_CONTROL, None, True), ("WINDOWS", "win", win32con.VK_LWIN, None), ("APPKEY", "app", win32con.VK_LWIN, None), 
        ("LCTRL", "left ctrl", win32con.VK_LCONTROL, None), ("RCTRL", "right ctrl", win32con.VK_RCONTROL, None),
        ("LSHIFT", "left shift", win32con.VK_LSHIFT, None), ("RSHIFT", "right shift", win32con.VK_RSHIFT, None),
        ("RALT", "right alt", win32con.VK_RMENU, None), ("LALT", "alt", win32con.VK_LMENU, None),
        ("CAPSLOCK", "caps", win32con.VK_CAPITAL, None),
        ("F1", "F1", win32con.VK_F1, None), ("F2", "F2", win32con.VK_F2, None), ("F3", "F3", win32con.VK_F3, None), ("F4", "F4", win32con.VK_F4, None), ("F5", "F5", win32con.VK_F5, None), 
        ("F6", "F6", win32con.VK_F6, None), ("F7", "F7", win32con.VK_F7, None), ("F8", "F8", win32con.VK_F8, None), ("F9", "F9", win32con.VK_F9, None), ("F10", "F10", win32con.VK_F10, None),
        ("F11", "F11", win32con.VK_F11, None), ("F12", "F12", win32con.VK_F12, None))))
    keystrokes = list(map(lambda a: a[0], keystrokesdata))
    keystrokemap = dict(map(lambda a: (a.name, a), keystrokes))
    actionskwargs = dict(map(lambda a: (a[0], (ActionLegacy, a[1], a[2])),
       (("REPEATMODE", 0, "repeat"), ("SOUND", 8, "snd"), ("CODESET", 9, "code"),
        ("MOUSERIGHT5", 2, "ms right 5"),
        ("MOUSEUP5", 3, "ms up 5"), ("MOUSECLICKLEFT", 4, "ms clkleft"), ("MOUSEDBLCLICKLEFT", 5, "ms dblclkleft"), 
        ("MOUSECLKHLDLEFT", 6, "ms hldleft"), ("MOUSEUPLEFT5", 7, "ms leftup 5"), ("MOUSEDOWNLEFT5", 8, "ms leftdown 5"),
        ("MOUSERELEASEHOLD", 9, "ms release"), ("MOUSELEFT5", 0, "ms left 5"), ("MOUSEDOWN5", 1, "ms down 5"), ("MOUSECLICKRIGHT", 2, "ms clkright"), 
        ("MOUSEDBLCLICKRIGHT", 3, "ms dblclkright"), ("MOUSECLKHLDRIGHT", 4, "ms hldright"), ("MOUSEUPRIGHT5", 5, "ms rightup 5"), 
        ("MOUSEDOWNRIGHT5", 6, "ms rightdown 5"), ("NORMALMODE", 7, "normal mode"), ("MOUSEUP40", 8, "ms up 40"), ("MOUSEUP250", 9, "ms up 250"), 
        ("MOUSEDOWN40", 0, "ms down 40"), ("MOUSEDOWN250", 1, "ms down 250"), ("MOUSELEFT40", 2, "ms left 40"), ("MOUSELEFT250", 3, "ms left 250"), 
        ("MOUSERIGHT40", 4, "ms right 40"), ("MOUSERIGHT250", 5, "ms right 250"), ("MOUSEUPLEFT40", 6, "ms leftup 40"), 
        ("MOUSEUPLEFT250", 7, "ms leftup 250"), ("MOUSEDOWNLEFT40", 8, "ms leftdown 40"), ("MOUSEDOWNLEFT250", 9, "ms leftdown 250"), 
        ("MOUSEUPRIGHT40", 0, "ms rightup 40"), ("MOUSEUPRIGHT250", 1, "ms rightup 250"), ("MOUSEDOWNRIGHT40", 2, "ms rightdown 40"),
        ("MOUSEDOWNRIGHT250", 3, "ms rightdown 250"))
    ))
    actionskwargs.update(dict(
        CHANGELAYOUT=(ChangeLayoutAction,), PREDICTION_SELECT=(PredictionSelectLayoutAction,)
    ))
    actionskwargs.update(dict(map(lambda a: (a[0].name, (ActionKeyStroke,) + a), keystrokesdata)))
    actions = enum('Actions', **actionskwargs)
    '''
    normalmapping = OrderedDict([('12',actions.A), ('2111',actions.B), ('2121',actions.C), ('211',actions.D), ('1',actions.E), ('1121',actions.F), 
                                 ('221',actions.G), ('1111',actions.H), ('11',actions.I), ('1222',actions.J), ('212',actions.K), ('1211',actions.L), 
                                 ('22',actions.M), ('21',actions.N), ('222',actions.O), ('1221',actions.P), ('2212',actions.Q), ('121',actions.R), 
                                 ('111',actions.S), ('2',actions.T), ('112',actions.U), ('1112',actions.V), ('122',actions.W), ('2112',actions.X), 
                                 ('2122',actions.Y), ('2211',  actions.Z), ('12222',actions.ONE), ('11222',actions.TWO), ('11122',actions.THREE), 
                                 ('11112',actions.FOUR), ('11111',actions.FIVE), ('21111',actions.SIX), ('22111',actions.SEVEN), ('22211',actions.EIGHT), 
                                 ('22221',actions.NINE), ('22222',actions.ZERO), ('121212',actions.DOT), ('221122',actions.COMMA), 
                                 ('112211',actions.QUESTION), ('121122',actions.EXCLAMATION), ('212121',actions.COLON), ('11121',actions.SEMICOLON), 
                                 ('12221',actions.AT), ('21222',actions.BASH), ('211121',actions.DOLLAR), ('122121',actions.PERCENT), 
                                 ('21122',actions.AMPERSAND), ('12111',actions.STAR), ('12211',actions.PLUS), ('2221',actions.MINUS), 
                                 ('12212',actions.EQUALS), ('22112',actions.FSLASH), ('211111',actions.BSLASH), ('121221',actions.SINGLEQUOTE), 
                                 ('22122',actions.DOUBLEQUOTE), ('111221',actions.OPENBRACKET), ('211221',actions.CLOSEBRACKET), 
                                 ('121112',actions.LESSTHAN), ('221121',actions.MORETHAN), ('212112',actions.CIRCONFLEX), ('1212',actions.ENTER), 
                                 ('1122',actions.SPACE), ('2222',actions.BACKSPACE), ('21221',actions.TAB), ('221211',actions.TABLEFT), 
                                 ('11221',actions.UNDERSCORE), ('222112',actions.PAGEUP), ('222121',actions.PAGEDOWN), ('222212',actions.LEFTARROW), 
                                 ('222221',actions.RIGHTARROW), ('222211',actions.UPARROW), ('222222',actions.DOWNARROW), ('11211',actions.ESCAPE), 
                                 ('111121',actions.HOME), ('21211',actions.END), ('12112',actions.INSERT), ('21121',actions.DELETE), 
                                 ('221111',actions.STARTMENU), ('11212',actions.SHIFT), ('12122',actions.ALT), ('21212',actions.CTRL), 
                                 ('112122',actions.WINDOWS), ('211122',actions.APPKEY), ('112121',actions.CAPSLOCK), ('22121',actions.MOUSEMODE), 
                                 ('21112',actions.NUMBERMODE), ('121121',actions.REPEATMODE), ('121211',actions.SOUND), ('22212',actions.CODESET), 
                                 ('112222',actions.F1), ('111222',actions.F2), ('111122',actions.F3), ('111112',actions.F4), ('111111',actions.F5), 
                                 ('121111',actions.F6), ('122111',actions.F7), ('122211',actions.F8), ('122221',actions.F9), ('122222',actions.F10),
                                 ('212222',actions.F11), ('211222',actions.F12)])
    mousemapping = OrderedDict([('1', actions.MOUSERIGHT5), ('21', actions.MOUSERIGHT40), ('121', actions.MOUSERIGHT250), 
                                ('2', actions.MOUSELEFT5), ('22', actions.MOUSELEFT40), ('122', actions.MOUSELEFT250),
                                ('11', actions.MOUSEUP5), ('111', actions.MOUSEUP40), ('211', actions.MOUSEUP250),
                                ('12', actions.MOUSEDOWN5), ('112', actions.MOUSEDOWN40), ('212', actions.MOUSEDOWN250),
                                ('221', actions.MOUSEUPRIGHT5), ('1121', actions.MOUSEUPRIGHT40), ('1221', actions.MOUSEUPRIGHT250),
                                ('222', actions.MOUSEDOWNRIGHT5), ('1122', actions.MOUSEDOWNRIGHT40), ('1222', actions.MOUSEDOWNRIGHT250),
                                ('1111', actions.MOUSEUPLEFT5), ('1211', actions.MOUSEUPLEFT40), ('2111', actions.MOUSEUPLEFT250),
                                ('1112', actions.MOUSEDOWNLEFT5), ('1212', actions.MOUSEDOWNLEFT40), ('2112', actions.MOUSEDOWNLEFT250),
                                ('2121',actions.MOUSECLICKLEFT), ('2122',actions.MOUSEDBLCLICKLEFT), 
                                ('2211',actions.MOUSECLKHLDLEFT), ('2212',actions.MOUSERELEASEHOLD), ('2221',actions.MOUSECLICKRIGHT), 
                                ('2222',actions.MOUSEDBLCLICKRIGHT), ('11111',actions.MOUSECLKHLDRIGHT), ('22121',actions.NORMALMODE)])
    numbermapping = OrderedDict([('1',actions.ONE), ('2',actions.TWO), ('12',actions.THREE), ('11',actions.FOUR), ('21',actions.FIVE), ('22',actions.SIX), 
                                 ('122',actions.SEVEN), ('112',actions.EIGHT), ('111',actions.NINE), ('211',actions.ZERO), ('221',actions.PLUS), 
                                 ('222',actions.MINUS), ('212',actions.FSLASH), ('121',actions.STAR), ('1212',actions.ENTER), ('121212',actions.DOT)])
    
    aitems = list(actions)
    def aname (map, key):
        return map[key].name
    maps = {}
    maps["main"] = {
        "items": list("{{ \"code\": \"{}\", \"action\": \"{}\" }}".format(key, aname(normalmapping, key)) for key in normalmapping)
    }
    maps["mouse"] = {
        "items": list("{{ \"code\": \"{}\", \"action\": \"{}\" }}".format(key, aname(mousemapping, key)) for key in mousemapping)
    }
    maps["number"] = {
        "items": list("{{ \"code\": \"{}\", \"action\": \"{}\" }}".format(key, aname(numbermapping, key)) for key in numbermapping)
    }
    with open("codemaps.json", "w") as f:
        f.write(json.dumps({ "maps": maps, "mainmap": "main" }, indent=2))
    '''

def Init():
    global MyEvents, currentCharacter, hm, repeaton, repeatkey, codeslayoutview, typestate
    MyEvents = enum('DITDAH', DIT=1, DAH=2)
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
            ["MB_OK", winsound.MB_OK],
            ["MB_ICONQUESTION", winsound.MB_ICONQUESTION],
            ["MB_ICONHAND", winsound.MB_ICONHAND],
            ["MB_ICONEXCLAMATION", winsound.MB_ICONEXCLAMATION],
            ["MB_ICONASTERISK", winsound.MB_ICONASTERISK],
            ["DEFAULT", -1],
        ], myConfig.get('SoundDit', None))

        self.iconComboBoxSoundDah = self.mkKeyStrokeComboBox([
            ["MB_OK", winsound.MB_OK],
            ["MB_ICONQUESTION", winsound.MB_ICONQUESTION],
            ["MB_ICONHAND", winsound.MB_ICONHAND],
            ["MB_ICONEXCLAMATION", winsound.MB_ICONEXCLAMATION],
            ["MB_ICONASTERISK", winsound.MB_ICONASTERISK],
            ["DEFAULT", -1],
        ], myConfig.get('SoundDah', None))

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
