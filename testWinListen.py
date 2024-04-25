import sys
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from pynput.keyboard import Listener, Key


class KeyListenerWorker(QThread):
    keyPressed = pyqtSignal(str, bool)  

    def __init__(self, configured_keys=None):
        super(KeyListenerWorker, self).__init__()
        self.configured_keys = configured_keys or []
        self.listener = None

    def run(self):
        with Listener(on_press=self.on_press, on_release=self.on_release) as self.listener:
            self.listener.join()

    def on_press(self, key):
        key_description = self.get_key_description(key)
        self.keyPressed.emit(key_description, True)
        # Block the key if it is in the configured keys
        return False if key_description in self.configured_keys else True

    def on_release(self, key):
        key_description = self.get_key_description(key)
        self.keyPressed.emit(key_description, False)
        # Block the key if it is in the configured keys
        return False if key_description in self.configured_keys else True

    def get_key_description(self, key):
        if hasattr(key, 'char') and key.char:
            return key.char
        return str(key)
            
class MainWindow(QDialog):
    def __init__(self, configured_keys):
        super().__init__()
        self.setWindowTitle("KeyListener Running")
        self.resize(300, 100)

        self.listener_thread = KeyListenerWorker(configured_keys=configured_keys)
        self.listener_thread.keyPressed.connect(self.handle_key_event)
        self.listener_thread.start()

    def handle_key_event(self, key, is_press):
        action = "Pressed" if is_press else "Released"
        print(f"{action}: {key}")

    def closeEvent(self, event):
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    configured_keys = [str(Key.space)]  # Configure to react to the space bar
    mainWindow = MainWindow(configured_keys)
    mainWindow.show()
    sys.exit(app.exec_())
