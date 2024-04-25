import sys
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import pyqtSignal, QThread
from pynput.keyboard import Listener, Key, KeyCode

class KeyListenerThread(QThread):
    keyEvent = pyqtSignal(str, bool)  # Emit key description and press/release status

    def __init__(self, configured_keys):
        super().__init__()
        self.configured_keys = configured_keys
        logging.debug(f"KeyListener initialized with keys: {[key.name for key in self.configured_keys if hasattr(key, 'name')] + [key.char for key in self.configured_keys if hasattr(key, 'char') and key.char]}")

    def run(self):
        with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

    def on_press(self, key):
        if any(key == k for k in self.configured_keys):
            key_description = self.get_key_description(key)
            self.keyEvent.emit(key_description, True)

    def on_release(self, key):
        if any(key == k for k in self.configured_keys):
            key_description = self.get_key_description(key)
            self.keyEvent.emit(key_description, False)

    def get_key_description(self, key):
        if hasattr(key, 'char') and key.char:
            return key.char
        elif hasattr(key, 'name'):
            return key.name
        return 'Unknown key' 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt with Pynput")
        self.resize(300, 200)

        pynput_keys = {
            "SPACE": Key.space, "ENTER": Key.enter,
            "ONE": KeyCode.from_char('1'), "TWO": KeyCode.from_char('2'),
            "Z": KeyCode.from_char('z'), "X": KeyCode.from_char('x'),
            "F8": Key.f8, "F9": Key.f9,
            "RCTRL": Key.ctrl_r, "LCTRL": Key.ctrl_l,
            "RSHIFT": Key.shift_r, "LSHIFT": Key.shift_l,
            "LALT": Key.alt_l
        }

        key_names = ["SPACE", "ENTER", "RCTRL"]
        configured_keys = [pynput_keys[key] for key in key_names]

        self.listenerThread = KeyListenerThread(configured_keys=configured_keys)
        self.listenerThread.keyEvent.connect(self.handle_key_event)
        self.listenerThread.start()

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
            
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
