#!/bin/bash
# Extract proxy with credentials from environment
PROXY_URL="$HTTPS_PROXY"

# Launch Chrome with proxy that includes auth
google-chrome-stable \
  --headless \
  --disable-gpu \
  --remote-debugging-port=9222 \
  --no-sandbox \
  --disable-dev-shm-usage \
  --user-data-dir=/tmp/chrome-cdp-10 \
  --proxy-server="$PROXY_URL" \
  about:blank
