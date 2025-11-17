# Notes
- Start project. Objective: minimal web app for fuzzy matched PDF text linking.
- Added initial failing backend and frontend tests.
- Encountered proxy blocks fetching PyPI and npm packages; pivoted to avoid external installs by vendoring minimal utilities and relying on system-installed FastAPI.
- Implemented upload endpoint using raw body to avoid python-multipart dependency.
- Added custom fuzzy matcher and lit-style helpers locally to keep app offline-friendly.
