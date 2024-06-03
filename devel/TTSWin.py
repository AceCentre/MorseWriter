import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QRadioButton, QVBoxLayout, QWidget, QDialog, QComboBox, QSlider, QLabel, QHBoxLayout, QLineEdit, QColorDialog
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor
from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal
import pyttsx3
from tts_wrapper import PollyClient, PollyTTS, GoogleClient, GoogleTTS
import wave
import pyaudio
import json

def load_voices_from_json(engine_name):
    with open(f"{engine_name}_voices.json", 'r') as file:
        return json.load(file)



class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.parent = parent
        self.engine = pyttsx3.init()  # Default to system TTS engine
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # Engine selection combo box
        self.engineCombo = QComboBox()
        self.engineCombo.addItems(['System Voice (SAPI)', 'Polly', 'Google', 'Azure', 'Watson'])
        self.engineCombo.currentIndexChanged.connect(self.on_engine_change)
        layout.addWidget(QLabel("Select TTS Engine:"))
        layout.addWidget(self.engineCombo)

        # Voice selection combo box
        self.voiceCombo = QComboBox()
        self.update_voice_list()  # Populate voices for pyttsx3
        layout.addWidget(QLabel("Select Voice:"))
        layout.addWidget(self.voiceCombo)

        # Speech rate slider
        self.rateSlider = QSlider(Qt.Horizontal)
        self.rateSlider.setMinimum(50)
        self.rateSlider.setMaximum(400)
        self.rateSlider.setValue(self.engine.getProperty('rate'))
        self.rateSlider.setTickInterval(10)
        self.rateSlider.setTickPosition(QSlider.TicksBelow)
        layout.addWidget(QLabel("Set Speech Rate:"))
        layout.addWidget(self.rateSlider)

        # Credentials inputs for TTS services
        self.credentialsInput = QLineEdit()
        layout.addWidget(QLabel("Enter Credentials:"))
        layout.addWidget(self.credentialsInput)
        
        # Color picker for highlight color
        self.colorButton = QPushButton(f'Choose Highlight Color (Current: {self.parent.highlight_color.name()})', self)
        self.colorButton.clicked.connect(self.choose_color)
        layout.addWidget(self.colorButton)


        # Save button
        saveButton = QPushButton('Save Settings')
        saveButton.clicked.connect(self.save_settings)
        layout.addWidget(saveButton)

        self.setLayout(layout)

    def choose_color(self):
        color = QColorDialog.getColor(self.parent.highlight_color)
        if color.isValid():
            self.parent.highlight_color = color
            self.colorButton.setText(f'Choose Highlight Color (Current: {color.name()})')
            
    def update_voice_list(self):
        self.voiceCombo.clear()
        voices = self.engine.getProperty('voices')
        for voice in voices:
            self.voiceCombo.addItem(voice.name, voice.id)

    def on_engine_change(self, index):
        engine_choice = self.engineCombo.currentText()
        if engine_choice == 'System Voice (SAPI)':
            self.engine = pyttsx3.init()
            self.update_voice_list()
            self.credentialsInput.setDisabled(True)
        else:
            self.credentialsInput.setEnabled(True)
            # Load voices from JSON for selected TTS engine
            voices = load_voices_from_json(engine_choice.lower())
            self.voiceCombo.clear()
            for voice in voices:
                self.voiceCombo.addItem(voice['name'], voice)


    def save_settings(self):
        engine_choice = self.engineCombo.currentText()
        if engine_choice == 'System Voice (SAPI)':
            selected_voice_id = self.voiceCombo.currentData()
            self.parent.engine.setProperty('voice', selected_voice_id)
            self.parent.engine.setProperty('rate', self.rateSlider.value())
            self.parent.tts_type = 'system'
        else:
            creds = self.credentialsInput.text().split(',')
            if engine_choice == 'Polly':
                client = PollyClient(credentials=(creds[0], creds[1], creds[2]))
                self.parent.engine = PollyTTS(client=client)
            elif engine_choice == 'Google':
                client = GoogleClient(credentials=creds[0])
                self.parent.engine = GoogleTTS(client=client)
            elif engine_choice == 'Azure':
                client = MicrosoftClient(credentials=creds[0], creds[1])
                self.parent.engine = AzureTTS(client=client)
            elif engine_choice == 'Watson':
                client = WatsonClient(credentials=creds[0], creds[1])
                self.parent.engine = WatsonTTS(client=client)
            self.parent.tts_type = 'wrapper'
        self.accept()

def save_settings(self):
    engine_choice = self.engineCombo.currentText()
    selected_voice = self.voiceCombo.currentData()

    if engine_choice == 'System Voice (SAPI)':
        self.parent.engine.setProperty('voice', selected_voice['id'])
        self.parent.engine.setProperty('rate', self.rateSlider.value())
        self.parent.tts_type = 'system'
    else:
        creds = self.credentialsInput.text().split(',')
        if engine_choice == 'Polly':
            client = PollyClient(credentials=(creds[0], creds[1], creds[2]))
            self.parent.engine = PollyTTS(client=client, voice=selected_voice['name'], lang=selected_voice['languageCodes'][0])
        elif engine_choice == 'Google':
            client = GoogleClient(credentials=creds[0])
            self.parent.engine = GoogleTTS(client=client, voice=selected_voice['name'], lang=selected_voice['languageCodes'][0])
        elif engine_choice == 'Azure':
            client = MicrosoftClient(credentials=creds[0], creds[1])
            self.parent.engine = AzureTTS(client=client, voice=selected_voice['name'], lang=selected_voice['languageCodes'][0])
        elif engine_choice == 'Watson':
            client = WatsonClient(credentials=creds[0], creds[1])
            self.parent.engine = WatsonTTS(client=client, voice=selected_voice['name'], lang=selected_voice['languageCodes'][0])
        self.parent.tts_type = 'wrapper'
    self.accept()



class SpeechThread(QThread):
    finished = pyqtSignal()

    def __init__(self, text, engine, tts_type, parent=None):
        super(SpeechThread, self).__init__(parent)
        self.text = text
        self.engine = engine
        self.tts_type = tts_type  # 'system' for pyttsx3, 'wrapper' for TTS-Wrapper engines

    def run(self):
        if self.tts_type == 'system':
            # Using pyttsx3
            self.engine.say(self.text)
            self.engine.runAndWait()
        elif self.tts_type == 'wrapper':
            # Using TTS-Wrapper
            audio_bytes = self.engine.synth_to_bytes(self.text, format='wav')
            self.play_audio(audio_bytes)
        self.finished.emit()

    def play_audio(self, audio_bytes):
        # Play audio from bytes
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,  # Assumes 16-bit audio
                        channels=1,  # Mono
                        rate=22050,  # Sample rate
                        output=True)
        stream.write(audio_bytes)
        stream.stop_stream()
        stream.close()
        p.terminate()

class TextToSpeechApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = pyttsx3.init()
        self.tts_type = 'system'  # Default to system type
        self.highlight_color = QColor('yellow')
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Text-to-Speech App')
        self.setGeometry(100, 100, 480, 320)

        # Main layout and widgets
        mainLayout = QVBoxLayout()
        widget = QWidget(self)
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)

        # Text edit field
        self.textEdit = QTextEdit()
        mainLayout.addWidget(self.textEdit)

        # Radio buttons for reading modes
        self.radio_sentence = QRadioButton("Read Sentence", self)
        self.radio_paragraph = QRadioButton("Read Paragraph", self)
        self.radio_word = QRadioButton("Read Word", self)
        self.radio_all = QRadioButton("Read All", self)
        self.radio_all.setChecked(True)
        radio_layout = QVBoxLayout()
        radio_layout.addWidget(self.radio_sentence)
        radio_layout.addWidget(self.radio_paragraph)
        radio_layout.addWidget(self.radio_word)
        radio_layout.addWidget(self.radio_all)
        mainLayout.addLayout(radio_layout)

        # Read button
        self.button_read = QPushButton('Read', self)
        self.button_read.clicked.connect(self.read_text)
        mainLayout.addWidget(self.button_read)

        # Settings button
        self.button_settings = QPushButton('Settings', self)
        self.button_settings.clicked.connect(self.open_settings)
        mainLayout.addWidget(self.button_settings)

        self.show()


    def read_text(self):
        text = self.textEdit.toPlainText()
        cursor = self.textEdit.textCursor()
        format = QTextCharFormat()
        format.setBackground(self.highlight_color)

        selected_text = ""
        if self.radio_sentence.isChecked():
            selected_text = text.split('.')[0]
        elif self.radio_paragraph.isChecked():
            selected_text = text.split('\n')[0]
        elif self.radio_word.isChecked():
            selected_text = text.split()[0]
        elif self.radio_all.isChecked():
            selected_text = text

        self.highlight_text(selected_text, cursor, format)
        self.start_speech_thread(selected_text)

    def highlight_text(self, text, cursor, format):
        # Find and highlight text
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(text))
        self.textEdit.setTextCursor(cursor)
        cursor.setCharFormat(format)

    def start_speech_thread(self, text):
        self.thread = SpeechThread(text, self.engine, self.tts_type)
        self.thread.finished.connect(self.reset_highlight)
        self.thread.start()

    def reset_highlight(self):
        cursor = self.textEdit.textCursor()
        cursor.setCharFormat(QTextCharFormat())  # Reset format
        cursor.clearSelection()
        self.textEdit.setTextCursor(cursor)

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec_()

def main():
    app = QApplication(sys.argv)
    ex = TextToSpeechApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
    