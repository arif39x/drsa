#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "=========================================="
echo "    Starting DRSA (Definitive Assistant)   "
echo "=========================================="

# 1. Start Docker SearXNG service for metasearch
echo "[1/3] Starting local SearXNG Docker container..."
if command -v docker &> /dev/null; then
    docker compose -f docker/searxng/docker-compose.yml up -d
else
    echo "⚠️  Docker not found. Skipping SearXNG startup."
fi

# 2. Setup Python ABI flag for PyO3 v0.22 and Python 3.14 compatibility
echo "[2/3] Setting Python ABI configuration via PYO3_USE_ABI3_FORWARD_COMPATIBILITY..."
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

# 3. Start Tauri App
echo "[3/3] Launching Tauri Glass UI..."
npm run tauri dev
