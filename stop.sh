#!/bin/bash
# Stop all bird listener components and clean up data

if [ -f .pids ]; then
    source .pids
    echo "🛑 Stopping all components..."
    kill $RECORDER_PID $DETECTOR_PID $ARTIST_PID $WEB_PID 2>/dev/null
    rm .pids
else
    echo "No .pids file found. Killing by name..."
    pkill -f audio_recorder.py
    pkill -f bird_detector.py
    pkill -f auto_photo_fetcher.py
    pkill -f bird_artist.py
    pkill -f web_display.py
fi

sleep 1

echo "🧹 Cleaning up data..."
rm -rf audio_chunks/*
rm -rf artwork/*
rm -f detections.txt
rm -f generated.json

echo "✅ Stopped and cleaned"
