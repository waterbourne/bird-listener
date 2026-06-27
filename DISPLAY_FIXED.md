# Bird Listener Display - Fixed

## What Was Broken

1. **Detector duplicates**: Was logging the same bird every 3 seconds
   - **Fixed**: Now tracks `detected_today` set, only logs each species once per day

2. **Artist generating junk**: Was creating artwork for "Human vocal", "Dog", etc.
   - **Fixed**: Artist now filters excluded species before generating

3. **Display logic**: Web display filtered correctly but artist didn't
   - **Fixed**: Both now use same exclusion list

4. **Carousel wait**: Old display didn't show birds until artwork finished
   - **Fixed**: New grid shows birds immediately with placeholder, artwork loads in

## New Display Architecture

### Main Grid View (/)
- **Instant appearance**: Birds show up the moment they're detected
- **Placeholder**: Shows 🎨 "Generating artwork..." while waiting
- **Live updates**: Refreshes every 5 seconds
- **Artwork loads in-place**: When artist finishes, image replaces placeholder
- **Card layout**: All birds visible at once in responsive grid
- **Stats**: Shows total species count

### Monitor View (/monitor)
- **Live feed**: Last 50 detections with timestamps
- **Filter status**: Each detection labeled DISPLAYED or FILTERED
- **Audio status**: Shows if system is actively listening
- **Stats**: Total/displayed/filtered counts

### Carousel View (/carousel)
- **Original view**: Auto-scrolling full-screen carousel
- **Still available**: For ambient display mode

## Excluded Species

The following are detected but NOT displayed or turned into art:
- Human vocal
- Human non-vocal
- Human whistle
- Dog
- Gun
- Engine
- Power tools

## Data Flow

1. **Audio Recorder** → Captures 3-sec chunks every 3 seconds
2. **Detector** → Analyzes with BirdNET (15% threshold)
   - Logs to `detections.txt` (once per species per day)
   - Filters excluded species
3. **Artist** → Watches `detections.txt`
   - Reads only real bird species (filters excluded)
   - Generates SD 1.5 artwork (~60s per bird on M4 CPU)
   - Updates `generated.json`
4. **Display** → Shows all detected birds
   - Reads `detections.txt` for species list (filters excluded)
   - Reads `generated.json` for artwork status
   - Shows placeholder until art ready

## Reset Behavior

**Reset button clears:**
- `detections.txt` (keeps header only)
- `generated.json` (empties to `{}`)
- Browser localStorage

**Next detection after reset = first bird of new day**

## Current Status

✅ 6+ birds detected from your video
✅ Artist generating (started with "Greenish Schiffornis")
✅ Grid display live at http://localhost:5555
✅ Monitor view at http://localhost:5555/monitor
✅ Deduplication working
✅ Exclusion filters applied everywhere
