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

echo "🧹 Cleaning up audio chunks..."
rm -rf audio_chunks/*

echo "✅ Stopped and cleaned (artwork preserved)"
