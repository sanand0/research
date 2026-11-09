# Mobile Field Lab

Open [`index.html`](index.html) over HTTPS on a smartphone, then tap **Enable available features** to discover and monitor browser-exposed sensors and capabilities. No dependencies, network requests, telemetry or recording.

The page tests accelerometer, gyroscope, physical and screen orientation, touch, camera, microphone (local RMS/dBFS/FFT analysis), geolocation, battery, network, wake lock, vibration, NFC, magnetic field, ambient light, proximity, plus explicit Bluetooth, USB and Serial device pickers. It also explains why raw barometer, temperature/humidity, step count/health and biometric readings are unavailable through ordinary browsers.

The **Stop & reset** button stops media streams, geolocation watch, sensor events, NFC scans, wake lock, and Web Audio processing, resets the display, and explains how to revoke persistent browser permission grants manually. Site permissions cannot be revoked programmatically across browsers.

Use HTTPS or localhost. Test both iOS Safari and Android Chrome; platform permissions, iframe policies, and device hardware can differ. A physical device is needed to test actual sensor streams.

## Air Ink: motion drawing

Open [`draw.html`](draw.html) on a phone over HTTPS, and tap **Start drawing**. Hold the large bottom button to draw and release to lift the pen. Tilting the phone moves the on-screen cursor whether drawing or not. Tap **Recenter** to establish a comfortable neutral wrist pose; **Undo**, **Clear**, and **Save** work on the same page. Stroke width responds to on-screen movement speed: slow movement deposits thick ink and pausing builds a small puddle; fast movement makes fine lines.

The design uses `deviceorientation` (relative pitch/roll) as an *absolute, anchored cursor position*. Integrating acceleration would drift and become hard to control; recalibration makes relative tilt deterministic. On iOS, the Start button requests motion permission. If actual orientation events don't arrive within 3.5 seconds or permission is denied, the app reports that motion is unavailable. There is no finger-drawing fallback. The visible aiming marker is a compact, high-contrast 12px ring that stays the same size even while drawing; only the ink width changes (approximately 2–22px). Drawing stays local to the browser; Save exports a PNG, and resizing redraws existing strokes at their normalized coordinates.

**Limitations:** the brush radius was corrected on 16 Oct 2026 (a reversed `clamp` argument order previously made strokes uniformly 46px wide). Exact natural direction/sensitivity of the vertical tilt axis should be validated with real phones; device manufacturers may interpret/smooth orientation differently, and extreme phone tilts can reach the edges of the cursor range. Browser tests can simulate orientation events but cannot confirm ergonomic feel with a real device.
