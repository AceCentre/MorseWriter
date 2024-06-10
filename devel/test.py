import sys
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import QThread, pyqtSignal
from pynput.keyboard import Listener, Key

class KeyListenerThread(QThread):
    keyPressed = pyqtSignal(str)

    def run(self):
        with Listener(on_press=self.on_press) as listener:
            listener.join()

    def on_press(self, key):
        try:
            # Emit the character pressed
            self.keyPressed.emit(key.char)
        except AttributeError:
            # If the key does not have a character representation (like special keys)
            self.keyPressed.emit(str(key))

class MainWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Key Listener Example")
        self.resize(300, 200)

        # Initialize and start the key listener thread
        self.listenerThread = KeyListenerThread()
        self.listenerThread.keyPressed.connect(self.handleKeyPress)
        self.listenerThread.start()

    def handleKeyPress(self, key):
        print(f"Key pressed: {key}")

    def closeEvent(self, event):
        # Stop the listener thread cleanly
        self.listenerThread.quit()
        self.listenerThread.wait()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
