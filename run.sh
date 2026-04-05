#!/usr/bin/env bash

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_ROOT}/venv"
DOCKER_COMPOSE_FILE="${PROJECT_ROOT}/docker/searxng/docker-compose.yml"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

function log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
function log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
function log_err()  { echo -e "${RED}[ERROR]${NC} $1"; }

echo "=========================================================="
echo "          DRSA: Deep Research & Search Assistant          "
echo "=========================================================="

if [ -d "$VENV_DIR" ]; then
    log_info "Activating virtual environment..."
    source "${VENV_DIR}/bin/activate"
else
    log_warn "Virtual environment not found at ${VENV_DIR}. Using system python."
fi

for cmd in chafa mmdc docker; do
    if ! command -v $cmd &> /dev/null; then
        log_warn "Missing binary: $cmd. Some functionality may be degraded."
    fi
done

if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    if docker info >/dev/null 2>&1; then
        if [ -f "$DOCKER_COMPOSE_FILE" ]; then
            log_info "Docker is running. Starting SearXNG metasearch via Docker..."
            docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
        else
            log_warn "SearXNG docker-compose file not found. Skipping."
        fi
    else
        log_warn "Docker daemon is not running. Start it to run SearXNG."
    fi
else
    log_warn "Docker or docker-compose not installed. SearXNG features may be unavailable."
fi

log_info "Configuring environment..."
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

if [ ! -f "${PROJECT_ROOT}/grammars/languages.so" ]; then
    log_info "languages.so not found, building Tree-Sitter grammars..."
    if [ -f "${PROJECT_ROOT}/setup_grammars.py" ]; then
        python "${PROJECT_ROOT}/setup_grammars.py"
    else
        log_err "setup_grammars.py not found!"
    fi
else
    log_info "Tree-Sitter grammars are ready."
fi
log_info "Launching Deep Research Command Center (Textual)..."
if python -c "import textual" &> /dev/null; then
    python -m src.main_tui
else
    log_warn "Textual not installed. Falling back to PyTermGUI..."
    if python -c "import pytermgui" &> /dev/null; then
        python -m src.main_tui_ptg
    else
        log_err "No suitable UI (Textual or PyTermGUI) found. Run 'pip install -r requirements.txt'"
        exit 1
    fi
fi
