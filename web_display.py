#!/usr/bin/env python3
"""
Web display for bird collage
Shows all birds ever detected with daily 3am color reset
"""

from flask import Flask, render_template, jsonify, send_from_directory
from pathlib import Path
from datetime import datetime, timedelta
import json

app = Flask(__name__)

DETECTIONS_FILE = Path(__file__).parent / "detections.txt"
GENERATED_LOG = Path(__file__).parent / "generated.json"
ARTWORK_DIR = Path(__file__).parent / "artwork"

def load_generated_birds():
    """Load generated artwork log"""
    if GENERATED_LOG.exists():
        with open(GENERATED_LOG) as f:
            return json.load(f)
    return {}

def get_todays_birds():
    """Get all birds heard in last 24 hours"""
    if not DETECTIONS_FILE.exists():
        return []
    
    cutoff = datetime.now() - timedelta(hours=24)
    birds = {}
    
    # Species to exclude from display
    excluded_species = {'Human vocal', 'Human non-vocal', 'Human whistle', 'Dog'}
    
    with open(DETECTIONS_FILE) as f:
        next(f)  # Skip header
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                timestamp_str = parts[0]
                species = parts[1]
                scientific = parts[2]
                confidence = float(parts[3])
                
                # Skip excluded species
                if species in excluded_species:
                    continue
                
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    if timestamp > cutoff:
                        # Keep only the highest confidence detection per species
                        if species not in birds or birds[species]['confidence'] < confidence:
                            birds[species] = {
                                'species': species,
                                'scientific_name': scientific,
                                'confidence': confidence,
                                'last_heard': timestamp.strftime('%I:%M %p'),
                                'timestamp': timestamp
                            }
                except:
                    continue
    
    # Sort by most recent first
    birds_list = sorted(birds.values(), key=lambda x: x['timestamp'], reverse=True)
    
    # Add artwork info
    generated = load_generated_birds()
    for bird in birds_list:
        if bird['species'] in generated:
            bird['has_artwork'] = True
            bird['artwork_path'] = generated[bird['species']]['image_path']
        else:
            bird['has_artwork'] = False
    
    return birds_list

def get_all_artwork():
    """Get all generated artwork paths keyed by species"""
    return load_generated_birds()

@app.route('/')
def index():
    """Main display page - grid gallery"""
    return render_template('gallery.html')

@app.route('/carousel')
def carousel():
    """Carousel display page"""
    return render_template('index.html')

@app.route('/monitor')
def monitor():
    """Monitoring page - shows live detections and audio input"""
    return render_template('monitor.html')

@app.route('/soundscape')
def soundscape():
    """Artistic audio-reactive visualization"""
    return render_template('soundscape.html')

@app.route('/api/birds')
def api_birds():
    """API endpoint for bird data (today's detections)"""
    birds = get_todays_birds()
    return jsonify(birds)

@app.route('/api/detections/raw')
def api_raw_detections():
    """API endpoint for all raw detections (last 50, including filtered)"""
    if not DETECTIONS_FILE.exists():
        return jsonify([])
    
    detections = []
    excluded_species = {'Human vocal', 'Human non-vocal', 'Human whistle', 'Dog'}
    
    with open(DETECTIONS_FILE) as f:
        next(f)  # Skip header
        lines = f.readlines()
        
    # Get last 50 detections
    for line in lines[-50:]:
        parts = line.strip().split('\t')
        if len(parts) >= 5:
            timestamp_str = parts[0]
            species = parts[1]
            scientific = parts[2]
            confidence = float(parts[3])
            audio_file = parts[4]
            
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                detections.append({
                    'timestamp': timestamp.strftime('%I:%M:%S %p'),
                    'species': species,
                    'scientific_name': scientific,
                    'confidence': confidence,
                    'audio_file': audio_file,
                    'filtered': species in excluded_species
                })
            except:
                continue
    
    # Return newest first
    return jsonify(list(reversed(detections)))

@app.route('/api/artwork')
def api_artwork():
    """API endpoint for all generated artwork"""
    artwork = get_all_artwork()
    return jsonify(artwork)

@app.route('/artwork/<path:filename>')
def serve_artwork(filename):
    """Serve generated artwork images"""
    return send_from_directory(ARTWORK_DIR, filename)

@app.route('/api/reset', methods=['POST'])
def reset_data():
    """Reset all detection and artwork data"""
    try:
        # Clear detections.txt (keep header)
        with open(DETECTIONS_FILE, 'w') as f:
            f.write("timestamp\tspecies\tscientific_name\tconfidence\taudio_file\n")
        
        # Clear generated.json
        with open(GENERATED_LOG, 'w') as f:
            json.dump({}, f)
        
        return jsonify({"status": "success", "message": "All data reset"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5555, debug=True)
