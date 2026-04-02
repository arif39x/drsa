from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Input, Button, Markdown, ListItem, ListView
from textual.binding import Binding
from textual.reactive import reactive

from src.features.github.analyzer import DeepCodeAnalyzer
from src.features.research.visualizer import ResearchVisualizer
from src.features.brain.orchestrator import build_orchestrator
try:
    from src.features.research.scraper import ResearchScraper
    from src.features.vault.parser import TechDocParser
except ImportError:
    ResearchScraper = None
    TechDocParser = None

class DRSAUnifiedApp(App):
    # unified TUI for deep research and code analysis.

    CSS = """
    Screen { background: #0f172a; }
    Header { background: #1e293b; color: #38bdf8; }
    Footer { background: #1e293b; color: #94a3b8; }
    .panel_title { color: #38bdf8; border-bottom: solid #334155; }
    .panel { background: #1e293b; border: solid #334155; }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("ctrl+b", "toggle_sidebar", "Sidebar"),
        Binding("ctrl+v", "toggle_viz", "Viz Panel"),
    ]

    current_mode = reactive("code_import")

    def on_mount(self) -> None:
        self.code_analyzer = DeepCodeAnalyzer()
        self.viz_engine = ResearchVisualizer()
        self.orchestrator = build_orchestrator()
        self.scraper = ResearchScraper() if ResearchScraper else None
        self.parser = TechDocParser() if TechDocParser else None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Static("MODES", classes="panel_title")
                with ListView(id="mode_list"):
                    yield ListItem(Static("Code Import"), id="code_import")
                    yield ListItem(Static("Doc Research"), id="doc_research")
                    yield ListItem(Static("Web Scrap"), id="web_scrap")
                yield Static("ACTIONS", classes="panel_title")
                yield Button("Visualize Research", variant="primary", id="viz_btn")
                yield Button("Convert to Doc", variant="success", id="convert_btn")

            with Container(id="main_container"):
                with Vertical(id="chat_area"):
                    yield Static("UNIFIED CHATBOT", classes="panel_title")
                    yield Markdown("", id="chat_output")
                    yield Input(placeholder="Ask a question...", id="chat_input")

            with Vertical(id="viz_panel"):
                yield Static("VISUALIZATION PANEL", classes="panel_title")
                yield Static("---")
                yield Static("Analysis Output", id="viz_content", classes="panel")
                yield Markdown("", id="viz_md_output")

        yield Footer()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        query = event.value
        self.query_one("#chat_output").update(f"Processing: {query}")

        if self.current_mode == "web_scrap":
            results = await self.scraper.search_and_scrape(query)
            summary = "\n\n".join([f"### {res['title']}\n{res['markdown'][:500]}..." for res in results])
            self.query_one("#chat_output").update(summary)

        elif self.current_mode == "code_import":
            if "github.com" in query:
                status = self.code_analyzer.clone_and_index(query)
                self.query_one("#chat_output").update(status)
            else:
                answer = self.code_analyzer.query(query)
                self.query_one("#chat_output").update(answer)

    def on_list_view_selected(self, event: ListView.Selected):
        self.current_mode = event.item.id
        self.query_one("#chat_output").update(f"Mode switched to: {self.current_mode}")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "viz_btn":
            self.query_one("#viz_content").update("Generating visualization...")
            self.query_one("#viz_md_output").update("Research Graph Synthesis")

    def action_toggle_sidebar(self) -> None:
        self.query_one("#sidebar").toggle_class("hidden")

    def action_toggle_viz(self) -> None:
        self.query_one("#viz_panel").toggle_class("hidden")

if __name__ == "__main__":
    DRSAUnifiedApp().run()
