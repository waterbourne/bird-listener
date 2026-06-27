#!/usr/bin/env python3
"""
Bird detector using BirdNET
Processes audio chunks and identifies bird species
"""

import os
import time
from pathlib import Path
from datetime import datetime
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

AUDIO_DIR = Path(__file__).parent / "audio_chunks"
DETECTIONS_FILE = Path(__file__).parent / "detections.txt"

# Minimum confidence threshold
MIN_CONFIDENCE = 0.15

# Filter out non-bird detections
NON_BIRD_LABELS = {
    'Human vocal', 'Human non-vocal', 'Human whistle',
    'Dog', 'Engine', 'Alarm',
    'Siren', 'Fireworks', 'Power tools',
    'Rain', 'Wind', 'Stream', 'Waterfall',
    'Thunder', 'Aircraft', 'Boat'
}

def setup_analyzer():
    """Initialize BirdNET analyzer"""
    analyzer = Analyzer()
    return analyzer

def process_audio_file(analyzer: Analyzer, audio_path: str) -> list:
    """
    Process audio file and return bird detections
    Returns list of (species, confidence, timestamp) tuples
    """
    recording = Recording(
        analyzer,
        audio_path,
        min_conf=MIN_CONFIDENCE,
    )
    recording.analyze()
    
    detections = []
    for detection in recording.detections:
        species = detection['common_name']
        confidence = detection['confidence']
        start_time = detection['start_time']
        
        detections.append({
            'species': species,
            'scientific_name': detection['scientific_name'],
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'audio_file': audio_path
        })
    
    return detections

def save_detection(detection: dict):
    """Save detection to file"""
    with open(DETECTIONS_FILE, 'a') as f:
        f.write(f"{detection['timestamp']}\t{detection['species']}\t{detection['scientific_name']}\t{detection['confidence']:.2f}\t{detection['audio_file']}\n")

def watch_and_process():
    """Watch audio directory and process new files"""
    analyzer = setup_analyzer()
    processed = set()
    detected_today = set()  # Track species already detected today
    
    # Load existing detections from today to avoid duplicates on restart
    if DETECTIONS_FILE.exists():
        try:
            with open(DETECTIONS_FILE) as f:
                next(f)  # Skip header
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        detected_today.add(parts[1])  # Add species name
        except:
            pass
    
    print(f"👁️  Watching {AUDIO_DIR} for new audio files...")
    print(f"📋 Already detected today: {len(detected_today)} species")
    
    while True:
        if not AUDIO_DIR.exists():
            time.sleep(1)
            continue
            
        audio_files = sorted(AUDIO_DIR.glob("bird_*.wav"))
        
        for audio_file in audio_files:
            if audio_file in processed:
                continue
                
            print(f"🔍 Processing: {audio_file.name}")
            
            try:
                detections = process_audio_file(analyzer, str(audio_file))
                
                if detections:
                    for det in detections:
                        species = det['species']
                        
                        # Filter out non-bird detections
                        if species in NON_BIRD_LABELS:
                            print(f"   🚫 Filtered: {species} (non-bird)")
                            continue
                        
                        # Check if we've already seen this species today
                        if species in detected_today:
                            print(f"   🔁 Skipped: {species} (already detected today)")
                        else:
                            print(f"   🐦 Found: {species} (confidence: {det['confidence']:.2f})")
                            save_detection(det)
                            detected_today.add(species)
                else:
                    print(f"   🔇 No birds detected")
                    
                processed.add(audio_file)
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                processed.add(audio_file)  # Don't retry
        
        time.sleep(1)

def main():
    """Main entry point"""
    # Initialize detections file with header
    if not DETECTIONS_FILE.exists():
        with open(DETECTIONS_FILE, 'w') as f:
            f.write("Timestamp\tSpecies\tScientific Name\tConfidence\tAudio File\n")
    
    watch_and_process()

if __name__ == "__main__":
    main()
