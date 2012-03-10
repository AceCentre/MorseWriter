*MorseWriter*

This is a small system tray app designed in Python to interpret one or two key presses pressed in a set way (morse) and convert them to the key equivalent. This should mean that a user who has good timing can access the entire computer and write. 

**Requirements**
Currently built for Windows. Let us know how you get on with different variants of Windows. Plan is to port this to Mac after v2. 

**Usage**

*   [Download the MorseWriter Application and Code Chart from here](https://github.com/downloads/willwade/MorseWriter/MorseWriter.zip)
*   Run the MorseWriter.exe 
*   Select your options
*   Note the two key option: the key on the left hand pull down menu relates to dit (*) and one on the right relates to dah (-)
*   Set your sounds
*   Press go
*   Minimise the black debug window. NB: If you close it you are closing the app. 
*   Note that all normal key entry is now disabled. To halt the script use a mouse to navigate to the system tray icon and quit the app

**Tips for first use**

* Open up the code chart document or print it!
* Use notepad to test your typing skills
* To get used to typing you have to first get used to the speed of things. Just try a e and a t for starters. 

**Issues:**

* Debug window needs to be minimised even if debug switched off
* If you set to two key mode you need to be careful not to set both keys as input
* 1 & 2 input keys relate to the keys above the letters on the keyboard - not a numeric keypad
* Sounds can't be edited - these are from the system folder 

**Tips for Building yourself**

- Python 2.6 or earlier for [pyinstaller](http://www.pyinstaller.org/) 
- [PyHook](http://sourceforge.net/projects/uncassist/) 
- [PyWin32](http://sourceforge.net/projects/pywin32/)
- [PyQt](http://www.riverbankcomputing.com/software/pyqt/intro)


    python Configure.py
    python Makespec.py --onefile path_to_your_morsecodegui.py 
    python Build.py path_to_the_Morsecodegui.spec

**Credits**

* DavidDW for pure awesomeness
* [Darci USB for code conversion](http://www.westest.com/darci/index.html) 
* Andy/[ACE North](http://www.ace-north.org.uk/) for inspiration 
* [Jim Rubin and others](http://www.makoa.org/jlubin/morsecode.htm)

Please contact me if you intend to fork this or do anything fun with it - will AT e-wade.net   

Enjoy! 