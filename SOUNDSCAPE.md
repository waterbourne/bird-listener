# 🎨 Soundscape – Audio-Reactive Bird Visualization

**Live at: http://localhost:5555/soundscape**

## Overview

A full-screen, immersive audio-reactive visualization that transforms bird song detections into a living work of art. Built with vanilla JavaScript + HTML5 Canvas for maximum performance.

## Visual Elements

### 1. **The Mandala (Center)**
- Ambient breathing pulse representing the listening environment
- Expands dramatically on each new detection
- Sends elegant watercolor ripples outward
- Each ripple colored uniquely per species

### 2. **Falling Particles (Spectrogram)**
- 40 painterly particles spawn at detection
- Float downward over 30 seconds, creating layered "paintings"
- Horizontal position randomized for visual variety
- Color-coded by bird species
- Watercolor/ink aesthetic with alpha blending

### 3. **Living Journal (Right Sidebar)**
- Glassmorphism design with backdrop blur
- New detections slide in from top
- Each entry shows:
  - Species name (Cormorant Garamond serif)
  - Scientific name (italic)
  - Precision timestamp
  - Confidence percentage
  - Animated SVG soundwave (unique pulse timing)
- Hover effects and smooth animations

### 4. **Status Indicator (Top Left)**
- Breathing green dot shows system is active
- "Listening for birds..." text

## Color Mapping

Birds are assigned colors based on species or name hash:
- **Blue Jay** → `#4169e1` (royal blue)
- **American Goldfinch** → `#ffd700` (gold)
- **Northern Cardinal** → `#dc143c` (crimson)
- **American Robin** → `#cd5c5c` (indian red)
- **Others** → HSL generated from name hash

## Data Integration

### Current: Polling Mode (Active)
```javascript
// Polls /api/birds every 3 seconds
// Detects new species and triggers visuals
```

### Ready for WebSocket/SSE
Uncomment MODE 1 in the code:
```javascript
const eventSource = new EventSource('/api/stream');
eventSource.onmessage = (event) => {
    const detection = JSON.parse(event.data);
    addDetectionToUI(detection);
};
```

### Mock Mode (Testing)
Uncomment MODE 3 for demo without real data:
```javascript
// Generates random bird detections every 7-12 seconds
```

## Technical Architecture

### Canvas Rendering
- **Mandala Canvas**: 600x600px, centered
- **Spectrogram Canvas**: Full screen, continuous fade
- Requestanimationframe loop at 60fps
- Efficient particle system with alpha blending

### Performance
- Particles auto-cleanup when alpha ≤ 0
- Smooth easing on all animations (cubic-bezier)
- GPU-accelerated CSS transforms
- Minimal DOM manipulation (only on new detections)

### Typography
- **Serif**: Cormorant Garamond (elegant, classical)
- **Sans**: Inter (clean metadata)
- Google Fonts loaded via CDN

## Features

✅ **Real-time detection visualization**  
✅ **Species-specific color coding**  
✅ **Glassmorphism UI**  
✅ **Particle spectrogram**  
✅ **Pulsing mandala with ripples**  
✅ **Animated soundwave SVGs**  
✅ **Auto-counting species tracker**  
✅ **Smooth slide-in animations**  
✅ **Empty state handling**  
✅ **Responsive (works on mobile)**

## Integration Points

### Expected API Response Format
```json
{
  "species": "Blue Jay",
  "scientific_name": "Cyanocitta cristata",
  "confidence": 0.94,
  "timestamp": "2026-06-25T10:30:45Z"
}
```

### Navigation
- **Grid View** button → Returns to `/`
- **Monitor** button → Opens `/monitor`

## Usage

1. Open http://localhost:5555/soundscape
2. Play bird sounds near microphone
3. Watch the mandala pulse and particles paint the screen
4. Journal updates in real-time on the right

## Customization

### Change Colors
Edit `BIRD_COLORS` object at top of `<script>` section

### Adjust Particle Count
Change `const count = 40;` in `createDetectionBurst()`

### Modify Fade Speed
Adjust `this.life -= 0.001;` in `SpectrogramParticle.update()`

### Ripple Behavior
Tune `ripple.radius += 2;` and `ripple.alpha -= 0.008;` in `Mandala.update()`

---

**Built with:** Vanilla JS, HTML5 Canvas, CSS3 Animations  
**Dependencies:** None (Google Fonts loaded via CDN)  
**Browser Support:** Modern browsers with Canvas + Backdrop-filter support
