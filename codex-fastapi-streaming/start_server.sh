#!/bin/bash

# Startup script for Codex FastAPI Streaming Server

echo "Starting Codex FastAPI Streaming Server..."
echo "=========================================="
echo ""

# Check if codex is installed
if ! command -v codex &> /dev/null; then
    echo "Error: Codex CLI not found. Please install it first:"
    echo "  npm install -g @openai/codex"
    exit 1
fi

# Check if python dependencies are installed
if ! python -c "import fastapi" &> /dev/null; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

echo "Codex CLI version: $(codex --version)"
echo ""
echo "Starting server on http://0.0.0.0:8000"
echo "Web interface: http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python app.py
