from pynput.keyboard import Controller as KeyboardController, Listener, Key, KeyCode
from pynput.mouse import Controller as MouseController, Button
from nava import play
import keyboard
import pprint


def convert_to_keyboard_lib_format(key_data):
    # Mapping of pynput keys to keyboard keys for modifiers
    pynput_to_keyboard_modifiers = {
        'ctrl_l': 'left ctrl',
        'ctrl_r': 'right ctrl',
        'shift_l': 'left shift',
        'shift_r': 'right shift',
        'alt_l': 'left alt',
        'alt_r': 'right alt',
        'cmd_l': 'left windows',
        'cmd_r': 'right windows'
    }

    # Initialize the new dictionary for keyboard library compatibility
    key_data_keyboard = {}

    for key, value in key_data.items():
        label, key_code_pynput, character, arg = value

        if key_code_pynput is None:
            # Handle None cases by setting a placeholder or continuing without processing
            key_code_keyboard = 'unknown'
        elif hasattr(key_code_pynput, 'char'):
            # Convert to simple character keys
            key_code_keyboard = key_code_pynput.char
        else:
            # For special keys like modifiers, function keys, etc.
            key_code_name = key_code_pynput.name if key_code_pynput else 'unknown'
            if key_code_name in pynput_to_keyboard_modifiers:
                key_code_keyboard = pynput_to_keyboard_modifiers[key_code_name]
            else:
                # Convert Key names like 'Key.space' to 'space'
                key_code_keyboard = key_code_name.replace('Key.', '').replace('_', ' ')

        # Add the converted key data to the new dictionary
        key_data_keyboard[key] = {
            'label': label,
            'key_code': key_code_keyboard,  # Adjusted key code for keyboard lib
            'character': character,
            'arg': arg
        }

    return key_data_keyboard

# Example usage with the original dictionary data
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

converted_key_data = convert_to_keyboard_lib_format(key_data)
def print_formatted_key_data(key_data):
    for key, value in key_data.items():
        print(f'"{key}": {value},')


print_formatted_key_data(converted_key_data)
