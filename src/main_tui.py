from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Input, Button, Markdown, ListItem, ListView
from textual.binding import Binding
from textual.reactive import reactive
import os

from src.features.github.analyzer import DeepCodeAnalyzer
from src.features.research.visualizer import ResearchVisualizer
from src.features.brain.orchestrator import build_orchestrator

try:
    from src.features.research.scraper import ResearchScraper
except ImportError:
    ResearchScraper = None

try:
    from src.features.vault.parser import TechDocParser
except ImportError:
    TechDocParser = None

class DRSAUnifiedApp(App):
    # unified TUI for deep research and code analysis.

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
        if not query:
            return

        chat_output = self.query_one("#chat_output", Markdown)
        chat_output.update(f"⏳ Processing query in **{self.current_mode}** mode...")
        event.input.value = ""

        try:
            if self.current_mode == "web_scrap":
                if self.scraper:
                    results = await self.scraper.search_and_scrape(query)
                    summary = "## Web Research Results\n\n"
                    summary += "\n\n".join([f"### {res['title']}\n{res['markdown'][:500]}..." for res in results])
                    chat_output.update(summary)
                else:
                    chat_output.update("❌ `ResearchScraper` is not available.")

            elif self.current_mode == "code_import":
                if "github.com" in query:
                    status = self.code_analyzer.clone_and_index(query)
                    chat_output.update(f"✅ {status}")
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
                else:
                    chat_output.update(f"❌ Document not found at path: {query}")

        except Exception as e:
            chat_output.update(f"❌ Error: {str(e)}")

    def on_list_view_selected(self, event: ListView.Selected):
        self.current_mode = event.item.id if event.item else "code_import"
        self.query_one("#chat_output", Markdown).update(f"🔄 Mode switched to: **{self.current_mode}**")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "viz_btn":
            self.query_one("#viz_content").update("Generating visualization...")
            # Example visualization rendering
            mermaid_sample = "graph TD\nA[Research Query] --> B(Search)\nB --> C{Found?}\nC -->|Yes| D[Scrape]\nC -->|No| E[End]"
            viz_output = self.viz_engine.render_mermaid_to_ansi(mermaid_sample)
            self.query_one("#viz_md_output", Markdown).update(f"### Research Graph Synthesis\n\n```mermaid\n{mermaid_sample}\n```")
            self.query_one("#viz_content").update(viz_output)

        elif event.button.id == "convert_btn":
            self.query_one("#chat_output", Markdown).update("📄 Converting research to technical document...")

    def action_toggle_sidebar(self) -> None:
        self.query_one("#sidebar").toggle_class("hidden")

    def action_toggle_viz(self) -> None:
        self.query_one("#viz_panel").toggle_class("hidden")

if __name__ == "__main__":
    DRSAUnifiedApp().run()
