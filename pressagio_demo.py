import configparser
import os

import pressagio.callback
import pressagio

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# Define and create PresageCallback object
class DemoCallback(pressagio.callback.Callback):
    def __init__(self, buffer):
        super().__init__()
        self.buffer = buffer

    def past_stream(self):
        return self.buffer

    def future_stream(self):
        return ""


config_file = os.path.join(SCRIPT_DIR, "res", "morsewriter_pressagio.ini")

config = configparser.ConfigParser()
config.read(config_file)

callback = DemoCallback("Hello my name is ")
prsgio = pressagio.Pressagio(callback, config)

predictions = prsgio.predict()
print(predictions)