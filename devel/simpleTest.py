import sys
import keyboard
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import QThread, pyqtSignal, QTimer

class KeyListenerThread(QThread):
    keyPressed = pyqtSignal(str, bool)  # Emit key name and press/release status

    def __init__(self, configured_keys):
        super().__init__()
        self.configured_keys = configured_keys  # These keys should be in the format expected by `keyboard`

    def run(self):
        # Set up hooks only for the specified keys with suppression
        for key in self.configured_keys:
            keyboard.on_press_key(key, self.on_press, suppress=True)
            keyboard.on_release_key(key, self.on_release, suppress=True)
        self.exec_()  # Start the Qt event loop

    def on_press(self, event):
        self.keyPressed.emit(event.name, True)

    def on_release(self, event):
        self.keyPressed.emit(event.name, False)

class MainWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Key Listener Example")
        self.resize(300, 200)
        self.startKeyListener()

    def startKeyListener(self):
        # Define keys that need to be suppressed
        key_names = self.get_configured_keys()
        if key_names:
            if not hasattr(self, 'listenerThread'):
                self.listenerThread = KeyListenerThread(configured_keys=key_names)
                self.listenerThread.keyPressed.connect(self.handleKeyPress)
                self.listenerThread.start()

    def get_configured_keys(self):
        # Your logic to determine which keys to suppress
        return ['space', 'enter', 'right ctrl']  # Example keys

    def handleKeyPress(self, key, is_press):
        action = "Pressed" if is_press else "Released"
        print(f"Key {action}: {key}")
        
    
    def closeEvent(self, event):
        # Ensure all hooks are cleared when the window is closed
        keyboard.unhook_all()
        self.listenerThread.quit()
        self.listenerThread.wait()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
