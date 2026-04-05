import asyncio
import os
import threading

import httpx
import pytermgui as ptg

from src.features.brain.agentic_reasoning import run_agent
from src.features.brain.orchestrator import build_orchestrator
from src.features.github.analyzer import DeepCodeAnalyzer
from src.features.research.visualizer import ResearchVisualizer

_DEP_STATUS: dict[str, str | bool] = {}

try:
    from src.features.research.scraper import ResearchScraper

    _DEP_STATUS["scraper"] = True
except ImportError as _e:
    ResearchScraper = None
    _DEP_STATUS["scraper"] = f"UNAVAIL: {_e}"

try:
    from src.features.vault.parser import TechDocParser

    _DEP_STATUS["parser"] = True
except ImportError as _e:
    TechDocParser = None
    _DEP_STATUS["parser"] = f"UNAVAIL: {_e}"


def _dep_summary() -> str:
    ok = [k for k, v in _DEP_STATUS.items() if v is True]
    bad = [k for k, v in _DEP_STATUS.items() if v is not True]
    parts = []
    if ok:
        parts.append("[ptg.color=2]" + ",".join(ok) + "[/ptg.color=2]")
    if bad:
        parts.append("[ptg.color=1]" + ",".join(bad) + "[/ptg.color=1]")
    return " | ".join(parts) if parts else "all OK"


class DRSAUnifiedAppPTG:
    def __init__(self) -> None:
        self.viz_engine = ResearchVisualizer()
        self.orchestrator = build_orchestrator()

        try:
            self.code_analyzer: DeepCodeAnalyzer | None = DeepCodeAnalyzer()
        except RuntimeError as exc:
            self.code_analyzer = None
            _DEP_STATUS["grammar"] = f"UNAVAIL: {exc}"

        self.scraper = ResearchScraper() if ResearchScraper else None
        self.parser = TechDocParser() if TechDocParser else None

        self.current_mode = "code_import"
        self.manager: ptg.WindowManager | None = None
        self.header_label: ptg.Label | None = None
        self.footer_content: ptg.Label | None = None

        self.loop = asyncio.new_event_loop()
        bg = threading.Thread(
            target=lambda: (
                asyncio.set_event_loop(self.loop),
                self.loop.run_forever(),
            ),
            daemon=True,
        )
        bg.start()

    def _setup_header(self) -> ptg.Window:
        self.header_label = ptg.Label(
            f"[ptg.bold]DRSA[/ptg.bold]  |  MODE: [6]{self.current_mode.upper()}[/]",
            parent_align=0,
        )
        win = ptg.Window(self.header_label, is_bindable=False, is_movable=False)
        win.styles.border = "thin"
        return win

    def _setup_footer(self) -> ptg.Window:
        initial_status = (
            f"Q: Quit | CTRL+B: Sidebar | CTRL+V: Viz"
            f" | DEPS: {_dep_summary()}"
            f" | SearXNG: [ptg.color=1]checking...[/ptg.color=1]"
            f" | DB: [ptg.color=1]checking...[/ptg.color=1]"
        )
        self.footer_content = ptg.Label(initial_status, parent_align=0)
        win = ptg.Window(self.footer_content, is_bindable=False, is_movable=False)
        win.styles.border = "thin"
        return win

    def _setup_sidebar(self) -> ptg.Window:

        def set_mode(mode_name: str) -> None:
            self.current_mode = mode_name
            self._update_header()
            self.chat_output.set_text(
                f"Mode switched to: [6]{mode_name.replace('_', ' ').upper()}[/]"
            )

        sidebar = ptg.Window(
            ptg.Label("[ptg.title]MODES", parent_align=0),
            ptg.Button("Code Import", lambda *_: set_mode("code_import")),
            ptg.Button("Doc Research", lambda *_: set_mode("doc_research")),
            ptg.Button("Web Scrap", lambda *_: set_mode("web_scrap")),
            ptg.Button("Studio", lambda *_: set_mode("studio")),
            ptg.Label(""),
            ptg.Label("[ptg.title]QUICK ACTIONS", parent_align=0),
            ptg.Button("Visualize", self._on_viz_pressed),
            ptg.Button(
                "Convert PDF",
                lambda *_: self.chat_output.set_text("Converting PDF content..."),
            ),
            ptg.Button("Scan Vault", self._on_scan_vault),
            width=30,
            is_bindable=False,
        )
        sidebar.set_title("[ptg.bold]DRSA SIDEBAR")
        return sidebar

    def _setup_chat(self) -> ptg.Window:
        """Build the main console with output area and chat input."""
        self.chat_output = ptg.Label(
            "Welcome to DRSA Unified Assistant\nUse the sidebar to select your focus.",
            parent_align=0,
        )
        self.chat_input = ptg.InputField(prompt="Query: ")

        original_handle = self.chat_input.handle_key

        def handle_key(key: str) -> bool:
            if key == ptg.keys.RETURN:
                query = self.chat_input.value
                self.chat_input.value = ""
                asyncio.run_coroutine_threadsafe(self._process_query(query), self.loop)
                return True
            return original_handle(key)

        self.chat_input.handle_key = handle_key

        win = ptg.Window(
            ptg.Label("[ptg.title]MAIN RESEARCH CONSOLE", parent_align=0),
            ptg.Container(self.chat_output, static_width=True),
            ptg.Label(""),
            self.chat_input,
            vertical_align=ptg.VerticalAlignment.TOP,
        )
        win.set_title("[ptg.bold]MAIN CONSOLE")
        return win

    def _setup_viz(self) -> ptg.Window:
        """Build the right-hand visualization panel."""
        self.viz_content = ptg.Label(
            "Analysis output will appear here.", parent_align=0
        )
        self.viz_md = ptg.Label("", parent_align=0)

        win = ptg.Window(
            ptg.Label("[ptg.title]VISUALIZATION PANEL", parent_align=0),
            ptg.Container(self.viz_content, static_width=True),
            ptg.Label("---"),
            self.viz_md,
            width=40,
        )
        win.set_title("[ptg.bold]VIZ PANEL")
        return win

    async def _update_status_bar_loop(self) -> None:
        """Periodically probe SearXNG and LanceDB, updating the footer."""
        while True:
            searx_status = "[ptg.color=1]SearXNG: Offline[/ptg.color=1]"
            lancedb_status = "[ptg.color=1]DB: Not found[/ptg.color=1]"

            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get("http://localhost:8080", timeout=2.0)
                    if resp.status_code == 200:
                        searx_status = "[ptg.color=2]SearXNG: Online[/ptg.color=2]"
            except Exception:
                pass

            if os.path.exists("./lancedb_vault"):
                lancedb_status = "[ptg.color=2]DB: Connected[/ptg.color=2]"

            self.footer_content.set_text(
                f"Q: Quit | CTRL+B: Sidebar | CTRL+V: Viz"
                f" | DEPS: {_dep_summary()}"
                f" | {searx_status} | {lancedb_status}"
            )
            await asyncio.sleep(10)

    async def _process_query(self, query: str) -> None:
        """Dispatch a query to the appropriate backend based on the active mode."""
        if not query.strip():
            return

        self.chat_output.set_text(
            f"Processing in [ptg.bold]{self.current_mode}[/ptg.bold] mode..."
        )

        try:
            if self.current_mode == "web_scrap":
                if self.scraper:
                    results = await self.scraper.search_and_scrape(query)
                    summary = "[ptg.bold]Web Research Results[/ptg.bold]\n\n"
                    summary += "\n\n".join(
                        [f"• {r['title']}\n  {r['url']}" for r in results]
                    )
                    self.chat_output.set_text(summary)
                else:
                    msg = _DEP_STATUS.get("scraper", "unknown")
                    self.chat_output.set_text(
                        f"[1]ResearchScraper unavailable[/]: {msg}\n"
                        "Install: pip install crawl4ai"
                    )

            elif self.current_mode == "code_import":
                if self.code_analyzer is None:
                    msg = _DEP_STATUS.get("grammar", "Grammar build failed.")
                    self.chat_output.set_text(f"[1]Code Analyzer unavailable[/]: {msg}")
                elif "github.com" in query:
                    status = self.code_analyzer.clone_and_index(query)
                    self.chat_output.set_text(status)
                else:
                    answer = self.code_analyzer.query(query)
                    self.chat_output.set_text(
                        f"[ptg.bold]Code Analysis[/ptg.bold]\n\n{answer}"
                    )

            elif self.current_mode == "doc_research":
                if self.parser and os.path.exists(query):
                    if query.endswith(".pdf"):
                        content = self.parser.parse_technical_pdf(query)
                    else:
                        content = self.parser.parse_office_doc(query)
                    self.chat_output.set_text(
                        f"[ptg.bold]Document Content[/ptg.bold]\n\n{content}"
                    )
                elif not self.parser:
                    msg = _DEP_STATUS.get("parser", "unknown")
                    self.chat_output.set_text(
                        f"[1]Document Parser unavailable[/]: {msg}"
                    )
                else:
                    self.chat_output.set_text(f"[1]File not found:[/] {query}")

            elif self.current_mode == "studio":
                self.chat_output.set_text(
                    f"Synthesising expert report for '{query}'..."
                )
                answer = run_agent(query, context="")
                self.chat_output.set_text(
                    f"[ptg.bold]Studio Report[/ptg.bold]\n\n{answer}"
                )

        except Exception as exc:
            self.chat_output.set_text(f"[1]Error:[/] {exc}")

    def _on_viz_pressed(self, *args) -> None:
        """Build a knowledge graph and render it in the Viz Panel."""
        from src.features.studio.knowledge_graph import build_graph

        self.viz_content.set_text("Building knowledge graph...")
        sample_text = (
            "Python and FastAPI are used together. "
            "LanceDB stores vector embeddings. "
            "LangGraph orchestrates agent nodes in Python."
        )
        graph = build_graph(sample_text)
        ansi_output = self.viz_engine.render_knowledge_graph(graph)
        self.viz_md.set_text(graph["mermaid"])
        self.viz_content.set_text(ansi_output)

    def _on_scan_vault(self, *args) -> None:
        """Scan the LanceDB vault and list tables in the main console."""
        try:
            import lancedb

            db = lancedb.connect("./lancedb_vault")
            tables = db.table_names()
            if tables:
                report = "Vault Tables:\n" + "\n".join(f"  - {t}" for t in tables)
            else:
                report = "Vault scan complete: no tables found."
            self.chat_output.set_text(report)
        except Exception as exc:
            self.chat_output.set_text(f"[1]Vault scan error:[/] {exc}")

    def _update_header(self) -> None:
        """Refresh header label with the current mode name."""
        if self.header_label:
            self.header_label.set_text(
                f"[ptg.bold]DRSA[/ptg.bold]  |  MODE: [6]{self.current_mode.upper()}[/]"
            )

    def run(self) -> None:
        """Launch the PyTermGUI window manager and render the layout."""
        with ptg.WindowManager() as manager:
            self.manager = manager

            manager.layout = ptg.Layout()
            manager.layout.add_slot("Header", height=3)
            manager.layout.add_break()
            manager.layout.add_slot("Side", width=30)
            manager.layout.add_slot("Main")
            manager.layout.add_slot("Viz", width=40)
            manager.layout.add_break()
            manager.layout.add_slot("Footer", height=3)

            header = self._setup_header()
            sidebar = self._setup_sidebar()
            self.chat = self._setup_chat()
            self.viz = self._setup_viz()
            footer = self._setup_footer()

            # Slot indices: 0=Header, 1=break, 2=Side, 3=Main, 4=Viz, 5=break, 6=Footer
            manager.layout.slots[0].content = header
            manager.layout.slots[2].content = sidebar
            manager.layout.slots[3].content = self.chat
            manager.layout.slots[4].content = self.viz
            manager.layout.slots[6].content = footer

            manager.add(header)
            manager.add(sidebar)
            manager.add(self.chat)
            manager.add(self.viz)
            manager.add(footer)

            manager.bind("q", lambda *_: manager.stop())
            manager.bind("ctrl-b", lambda *_: sidebar.toggle_visibility())
            manager.bind("ctrl-v", lambda *_: self.viz.toggle_visibility())

            asyncio.run_coroutine_threadsafe(self._update_status_bar_loop(), self.loop)
            manager.run()


if __name__ == "__main__":
    DRSAUnifiedAppPTG().run()
