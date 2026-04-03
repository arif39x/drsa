# DRSA: Deep Research and Search Assistant

DRSA is a professional, Python-based terminal assistant designed for deep technical research, codebase analysis, and document management. It integrates state-of-the-art AI tools including LlamaIndex, LangGraph, Tree-Sitter, and more into a unified "Command Center" interface.

## Key Features

- **Unified TUI Command Center**: Responsive 3-column layout (Sidebar, Main Console, Visualization Panel).
- **Four Research Modes**:
  - **Code Import**: Multi-level codebase analysis via Tree-Sitter and LlamaIndex.
  - **Doc Research**: High-fidelity technical document parsing (PDF, Office) using Marker.
  - **Web Scrap**: Automated web research and deep scraping via Crawl4AI and SearXNG.
  - **Studio Mode**: Expert report synthesis using LangGraph agentic reasoning.
- **Dynamic Visualizations**: Automatic Mermaid graph generation and LaTeX rendering (via `chafa` to ANSI).
- **System Robustness**: Graceful dependency degradation and automated Tree-Sitter grammar compilation.

## 🛠️ Installation

### 1. Prerequisites

Ensure you have the following installed on your system:

- Python 3.10+
- Node.js & NPM (for Mermaid CLI: `npm install -g @mermaid-js/mermaid-cli`)
- Chafa (for terminal graphics: `sudo apt install chafa`)
- Docker (required if running SearXNG or LanceDB in containers)

### 2. Setup DRSA

```bash
# Clone the repository
git clone <your-repo-url>
cd DRSA

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here
SEARXNG_URL=http://localhost:8080
LANCEDB_URI=./lancedb_vault
```

## ⌨️ Usage

Launch the assistant using the provided runner script:

```bash
bash run.sh
```

### Hotkeys

- `CTRL + B`: Toggle Sidebar (Modes & Actions)
- `CTRL + V`: Toggle Visualization Panel
- `Q`: Quit Application
- `ENTER`: Submit Query in Main Console

## 🏗️ Architecture

- **UI Frameworks**: Supports both `Textual` (`src/main_tui.py`) and `PyTermGUI` (`src/main_tui_ptg.py`).
- **Reasoning Engine**: LangGraph cyclic agent located in `src/features/brain/`.
- **Storage**: Vector indexing via LanceDB in `src/features/vault/`.
- **Analysis**: Tree-Sitter based code parsing in `src/features/github/`.

## 📦 Troubleshooting

- **Missing Dependencies**: If a feature (like `crawl4ai`) is missing, DRSA will surface a warning in the Sidebar/Footer instead of crashing.
- **Grammar Errors**: If code analysis fails, run `python setup_grammars.py` manually to recompile Tree-Sitter languages.
