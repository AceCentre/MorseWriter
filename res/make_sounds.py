from pydub import AudioSegment
from pydub.generators import Square, Sawtooth, Triangle, Sine

# Generate Dit sound
dit = Sine(800).to_audio_segment(duration=100)  # Frequency = 800 Hz, Duration = 100 ms
dit.export("dit_sound.wav", format="wav")

# Generate Dah sound
dah = Sine(800).to_audio_segment(duration=300)  # Frequency = 800 Hz, Duration = 300 ms
dah.export("dah_sound.wav", format="wav")

# Dit with fade in and fade out
fade_dit = Sine(800).to_audio_segment(duration=100).fade_in(20).fade_out(20)
fade_dah = Sine(800).to_audio_segment(duration=300).fade_in(30).fade_out(30)
fade_dit.export("fade_dit_sound.wav", format="wav")
fade_dah.export("fade_dah_sound.wav", format="wav")

square_dit = Square(800).to_audio_segment(duration=100)
square_dah = Square(800).to_audio_segment(duration=300)
square_dit.export("square_dit_sound.wav", format="wav")
square_dah.export("square_dah_sound.wav", format="wav")

high_freq_dit = Sine(1200).to_audio_segment(duration=100)
high_freq_dah = Sine(1200).to_audio_segment(duration=300)
high_freq_dit.export("high_freq_dit_sound.wav", format="wav")
high_freq_dah.export("high_freq_dah_sound.wav", format="wav")