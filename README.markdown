MorseWriter
-----------

![](https://github.com/willwade/MorseWriter/raw/master/icon.png)
![](https://github.com/willwade/MorseWriter/raw/master/screenshot1.png)
![](https://github.com/willwade/MorseWriter/raw/master/screenshot2.png)

This is a small system tray app designed in Python to interpret one or two key presses pressed in a set way (morse) and convert them to the key equivalent. This should mean that a user who has good timing can access the entire computer to write and control their machine - potentially with one or two keys or switches. Mouse implementation is flaky right now.  

For code, bug tracking and feature requests see [https://github.com/willwade/MorseWriter/](https://github.com/willwade/MorseWriter/)

**Requirements**

Currently built for Windows. Let us know how you get on with different variants of Windows. Plan is to port this to Mac at some point. 

**Usage**

*   [Download the MorseWriter Application and Code Chart from here](https://github.com/downloads/willwade/MorseWriter/MorseWriterv2.zip)
*   Run the MorseWriter.exe 
*   Select your options
*   Note the two key option: the key on the left hand pull down menu relates to dit (*) and one on the right relates to dah (-)
*   If you want to use a third key for the return character (removing the need for good timing) then you can do that with the third dropdown
*   Press go
*   Minimise the coding window if needed
*   Minimise the black debug window. NB: If you close it you are closing the app. 
*   Note that all normal key entry is now disabled. To halt the script use a mouse to navigate to the system tray icon and quit the app
*   If you want to escape morse entry : ctrl+shift+p will pause it. 

**Tips for first use**

* Look at the the code chart below or the coding window. Have it handy or print it!
* Use notepad to test your typing skills
* To get used to typing you have to first get used to the speed of things. Just try a e and a t for starters. 
* Getting auditory feedback on the key entered may be useful. In which case you may find [this additional program](https://github.com/willwade/Scripting-Recipes-for-AT/tree/master/Autohotkey/SoundingKeyboardMouse#keyboard-sounder) of use. 

**Issues:**

* Debug window needs to be minimised even if debug switched off
* 1 & 2 input keys relate to the keys above the letters on the keyboard - not a numeric keypad

**Tips for Building yourself**

You will need Python 2.6 or earlier for [pyinstaller](http://www.pyinstaller.org/). You will also need to install some extra libraries - notably [PyHook](http://sourceforge.net/projects/uncassist/), [PyWin32](http://sourceforge.net/projects/pywin32/) and [PyQt](http://www.riverbankcomputing.com/software/pyqt/intro)

    python Configure.py
    python Makespec.py --onefile path_to_your_morsecodegui.py 
    python Build.py path_to_the_Morsecodegui.spec

**Getting Involved**

In order to start contributing code to the project, follow the steps below:

1. Fork this repo. For detailed instructions visit [http://help.github.com/fork-a-repo/](http://help.github.com/fork-a-repo/)
2. Hack away! but please make sure you follow [this branching model] (http://nvie.com/posts/a-successful-git-branching-model/). That means, make your pull requests against the **develop** branch, not the **master** branch. 

**Research**

For further research and reading material on the use of Morse in assistive technology see [http://www.citeulike.org/user/willwade/tag/morse](http://www.citeulike.org/user/willwade/tag/morse) as a starting point

**Credits**

* DavidDW for coding geniusness
* [Darci USB for code conversion](http://www.westest.com/darci/index.html) 
* Andy/Lisa/[ACE North](http://www.ace-north.org.uk/) for original thoughts 
* [Jim Lubin and others](http://www.makoa.org/jlubin/morsecode.htm)
* [The Noun Project](http://thenounproject.com/) for the icon 

Please contact me if you intend to fork this or do anything fun with it - will AT e-wade.net   

Enjoy!

<table border="0" cellspacing="0" cellpadding="0">
    <tr>
        <th colspan="6">MorseWriter Key Codes</th>
    </tr>
    <tr>
        <td style="white-space: nowrap"> <br />
        A<br />&bull;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        B<br />&mdash;&bull;&bull;&bull; </td>
        <td style="white-space: nowrap"> <br />
        C<br />&mdash;&bull;&mdash;&bull; </td>
        <td style="white-space: nowrap"> <br />
        D<br />&mdash;&bull;&bull; </td>
        <td style="white-space: nowrap"> <br />
        E<br />&bull;<br />  </td>
        <td style="white-space: nowrap"> <br />
        F<br />&bull;&bull;&mdash;&bull; </td>
    </tr>
    <tr>
        <td style="white-space: nowrap"> <br />
        G<br />&mdash;&mdash;&bull; </td>
        <td style="white-space: nowrap"> <br />
        H<br />&bull;&bull;&bull;&bull; </td>
        <td style="white-space: nowrap"> <br />
        I<br />&bull;&bull; </td>
        <td style="white-space: nowrap"> <br />
        J<br />&bull;&mdash;&mdash;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        K<br />&mdash;&bull;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        L<br />&bull;&mdash;&bull;&bull; </td>
    </tr>
    <tr>
        <td style="white-space: nowrap"> <br />
        M<br />&mdash;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        N<br />&mdash;&bull; </td>
        <td style="white-space: nowrap"> <br />
        O<br />&mdash;&mdash;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        P<br />&bull;&mdash;&mdash;&bull; </td>
        <td style="white-space: nowrap"> <br />
        Q<br />&mdash;&mdash;&bull;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        R<br />&bull;&mdash;&bull; </td>
    </tr>
    <tr>
        <td style="white-space: nowrap"> <br />
        S<br />&bull;&bull;&bull; </td>
        <td style="white-space: nowrap"> <br />
        T<br />             &mdash; </td>
        <td style="white-space: nowrap"> <br />
        U<br />&bull;&bull;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        V<br />&bull;&bull;&bull;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        W<br />&bull;&mdash;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        X<br />&mdash;&bull;&bull;&mdash; </td>
    </tr>
    <tr>
        <td style="white-space: nowrap"> <br />
        Y<br />&mdash;&bull;&mdash;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        Z<br />&mdash;&mdash;&bull;&bull; </td>
        <td style="white-space: nowrap"> <br />
        1<br />&bull;&mdash;&mdash;&mdash;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        2<br />&bull;&bull;&mdash;&mdash;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        3<br />&bull;&bull;&bull;&mdash;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        4<br />&bull;&bull;&bull;&bull;&mdash; </td>
    </tr>
    <tr>
        <td style="white-space: nowrap"> <br />
        5<br />&bull;&bull;&bull;&bull;&bull; </td>
        <td style="white-space: nowrap"> <br />
        6<br />&mdash;&bull;&bull;&bull;&bull; </td>
        <td style="white-space: nowrap"> <br />
        7<br />&mdash;&mdash;&bull;&bull;&bull; </td>
        <td style="white-space: nowrap"> <br />
        8<br />&mdash;&mdash;&mdash;&bull;&bull; </td>
        <td style="white-space: nowrap"> <br />
        9<br />&mdash;&mdash;&mdash;&mdash;&bull; </td>
        <td style="white-space: nowrap"> <br />
        0<br />&mdash;&mdash;&mdash;&mdash;&mdash; </td>
    </tr>
    <tr>
        <td style="white-space: nowrap"> <br />
           .<br />&bull;&mdash;&bull;&mdash;&bull;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        ,<br />&mdash;&mdash;&bull;&bull;&mdash;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        &#8204;<br />&bull;&bull;&mdash;&mdash;&bull;&bull; </td>
        <td style="white-space: nowrap"> <br />
        !<br />&bull;&mdash;&bull;&bull;&mdash;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        :<br />&mdash;&bull;&mdash;&bull;&mdash;&bull; </td>
        <td style="white-space: nowrap"> <br />
        ;<br />&bull;&bull;&bull;&mdash;&bull; </td>
    </tr>
    <tr>
        <td style="white-space: nowrap"> <br />
        @<br />    &bull;&mdash;&mdash;&mdash;&bull; </td>
        <td style="white-space: nowrap"> <br />
        #<br />     &mdash;&bull;&mdash;&mdash;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        $<br />&mdash;&bull;&bull;&bull;&mdash;&bull; </td>
        <td style="white-space: nowrap"> <br />
        %<br />&bull;&mdash;&mdash;&bull;&mdash;&bull; </td>
        <td style="white-space: nowrap"> <br />
        &<br />&mdash;&bull;&bull;&mdash;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        &lowast;<br />&bull;&mdash;&bull;&bull;&bull; </td>
    </tr>
    <tr>
        <td style="white-space: nowrap"> <br />
        +<br />&bull;&mdash;&mdash;&bull;&bull; </td>
        <td style="white-space: nowrap"> <br />
        &mdash;<br />&mdash;&mdash;&mdash;&bull; </td>
        <td style="white-space: nowrap"> <br />
        =<br />&bull;&mdash;&mdash;&bull;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        /<br />&mdash;&mdash;&bull;&bull;&mdash; </td>
        <td style="white-space: nowrap"> <br />
         \<br />&mdash;&bull;&bull;&bull;&bull;&bull; </td>
        <td style="white-space: nowrap"> <br />
        &apos;<br />&bull;&mdash;&bull;&mdash;&mdash;&bull; </td>
    </tr>
    <tr>
        <td style="white-space: nowrap"> <br />
        &quot;<br />&mdash;&mdash;&bull;&mdash;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        (<br />&bull;&bull;&bull;&mdash;&mdash;&bull; </td>
        <td style="white-space: nowrap"> <br />
        )<br />&mdash;&bull;&bull;&mdash;&mdash;&bull; </td>
        <td style="white-space: nowrap"> <br />
        <<br />&bull;&mdash;&bull;&bull;&bull;&mdash; </td>
        <td style="white-space: nowrap"> <br />
         ><br />&mdash;&mdash;&bull;&bull;&mdash;&bull; </td>
        <td style="white-space: nowrap"> <br />
        ^<br />&mdash;&bull;&mdash;&bull;&bull;&mdash; </td>
    </tr>
    <tr>
        <td style="white-space: nowrap"> <br />
        Enter <br />
        &bull;&mdash;&bull;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        Space <br />
          <br />&bull;&bull;&mdash;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        Back<br /> Space <br />
        &mdash;&mdash;&mdash;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        Tab <br />
        &mdash;&bull;&mdash;&mdash;&bull; </td>
        <td style="white-space: nowrap"> <br />
        Tab<br /> Left <br />
        &mdash;&mdash;&bull;&mdash;&bull;&bull; </td>
        <td style="white-space: nowrap"> <br />
        Uderscore<br /> <br />
        &bull;&bull;&mdash;&mdash;&bull; </td>
    </tr>
    <tr>
        <td style="white-space: nowrap"> <br />
        Page<br /> Up <br />
        &mdash;&mdash;&mdash;&bull;&bull;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        Page<br /> Dwn <br />
        &mdash;&mdash;&mdash;&bull;&mdash;&bull; </td>
        <td style="white-space: nowrap"> <br />
        Left<br /> Arrow <br />
        &mdash;&mdash;&mdash;&mdash;&bull;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        Right<br /> Arrow <br />
        &mdash;&mdash;&mdash;&mdash;&mdash;&bull; </td>
        <td style="white-space: nowrap"> <br />
        Up<br /> Arrow <br />
        &mdash;&mdash;&mdash;&mdash;&bull;&bull; </td>
        <td style="white-space: nowrap"> <br />
        Down<br /> Arrow <br />
        &mdash;&mdash;&mdash;&mdash;&mdash;&mdash; </td>
    </tr>
    <tr>
        <td style="white-space: nowrap"> <br />
        Escape <br />
        &bull;&bull;&mdash;&bull;&bull; </td>
        <td style="white-space: nowrap"> <br />
        Home <br />
        &bull;&bull;&bull;&bull;&mdash;&bull; </td>
        <td style="white-space: nowrap"> <br />
        End <br />
        &mdash;&bull;&mdash;&bull;&bull; </td>
        <td style="white-space: nowrap"> <br />
        Insert <br />
        &bull;&mdash;&bull;&bull;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        Delete <br />
        &mdash;&bull;&bull;&mdash;&bull; </td>
        <td style="white-space: nowrap"> <br />
        Start<br /> Menu <br />
        &mdash;&mdash;&bull;&bull;&bull;&bull; </td>
    </tr>
    <tr>
        <th  colspan="6"> 
            Modifier Keys
        </th>
    </tr>
    <tr>
        <td style="white-space: nowrap"> <br />
        Shift <br />
        &bull;&bull;&mdash;&bull;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        Alt <br />
        &bull;&mdash;&bull;&mdash;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        Ctrl <br />
        &mdash;&bull;&mdash;&bull;&mdash; </td>
        <td style="white-space: nowrap"> <br />
        Windows <br />
        &bull;&bull;&mdash;&bull;&mdash;&mdash; </td>
        <td  colspan="3"> <br />
        Application<br /> Key <br />
        &mdash;&bull;&bull;&bull;&mdash;&mdash; </td>
    </tr>
    <tr>
        <th colspan="6"> 
            Command Keys
        </th>
    </tr>
    <tr>
        <td style="white-space: nowrap"> <br />
        Caps Lock <br />
        &bull;&bull;&mdash;&bull;&mdash;&bull; </td>
        <td colspan="5"> <br />
        Repeat Mode* <br />
        &bull;&mdash;&bull;&bull;&mdash;&bull; </td>
    </tr>
    <tr>
        <td  colspan="6"><b>Function Keys</b><br />
        F1 &mdash; F10<br /> dot + number (F1 = &bull;&bull;&mdash;&mdash;&mdash;&mdash;)<br />F11 &amp; F12<br /> dash + number (F11 =&mdash;&bull;&mdash;&mdash;&mdash;&mdash;) </td>
    </tr>
</table>

\*NB: To type Control+V you need to first go into repeat mode, then type Control and then type V. To release the CTRL, press repeat again

## License

MorseWriter is licensed under the MIT License:

  Copyright (c) 2012 Will Wade (http://sourceymonkey.com/)

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in
  all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
  THE SOFTWARE.
