# Platform Promise

An evidence-led commuter application about Singapore MRT/LRT timing and reliability. It uses downloaded Singapore government datasets and deliberately separates:

- end-of-line train punctuality;
- scheduled service delivered;
- service disruptions over 30 minutes;
- distance between delays over five minutes; and
- the unavailable quantity commuters often assume they are seeing: actual arrival delay at every station.

## Run

```bash
uv run python -m http.server 8000
```

Open <http://localhost:8000>.

## Data

Raw downloads are in `data/raw/`; the browser-ready transcription is `data/app-data.json`. Source URLs, coverage dates and download dates are included in the JSON and exposed in the application’s Sources dialog.

The LTA GTFS Train Schedule descriptor was downloaded, but its embedded S3 URL had already expired. It is preserved for provenance and contributes no values to the application. Dynamic or refreshed GTFS feeds should be archived before they can support historical platform-level delay analysis.

## Verify

```bash
node --test tests/app.test.js
uv run scripts/validate_sources.py
```
## Rebuild downloads and analysis

The resumable pipeline skips non-empty downloads, streams new files through atomic .part files, and runs the source validator after downloads complete. Raw downloads are intentionally ignored by Git; the checked-in data/app-data.json keeps index.html immediately viewable.

```bash
uv run scripts/download_data.py
```

Use --force to refresh every source. Use --skip-validation only when you need downloads without the analysis checks.
