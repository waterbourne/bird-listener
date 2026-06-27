#!/usr/bin/env python3
"""
Automatic bird photo fetcher - watches for new detections and fetches real photos.
Replaces the bird_artist.py AI generation system.
"""

import time
from pathlib import Path
from datetime import datetime, timedelta
from fetch_bird_photos import (
    load_species_from_detections,
    fetch_photo_for_species,
    update_generated_json,
    EXCLUDED_SPECIES,
    GENERATED_LOG
)
import json

DETECTIONS_FILE = Path(__file__).parent / "detections.txt"

def load_generated_birds():
    """Load what's already in generated.json"""
    if GENERATED_LOG.exists():
        with open(GENERATED_LOG) as f:
            return set(json.load(f).keys())
    return set()

def get_recent_detections(hours=24):
    """Get species from recent detections"""
    if not DETECTIONS_FILE.exists():
        return []
    
    cutoff = datetime.now() - timedelta(hours=hours)
    birds = []
    species_map = load_species_from_detections()
    
    with open(DETECTIONS_FILE) as f:
        next(f, None)  # skip header
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 3:
                timestamp_str = parts[0]
                species = parts[1]
                scientific = parts[2]
                
                if species in EXCLUDED_SPECIES:
                    continue
                
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    if timestamp > cutoff:
                        birds.append((species, scientific))
                except:
                    continue
    
    return birds

def main():
    print("🖼️  Auto Photo Fetcher started")
    print("   Watching for new bird detections...")
    
    while True:
        try:
            # Check what we already have
            existing = load_generated_birds()
            
            # Get recent detections
            recent = get_recent_detections(hours=24)
            
            # Find birds that need photos
            for species, scientific in recent:
                if species not in existing:
                    print(f"\n🔍 New bird: {species}")
                    path = fetch_photo_for_species(species, scientific)
                    if path:
                        update_generated_json(species, path)
                        print(f"   ✅ Photo saved and registered")
                        existing.add(species)
                    else:
                        print(f"   ❌ Failed to fetch photo")
                    
                    # Rate limiting: wait between fetches
                    time.sleep(2)
            
            # Check every 3 seconds for faster response
            time.sleep(3)
            
        except KeyboardInterrupt:
            print("\n🛑 Shutting down photo fetcher")
            break
        except Exception as e:
            print(f"⚠️  Error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
