#!/usr/bin/env python3
"""
Audio recorder that continuously captures sound from USB mic
and saves 3-second chunks for BirdNET processing
"""

import sounddevice as sd
import soundfile as sf
import numpy as np
import time
import os
from pathlib import Path
from datetime import datetime

# Audio settings
RATE = 48000
CHANNELS = 2  # Yeti is stereo
RECORD_SECONDS = 3
AUDIO_DIR = Path(__file__).parent / "audio_chunks"

def setup_audio_dir():
    """Create audio directory if it doesn't exist"""
    AUDIO_DIR.mkdir(exist_ok=True)
    
def find_yeti():
    """Find Yeti microphone device index"""
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if 'yeti' in dev['name'].lower() and dev['max_input_channels'] > 0:
            return i
    return None

def record_chunk(device_index) -> str:
    """Record a 3-second chunk and save to file"""
    
    # Record audio
    recording = sd.rec(
        int(RECORD_SECONDS * RATE), 
        samplerate=RATE, 
        channels=CHANNELS, 
        device=device_index,
        dtype='int16'
    )
    sd.wait()
    
    # Save with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = AUDIO_DIR / f"bird_{timestamp}.wav"
    
    sf.write(str(filename), recording, RATE)
    
    return str(filename)

def main():
    """Continuously record audio in 3-second chunks"""
    setup_audio_dir()
    
    # Find Yeti mic
    device_index = find_yeti()
    
    if device_index is None:
        print("❌ No Yeti mic found!")
        devices = sd.query_devices()
        print("\nAvailable input devices:")
        for i, dev in enumerate(devices):
            if dev['max_input_channels'] > 0:
                print(f"  {i}: {dev['name']}")
        return
    
    device_info = sd.query_devices(device_index)
    print(f"🎤 Found: {device_info['name']}")
    print(f"📼 Recording started. Saving 3s chunks to {AUDIO_DIR}")
    
    try:
        while True:
            filename = record_chunk(device_index)
            print(f"✅ Saved: {filename}")
            
    except KeyboardInterrupt:
        print("\n⏹️  Recording stopped")

if __name__ == "__main__":
    main()
