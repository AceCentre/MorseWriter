# from time import sleep
from pynput import keyboard
from pynput.keyboard import Key, Listener, Controller

controller = Controller()

def on_press(key):
    if key == Key.esc:
        # Stop listener
        return False

    elif key == Key.f1:
        controller.press(Key.enter)
        controller.release(Key.enter)
        controller.type('a')

# Collect events until released
with Listener(on_press=on_press) as listener:
# with Listener(on_press=on_press, suppress=True) as listener:
    listener.join()