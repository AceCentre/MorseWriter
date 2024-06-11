from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
import sys

class KeyListenerWidget(QWidget):
    keyEvent = pyqtSignal(str, bool)  # Emit key name and press/release status

    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)  # Ensure widget can receive key events

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.keyEvent.emit('space', True)
        elif event.key() == Qt.Key_Return:
            self.keyEvent.emit('enter', True)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.keyEvent.emit('space', False)
        elif event.key() == Qt.Key_Return:
            self.keyEvent.emit('enter', False)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.key_listener_widget = KeyListenerWidget()
        self.key_listener_widget.keyEvent.connect(self.handle_key_event)

        layout = QVBoxLayout()

        layout.addWidget(self.key_listener_widget)  # Add the key listener widget to the layout

        start_button = QPushButton("Start Key Listener")
        start_button.clicked.connect(self.startKeyListener)
        layout.addWidget(start_button)

        stop_button = QPushButton("Stop Key Listener")
        stop_button.clicked.connect(self.stopKeyListener)
        layout.addWidget(stop_button)

        self.setLayout(layout)

    def handle_key_event(self, key_name, is_pressed):
        action = "pressed" if is_pressed else "released"
        print(f"Key {key_name} {action}")

    def startKeyListener(self):
        self.key_listener_widget.setFocus()
        print("Key listener started")

    def stopKeyListener(self):
        self.key_listener_widget.clearFocus()
        print("Key listener stopped")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())
