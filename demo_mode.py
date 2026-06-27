#!/usr/bin/env python3
"""
Demo mode - simulates bird detections for testing the display
Run this instead of the real components to see the system in action
"""

import time
import random
from datetime import datetime
from pathlib import Path

DETECTIONS_FILE = Path(__file__).parent / "detections.txt"

# Sample birds from San Francisco Bay Area
SF_BIRDS = [
    ("American Robin", "Turdus migratorius"),
    ("Anna's Hummingbird", "Calypte anna"),
    ("Dark-eyed Junco", "Junco hyemalis"),
    ("Song Sparrow", "Melospiza melodia"),
    ("California Towhee", "Melozone crissalis"),
    ("Black Phoebe", "Sayornis nigricans"),
    ("American Crow", "Corvus brachyrhynchos"),
    ("Steller's Jay", "Cyanocitta stelleri"),
    ("House Finch", "Haemorhous mexicanus"),
    ("Mourning Dove", "Zenaida macroura"),
    ("White-crowned Sparrow", "Zonotrichia leucophrys"),
    ("Scrub Jay", "Aphelocoma californica"),
    ("Red-tailed Hawk", "Buteo jamaicensis"),
    ("Turkey Vulture", "Cathartes aura"),
    ("Great Blue Heron", "Ardea herodias"),
]

def create_detection(species: str, scientific_name: str, confidence: float):
    """Add a simulated detection"""
    timestamp = datetime.now().isoformat()
    audio_file = f"demo_audio_{int(time.time())}.wav"
    
    with open(DETECTIONS_FILE, 'a') as f:
        f.write(f"{timestamp}\t{species}\t{scientific_name}\t{confidence:.2f}\t{audio_file}\n")
    
    print(f"🐦 Detected: {species} (confidence: {confidence:.2f})")

def main():
    """Run demo mode"""
    print("="*60)
    print("DEMO MODE - Simulating Bird Detections")
    print("="*60)
    print()
    print("This will add random bird detections every 5-15 seconds")
    print("Open http://localhost:5555 in another terminal to see them appear")
    print()
    print("Press Ctrl+C to stop")
    print("="*60)
    print()
    
    # Initialize detections file
    if not DETECTIONS_FILE.exists():
        with open(DETECTIONS_FILE, 'w') as f:
            f.write("Timestamp\tSpecies\tScientific Name\tConfidence\tAudio File\n")
    
    used_birds = set()
    
    try:
        while True:
            # Pick a random bird we haven't seen yet (or reuse if we've seen them all)
            available = [b for b in SF_BIRDS if b[0] not in used_birds]
            if not available:
                available = SF_BIRDS
                used_birds.clear()
            
            bird = random.choice(available)
            confidence = random.uniform(0.65, 0.98)  # Realistic confidence range
            
            create_detection(bird[0], bird[1], confidence)
            used_birds.add(bird[0])
            
            # Random delay between detections
            delay = random.uniform(5, 15)
            time.sleep(delay)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo mode stopped")
        print(f"Total unique species detected: {len(used_birds)}")

if __name__ == "__main__":
    main()
