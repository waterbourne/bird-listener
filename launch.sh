#!/bin/bash
# Launch all bird listener components

cd ~/bird-listener-project
source venv/bin/activate

# Create necessary directories
mkdir -p audio_chunks artwork templates logs

echo "🚀 Starting Bird Listener System..."
echo ""

# Start all components in background with logging
echo "📼 Starting audio recorder..."
python audio_recorder.py > logs/recorder.log 2>&1 &
RECORDER_PID=$!

sleep 2

echo "🔍 Starting bird detector..."
python bird_detector.py > logs/detector.log 2>&1 &
DETECTOR_PID=$!

sleep 2

echo "🖼️  Starting photo fetcher..."
python auto_photo_fetcher.py >> logs/artist.log 2>&1 &
ARTIST_PID=$!

sleep 2

echo "🌐 Starting web display..."
python web_display.py > logs/web.log 2>&1 &
WEB_PID=$!

sleep 2

echo ""
echo "✅ All components running!"
echo ""
echo "PIDs:"
echo "  Recorder: $RECORDER_PID"
echo "  Detector: $DETECTOR_PID"
echo "  Artist:   $ARTIST_PID"
echo "  Web:      $WEB_PID"
echo ""
echo "🌐 Open http://localhost:5555 to see your birds!"
echo ""
echo "To stop all:"
echo "  kill $RECORDER_PID $DETECTOR_PID $ARTIST_PID $WEB_PID"
echo ""
echo "Or save PIDs to file:"
cat > .pids <<EOF
RECORDER_PID=$RECORDER_PID
DETECTOR_PID=$DETECTOR_PID
ARTIST_PID=$ARTIST_PID
WEB_PID=$WEB_PID
EOF

echo "Saved PIDs to .pids"
echo "Stop with: source .pids && kill \$RECORDER_PID \$DETECTOR_PID \$ARTIST_PID \$WEB_PID"
