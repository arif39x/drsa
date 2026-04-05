from textual.containers import Vertical
from textual.widgets import Static, Markdown, Input

class Mode3StudioResearch(Vertical):
    def compose(self):
        yield Static("MODE 3: STUDIO RESEARCH", classes="panel_title")
        yield Markdown("Interact with the full agentic reasoning system (Planning, Searching, Synthesizing).", id="m3_chat_output")
        yield Input(placeholder="Ask a deep research question...", id="m3_chat_input")
