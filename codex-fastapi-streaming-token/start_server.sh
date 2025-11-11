#!/bin/bash

echo "Starting Codex Token Streaming Server..."
echo ""
echo "Make sure you have:"
echo "1. Installed dependencies: pip install -r requirements.txt"
echo "2. Installed Codex CLI: npm install -g @openai/codex"
echo "3. Authenticated: codex login"
echo ""

python app.py
