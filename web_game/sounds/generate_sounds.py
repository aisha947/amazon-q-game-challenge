import wave
import struct
import math
import os

def create_simple_sound(filename, frequency=440, duration=0.5, volume=1.0):
    """Create a simple sine wave sound file"""
    sample_rate = 44100
    num_samples = int(duration * sample_rate)
    
    # Create sine wave
    buf = []
    for i in range(num_samples):
        sample = int(32767.0 * volume * 
                    math.sin(2 * math.pi * frequency * i / sample_rate))
        buf.append(struct.pack('h', sample))
    
    # Write to file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(buf))

def create_background_music(filename, duration=10.0):
    """Create a simple background music loop"""
    sample_rate = 44100
    
    # Create a simple melody
    notes = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]  # C4 to C5
    
    # Generate the audio data
    audio_data = []
    for i in range(int(duration * sample_rate)):
        t = i / sample_rate
        
        # Create a simple melody by selecting different notes over time
        note_idx = int((t * 2) % len(notes))
        freq = notes[note_idx]
        
        # Add some variation
        if int(t * 4) % 4 == 0:
            freq *= 0.5  # Octave down occasionally
        
        # Generate the sample
        sample = int(10000 * math.sin(2 * math.pi * freq * t))
        
        # Add a simple bass line
        bass_freq = 65.41 * (1 + int(t * 0.5) % 3)  # C2 with variations
        sample += int(5000 * math.sin(2 * math.pi * bass_freq * t))
        
        # Apply envelope to avoid clicks
        envelope = min(1.0, (duration - t) / 2.0, t / 2.0)
        sample = int(sample * envelope)
        
        # Pack the sample
        audio_data.append(struct.pack('h', sample))
    
    # Write to file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(audio_data))

# Create directory if it doesn't exist
os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)

# Create sound effects
create_simple_sound("catch.wav", frequency=600, duration=0.15, volume=0.8)
create_simple_sound("miss.wav", frequency=200, duration=0.2, volume=0.5)
create_simple_sound("bad_catch.wav", frequency=300, duration=0.3, volume=0.7)
create_simple_sound("bomb.wav", frequency=100, duration=0.4, volume=0.9)
create_simple_sound("game_over.wav", frequency=150, duration=1.0, volume=0.8)

# Create background music tracks with different characteristics
create_background_music("music1.wav", duration=10.0)

# Music 2 - different notes
notes2 = [440.00, 493.88, 523.25, 587.33, 659.25, 698.46, 783.99, 880.00]  # A4 to A5
sample_rate = 44100
duration = 10.0
audio_data = []
for i in range(int(duration * sample_rate)):
    t = i / sample_rate
    note_idx = int((t * 1.5) % len(notes2))
    freq = notes2[note_idx]
    sample = int(10000 * math.sin(2 * math.pi * freq * t))
    bass_freq = 110.00 * (1 + int(t * 0.7) % 3)
    sample += int(5000 * math.sin(2 * math.pi * bass_freq * t))
    envelope = min(1.0, (duration - t) / 2.0, t / 2.0)
    sample = int(sample * envelope)
    audio_data.append(struct.pack('h', sample))
with wave.open("music2.wav", 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(audio_data))

# Music 3 - different rhythm
notes3 = [261.63, 329.63, 392.00, 523.25]  # C4, E4, G4, C5
sample_rate = 44100
duration = 10.0
audio_data = []
for i in range(int(duration * sample_rate)):
    t = i / sample_rate
    note_idx = int((t * 3) % len(notes3))
    freq = notes3[note_idx]
    sample = int(10000 * math.sin(2 * math.pi * freq * t))
    bass_freq = 65.41 * (1 + int(t) % 2)
    sample += int(5000 * math.sin(2 * math.pi * bass_freq * t))
    envelope = min(1.0, (duration - t) / 2.0, t / 2.0)
    sample = int(sample * envelope)
    audio_data.append(struct.pack('h', sample))
with wave.open("music3.wav", 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(audio_data))

print("Sound files generated successfully!")
