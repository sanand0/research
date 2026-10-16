# Mobile Field Lab

Open [`index.html`](index.html) over HTTPS on a smartphone, then tap **Enable available features** to discover and monitor browser-exposed sensors and capabilities. No dependencies, network requests, telemetry or recording.

The page tests accelerometer, gyroscope, physical and screen orientation, touch, camera, microphone (local RMS/dBFS/FFT analysis), geolocation, battery, network, wake lock, vibration, NFC, magnetic field, ambient light, proximity, plus explicit Bluetooth, USB and Serial device pickers. It also explains why raw barometer, temperature/humidity, step count/health and biometric readings are unavailable through ordinary browsers.

The **Stop & reset** button stops media streams, geolocation watch, sensor events, NFC scans, wake lock, and Web Audio processing, resets the display, and explains how to revoke persistent browser permission grants manually. Site permissions cannot be revoked programmatically across browsers.

Use HTTPS or localhost. Test both iOS Safari and Android Chrome; platform permissions, iframe policies, and device hardware can differ. A physical device is needed to test actual sensor streams.
