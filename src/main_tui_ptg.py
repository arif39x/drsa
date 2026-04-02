import os
import sys
import asyncio
import pytermgui as ptg

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

class DRSAUnifiedAppPTG:
    def __init__(self):
        self.code_analyzer = DeepCodeAnalyzer()
        self.viz_engine = ResearchVisualizer()
        self.orchestrator = build_orchestrator()
        self.scraper = ResearchScraper() if ResearchScraper else None
        self.parser = TechDocParser() if TechDocParser else None
        
        self.current_mode = "code_import"
        self.manager = None

    def setup_sidebar(self) -> ptg.Window:
        def set_mode(mode_name: str):
            self.current_mode = mode_name
            self.chat_output.set_text(f"🔄 Mode switched to: [{ptg.Color.CYAN}]{self.current_mode}")

        sidebar = ptg.Window(
            ptg.Label("[ptg.title]MODES", parent_align=0),
            ptg.Button("Code Import", lambda *_: set_mode("code_import")),
            ptg.Button("Doc Research", lambda *_: set_mode("doc_research")),
            ptg.Button("Web Scrap", lambda *_: set_mode("web_scrap")),
            ptg.Label(""),
            ptg.Label("[ptg.title]ACTIONS", parent_align=0),
            ptg.Button("Visualize Research", self.on_viz_pressed),
            ptg.Button("Convert to Doc", self.on_convert_pressed),
            width=30,
            is_bindable=False,
        )
        sidebar.set_title("[ptg.bold]DRSA SIDEBAR")
        return sidebar

    def setup_chat(self) -> ptg.Window:
        self.chat_output = ptg.Label("Welcome to DRSA Unified Assistant (PyTermGUI)\nUse the sidebar to switch modes.", parent_align=0)
        self.chat_input = ptg.InputField(prompt="Ask a question: ")
        
        # Override submit
        original_submit = self.chat_input.handle_key
        def handle_key(key):
            if key == ptg.keys.RETURN:
                asyncio.create_task(self.process_query(self.chat_input.value))
                self.chat_input.value = ""
                return True
            return original_submit(key)
        
        self.chat_input.handle_key = handle_key

        chat_window = ptg.Window(
            ptg.Label("[ptg.title]UNIFIED CHATBOT", parent_align=0),
            ptg.Container(self.chat_output, static_width=True),
            ptg.Label(""),
            self.chat_input,
            vertical_align=ptg.VerticalAlignment.TOP
        )
        chat_window.set_title("[ptg.bold]MAIN CONSOLE")
        return chat_window

    def setup_viz(self) -> ptg.Window:
        self.viz_content = ptg.Label("Analysis Output", parent_align=0)
        self.viz_md = ptg.Label("", parent_align=0)
        
        viz_window = ptg.Window(
            ptg.Label("[ptg.title]VISUALIZATION", parent_align=0),
            ptg.Container(self.viz_content, static_width=True),
            ptg.Label("---"),
            self.viz_md,
            width=40
        )
        viz_window.set_title("[ptg.bold]VIZ PANEL")
        return viz_window

    async def process_query(self, query: str):
        if not query:
            return

        self.chat_output.set_text(f"⏳ Processing query in [ptg.bold]{self.current_mode}[/ptg.bold] mode...")
        
        try:
            if self.current_mode == "web_scrap":
                if self.scraper:
                    results = await self.scraper.search_and_scrape(query)
                    summary = "[ptg.bold]Web Research Results[/ptg.bold]\n\n"
                    summary += "\n\n".join([f"• {res['title']}\n  {res['url']}" for res in results])
                    self.chat_output.set_text(summary)
                else:
                    self.chat_output.set_text("❌ [ptg.color=1]ResearchScraper is not available.")

            elif self.current_mode == "code_import":
                if "github.com" in query:
                    status = self.code_analyzer.clone_and_index(query)
                    self.chat_output.set_text(f"✅ {status}")
                else:
                    answer = self.code_analyzer.query(query)
                    self.chat_output.set_text(f"[ptg.bold]Code Analysis[/ptg.bold]\n\n{answer}")

            elif self.current_mode == "doc_research":
                if self.parser and os.path.exists(query):
                    if query.endswith(".pdf"):
                        content = self.parser.parse_technical_pdf(query)
                    else:
                        content = self.parser.parse_office_doc(query)
                    self.chat_output.set_text(f"[ptg.bold]Document Content[/ptg.bold]\n\n{content}")
                else:
                    self.chat_output.set_text(f"❌ [ptg.color=1]Document not found at path: {query}")

        except Exception as e:
            self.chat_output.set_text(f"❌ [ptg.color=1]Error: {str(e)}")

    def on_viz_pressed(self, *args):
        self.viz_content.set_text("Generating visualization...")
        mermaid_sample = "graph TD\nA[Research Query] --> B(Search)\nB --> C{Found?}\nC -->|Yes| D[Scrape]\nC -->|No| E[End]"
        viz_output = self.viz_engine.render_mermaid_to_ansi(mermaid_sample)
        self.viz_md.set_text(f"Research Graph Synthesis\n\n{mermaid_sample}")
        self.viz_content.set_text(viz_output)

    def on_convert_pressed(self, *args):
        self.chat_output.set_text("📄 Converting research to technical document...")

    def run(self):
        with ptg.WindowManager() as manager:
            self.manager = manager
            
            # Clear default layout and setup custom slots
            manager.layout = ptg.Layout()
            manager.layout.add_slot("Side", width=30)
            manager.layout.add_slot("Main")
            manager.layout.add_slot("Viz", width=40)
            
            sidebar = self.setup_sidebar()
            chat = self.setup_chat()
            viz = self.setup_viz()
            
            # Assign windows directly to slots to avoid AttributeError in manager.add
            manager.layout.slots[0].content = sidebar
            manager.layout.slots[1].content = chat
            manager.layout.slots[2].content = viz
            
            # We still need to 'add' them to the manager to ensure they are managed/rendered
            manager.add(sidebar)
            manager.add(chat)
            manager.add(viz)
            
            manager.bind("q", lambda *_: manager.stop())
            manager.bind("ctrl-b", lambda *_: sidebar.toggle_visibility())
            manager.bind("ctrl-v", lambda *_: viz.toggle_visibility())
            
            manager.run()

if __name__ == "__main__":
    app = DRSAUnifiedAppPTG()
    app.run()
