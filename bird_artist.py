#!/usr/bin/env python3
"""
Bird artist using Stable Diffusion via diffusers (local on M4)
Generates Edo-period Japanese woodblock style artwork
"""

import os
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import for image generation
try:
    from diffusers import StableDiffusionPipeline
    import torch
    HAS_DIFFUSERS = True
except ImportError:
    HAS_DIFFUSERS = False
    print("⚠️  diffusers not installed. Run: source venv/bin/activate && pip install diffusers torch")

load_dotenv()

DETECTIONS_FILE = Path(__file__).parent / "detections.txt"
ARTWORK_DIR = Path(__file__).parent / "artwork"
GENERATED_LOG = Path(__file__).parent / "generated.json"

# Global pipeline (load once, reuse)
_pipeline = None

def setup_sd_pipeline():
    """Initialize Stable Diffusion pipeline for M4"""
    global _pipeline
    
    if not HAS_DIFFUSERS:
        raise RuntimeError("diffusers library not installed")
    
    if _pipeline is not None:
        return _pipeline
    
    print("🎨 Loading Stable Diffusion 1.5 model...")
    print("   (This takes ~30 seconds on first run)")
    
    # Use SD 1.5 - lighter weight for M4 with 16GB RAM
    model_id = "stable-diffusion-v1-5/stable-diffusion-v1-5"
    
    _pipeline = StableDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float32,  # Use float32 on CPU (MPS has NaN issues)
        use_safetensors=True,
        safety_checker=None,  # Disable NSFW filter (birds trigger it!)
        requires_safety_checker=False
    )
    
    # Use CPU (MPS on M4 has known NaN issues with SD)
    # Slower but stable - ~60s per image vs ~25s on MPS
    _pipeline = _pipeline.to("cpu")
    
    # Enable memory-efficient attention
    _pipeline.enable_attention_slicing()
    
    print("✅ Model loaded and ready (running on CPU)")
    print("   ⏱️  Expect ~60 seconds per image")
    return _pipeline

def load_generated_birds():
    """Load already-generated birds"""
    if GENERATED_LOG.exists():
        with open(GENERATED_LOG) as f:
            return json.load(f)
    return {}

def save_generated_bird(species: str, image_path: str):
    """Save generated bird to log"""
    generated = load_generated_birds()
    generated[species] = {
        'image_path': image_path,
        'timestamp': datetime.now().isoformat()
    }
    with open(GENERATED_LOG, 'w') as f:
        json.dump(generated, f, indent=2)

def generate_bird_artwork(pipeline, species: str, scientific_name: str) -> str:
    """
    Generate Edo-period woodblock print of bird species using SD 1.5
    Returns path to saved image
    """
    ARTWORK_DIR.mkdir(exist_ok=True)
    
    # Craft prompt for Edo/ukiyo-e style
    prompt = f"""Edo period Japanese woodblock print ukiyo-e style illustration of {species} ({scientific_name}), traditional Hokusai Hiroshige art style, bold black outlines, flat colors, minimal shading, elegant bird pose, simple branch background, masterpiece, highly detailed"""
    
    negative_prompt = "photograph, realistic, 3d render, modern, digital art, blurry, low quality, watermark"
    
    try:
        print(f"   🎨 Generating artwork for {species}...")
        
        # Generate image with explicit seed for reproducibility
        import random
        seed = random.randint(0, 2**32 - 1)
        generator = torch.Generator(device="cpu").manual_seed(seed)
        
        # Generate image
        result = pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=20,  # Reduced from 30 for faster M4 generation
            guidance_scale=7.5,      # How much to follow the prompt
            height=512,              # SD 1.5 optimal size
            width=512,
            generator=generator
        )
        
        image = result.images[0]
        
        # Save image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_species = species.replace(" ", "_").replace("'", "")
        img_path = ARTWORK_DIR / f"{safe_species}_{timestamp}.png"
        
        image.save(img_path, format="PNG")
        
        print(f"   ✅ Artwork saved: {img_path.name} (seed: {seed})")
        return str(img_path)
        
    except Exception as e:
        print(f"   ❌ Error generating artwork: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_recent_detections(hours=24):
    """Get bird detections from last N hours (excluding filtered species)"""
    if not DETECTIONS_FILE.exists():
        return []
    
    # Species to exclude from artwork generation
    excluded_species = {'Human vocal', 'Human non-vocal', 'Human whistle', 'Dog', 'Gun', 'Engine', 'Power tools'}
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    recent_birds = []
    
    with open(DETECTIONS_FILE) as f:
        next(f)  # Skip header
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 3:
                timestamp_str = parts[0]
                species = parts[1]
                scientific = parts[2]
                
                # Skip filtered species
                if species in excluded_species:
                    continue
                
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    if timestamp > cutoff_time:
                        recent_birds.append({
                            'species': species,
                            'scientific_name': scientific,
                            'timestamp': timestamp
                        })
                except:
                    continue
    
    return recent_birds

def watch_and_generate():
    """Watch for new bird detections and generate artwork"""
    pipeline = setup_sd_pipeline()
    
    print(f"🎨 Artist ready. Watching for new birds...")
    
    while True:
        # Reload generated list each iteration to pick up any external changes
        generated = load_generated_birds()
        recent = get_recent_detections(hours=24)
        
        for bird in recent:
            species = bird['species']
            
            # Skip if already generated (reload to check latest state)
            if species in generated:
                continue
            
            print(f"🖌️  New bird: {species}")
            artwork_path = generate_bird_artwork(
                pipeline,
                species,
                bird['scientific_name']
            )
            
            if artwork_path:
                save_generated_bird(species, artwork_path)
                generated[species] = {'image_path': artwork_path, 'timestamp': datetime.now().isoformat()}  # Update in-memory cache
                print(f"   ✅ Artwork saved: {artwork_path}")
        
        time.sleep(10)  # Check every 10 seconds

def main():
    """Main entry point"""
    watch_and_generate()

if __name__ == "__main__":
    main()
