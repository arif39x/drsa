#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_ROOT}/venv"
DOCKER_COMPOSE_FILE="${PROJECT_ROOT}/docker/searxng/docker-compose.yml"

# --- Visuals ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

function log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
function log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
function log_err()  { echo -e "${RED}[ERROR]${NC} $1"; }

# --- Header ---
echo "=========================================================="
echo "          DRSA: Deep Research & Search Assistant          "
echo "=========================================================="

# 1. Virtual Environment Check
if [ -d "$VENV_DIR" ]; then
    log_info "Activating virtual environment..."
    source "${VENV_DIR}/bin/activate"
else
    log_warn "Virtual environment not found at ${VENV_DIR}. Using system python."
fi

# 2. Dependency Services (Docker)
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    if [ -f "$DOCKER_COMPOSE_FILE" ]; then
        log_info "Starting SearXNG metasearch via Docker..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    else
        log_warn "SearXNG docker-compose file not found. Skipping."
    fi
else
    log_warn "Docker or docker-compose not installed. SearXNG features may be unavailable."
fi

# 3. Environment Variables
log_info "Configuring environment..."
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

# 4. Grammar Build (Handled automatically by analyzer, but good to check)
if [ -f "${PROJECT_ROOT}/setup_grammars.py" ]; then
    log_info "Ensuring Tree-Sitter grammars are ready..."
    # We call it manually just to pre-compile and avoid first-run lag in the UI
    python "${PROJECT_ROOT}/setup_grammars.py"
fi

# 5. Launch TUI
# Determine which TUI to launch based on argument, default to Textual as it is most feature-rich
TUI_MODE="textual"
if [[ "$1" == "--ptg" ]]; then
    TUI_MODE="pytermgui"
elif [[ "$1" == "--textual" ]]; then
    TUI_MODE="textual"
fi

case $TUI_MODE in
    "textual")
        log_info "Launching Command Center (Textual)..."
        if python -c "import textual" &> /dev/null; then
            python -m src.main_tui
        else
            log_err "Textual not installed. Run 'pip install textual'"
            exit 1
        fi
        ;;
    "pytermgui")
        log_info "Launching Terminal Dashboard (PyTermGUI)..."
        if python -c "import pytermgui" &> /dev/null; then
            python -m src.main_tui_ptg
        else
            log_err "PyTermGUI not installed. Run 'pip install pytermgui'"
            exit 1
        fi
        ;;
esac
