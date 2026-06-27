# 🐦 Bird Listener

> Inspired by [this tweet](https://x.com/itsolelehmann/status/2069244042349535252) - a real-time AI system that listens for birds 24/7, identifies them using Cornell's BirdNET, and displays them with real photos from Wikipedia.

## What It Does

1. **Listens** continuously via Blue Yeti USB microphone
2. **Identifies** bird species using BirdNET AI (6,522+ species)
3. **Fetches** real bird photos from Wikipedia
4. **Displays** today's visitors on a beautiful web interface

## Quick Start

```bash
cd ~/bird-listener-project

# Launch everything
./launch.sh

# Open in browser
open http://localhost:5555
```

**Stop:** `./stop.sh`

## Views

- **Gallery** (`/`) - Grid view of all birds detected today
- **Soundscape** (`/soundscape`) - Artistic tree visualization with live birds
- **Monitor** (`/monitor`) - Live audio monitoring and detection feed

## How It Works

```
┌──────────┐    ┌─────────┐    ┌─────────┐    ┌──────────┐
│Blue Yeti │───▶│ 3s WAV  │───▶│ BirdNET │───▶│ Species  │
│ Stereo   │    │ Chunks  │    │  6522+  │    │   ID     │
└──────────┘    └─────────┘    │ species │    └──────────┘
                               └─────────┘          │
                                                    ▼
                               ┌─────────┐    ┌──────────┐
                               │  Web    │◀───│Wikipedia │
                               │ :5555   │    │  Photos  │
                               └─────────┘    └──────────┘
```

**Pipeline:**
1. **audio_recorder.py** - Captures 3-second audio chunks from Blue Yeti
2. **bird_detector.py** - Analyzes audio with BirdNET, filters out non-bird sounds
3. **auto_photo_fetcher.py** - Grabs real bird photos from Wikipedia (2-3s)
4. **web_display.py** - Flask server with multiple view options

## Features

- ✅ **Filters non-birds** - Ignores human voices, engines, dogs, alarms
- ✅ **One detection per species per day** - Clean, non-repetitive log
- ✅ **Real photos** - Wikipedia images, not AI-generated art
- ✅ **Fast updates** - Photos appear 2-5 seconds after detection
- ✅ **Beautiful UI** - Multiple visualization styles
- ✅ **24-hour rolling window** - Shows birds from last 24 hours

## Requirements

**Hardware:**
- Blue Yeti USB microphone (or similar)
- Mac mini M4 (or any Mac with Python 3.9+)

**Software:**
- Python 3.9+
- See `requirements.txt` for dependencies

## Project Structure

```
bird-listener-project/
├── audio_recorder.py         # Records 3s chunks from mic
├── bird_detector.py          # BirdNET species identification
├── auto_photo_fetcher.py     # Fetches real bird photos
├── web_display.py            # Flask web server
├── templates/
│   ├── gallery.html          # Grid view (default)
│   ├── soundscape.html       # Tree visualization
│   ├── index.html            # Carousel view
│   └── monitor.html          # Live monitoring
├── launch.sh                 # Start all components
├── stop.sh                   # Stop everything
└── detections.txt            # Detection log (TSV)
```

## Configuration

**Minimum confidence:** 0.15 (15%)  
**Poll interval:** 2-3 seconds  
**Non-bird filters:** Human vocal/non-vocal, Dog, Engine, Alarm, Rain, Wind, Thunder, Aircraft, etc.

Edit thresholds in:
- `bird_detector.py` - MIN_CONFIDENCE, NON_BIRD_LABELS
- `auto_photo_fetcher.py` - polling intervals

## Cost

- **BirdNET**: Free (runs locally)
- **Wikipedia API**: Free
- **Total**: $0/month - fully local, zero cloud costs

## Future Ideas

- [ ] E-ink display for wall mount
- [ ] Bird song playback
- [ ] Migration pattern tracking
- [ ] Rare species alerts
- [ ] Export daily reports

---

**Built:** June 2026  
**Location:** San Francisco, CA  
**Inspired by:** [@itsolelehmann's tweet](https://x.com/itsolelehmann/status/2069244042349535252)
