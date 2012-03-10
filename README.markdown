MorseWriter
-----------

This is a small system tray app designed in Python to interpret one or two key presses pressed in a set way (morse) and convert them to the key equivalent. This should mean that a user who has good timing can access the entire computer to write and control their machine - potentially with one or two keys or switches. 

For code, bug tracking and feature requests see [https://github.com/willwade/MorseWriter/](https://github.com/willwade/MorseWriter/)

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

* Look at the the code chart below or the separate document. Have it handy or print it!
* Use notepad to test your typing skills
* To get used to typing you have to first get used to the speed of things. Just try a e and a t for starters. 

**Issues:**

* Debug window needs to be minimised even if debug switched off
* If you set to two key mode you need to be careful not to set both keys as input
* 1 & 2 input keys relate to the keys above the letters on the keyboard - not a numeric keypad
* Sounds can't be edited - these are from the system folder 

**Tips for Building yourself**

You will need Python 2.6 or earlier for [pyinstaller](http://www.pyinstaller.org/). You will also need to install some extra libraries - notably [PyHook](http://sourceforge.net/projects/uncassist/), [PyWin32](http://sourceforge.net/projects/pywin32/) and [PyQt](http://www.riverbankcomputing.com/software/pyqt/intro)

    python Configure.py
    python Makespec.py --onefile path_to_your_morsecodegui.py 
    python Build.py path_to_the_Morsecodegui.spec

**Research**

For further research and reading material on the use of Morse in assistive technology see [http://www.citeulike.org/user/willwade/tag/morse](http://www.citeulike.org/user/willwade/tag/morse) as a starting point

**Credits**

* DavidDW for coding geniusness
* [Darci USB for code conversion](http://www.westest.com/darci/index.html) 
* Andy/Lisa/[ACE North](http://www.ace-north.org.uk/) for original thoughts 
* [Jim Rubin and others](http://www.makoa.org/jlubin/morsecode.htm)
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

\*NB:To type Control+V you need to first go into repeat mode then type V.