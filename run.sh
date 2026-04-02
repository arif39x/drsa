#!/usr/bin/env bash

set -e

echo "=========================================="
echo "          Starting DRSA                 "
echo "=========================================="

# Starting Docker SearXNG service for metasearch
echo "Starting local SearXNG Docker container..."
if command -v docker &> /dev/null; then
    docker compose -f docker/searxng/docker-compose.yml up -d
else
    echo "  Docker not found. Skipping SearXNG startup."
fi

# Python ABI flag
echo "Setting Python ABI configuration..."
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

# Handle manual TUI setup
echo " Ensuring system-specific grammars are built..."
python3 setup_grammars.py

# Start Python TUI (PyTermGUI)
echo "Launching DRSA Professional TUI (PyTermGUI)..."
if python3 -c "import pytermgui" &> /dev/null; then
    python3 -m src.main_tui_ptg
else
    echo "❌ ERROR: 'pytermgui' not found. Please run 'pip install -r requirements.txt' again."
fi
