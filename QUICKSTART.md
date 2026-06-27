# Bird Listener & Artist - Quick Start

## What you need

1. **USB microphone** (any cheap USB mic works)
2. **Gemini API key** (for artwork generation)
3. **Python 3.11+**

## Setup

1. Create virtual environment and install dependencies:
```bash
cd ~/bird-listener-project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Create `.env` file with your Gemini API key:
```bash
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

3. Plug in USB microphone

## Running the system

You need 3 processes running simultaneously:

**Terminal 1 - Audio Recorder:**
```bash
source venv/bin/activate
python audio_recorder.py
```

**Terminal 2 - Bird Detector:**
```bash
source venv/bin/activate  
python bird_detector.py
```

**Terminal 3 - Artist:**
```bash
source venv/bin/activate
python bird_artist.py
```

**Terminal 4 - Web Display:**
```bash
source venv/bin/activate
python web_display.py
```

Then open: http://localhost:5555

## How it works

1. **audio_recorder.py** - Records 3-second chunks from USB mic → saves to `audio_chunks/`
2. **bird_detector.py** - Watches audio_chunks/, runs BirdNET → saves detections to `detections.txt`
3. **bird_artist.py** - Watches detections.txt, generates Edo-style art via Gemini → saves to `artwork/`
4. **web_display.py** - Serves web UI showing last 24h of birds

## E-ink display (later)

For the real "wall frame" experience, you'll need:
- Waveshare e-ink display (7.5" or 10.3")
- Raspberry Pi Zero W or similar
- Frame + mounting

The web UI works as-is on any browser, including Pi browsers.

## Testing without a mic

To test the detection/art pipeline without recording:
1. Download sample bird audio from Xeno-canto.org
2. Save as `audio_chunks/bird_test.wav`
3. Run just the detector and artist

## Costs

- BirdNET: Free (runs locally)
- Gemini API: ~$0.01 per image generation
- Expect ~$0.50-1.00/day if you get 50-100 bird detections
