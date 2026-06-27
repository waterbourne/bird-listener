#!/usr/bin/env python3
"""
Test script for Stable Diffusion image generation
Generates one bird artwork to verify the pipeline works
"""

from bird_artist import setup_sd_pipeline, generate_bird_artwork
from pathlib import Path

def test_generation():
    print("🧪 Testing Stable Diffusion image generation...")
    print("=" * 60)
    
    # Setup pipeline (this will download the model ~4GB on first run)
    print("\n1️⃣  Loading Stable Diffusion pipeline...")
    pipeline = setup_sd_pipeline()
    
    # Generate test bird
    test_species = "American Robin"
    test_scientific = "Turdus migratorius"
    
    print(f"\n2️⃣  Generating artwork for {test_species}...")
    result = generate_bird_artwork(pipeline, test_species, test_scientific)
    
    if result:
        print(f"\n✅ SUCCESS!")
        print(f"   Image saved to: {result}")
        print(f"\n   To view: open {result}")
    else:
        print(f"\n❌ FAILED - check errors above")
    
    print("\n" + "=" * 60)
    print("Test complete!")

if __name__ == "__main__":
    test_generation()
