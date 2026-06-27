#!/bin/bash
# Stop all bird listener components

if [ -f .pids ]; then
    source .pids
    echo "Stopping all components..."
    kill $RECORDER_PID $DETECTOR_PID $ARTIST_PID $WEB_PID 2>/dev/null
    rm .pids
    echo "✅ Stopped"
else
    echo "No .pids file found. Killing by name..."
    pkill -f audio_recorder.py
    pkill -f bird_detector.py
    pkill -f bird_artist.py
    pkill -f web_display.py
    echo "✅ Stopped"
fi
