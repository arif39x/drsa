"""DRSA Unified TUI built with Textual — Command Center layout."""

import os

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    ListItem,
    ListView,
    Markdown,
    Static,
)

from src.features.github.analyzer import DeepCodeAnalyzer
from src.features.research.visualizer import ResearchVisualizer
from src.features.brain.orchestrator import build_orchestrator
from src.features.brain.agentic_reasoning import run_agent

# ---------------------------------------------------------------------------
# Dependency availability tracking
# ---------------------------------------------------------------------------
_DEP_STATUS: dict[str, str | bool] = {}

try:
    from src.features.research.scraper import ResearchScraper

    _DEP_STATUS["scraper"] = True
except ImportError as _e:
    ResearchScraper = None  # type: ignore[assignment]
    _DEP_STATUS["scraper"] = f"UNAVAIL: {_e}"

try:
    from src.features.vault.parser import TechDocParser

    _DEP_STATUS["parser"] = True
except ImportError as _e:
    TechDocParser = None  # type: ignore[assignment]
    _DEP_STATUS["parser"] = f"UNAVAIL: {_e}"


def _dep_warnings() -> str:
    """Return a newline-joined list of dependency warnings (if any)."""
    lines = []
    for name, status in _DEP_STATUS.items():
        if status is not True:
            lines.append(f"[yellow]WARN[/yellow] {name}: {status}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

class DRSAUnifiedApp(App):
    """Unified TUI for deep research and code analysis."""

    CSS = """
    Screen {
        background: #0f172a;
    }

    Header {
        background: #1e293b;
        color: #38bdf8;
        text-style: bold;
    }

    Footer {
        background: #1e293b;
        color: #94a3b8;
    }

    #sidebar {
        width: 30;
        background: #1e293b;
        border-right: tall #334155;
        padding: 1;
    }

    .panel_title {
        color: #38bdf8;
        text-style: bold;
        margin-bottom: 1;
        border-bottom: solid #334155;
    }

    .panel {
        background: #1e293b;
        border: solid #334155;
        padding: 1;
    }

    .dep_warning {
        color: #fbbf24;
        margin-top: 1;
    }

    #main_container {
        padding: 1;
    }

    #chat_area {
        height: 1fr;
    }

    #chat_output {
        height: 1fr;
        border: solid #334155;
        background: #0f172a;
        padding: 1;
    }

    #chat_input {
        margin-top: 1;
        border: solid #38bdf8;
    }

    #viz_panel {
        width: 40;
        background: #1e293b;
        border-left: tall #334155;
        padding: 1;
        display: block;
    }

    #viz_panel.hidden {
        display: none;
    }

    #sidebar.hidden {
        display: none;
    }

    ListItem {
        padding: 1;
        background: transparent;
    }

    ListItem:hover {
        background: #334155;
    }

    ListItem.--highlight {
        background: #38bdf8;
        color: #0f172a;
    }

    Button {
        width: 100%;
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("ctrl+b", "toggle_sidebar", "Sidebar"),
        Binding("ctrl+v", "toggle_viz", "Viz Panel"),
    ]

    current_mode: reactive[str] = reactive("code_import")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_mount(self) -> None:
        """Initialise backend components and show dependency status."""
        try:
            self.code_analyzer: DeepCodeAnalyzer | None = DeepCodeAnalyzer()
        except RuntimeError as exc:
            self.code_analyzer = None
            _DEP_STATUS["grammar"] = str(exc)

        self.viz_engine = ResearchVisualizer()
        self.orchestrator = build_orchestrator()
        self.scraper = ResearchScraper() if ResearchScraper else None
        self.parser = TechDocParser() if TechDocParser else None

        # Surface any dep warnings in the sidebar
        warnings = _dep_warnings()
        if warnings:
            self.query_one("#dep_warnings", Static).update(warnings)
            self.sub_title = "System warnings — check sidebar"

    # ------------------------------------------------------------------
    # Compose
    # ------------------------------------------------------------------

    def compose(self) -> ComposeResult:
        """Build the 3-column Command Center layout."""
        yield Header(show_clock=True)
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Static("MODES", classes="panel_title")
                with ListView(id="mode_list"):
                    yield ListItem(Static("Code Import"), id="code_import")
                    yield ListItem(Static("Doc Research"), id="doc_research")
                    yield ListItem(Static("Web Scrap"), id="web_scrap")
                    yield ListItem(Static("Studio"), id="studio")
                yield Static("QUICK ACTIONS", classes="panel_title")
                yield Button("Visualize", variant="primary", id="viz_btn")
                yield Button("Convert PDF", variant="success", id="convert_btn")
                yield Button("Scan Vault", variant="warning", id="scan_btn")
                yield Static("", id="dep_warnings", classes="dep_warning")

            with Container(id="main_container"):
                with Vertical(id="chat_area"):
                    yield Static("MAIN RESEARCH CONSOLE", classes="panel_title")
                    yield Markdown("Welcome to DRSA. Select a mode and ask a question.", id="chat_output")
                    yield Input(placeholder="Ask a question...", id="chat_input")

            with Vertical(id="viz_panel"):
                yield Static("VISUALIZATION PANEL", classes="panel_title")
                yield Static("Analysis output will appear here.", id="viz_content", classes="panel")
                yield Markdown("", id="viz_md_output")

        yield Footer()

    # ------------------------------------------------------------------
    # Event Handlers
    # ------------------------------------------------------------------

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Process a query from the chat input box."""
        query = event.value.strip()
        if not query:
            return

        chat_output = self.query_one("#chat_output", Markdown)
        chat_output.update(f"Processing query in **{self.current_mode}** mode...")
        event.input.value = ""

        try:
            if self.current_mode == "web_scrap":
                if self.scraper:
                    results = await self.scraper.search_and_scrape(query)
                    summary = "## Web Research Results\n\n"
                    summary += "\n\n".join(
                        [f"### {r['title']}\n{r['markdown'][:500]}..." for r in results]
                    )
                    chat_output.update(summary)
                else:
                    status = _DEP_STATUS.get("scraper", "unknown error")
                    chat_output.update(
                        f"**ResearchScraper unavailable.**\n\n`{status}`\n\n"
                        "Install crawl4ai: `pip install crawl4ai`"
                    )

            elif self.current_mode == "code_import":
                if self.code_analyzer is None:
                    chat_output.update(
                        f"**Code Analyzer unavailable.**\n\n"
                        f"`{_DEP_STATUS.get('grammar', 'Grammar build failed.')}`"
                    )
                elif "github.com" in query:
                    status = self.code_analyzer.clone_and_index(query)
                    chat_output.update(f"**{status}**")
                else:
                    answer = self.code_analyzer.query(query)
                    chat_output.update(f"### Code Analysis\n\n{answer}")

            elif self.current_mode == "doc_research":
                if self.parser and os.path.exists(query):
                    if query.endswith(".pdf"):
                        content = self.parser.parse_technical_pdf(query)
                    else:
                        content = self.parser.parse_office_doc(query)
                    chat_output.update(f"### Document Content\n\n{content}")
                elif not self.parser:
                    status = _DEP_STATUS.get("parser", "unknown error")
                    chat_output.update(
                        f"**Document Parser unavailable.**\n\n`{status}`"
                    )
                else:
                    chat_output.update(f"**File not found:** `{query}`")

            elif self.current_mode == "studio":
                chat_output.update(f"Synthesising expert report for: *{query}*...")
                answer = run_agent(query, context="")
                chat_output.update(f"### Studio Report\n\n{answer}")

        except Exception as exc:
            chat_output.update(f"**Error:** `{exc}`")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Switch the active research mode."""
        self.current_mode = event.item.id if event.item else "code_import"
        self.query_one("#chat_output", Markdown).update(
            f"Mode switched to: **{self.current_mode.replace('_', ' ').title()}**"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle sidebar quick-action buttons."""
        if event.button.id == "viz_btn":
            self._run_visualization()
        elif event.button.id == "convert_btn":
            self.query_one("#chat_output", Markdown).update("Converting research to document...")
        elif event.button.id == "scan_btn":
            self._run_vault_scan()

    # ------------------------------------------------------------------
    # Actions (key bindings)
    # ------------------------------------------------------------------

    def action_toggle_sidebar(self) -> None:
        """Toggle sidebar visibility."""
        self.query_one("#sidebar").toggle_class("hidden")

    def action_toggle_viz(self) -> None:
        """Toggle visualization panel visibility."""
        self.query_one("#viz_panel").toggle_class("hidden")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _run_visualization(self) -> None:
        """Build and render a knowledge graph or Mermaid diagram."""
        from src.features.studio.knowledge_graph import build_graph

        viz_content = self.query_one("#viz_content", Static)
        viz_md = self.query_one("#viz_md_output", Markdown)

        viz_content.update("Building knowledge graph...")
        sample_text = (
            "Python and FastAPI are used together. "
            "LanceDB stores vector embeddings. "
            "LangGraph orchestrates agent nodes in Python."
        )
        graph = build_graph(sample_text)
        ansi = self.viz_engine.render_knowledge_graph(graph)
        viz_content.update(ansi)
        viz_md.update(f"```mermaid\n{graph['mermaid']}\n```")

    def _run_vault_scan(self) -> None:
        """Scan the LanceDB vault and report table count."""
        chat_output = self.query_one("#chat_output", Markdown)
        try:
            import lancedb

            db = lancedb.connect("./lancedb_vault")
            tables = db.table_names()
            report = "### Vault Scan Results\n\n"
            if tables:
                report += "\n".join(f"- `{t}`" for t in tables)
            else:
                report += "_No tables found in vault._"
            chat_output.update(report)
        except Exception as exc:
            chat_output.update(f"**Vault scan error:** `{exc}`")


if __name__ == "__main__":
    DRSAUnifiedApp().run()
