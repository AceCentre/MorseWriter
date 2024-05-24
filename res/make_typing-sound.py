import numpy as np
import wave

def generate_typing_sound(filename, duration=0.1, frequency=1500, volume=0.3, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave_data = (volume * np.sin(2 * np.pi * frequency * t)).astype(np.float32)

    with wave.open(filename, 'w') as wav_file:
        n_channels = 1
        sampwidth = 2  # 2 bytes per sample
        wav_file.setparams((n_channels, sampwidth, sample_rate, 0, 'NONE', 'not compressed'))

        for sample in wave_data:
            wav_file.writeframes((int(sample * 32767)).to_bytes(sampwidth, byteorder='little', signed=True))

generate_typing_sound('typing_sound.wav')