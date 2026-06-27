#!/usr/bin/env python3
"""
Fetch real bird photographs from Wikimedia Commons / Wikipedia.
Replaces AI-generated artwork with actual bird photos.
Uses optimized API calls to minimize requests and avoid rate limiting.
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from urllib.parse import quote, unquote
from PIL import Image
from io import BytesIO

DETECTIONS_FILE = Path(__file__).parent / "detections.txt"
DETECTIONS_BACKUP = Path(__file__).parent / "detections.txt.backup"
ARTWORK_DIR = Path(__file__).parent / "artwork"
GENERATED_LOG = Path(__file__).parent / "generated.json"

# Species to exclude (non-birds)
EXCLUDED_SPECIES = {
    'Human vocal', 'Human non-vocal', 'Human whistle', 'Dog', 'Gun', 'Engine', 'Power tools',
    'Gray Wolf', 'Green Frog', 'American Bullfrog'
}

HEADERS = {
    'User-Agent': 'BirdListenerBot/1.0 (sirius_bot@localhost) Python-requests'
}

session = requests.Session()
session.headers.update(HEADERS)


def load_species_from_detections():
    """Extract species -> scientific_name mapping from all detection files."""
    species_map = {}
    for filepath in [DETECTIONS_FILE, DETECTIONS_BACKUP]:
        if not filepath.exists():
            continue
        with open(filepath, 'r') as f:
            next(f, None)  # skip header
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 3:
                    species = parts[1]
                    scientific = parts[2]
                    if species not in EXCLUDED_SPECIES:
                        species_map[species] = scientific
    return species_map


def api_request(url, params, retries=3, backoff=5):
    """Make API request with retry logic for rate limiting."""
    for attempt in range(retries):
        try:
            r = session.get(url, params=params, timeout=20)
            if r.status_code == 429:
                wait = backoff * (attempt + 1)
                print(f"    ⏳ Rate limited (429), waiting {wait}s...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            wait = backoff * (attempt + 1)
            print(f"    ⚠️ Request error: {e}, retrying in {wait}s...")
            time.sleep(wait)
    return None


def get_wikipedia_thumbnail(species_name):
    """Get main image from Wikipedia article in a single API call using generator."""
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": species_name,
        "gsrlimit": 3,
        "prop": "pageimages",
        "pithumbsize": 800,
        "format": "json",
        "origin": "*"
    }
    data = api_request(url, params)
    if not data:
        return None

    pages = data.get("query", {}).get("pages", {})
    best_url = None
    best_area = 0

    for page_id, page in pages.items():
        if "thumbnail" in page:
            thumb = page["thumbnail"]
            w = thumb.get("width", 0)
            h = thumb.get("height", 0)
            area = w * h
            # Prefer images that are at least 400px in one dimension
            if (w >= 400 or h >= 400) and area > best_area:
                best_url = thumb.get("source")
                best_area = area

    return best_url


def search_wikimedia_commons(query, min_size=400):
    """Search Wikimedia Commons using generator for efficiency. Returns best image URL."""
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,  # File namespace
        "gsrlimit": 15,
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": 800,
        "format": "json",
        "origin": "*"
    }
    data = api_request(url, params)
    if not data:
        return None

    pages = data.get("query", {}).get("pages", {})
    best_url = None
    best_area = 0

    for page_id, page in pages.items():
        if "imageinfo" not in page:
            continue

        info = page["imageinfo"][0]
        filename = page.get("title", "").replace("File:", "")
        mime = info.get("mime", "")

        # Skip non-images
        if not mime.startswith("image/"):
            continue

        # Skip diagrams, maps, audio, etc.
        lower = filename.lower()
        skip_keywords = ['diagram', 'map', 'distribution', 'range', 'spectrogram', 'call', 'song',
                         'audio', 'video', '.ogg', '.oga', '.ogv', 'illustration', 'drawing',
                         'stamp', 'postage', 'logo', 'icon', 'chart', 'graph']
        if any(kw in lower for kw in skip_keywords):
            continue

        # Prefer thumburl (already sized) but fall back to direct url
        img_url = info.get("thumburl") or info.get("url")
        w = info.get("width", 0)
        h = info.get("height", 0)
        area = w * h

        if w >= min_size and h >= min_size and area > best_area:
            best_url = img_url
            best_area = area

    return best_url


def download_image(url, save_path, min_size=400):
    """Download image from URL, verify it's a proper image, resize if needed."""
    for attempt in range(3):
        try:
            r = session.get(url, timeout=30)
            if r.status_code == 429:
                wait = 5 * (attempt + 1)
                print(f"    ⏳ Download rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            img = Image.open(BytesIO(r.content))

            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            # Resize if too small or too large
            w, h = img.size
            if w < min_size or h < min_size:
                if w < 250 or h < 250:
                    print(f"    ⚠️ Image too small ({w}x{h}), skipping")
                    return False
                ratio = max(min_size / w, min_size / h)
                new_size = (int(w * ratio), int(h * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            elif w > 1024 or h > 1024:
                ratio = min(1024 / w, 1024 / h)
                new_size = (int(w * ratio), int(h * ratio))
                img = img.resize(new_size, Image.LANCZOS)

            img.save(save_path, format="PNG")
            return True
        except Exception as e:
            print(f"    ⚠️ Error downloading image: {e}")
            time.sleep(2)
    return False


def safe_filename(name):
    return name.replace(" ", "_").replace("'", "")


def fetch_photo_for_species(species, scientific_name=None):
    """Fetch a real bird photo for a given species. Returns saved path or None."""
    print(f"🔍 {species}")

    # Try Wikipedia thumbnail first
    print(f"   Trying Wikipedia...")
    url = get_wikipedia_thumbnail(species)

    # Try Wikimedia Commons with common name
    if not url:
        print(f"   Trying Wikimedia Commons...")
        url = search_wikimedia_commons(f"{species} bird", min_size=400)

    # Try scientific name
    if not url and scientific_name:
        print(f"   Trying scientific name...")
        url = search_wikimedia_commons(scientific_name, min_size=400)
        if not url:
            url = get_wikipedia_thumbnail(scientific_name)

    # Broader search
    if not url:
        print(f"   Trying broader search...")
        url = search_wikimedia_commons(species, min_size=300)

    if not url:
        print(f"   ❌ No suitable photo found")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = safe_filename(species)
    save_path = ARTWORK_DIR / f"{safe}_{timestamp}.png"

    if download_image(url, save_path):
        print(f"   ✅ Saved: {save_path.name}")
        return str(save_path)
    else:
        return None


def update_generated_json(species, image_path):
    """Update generated.json with the new photo path."""
    data = {}
    if GENERATED_LOG.exists():
        try:
            with open(GENERATED_LOG, 'r') as f:
                data = json.load(f)
        except:
            data = {}

    data[species] = {
        "image_path": image_path,
        "timestamp": datetime.now().isoformat()
    }

    with open(GENERATED_LOG, 'w') as f:
        json.dump(data, f, indent=2)


def main():
    ARTWORK_DIR.mkdir(exist_ok=True)

    species_map = load_species_from_detections()
    print(f"Found {len(species_map)} species in detection logs")

    # Also include species already in generated.json
    if GENERATED_LOG.exists():
        try:
            with open(GENERATED_LOG, 'r') as f:
                generated = json.load(f)
            for species in generated:
                if species not in species_map and species not in EXCLUDED_SPECIES:
                    species_map[species] = None
        except:
            pass

    # Priority species first
    priority = [
        "Dark-eyed Junco", "White-winged Crossbill", "Green-tailed Towhee",
        "Song Sparrow", "American Robin", "Northern Cardinal"
    ]

    species_list = list(species_map.keys())
    species_list.sort(key=lambda s: (0 if s in priority else 1, s))

    success_count = 0
    fail_count = 0

    for i, species in enumerate(species_list):
        if species in EXCLUDED_SPECIES:
            continue

        scientific = species_map.get(species)
        path = fetch_photo_for_species(species, scientific)
        if path:
            update_generated_json(species, path)
            success_count += 1
        else:
            fail_count += 1

        # Rate limiting: sleep between species, longer every 10
        sleep_time = 2.5 if (i + 1) % 10 != 0 else 6
        time.sleep(sleep_time)

    print(f"\n📊 Done! Success: {success_count}, Failed: {fail_count}")


if __name__ == "__main__":
    main()
