#!/usr/bin/env pythone

# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QVariant', 1)
import PyHook3, win32con, win32api, time, pythoncom, configparser, sys, threading, winsound, icons_rc, atexit
from collections import OrderedDict
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QWidget, QApplication, QSystemTrayIcon, QGroupBox, QRadioButton, \
  QMessageBox, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QLineEdit, QGridLayout, QCheckBox, QPushButton, QAction, \
  QMenu

lastkeydowntime = -1

ctrlpressed = False
shiftpressed = False
disabled = False

mousemode = False

currentX = 0
currentY = 0

pressingKey = False

def PressKey(down, key):
    global pressingKey
    pressingKey = True
    win32api.keybd_event(key, 0, (not down) * win32con.KEYEVENTF_KEYUP)
    pressingKey = False

def TypeKey(key, keystroke_time=10):
    PressKey(True, key)
    PressKey(False, key)
    if myConfig['debug']:
        print("typekey, ", key)

def endCharacter():
    if myConfig['debug']:
        print("End Character")
    global currentCharacter, hm, repeaton, repeatkey,  mousemode, currentX, currentY, allchars, mousechars
    morse = "".join(map(str, currentCharacter))
    if mousemode:
        action = mousemapping.get(morse, None)
    else: # normal mode
        action = normalmapping.get(morse, None)
    if myConfig['debug']:
        print("action: ", action)
    if action != None:
        key = action[0]
        if (key == actions.NORMALMODE[0]):
            mousemode = False
            allchars.showSignal.emit()
            mousechars.hideSignal.emit()
        elif (key == actions.MOUSEUP5[0]):
            currentY += -5
            moveMouse()
        elif (key == actions.MOUSEDOWN5[0]):
            currentY += 5
            moveMouse()
        elif (key == actions.MOUSELEFT5[0]):
            currentX += -5
            moveMouse()
        elif (key == actions.MOUSERIGHT5[0]):
            currentX += 5
            moveMouse()
        elif (key == actions.MOUSEUPLEFT5[0]):
            currentX += -5
            currentY += -5
            moveMouse()
        elif (key == actions.MOUSEUPRIGHT5[0]):
            currentX += 5
            currentY += -5
            moveMouse()
        elif (key == actions.MOUSEDOWNLEFT5[0]):
            currentX += -5
            currentY += 5
            moveMouse()
        elif (key == actions.MOUSEDOWNRIGHT5[0]):
            currentX += 5
            currentY += 5
            moveMouse()
        elif (key == actions.MOUSEUP40[0]):
            currentY += -40
            moveMouse()
        elif (key == actions.MOUSEDOWN40[0]):
            currentY += 40
            moveMouse()
        elif (key == actions.MOUSELEFT40[0]):
            currentX += -40
            moveMouse()
        elif (key == actions.MOUSERIGHT40[0]):
            currentX += 40
            moveMouse()
        elif (key == actions.MOUSEUPLEFT40[0]):
            currentX += -40
            currentY += -40
            moveMouse()
        elif (key == actions.MOUSEUPRIGHT40[0]):
            currentX += 40
            currentY += -40
            moveMouse()
        elif (key == actions.MOUSEDOWNLEFT40[0]):
            currentX += -40
            currentY += 40
            moveMouse()
        elif (key == actions.MOUSEDOWNRIGHT40[0]):
            currentX += 40
            currentY += 40
            moveMouse()
        elif (key == actions.MOUSEUP250[0]):
            currentY += -250
            moveMouse()
        elif (key == actions.MOUSEDOWN250[0]):
            currentY += 250
            moveMouse()
        elif (key == actions.MOUSELEFT250[0]):
            currentX += -250
            moveMouse()
        elif (key == actions.MOUSERIGHT250[0]):
            currentX += 250
            moveMouse()
        elif (key == actions.MOUSEUPLEFT250[0]):
            currentX += -250
            currentY += -250
            moveMouse()
        elif (key == actions.MOUSEUPRIGHT250[0]):
            currentX += 250
            currentY += -250
            moveMouse()
        elif (key == actions.MOUSEDOWNLEFT250[0]):
            currentX += -250
            currentY += 250
            moveMouse()
        elif (key == actions.MOUSEDOWNRIGHT250[0]):
            currentX += 250
            currentY += 250
            moveMouse()
        elif (key == actions.MOUSECLICKLEFT[0]):
            leftClickMouse()
        elif (key == actions.MOUSECLICKRIGHT[0]):
            rightClickMouse()
        elif (key == actions.MOUSECLKHLDLEFT[0]):
            leftMouseDown()
        elif (key == actions.MOUSECLKHLDRIGHT[0]):
            rightMouseDown()
        elif (key == actions.MOUSERELEASEHOLD[0]):
            releaseMouseDown()
        elif (key == actions.REPEATMODE[0]):
            if (repeaton == True):
                if myConfig['debug']:
                    print("repeat OFF")
                    repeaton = False
                    repeatkey = None
                else:
                    if myConfig['debug']:
                        print("repeat ON")
                    repeaton = True
        elif (key == actions.MOUSEMODE[0]):
            mousemode = True
            #mousechars.show()
            allchars.hideSignal.emit()
            mousechars.showSignal.emit()
            currentX, currentY = win32api.GetCursorPos()
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
    hm.KeyDown = OnKeyboardEventDown
    hm.KeyUp = OnKeyboardEventUp
    currentCharacter = []
    allchars.reset()
    mousechars.reset()
    return

def disableKeyUpDown(event):
    if pressingKey:
        return True
    return False

def OnKeyboardEventDown(event):
    global lastkeydowntime, endCharacterTimer, myConfig, ctrlpressed, shiftpressed, disabled
    #print "eventid: " + str(event.KeyID)
    if pressingKey:
        return True
    if (event.KeyID == 162 or event.KeyID == 163):
        ctrlpressed = True
    if (event.KeyID == 160 or event.KeyID == 161):
        shiftpressed = True
    if (event.KeyID == 80 and ctrlpressed and shiftpressed):
        if (disabled == True):
     #       print "set disabled = False"
            disabled = False
            ctrlpressed = False
            shiftpressed = False
            return True
        else:
     #       print "set disabled = True"
            disabled = True
            return True
            
    if (disabled):
        TypeKey(event.KeyID)
        return False
    
    if myConfig['debug']:
        print("Key down: ", event.Key, "   ", event.KeyID, "    ", str(event))
        print('MessageName:',event.MessageName)
        print('Message:',event.Message)
        print('Time:',event.Time)
        print('Ascii:', event.Ascii, chr(event.Ascii))
        print('Key:', event.Key)
        print('KeyID:', event.KeyID)
        print('ScanCode:', event.ScanCode)
#    if (myConfig['onekey']):
#        if ((event.KeyID != myConfig['keyone']) or (lastkeydowntime != -1)):
#            return False
#    elif (((event.KeyID != myConfig['keyone']) and (event.KeyID != myConfig['keytwo'])) or (lastkeydowntime != -1)):
#        return False
    if (myConfig['onekey']):
        if ((event.KeyID != myConfig['keyone']) or (lastkeydowntime != -1)):
            return False
    elif (myConfig['twokey']):
        if (((event.KeyID != myConfig['keyone']) and (event.KeyID != myConfig['keytwo'])) or (lastkeydowntime != -1)):
            return False
    else:  #threekey
        if (((event.KeyID != myConfig['keyone']) and (event.KeyID != myConfig['keytwo']) and (event.KeyID != myConfig['keythree'])) or (lastkeydowntime != -1)):
            return False
    try:
        endCharacterTimer.cancel()
        if (event.KeyID == myConfig['keythree']):
            endCharacter()
    except NameError:
        pass
    lastkeydowntime = event.Time
    hm.KeyDown = disableKeyUpDown
    hm.KeyUp = OnKeyboardEventUp
    return False

def moveMouse():
    global currentX, currentY
    print("movemouse: " + str(currentX) + " / " + str(currentY))
    if (win32api.SetCursorPos((currentX,currentY)) == True):
        print(win32api.GetLastError())
        print("OK")
    else:
        print(win32api.GetLastError())
        print("NOT OK")
        

def leftClickMouse():
    global currentX, currentY
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,currentX,currentY,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,currentX,currentY,0,0)

def rightClickMouse():
    global currentX, currentY
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,currentX,currentY,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,currentX,currentY,0,0)
        
def middleClickMouse():
    global currentX, currentY
    win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEDOWN,currentX,currentY,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEUP,currentX,currentY,0,0)

def leftMouseDown():
    global currentX, currentY
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,currentX,currentY,0,0)

def rightMouseDown():
    global currentX, currentY
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,currentX,currentY,0,0)

def releaseMouseDown():
    global currentX, currentY
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,currentX,currentY,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,currentX,currentY,0,0)

def enum(**enums):
    return type('Enum', (), enums)

def OnKeyboardEventUp(event):
    global lastkeydowntime, MyEvents, currentCharacter, endCharacterTimer, hm, myConfig, disabled

    if pressingKey:
        return True
    if (event.KeyID == 162 or event.KeyID == 163):
        ctrlpressed = False
    if (event.KeyID == 160 or event.KeyID == 161):
        shiftpressed = False
    
    if myConfig['off']:
        return True

    if (disabled):
        return False
    
    if myConfig['debug']:
        print("Key up: ", event.Key)
        #print 'MessageName:',event.MessageName
        #print 'Time:',event.Time
        #print 'Ascii:', event.Ascii, chr(event.Ascii)
        #print 'Key:', event.Key
        #print 'KeyID:', event.KeyID
        #print 'ScanCode:', event.ScanCode
        #print(str(lastkeydowntime))

    if (myConfig['onekey']):
        if (event.KeyID != myConfig['keyone']):
            return False
    else:
        if ((event.KeyID != myConfig['keyone']) and (event.KeyID != myConfig['keytwo'])):
            return False

    msSinceLastKeyDown = event.Time - lastkeydowntime
    lastkeydowntime = -1
    endCharacterTimer = threading.Timer(float(myConfig['minLetterPause'])/1000.0, endCharacter)
    #print str(float(myConfig['minLetterPause']))
    endCharacterTimer.start()
    
    if (myConfig['onekey']):    
        if (msSinceLastKeyDown < float(myConfig['maxDitTime'])):
            addDit()
            if (myConfig['withsound']):
                winsound.MessageBeep(myConfig['SoundDit'])
            #print(currentCharacter)
        else:
            addDah()
            if (myConfig['withsound']):
                winsound.MessageBeep(myConfig['SoundDah'])
            #print(currentCharacter)       
        if myConfig['debug']:
            print("Duration of keypress: " + str(msSinceLastKeyDown))
    else:
        if (event.KeyID == myConfig['keyone']):
            addDit()
            if (myConfig['withsound']):
                winsound.MessageBeep(myConfig['SoundDit'])
        else:
            addDah()
            if (myConfig['withsound']):
                winsound.MessageBeep(myConfig['SoundDah'])
            
    hm.KeyDown = OnKeyboardEventDown
    hm.KeyUp = disableKeyUpDown

    return False

def addDit():
    global allchars, mousechars
    currentCharacter.append(MyEvents.DIT)
    if (myConfig['withsound']):
        #winsound.Beep(int(myConfig['SoundDitFrequency']), int(myConfig['SoundDitDuration']))
        #winsound.MessageBeep(myConfig['SoundDit'].toInt()[0])
        winsound.Beep(440, 33)
    #combos = getPossibleCombos(currentCharacter)
    allchars.Dit()
    mousechars.Dit()

def addDah():
    global allchars, mousechars
    currentCharacter.append(MyEvents.DAH)
    if (myConfig['withsound']):
        #winsound.Beep(int(myConfig['SoundDitFrequency']), int(myConfig['SoundDitDuration']))
        #winsound.MessageBeep(myConfig['SoundDah'].toInt()[0])
        winsound.Beep(440, 100)
    #combos = getPossibleCombos(currentCharacter)
    allchars.Dah()
    mousechars.Dah()

def getPossibleCombos(currentCharacter):
    x = ""
    for i in currentCharacter:
        x += str(i)   
    possibleactions = []
    for action in normalmapping:
        if (len(action) >= len(x) and action[:len(x)] == x):
            possibleactions.append(action)
    print("possible: " + str(possibleactions))
    
#unused
def parseConfigFile():
    global maxDitTime, minLetterPause, debug
    config = configparser.RawConfigParser()
    config.read('MorseCode.cfg')
    config.sections
    maxDitTime = config.getint('Input', 'maxDitTime')
    minLetterPause = config.getint('Input', 'minLetterPause')
    debug = config.getboolean('Various', 'debug')
    
def createMapping():
    global normalmapping, numbermapping, mousemapping, actions
    actions = enum(A=(win32api.VkKeyScan('a'), 'a'), B=(win32api.VkKeyScan('b'), 'b'), C=(win32api.VkKeyScan('c'), 'c'), D=(win32api.VkKeyScan('d'), 'd'), 
                   E=(win32api.VkKeyScan('e'), 'e'), F=(win32api.VkKeyScan('f'), 'f'), G=(win32api.VkKeyScan('g'), 'g'), H=(win32api.VkKeyScan('h'), 'h'), 
                   I=(win32api.VkKeyScan('i'), 'i'), J=(win32api.VkKeyScan('j'), 'j'), K=(win32api.VkKeyScan('k'), 'k'), L=(win32api.VkKeyScan('l'), 'l'), 
                   M=(win32api.VkKeyScan('m'), 'm'), N=(win32api.VkKeyScan('n'), 'n'), O=(win32api.VkKeyScan('o'), 'o'), P=(win32api.VkKeyScan('p'), 'p'), 
                   Q=(win32api.VkKeyScan('q'), 'q'), R=(win32api.VkKeyScan('r'), 'r'), S=(win32api.VkKeyScan('s'), 's'), T=(win32api.VkKeyScan('t'), 't'),
                   U=(win32api.VkKeyScan('u'), 'u'), V=(win32api.VkKeyScan('v'), 'v'), W=(win32api.VkKeyScan('w'), 'w'), X=(win32api.VkKeyScan('x'), 'x'), 
                   Y=(win32api.VkKeyScan('y'), 'y'), Z=(win32api.VkKeyScan('z'), 'z'), ONE=(win32api.VkKeyScan('1'), '1'), TWO=(win32api.VkKeyScan('2'), '2'), 
                   THREE=(win32api.VkKeyScan('3'), '3'), FOUR=(win32api.VkKeyScan('4'), '4'), FIVE=(win32api.VkKeyScan('5'), '5'), 
                   SIX=(win32api.VkKeyScan('6'), '6'), 
                   SEVEN=(win32api.VkKeyScan('7'), '7'), EIGHT=(win32api.VkKeyScan('8'), '8'), NINE=(win32api.VkKeyScan('9'), '9'), 
                   ZERO=(win32api.VkKeyScan('0'), '0'), DOT=(win32api.VkKeyScan('.'), '.'), COMMA=(win32api.VkKeyScan(','), ','), 
                   QUESTION=(win32api.VkKeyScan('?'), '?'), EXCLAMATION=(win32api.VkKeyScan('!'), '!'), COLON=(win32api.VkKeyScan(':'), ':'), 
                   SEMICOLON=(win32api.VkKeyScan(';'), ';'), AT=(win32api.VkKeyScan('@'), '@'), BASH=(win32api.VkKeyScan('#'), '#'),
                   DOLLAR=(win32api.VkKeyScan('$'), '$'), PERCENT=(win32api.VkKeyScan('%'), '%'), AMPERSAND=(win32api.VkKeyScan('&'), '&'), 
                   STAR=(win32con.VK_MULTIPLY, '*'), PLUS=(win32con.VK_ADD, '+'), MINUS=(win32con.VK_SUBTRACT, '-'), 
                   EQUALS=(win32api.VkKeyScan('='), '='), FSLASH=(win32api.VkKeyScan('/'), '/'), BSLASH=(win32api.VkKeyScan('\\'), '\\'), 
                   SINGLEQUOTE=(win32api.VkKeyScan('\''), '\''), DOUBLEQUOTE=(win32api.VkKeyScan('"'), '"'), OPENBRACKET=(win32api.VkKeyScan('('), '('), 
                   CLOSEBRACKET=(win32api.VkKeyScan(')'), ')'), LESSTHAN=(win32api.VkKeyScan('<'), '<'), MORETHAN=(win32api.VkKeyScan('>'), '>'), 
                   CIRCONFLEX=(win32api.VkKeyScan('^'), '^'), ENTER=(win32con.VK_RETURN, 'ENTER'), SPACE=(win32con.VK_SPACE, 'space'),
                   BACKSPACE=(win32con.VK_BACK, 'bckspc'), TAB=(win32con.VK_TAB, 'tab'), TABLEFT=(win32con.VK_TAB, 'tab'), 
                   UNDERSCORE=(win32api.VkKeyScan('_'), '_'), PAGEUP=(win32con.VK_PRIOR, 'pageup'), PAGEDOWN=(win32con.VK_NEXT, 'pagedwn'), 
                   LEFTARROW=(win32con.VK_LEFT, 'left'), RIGHTARROW=(win32con.VK_RIGHT, 'right'),
                   UPARROW=(win32con.VK_UP, 'up'), DOWNARROW=(win32con.VK_DOWN, 'down'), ESCAPE=(win32con.VK_ESCAPE, 'esc'), HOME=(win32con.VK_HOME, 'home'), 
                   END=(win32con.VK_END, 'end'), INSERT=(win32con.VK_INSERT, 'insert'), DELETE=(win32con.VK_DELETE, 'del'), 
                   STARTMENU=(win32con.VK_MENU, 'start'), SHIFT=(win32con.VK_SHIFT, 'shift'), ALT=(win32con.VK_MENU, 'alt'),
                   CTRL=(win32con.VK_CONTROL, 'ctrl'), WINDOWS=(win32con.VK_LWIN, 'win'), APPKEY=(win32con.VK_LWIN, 'app'), 
                   CAPSLOCK=(win32con.VK_CAPITAL, 'caps'), MOUSEMODE=(285, 'mousemode'), NUMBERMODE=(286, 'nbrmode'), 
                   REPEATMODE=(400, 'repeat'), SOUND=(288, 'snd'), CODESET=(289, 'code'),
                   F1=(win32con.VK_F1, 'F1'), F2=(win32con.VK_F2, 'F2'), F3=(win32con.VK_F3, 'F3'), F4=(win32con.VK_F4, 'F4'), F5=(win32con.VK_F5, 'F5'), 
                   F6=(win32con.VK_F6, 'F6'), F7=(win32con.VK_F7, 'F7'), F8=(win32con.VK_F8, 'F8'), F9=(win32con.VK_F9, 'F9'), F10=(win32con.VK_F10, 'F10'), 
                   F11=(win32con.VK_F11, 'F11'), F12=(win32con.VK_F12, 'F12'), MOUSERIGHT5=(302, 'ms right 5'),
                   MOUSEUP5=(303, 'ms up 5'), MOUSECLICKLEFT=(304, 'ms clkleft'), MOUSEDBLCLICKLEFT=(305, 'ms dblclkleft'), 
                   MOUSECLKHLDLEFT=(306, 'ms hldleft'), MOUSEUPLEFT5=(307, 'ms leftup 5'), MOUSEDOWNLEFT5=(308, 'ms leftdown 5'),
                   MOUSERELEASEHOLD=(309, 'ms release'), MOUSELEFT5=(310, 'ms left 5'), MOUSEDOWN5=(311, 'ms down 5'), MOUSECLICKRIGHT=(312, 'ms clkright'), 
                   MOUSEDBLCLICKRIGHT=(313, 'ms dblclkright'), MOUSECLKHLDRIGHT=(314, 'ms hldright'), MOUSEUPRIGHT5=(315, 'ms rightup 5'), 
                   MOUSEDOWNRIGHT5=(316, 'ms rightdown 5'), NORMALMODE=(317, 'normal mode'), MOUSEUP40=(318, 'ms up 40'), MOUSEUP250=(319, 'ms up 250'), 
                   MOUSEDOWN40=(320, 'ms down 40'), MOUSEDOWN250=(321, 'ms down 250'), MOUSELEFT40=(322, 'ms left 40'), MOUSELEFT250=(323, 'ms left 250'), 
                   MOUSERIGHT40=(324, 'ms right 40'), MOUSERIGHT250=(325, 'ms right 250'), MOUSEUPLEFT40=(326, 'ms leftup 40'), 
                   MOUSEUPLEFT250=(327, 'ms leftup 250'), MOUSEDOWNLEFT40=(328, 'ms leftdown 40'), MOUSEDOWNLEFT250=(329, 'ms leftdown 250'), 
                   MOUSEUPRIGHT40=(330, 'ms rightup 40'), MOUSEUPRIGHT250=(331, 'ms rightup 250'), MOUSEDOWNRIGHT40=(332, 'ms rightdown 40'),
                   MOUSEDOWNRIGHT250=(333, 'ms rightdown 250'))
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
    
def Init():
    global MyEvents, currentCharacter, hm, repeaton, repeatkey
#    createMapping()
    MyEvents = enum(DIT=1, DAH=2)
    currentCharacter = []
    repeaton = False 
    repeatkey = None

def Go():
    global hm
    hm = PyHook3.HookManager()
    hm.KeyDown = OnKeyboardEventDown
    hm.KeyUp = OnKeyboardEventUp
    hm.HookKeyboard()
    pythoncom.PumpMessages()

class Window(QDialog):
    def __init__(self):
        super(Window, self).__init__()

        self.createIconGroupBox()

        self.createActions()
        self.createTrayIcon()
        
        self.trayIcon.activated.connect(self.iconActivated)

        self.GOButton.clicked.connect(self.goForIt)
        
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

    def goForIt(self):
        global myConfig
        if self.trayIcon.isVisible():
            QMessageBox.information(self, "MorseWriter", "The program will run in the system tray. To terminate the program, choose <b>Quit</b> in the context menu of the system tray entry.")
            self.hide()
        
        myConfig = dict();
        myConfig['onekey'] = self.keySelectionRadioOneKey.isChecked()
        myConfig['twokey'] = self.keySelectionRadioTwoKey.isChecked()
        myConfig['threekey'] = self.keySelectionRadioThreeKey.isChecked()
        myConfig['keyone'] = self.iconComboBoxKeyOne.itemData(self.iconComboBoxKeyOne.currentIndex())
        myConfig['keytwo'] = self.iconComboBoxKeyTwo.itemData(self.iconComboBoxKeyTwo.currentIndex())
        myConfig['keythree'] = self.iconComboBoxKeyThree.itemData(self.iconComboBoxKeyThree.currentIndex())
        myConfig['maxDitTime'] = self.maxDitTimeEdit.text()
        if (self.keySelectionRadioThreeKey.isChecked()):
            myConfig['minLetterPause'] = 10000000000
        else:
            myConfig['minLetterPause'] = self.minLetterPauseEdit.text()
        myConfig['withsound'] = self.withSound.isChecked() 
        myConfig['SoundDit'] = self.iconComboBoxSoundDit.itemData(self.iconComboBoxSoundDit.currentIndex())
        myConfig['SoundDah'] = self.iconComboBoxSoundDah.itemData(self.iconComboBoxSoundDah.currentIndex())
        myConfig['debug'] = self.withDebug.isChecked()
        myConfig['off'] = False
        if myConfig['debug']:
            print("Config: " + str(myConfig['onekey']) + " / " + str(myConfig['keyone']) + " / " + str(myConfig['keytwo']) + " / " + str(myConfig['keythree']) + " / " + str(myConfig['maxDitTime']) + " / " + str(myConfig['minLetterPause']))
        
        Init()
        Go()

    def setVisible(self, visible):
        self.minimizeAction.setEnabled(visible)
        self.maximizeAction.setEnabled(not self.isMaximized())
        self.restoreAction.setEnabled(self.isMaximized() or not visible)
        super(Window, self).setVisible(visible)

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

    def createIconGroupBox(self):
        self.iconGroupBox = QGroupBox("Input Settings")
        
        self.keySelectionRadioOneKey = QRadioButton("One Key");
        self.keySelectionRadioTwoKey = QRadioButton("Two Key");
        self.keySelectionRadioThreeKey = QRadioButton("Three Key");
        
        inputSettingsLayout = QVBoxLayout()
        
        inputRadioButtonsLayout = QHBoxLayout()
        inputRadioButtonsLayout.addWidget(self.keySelectionRadioOneKey)
        inputRadioButtonsLayout.addWidget(self.keySelectionRadioTwoKey)
        inputRadioButtonsLayout.addWidget(self.keySelectionRadioThreeKey)
        inputSettingsLayout.addLayout(inputRadioButtonsLayout)       

        inputKeyComboBoxesLayout = QHBoxLayout()
        self.iconComboBoxKeyOne = QComboBox()
        self.iconComboBoxKeyOne.addItem("SPACE", win32con.VK_SPACE)
        self.iconComboBoxKeyOne.addItem("ENTER", win32con.VK_RETURN)
        self.iconComboBoxKeyOne.addItem("1", win32api.VkKeyScan('1'))
        self.iconComboBoxKeyOne.addItem("2", win32api.VkKeyScan('2'))
        self.iconComboBoxKeyOne.addItem("Z", win32api.VkKeyScan('z'))
        self.iconComboBoxKeyOne.addItem("X", win32api.VkKeyScan('x'))
        self.iconComboBoxKeyOne.addItem("F8", win32con.VK_F8)
        self.iconComboBoxKeyOne.addItem("F9", win32con.VK_F9)
        self.iconComboBoxKeyTwo = QComboBox()
        self.iconComboBoxKeyTwo.addItem("ENTER", win32con.VK_RETURN)
        self.iconComboBoxKeyTwo.addItem("2", win32api.VkKeyScan('2'))
        self.iconComboBoxKeyTwo.addItem("Z", win32api.VkKeyScan('z'))
        self.iconComboBoxKeyTwo.addItem("F8", win32con.VK_F8)
        self.iconComboBoxKeyThree = QComboBox()
        self.iconComboBoxKeyThree.addItem("Right Ctrl", win32con.VK_RCONTROL)
        self.iconComboBoxKeyThree.addItem("left Ctrl", win32con.VK_LCONTROL)
        self.iconComboBoxKeyThree.addItem("Right Shift", win32con.VK_RSHIFT)
        self.iconComboBoxKeyThree.addItem("Left Shift", win32con.VK_LSHIFT)
        self.iconComboBoxKeyThree.addItem("Alt", win32con.VK_MENU)
        inputKeyComboBoxesLayout.addWidget(self.iconComboBoxKeyOne)
        inputKeyComboBoxesLayout.addWidget(self.iconComboBoxKeyTwo)
        inputKeyComboBoxesLayout.addWidget(self.iconComboBoxKeyThree)
        inputSettingsLayout.addLayout(inputKeyComboBoxesLayout)

        self.keySelectionRadioOneKey.toggled.connect(self.iconComboBoxKeyTwo.hide)
        self.keySelectionRadioOneKey.toggled.connect(self.iconComboBoxKeyThree.hide)
        self.keySelectionRadioTwoKey.toggled.connect(self.iconComboBoxKeyTwo.show)
        self.keySelectionRadioThreeKey.toggled.connect(self.iconComboBoxKeyThree.show)
        self.keySelectionRadioThreeKey.toggled.connect(self.iconComboBoxKeyTwo.show)        
        self.keySelectionRadioOneKey.click();     

        
        maxDitTimeLabel = QLabel("MaxDitTime (ms):")
        self.maxDitTimeEdit = QLineEdit("350")
        minLetterPauseLabel = QLabel("minLetterPause (ms):")
        self.minLetterPauseEdit = QLineEdit("1000")
        TimingsLayout = QGridLayout()
        TimingsLayout.addWidget(maxDitTimeLabel, 0, 0)
        TimingsLayout.addWidget(self.maxDitTimeEdit, 0, 1, 1, 4)
        TimingsLayout.addWidget(minLetterPauseLabel, 1, 0)
        TimingsLayout.addWidget(self.minLetterPauseEdit, 1, 1, 2, 4)
        TimingsLayout.setRowStretch(4, 1)
        inputSettingsLayout.addLayout(TimingsLayout)
        
        self.withDebug = QCheckBox("Debug On")
        self.withDebug.setChecked(False)
        inputSettingsLayout.addWidget(self.withDebug)
        
        self.withSound = QCheckBox("Audible beeps")
        self.withSound.setChecked(True)
        inputSettingsLayout.addWidget(self.withSound)

        self.iconComboBoxSoundDit = QComboBox()
        self.iconComboBoxSoundDit.addItem("MB_OK", winsound.MB_OK)
        self.iconComboBoxSoundDit.addItem("MB_ICONQUESTION", winsound.MB_ICONQUESTION)
        self.iconComboBoxSoundDit.addItem("MB_ICONHAND", winsound.MB_ICONHAND)
        self.iconComboBoxSoundDit.addItem("MB_ICONEXCLAMATION", winsound.MB_ICONEXCLAMATION)
        self.iconComboBoxSoundDit.addItem("MB_ICONASTERISK", winsound.MB_ICONASTERISK)
        self.iconComboBoxSoundDit.addItem("DEFAULT", -1)

        self.iconComboBoxSoundDah = QComboBox()
        self.iconComboBoxSoundDah.addItem("MB_OK", winsound.MB_OK)
        self.iconComboBoxSoundDah.addItem("MB_ICONQUESTION", winsound.MB_ICONQUESTION)
        self.iconComboBoxSoundDah.addItem("MB_ICONHAND", winsound.MB_ICONHAND)
        self.iconComboBoxSoundDah.addItem("MB_ICONEXCLAMATION", winsound.MB_ICONEXCLAMATION)
        self.iconComboBoxSoundDah.addItem("MB_ICONASTERISK", winsound.MB_ICONASTERISK)
        self.iconComboBoxSoundDah.addItem("DEFAULT", -1)

        DitSoundLabel = QLabel("Dit sound: ")
        DahSoundLabel = QLabel("Dah sound: ")
        SoundConfigLayout = QGridLayout()
        SoundConfigLayout.addWidget(DitSoundLabel, 0, 0)
        SoundConfigLayout.addWidget(self.iconComboBoxSoundDit, 0, 1, 1, 4)
        SoundConfigLayout.addWidget(DahSoundLabel, 1, 0)
        SoundConfigLayout.addWidget(self.iconComboBoxSoundDah, 1, 1, 1, 4)
        
        #inputSettingsLayout.addLayout(SoundConfigLayout)
        self.GOButton = QPushButton("GO!")
        inputSettingsLayout.addWidget(self.GOButton)
        
        self.iconGroupBox.setLayout(inputSettingsLayout)

    def toggleOnOff(self):
        global myConfig
        if myConfig['off']:
            myConfig['off'] = False
        else:
            myConfig['off'] = True

    def createActions(self):
        self.minimizeAction = QAction("Minimize", self, triggered=self.hide)
        self.maximizeAction = QAction("Maximize", self, triggered=self.showMaximized)
        self.restoreAction = QAction("Restore", self, triggered=self.showNormal)
        self.onOffAction = QAction("OnOff", self, triggered=self.toggleOnOff)
        self.quitAction = QAction("Quit", self, triggered=sys.exit)

    def createTrayIcon(self):
        self.trayIconMenu = QMenu(self)
        self.trayIconMenu.addAction(self.minimizeAction)
        self.trayIconMenu.addAction(self.maximizeAction)
        self.trayIconMenu.addAction(self.restoreAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.onOffAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAction)
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)


class CodeRepresentation(QWidget):
    def __init__(self, parent, char, code, c1):
        super(CodeRepresentation, self).__init__(None)       
        vlayout = QVBoxLayout()
        self.char = char
        self.character = QLabel("<font color='blue' size='3'>"+char+"</font>")
        self.character.setGeometry(10, 10, 10, 10)
        self.character.setContentsMargins(0, 0, 0, 0)
        self.character.setMaximumHeight(15)
        self.character.setAlignment(Qt.AlignTop)        
        self.codeline = QLabel() 
        self.codeline.setAlignment(Qt.AlignTop)
        self.codeline.setContentsMargins(0, 0, 0, 0)
        self.codeline.setMaximumHeight(200)
        self.codeline.move(20, 30)
        self.code = self.codetocode(code)
        vlayout.setContentsMargins(0, 0, 0, 0)
        vlayout.addWidget(self.character)
        vlayout.addWidget(self.codeline)
        vlayout.setAlignment(self.character, Qt.AlignCenter)
        vlayout.setAlignment(self.codeline, Qt.AlignCenter)        
        self.setLayout(vlayout)
        self.setContentsMargins(0, 0, 0, 0)
     #   self.show()
        self.disabledchars = 0
        self.codeline.setText("<font color='red' size='5'>"+self.code+"</font>")
        
    def codetocode(self, code):
        toReturn = code.replace('1', '.')
        toReturn = toReturn.replace('2', '-')
        return toReturn;
    
    def enable(self):
        self.character.setDisabled(False)
        self.codeline.setDisabled(False)
        self.character.setText("<font color='blue' size='3'>" + self.char + "</font>")
        self.codeline.setText("<font color='red' size='5'>" + self.code + "</font>")        
        
    def disable(self):    
        self.character.setDisabled(True)
        self.codeline.setDisabled(True)
        self.character.setText('<font color="lightgrey", size="3">' + self.char + "</font>")
        self.codeline.setText("<font color='lightgrey' size='5'>" + self.code + "</font>")        
        
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
        self.codeline.setText("<font color='green' size='5'>" + self.code[:self.disabledchars] + "</font><font color='red' size='5'>" + self.code[self.disabledchars:] + "</font>")
        if (self.disabledchars > len(self.code)):
            self.disable()
        pass
    
class AllChars(QWidget):
    
    hideSignal = pyqtSignal()
    showSignal = pyqtSignal()
    
    def __init__(self, maps, actions, perrow):
        super(AllChars, self).__init__()
        self.hideSignal.connect(self.hide)
        self.showSignal.connect(self.show)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.vlayout = QVBoxLayout()
        hlayout = QHBoxLayout()
        hlayout.setContentsMargins(0, 0, 0, 0)
        self.vlayout.addLayout(hlayout)
        self.crs = {}
        x = 0
        for item in maps:
            x += 1
            self.crs[item] = CodeRepresentation(None, str(maps[item][1]), str(item), "Green")
            #self.setStyleSheet("background: %s " % "green")
            hlayout.addWidget(self.crs[item])
            if (x > perrow):
                x = 0
                hlayout = QHBoxLayout()
                hlayout.setContentsMargins(0, 0, 0, 0)
                self.vlayout.addLayout(hlayout)
        self.setLayout(self.vlayout)
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        self.show()
        self.move(0, 0)
        
    def Dit(self):
        for item in self.crs.values():
            item.Dit()

    def Dah(self):
        for item in self.crs.values():
            item.Dah()
            
    def reset(self):
        for item in self.crs.values():
            item.reset()


if __name__ == '__main__':
    global normalmapping, actions, allchars, mousemapping, mousechars
    import sys
    createMapping()
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
    
    allchars = AllChars(normalmapping, actions, 15)
    mousechars = AllChars(mousemapping, actions, 2)
    mousechars.hide()
    
    window.show()
    sys.exit(app.exec_())
