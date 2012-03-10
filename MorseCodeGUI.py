#!/usr/bin/env pythone

# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QVariant', 1)
import pyHook, win32con, win32api, time, pythoncom, ConfigParser, sys, threading, winsound, icons_rc, atexit
from PyQt4 import QtCore, QtGui

#class Worker(QtCore.QThread):
#        parse_triggered = QtCore.pyqtSignal()
#        def __init__(self, parent = None):
#            super(Worker, self).__init__(parent)
#        def test(self):
#            print("hi")


lastkeydowntime = -1

def PressKey(down, key):
    win32api.keybd_event(key, 0, (not down) * win32con.KEYEVENTF_KEYUP)

def TypeKey(key, keystroke_time=10):
    PressKey(True, key)
    PressKey(False, key)

def endCharacter():
    #print "End Character"
    global currentCharacter, hm, repeaton, repeatkey
        
    x = ""
    for i in currentCharacter:
        x += str(i)
    #print("X: " + x + " = " + hex(normalmapping.get(x)))
    hm.KeyDown = 0
    hm.KeyUp = 0
    key = normalmapping.get(x)
    if (key != None):
        if (key == 400):
            if (repeaton == True):
                if myConfig['debug']:
                    print("repeat OFF")
                repeaton = False
                repeatkey = None
            else:
                if myConfig['debug']:
                    print("repeat ON")
                repeaton = True
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
                TypeKey(key) 
                win32api.VkKeyScan('1')
    #print "X: " + str(normalmapping.get(x)) 
    hm.KeyDown = OnKeyboardEventDown
    hm.KeyUp = OnKeyboardEventUp
    currentCharacter = []
    return

def disableKeyUpDown(event):
    return False;

def OnKeyboardEventDown(event):
    global lastkeydowntime, endCharacterTimer, myConfig
    if myConfig['debug']:
        print("Key down: ", event.Key)
        #print 'MessageName:',event.MessageName
        #print 'Message:',event.Message
        #print 'Time:',event.Time
        #print 'Ascii:', event.Ascii, chr(event.Ascii)
        #print 'Key:', event.Key
        #print 'KeyID:', event.KeyID
        #print 'ScanCode:', event.ScanCode
    if (myConfig['onekey']):
        if ((event.KeyID != myConfig['keyone']) or (lastkeydowntime != -1)):
            return False
    else:
        if (((event.KeyID != myConfig['keyone']) and (event.KeyID != myConfig['keytwo'])) or (lastkeydowntime != -1)):
            return False
    
    try:
        endCharacterTimer.cancel()
    except NameError:
        pass
    lastkeydowntime = event.Time
    hm.KeyDown = disableKeyUpDown
    hm.KeyUp = OnKeyboardEventUp
     
    return False

def enum(**enums):
    return type('Enum', (), enums)

def OnKeyboardEventUp(event):
    global lastkeydowntime, MyEvents, currentCharacter, endCharacterTimer, hm, myConfig
    
    if myConfig['off']:
        return True
    
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
            #print(MyEvents.DIT)
            currentCharacter.append(MyEvents.DIT)
            if (myConfig['withsound']):
                #winsound.Beep(int(myConfig['SoundDitFrequency']), int(myConfig['SoundDitDuration']))
                winsound.MessageBeep(myConfig['SoundDit'].toInt()[0])
            #print(currentCharacter)
        else:
            #print(MyEvents.DAH)
            currentCharacter.append(MyEvents.DAH)
            if (myConfig['withsound']):
                winsound.MessageBeep(myConfig['SoundDah'].toInt()[0])
            #print(currentCharacter)       
        if myConfig['debug']:
            print("Duration of keypress: " + str(msSinceLastKeyDown))
    else:
        if (event.KeyID == myConfig['keyone']):
            currentCharacter.append(MyEvents.DIT)
            if (myConfig['withsound']):
                winsound.MessageBeep(myConfig['SoundDit'].toInt()[0])
        else:
            currentCharacter.append(MyEvents.DAH)
            if (myConfig['withsound']):
                winsound.MessageBeep(myConfig['SoundDah'].toInt()[0])
            
    hm.KeyDown = OnKeyboardEventDown
    hm.KeyUp = disableKeyUpDown

    return False

#unused
def parseConfigFile():
    global maxDitTime, minLetterPause, debug
    config = ConfigParser.RawConfigParser()
    config.read('MorseCode.cfg')
    config.sections
    maxDitTime = config.getint('Input', 'maxDitTime')
    minLetterPause = config.getint('Input', 'minLetterPause')
    debug = config.getboolean('Various', 'debug')
    
def createMapping():
    global normalmapping, numbermapping, mousemapping, actions
    actions = enum(A=win32api.VkKeyScan('a'), B=win32api.VkKeyScan('b'), C=win32api.VkKeyScan('c'), D=win32api.VkKeyScan('d'), 
                   E=win32api.VkKeyScan('e'), F=win32api.VkKeyScan('f'), G=win32api.VkKeyScan('g'), H=win32api.VkKeyScan('h'), 
                   I=win32api.VkKeyScan('i'), J=win32api.VkKeyScan('j'), K=win32api.VkKeyScan('k'), L=win32api.VkKeyScan('l'), 
                   M=win32api.VkKeyScan('m'), N=win32api.VkKeyScan('n'), O=win32api.VkKeyScan('o'), P=win32api.VkKeyScan('p'), 
                   Q=win32api.VkKeyScan('q'), R=win32api.VkKeyScan('r'), S=win32api.VkKeyScan('s'), T=win32api.VkKeyScan('t'),
                   U=win32api.VkKeyScan('u'), V=win32api.VkKeyScan('v'), W=win32api.VkKeyScan('w'), X=win32api.VkKeyScan('x'), 
                   Y=win32api.VkKeyScan('y'), Z=win32api.VkKeyScan('z'), ONE=win32api.VkKeyScan('1'), TWO=win32api.VkKeyScan('2'), 
                   THREE=win32api.VkKeyScan('3'), FOUR=win32api.VkKeyScan('4'), FIVE=win32api.VkKeyScan('5'), SIX=win32api.VkKeyScan('6'), 
                   SEVEN=win32api.VkKeyScan('7'), EIGHT=win32api.VkKeyScan('8'), NINE=win32api.VkKeyScan('9'), 
                   ZERO=win32api.VkKeyScan('0'), DOT=win32api.VkKeyScan('.'), COMMA=win32api.VkKeyScan(','), 
                   QUESTION=win32api.VkKeyScan('?'), EXCLAMATION=win32api.VkKeyScan('!'), COLON=win32api.VkKeyScan(':'), 
                   SEMICOLON=win32api.VkKeyScan(';'), AT=win32api.VkKeyScan('@'), BASH=win32api.VkKeyScan('#'),
                   DOLLAR=win32api.VkKeyScan('$'), PERCENT=win32api.VkKeyScan('%'), AMPERSAND=win32api.VkKeyScan('&'), 
                   STAR=win32con.VK_MULTIPLY, PLUS=win32con.VK_ADD, MINUS=win32con.VK_SUBTRACT, 
                   EQUALS=win32api.VkKeyScan('='), FSLASH=win32api.VkKeyScan('/'), BSLASH=win32api.VkKeyScan('\\'), 
                   SINGLEQUOTE=win32api.VkKeyScan('\''), DOUBLEQUOTE=win32api.VkKeyScan('"'), OPENBRACKET=win32api.VkKeyScan('('), 
                   CLOSEBRACKET=win32api.VkKeyScan(')'), LESSTHAN=win32api.VkKeyScan('<'), MORETHAN=win32api.VkKeyScan('>'), 
                   CIRCONFLEX=win32api.VkKeyScan('^'), ENTER=win32con.VK_RETURN, SPACE=win32con.VK_SPACE,
                   BACKSPACE=win32con.VK_BACK, TAB=win32con.VK_TAB, TABLEFT=win32con.VK_TAB, UNDERSCORE=win32api.VkKeyScan('_'), 
                   PAGEUP=win32con.VK_PRIOR, PAGEDOWN=win32con.VK_NEXT, 
                   LEFTARROW=win32con.VK_LEFT, RIGHTARROW=win32con.VK_RIGHT,
                   UPARROW=win32con.VK_UP, DOWNARROW=win32con.VK_DOWN, ESCAPE=win32con.VK_ESCAPE, HOME=win32con.VK_HOME, 
                   END=win32con.VK_END, INSERT=win32con.VK_INSERT, DELETE=win32con.VK_DELETE, STARTMENU=win32con.VK_MENU, 
                   SHIFT=win32con.VK_SHIFT, ALT=win32con.VK_MENU,
                   CTRL=win32con.VK_CONTROL, WINDOWS=win32con.VK_LWIN, APPKEY=win32con.VK_LWIN, CAPSLOCK=win32con.VK_CAPITAL, 
                   MOUSEMODE=285, NUMBERMODE=286, REPEATMODE=400, SOUND=288, CODESET=289,
                   F1=win32con.VK_F1, F2=win32con.VK_F2, F3=win32con.VK_F3, F4=win32con.VK_F4, F5=win32con.VK_F5, F6=win32con.VK_F6, 
                   F7=win32con.VK_F7, F8=win32con.VK_F8, F9=win32con.VK_F9, F10=win32con.VK_F10, F11=win32con.VK_F11, 
                   F12=win32con.VK_F12, MOUSERIGHT=302,
                   MOUSEUP=303, MOUSECLICKLEFT=304, MOUSEDBLCLICKLEFT=305, MOUSECLKHLDLEFT=306, MOUSEUPLEFT=307, MOUSEDOWNLEFT=308,
                   MOUSERELEASEHOLD=309, MOUSELEFT=310, MOUSEDOWN=311, MOUSECLICKRIGHT=312, MOUSEDBLCLICKRIGHT=313,
                   MOUSECLKHLDRIGHT=314, MOUSEUPRIGHT=315, MOUSEDOWNRIGHT=316)
    normalmapping = dict({'12':actions.A, '2111':actions.B, '2121':actions.C, '211':actions.D, '1':actions.E, '1121':actions.F, 
                          '221':actions.G, '1111':actions.H, '11':actions.I, '1222':actions.J, '212':actions.K, '1211':actions.L, 
                          '22':actions.M, '21':actions.N, '222':actions.O, '1221':actions.P, '2212':actions.Q, '121':actions.R, 
                          '111':actions.S, '2':actions.T, '112':actions.U, '1112':actions.V, '122':actions.W, '2112':actions.X,
                          '2122':actions.Y, '2211':actions.Z, '12222':actions.ONE, '11222':actions.TWO, '11122':actions.THREE, 
                          '11112':actions.FOUR, '11111':actions.FIVE, '21111':actions.SIX, '22111':actions.SEVEN, '22211':actions.EIGHT, 
                          '22221':actions.NINE, '22222':actions.ZERO, '121212':actions.DOT, '221122':actions.COMMA, 
                          '112211':actions.QUESTION, '121122':actions.EXCLAMATION, '212121':actions.COLON, '11121':actions.SEMICOLON, 
                          '12221':actions.AT, '21222':actions.BASH, '211121':actions.DOLLAR, '122121':actions.PERCENT, 
                          '21122':actions.AMPERSAND, '12111':actions.STAR, '12211':actions.PLUS, '2221':actions.MINUS, 
                          '12212':actions.EQUALS, '22112':actions.FSLASH, '211111':actions.BSLASH, '121221':actions.SINGLEQUOTE, 
                          '22122':actions.DOUBLEQUOTE, '111221':actions.OPENBRACKET, '211221':actions.CLOSEBRACKET, 
                          '121112':actions.LESSTHAN, '221121':actions.MORETHAN, '212112':actions.CIRCONFLEX, '1212':actions.ENTER, 
                          '1122':actions.SPACE, '2222':actions.BACKSPACE, '21221':actions.TAB, '221211':actions.TABLEFT, 
                          '11221':actions.UNDERSCORE, '222112':actions.PAGEUP, '222121':actions.PAGEDOWN, '222212':actions.LEFTARROW, 
                          '222221':actions.RIGHTARROW, '222211':actions.UPARROW, '222222':actions.DOWNARROW, '11211':actions.ESCAPE, 
                          '111121':actions.HOME, '21211':actions.END, '12112':actions.INSERT, '21121':actions.DELETE, 
                          '221111':actions.STARTMENU, '11212':actions.SHIFT, '12122':actions.ALT, '21212':actions.CTRL, 
                          '112122':actions.WINDOWS, '211122':actions.APPKEY, '112121':actions.CAPSLOCK, '22121':actions.MOUSEMODE, 
                          '21112':actions.NUMBERMODE, '121121':actions.REPEATMODE, '121211':actions.SOUND, '22212':actions.CODESET, 
                          '112222':actions.F1, '111222':actions.F2, '111122':actions.F3, '111112':actions.F4, '111111':actions.F5,
                          '121111':actions.F6, '122111':actions.F7, '122211':actions.F8, '122221':actions.F9, '122222':actions.F10, 
                          '212222':actions.F11, '211222':actions.F12})
    mousemapping = dict({'1':actions.MOUSERIGHT, '11':actions.MOUSEUP, '21':actions.MOUSECLICKLEFT, '221':actions.MOUSEDBLCLICKLEFT, 
                         '222':actions.MOUSECLKHLDLEFT, '1122':actions.MOUSEUPLEFT, '2222':actions.MOUSEDOWNLEFT, 
                         '121':actions.MOUSERELEASEHOLD, '2':actions.MOUSELEFT, '22':actions.MOUSEDOWN, '12':actions.MOUSECLICKRIGHT, 
                         '112':actions.MOUSEDBLCLICKRIGHT, '111':actions.MOUSECLKHLDRIGHT, '1111':actions.MOUSEUPRIGHT, 
                         '2211':actions.MOUSEDOWNRIGHT})
    numbermapping = dict({'1':actions.ONE, '2':actions.TWO, '12':actions.THREE, '11':actions.FOUR, '21':actions.FIVE, '22':actions.SIX, 
                          '122':actions.SEVEN, '112':actions.EIGHT, '111':actions.NINE, '211':actions.ZERO, '221':actions.PLUS, 
                          '222':actions.MINUS, '212':actions.FSLASH, '121':actions.STAR, '1212':actions.ENTER, '121212':actions.DOT}) 
    
def Init():
    global MyEvents, currentCharacter, hm, repeaton, repeatkey
    createMapping()
    MyEvents = enum(DIT=1, DAH=2)
    currentCharacter = []
    repeaton = False 
    repeatkey = None

def Go():
    global hm
    hm = pyHook.HookManager()
    hm.KeyDown = OnKeyboardEventDown
    hm.KeyUp = OnKeyboardEventUp
    hm.HookKeyboard()
    pythoncom.PumpMessages()

class Window(QtGui.QDialog):
    def __init__(self):
        super(Window, self).__init__()

        self.createIconGroupBox()

        self.createActions()
        self.createTrayIcon()
        
        self.trayIcon.activated.connect(self.iconActivated)

        self.GOButton.clicked.connect(self.goForIt)
        
        self.withSound.clicked.connect(self.updateAudioProperties)
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.iconGroupBox)
        self.setLayout(mainLayout)
        
        self.setIcon()
        
        self.trayIcon.show()

        self.setWindowTitle("MorseWriter")
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
            QtGui.QMessageBox.information(self, "MorseWriter", "The program will run in the system tray. To terminate the program, choose <b>Quit</b> in the context menu of the system tray entry.")
            self.hide()
        
        myConfig = dict();
        myConfig['onekey'] = self.keySelectionRadioOneKey.isChecked()
        myConfig['keyone'] = self.iconComboBoxKeyOne.itemData(self.iconComboBoxKeyOne.currentIndex())
        myConfig['keytwo'] = self.iconComboBoxKeyTwo.itemData(self.iconComboBoxKeyTwo.currentIndex())
        myConfig['maxDitTime'] = self.maxDitTimeEdit.text()
        myConfig['minLetterPause'] = self.minLetterPauseEdit.text()
        myConfig['withsound'] = self.withSound.isChecked() 
        myConfig['SoundDit'] = self.iconComboBoxSoundDit.itemData(self.iconComboBoxSoundDit.currentIndex())
        myConfig['SoundDah'] = self.iconComboBoxSoundDah.itemData(self.iconComboBoxSoundDah.currentIndex())
        myConfig['debug'] = self.withDebug.isChecked()
        myConfig['off'] = False
        if myConfig['debug']:
            print "Config: " + str(myConfig['onekey']) + " / " + str(myConfig['keyone']) + " / " + str(myConfig['keytwo']) + " / " + str(myConfig['maxDitTime']) + " / " + str(myConfig['minLetterPause'])
        

        Init()
        Go()

    def setVisible(self, visible):
        self.minimizeAction.setEnabled(visible)
        self.maximizeAction.setEnabled(not self.isMaximized())
        self.restoreAction.setEnabled(self.isMaximized() or not visible)
        super(Window, self).setVisible(visible)

    def closeEvent(self, event):
        QtGui.qApp.quit
        sys.exit()
        
    def setIcon(self):
        icon = QtGui.QIcon(':/morse-writer.ico')
        self.trayIcon.setIcon(icon)
        self.setWindowIcon(icon)

    def iconActivated(self, reason):
        if reason in (QtGui.QSystemTrayIcon.Trigger, QtGui.QSystemTrayIcon.DoubleClick):
            self.iconComboBox.setCurrentIndex((self.iconComboBox.currentIndex() + 1) % self.iconComboBox.count())
        elif reason == QtGui.QSystemTrayIcon.MiddleClick:
            self.showMessage()

    def showMessage(self):
        icon = QtGui.QSystemTrayIcon.MessageIcon(self.typeComboBox.itemData(self.typeComboBox.currentIndex()))
        self.trayIcon.showMessage(self.titleEdit.text(), self.bodyEdit.toPlainText(), icon, self.durationSpinBox.value() * 1000)

    def createIconGroupBox(self):
        self.iconGroupBox = QtGui.QGroupBox("Input Settings")
        
        self.keySelectionRadioOneKey = QtGui.QRadioButton("One Key");
        self.keySelectionRadioTwoKey = QtGui.QRadioButton("Two Key");
        
        inputSettingsLayout = QtGui.QVBoxLayout()
        
        inputRadioButtonsLayout = QtGui.QHBoxLayout()
        inputRadioButtonsLayout.addWidget(self.keySelectionRadioOneKey)
        inputRadioButtonsLayout.addWidget(self.keySelectionRadioTwoKey)
        inputSettingsLayout.addLayout(inputRadioButtonsLayout)       

        inputKeyComboBoxesLayout = QtGui.QHBoxLayout()
        self.iconComboBoxKeyOne = QtGui.QComboBox()
        self.iconComboBoxKeyOne.addItem("SPACE", win32con.VK_SPACE)
        self.iconComboBoxKeyOne.addItem("ENTER", win32con.VK_RETURN)
        self.iconComboBoxKeyOne.addItem("1", win32api.VkKeyScan('1'))
        self.iconComboBoxKeyOne.addItem("2", win32api.VkKeyScan('2'))
        self.iconComboBoxKeyOne.addItem("Z", win32api.VkKeyScan('z'))
        self.iconComboBoxKeyOne.addItem("X", win32api.VkKeyScan('x'))
        self.iconComboBoxKeyOne.addItem("F8", win32con.VK_F8)
        self.iconComboBoxKeyOne.addItem("F9", win32con.VK_F9)
        self.iconComboBoxKeyTwo = QtGui.QComboBox()
        self.iconComboBoxKeyTwo.addItem("ENTER", win32con.VK_RETURN)
        self.iconComboBoxKeyTwo.addItem("2", win32api.VkKeyScan('2'))
        self.iconComboBoxKeyTwo.addItem("Z", win32api.VkKeyScan('z'))
        self.iconComboBoxKeyTwo.addItem("F8", win32con.VK_F8)
        inputKeyComboBoxesLayout.addWidget(self.iconComboBoxKeyOne)
        inputKeyComboBoxesLayout.addWidget(self.iconComboBoxKeyTwo)
        inputSettingsLayout.addLayout(inputKeyComboBoxesLayout)

        self.keySelectionRadioOneKey.toggled.connect(self.iconComboBoxKeyTwo.setDisabled)
        self.keySelectionRadioTwoKey.toggled.connect(self.iconComboBoxKeyTwo.setEnabled)        
        self.keySelectionRadioOneKey.click();     

        
        maxDitTimeLabel = QtGui.QLabel("MaxDitTime (ms):")
        self.maxDitTimeEdit = QtGui.QLineEdit("350")
        minLetterPauseLabel = QtGui.QLabel("minLetterPause (ms):")
        self.minLetterPauseEdit = QtGui.QLineEdit("1000")
        TimingsLayout = QtGui.QGridLayout()
        TimingsLayout.addWidget(maxDitTimeLabel, 0, 0)
        TimingsLayout.addWidget(self.maxDitTimeEdit, 0, 1, 1, 4)
        TimingsLayout.addWidget(minLetterPauseLabel, 1, 0)
        TimingsLayout.addWidget(self.minLetterPauseEdit, 1, 1, 2, 4)
        TimingsLayout.setRowStretch(4, 1)
        inputSettingsLayout.addLayout(TimingsLayout)
        
        self.withDebug = QtGui.QCheckBox("Debug On")
        self.withDebug.setChecked(False)
        inputSettingsLayout.addWidget(self.withDebug)
        
        self.withSound = QtGui.QCheckBox("Audible beeps")
        self.withSound.setChecked(True)
        inputSettingsLayout.addWidget(self.withSound)

        self.iconComboBoxSoundDit = QtGui.QComboBox()
        self.iconComboBoxSoundDit.addItem("MB_OK", winsound.MB_OK)
        self.iconComboBoxSoundDit.addItem("MB_ICONQUESTION", winsound.MB_ICONQUESTION)
        self.iconComboBoxSoundDit.addItem("MB_ICONHAND", winsound.MB_ICONHAND)
        self.iconComboBoxSoundDit.addItem("MB_ICONEXCLAMATION", winsound.MB_ICONEXCLAMATION)
        self.iconComboBoxSoundDit.addItem("MB_ICONASTERISK", winsound.MB_ICONASTERISK)
        self.iconComboBoxSoundDit.addItem("DEFAULT", -1)

        self.iconComboBoxSoundDah = QtGui.QComboBox()
        self.iconComboBoxSoundDah.addItem("MB_OK", winsound.MB_OK)
        self.iconComboBoxSoundDah.addItem("MB_ICONQUESTION", winsound.MB_ICONQUESTION)
        self.iconComboBoxSoundDah.addItem("MB_ICONHAND", winsound.MB_ICONHAND)
        self.iconComboBoxSoundDah.addItem("MB_ICONEXCLAMATION", winsound.MB_ICONEXCLAMATION)
        self.iconComboBoxSoundDah.addItem("MB_ICONASTERISK", winsound.MB_ICONASTERISK)
        self.iconComboBoxSoundDah.addItem("DEFAULT", -1)

        DitSoundLabel = QtGui.QLabel("Dit sound: ")
        DahSoundLabel = QtGui.QLabel("Dah sound: ")
        SoundConfigLayout = QtGui.QGridLayout()
        SoundConfigLayout.addWidget(DitSoundLabel, 0, 0)
        SoundConfigLayout.addWidget(self.iconComboBoxSoundDit, 0, 1, 1, 4)
        SoundConfigLayout.addWidget(DahSoundLabel, 1, 0)
        SoundConfigLayout.addWidget(self.iconComboBoxSoundDah, 1, 1, 1, 4)
        
        inputSettingsLayout.addLayout(SoundConfigLayout)
        self.GOButton = QtGui.QPushButton("GO!")
        inputSettingsLayout.addWidget(self.GOButton)
        
        self.iconGroupBox.setLayout(inputSettingsLayout)

    def toggleOnOff(self):
        global myConfig
        if myConfig['off']:
            myConfig['off'] = False
        else:
            myConfig['off'] = True

    def createActions(self):
        self.minimizeAction = QtGui.QAction("Minimize", self, triggered=self.hide)
        self.maximizeAction = QtGui.QAction("Maximize", self, triggered=self.showMaximized)
        self.restoreAction = QtGui.QAction("Restore", self, triggered=self.showNormal)
        self.onOffAction = QtGui.QAction("OnOff", self, triggered=self.toggleOnOff)
        self.quitAction = QtGui.QAction("Quit", self, triggered=sys.exit)

    def createTrayIcon(self):
        self.trayIconMenu = QtGui.QMenu(self)
        self.trayIconMenu.addAction(self.minimizeAction)
        self.trayIconMenu.addAction(self.maximizeAction)
        self.trayIconMenu.addAction(self.restoreAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.onOffAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAction)
        self.trayIcon = QtGui.QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)

    if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
        QtGui.QMessageBox.critical(None, "MorseWriter", "I couldn't detect any system tray on this system.")
        sys.exit(1)

    QtGui.QApplication.setQuitOnLastWindowClosed(False)

    window = Window()
    window.show()
    sys.exit(app.exec_())
