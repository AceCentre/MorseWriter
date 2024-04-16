import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import pyqtSignal, QObject, QThread
from pynput.keyboard import Listener, Key

class KeyboardListenerThread(QThread):
    # Define a signal that sends the key pressed
    keyPressed = pyqtSignal(str)

    def __init__(self):
        super(KeyboardListenerThread, self).__init__()

    def run(self):
        # This method runs in the new thread
        with Listener(on_press=self.on_press) as listener:
            listener.join()

    def on_press(self, key):
        # When a key is pressed, emit the keyPressed signal
        try:
            self.keyPressed.emit(key.char)
        except AttributeError:
            # Handle special keys here if needed
            if key == Key.esc:
                return False  # Stop listener

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Qt with Pynput")
        self.resize(300, 200)

        # Initialize the listener thread
        self.listenerThread = KeyboardListenerThread()
        self.listenerThread.keyPressed.connect(self.handle_key_press)
        self.listenerThread.start()

    def handle_key_press(self, key):
        print(f"Key pressed: {key}")
        # Here you can update the GUI or do other tasks

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
