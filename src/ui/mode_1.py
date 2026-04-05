from textual.containers import Vertical
from textual.widgets import Static, Markdown, Input

class Mode1CodeIntelligence(Vertical):
    def compose(self):
        yield Static("MODE 1: CODE INTELLIGENCE", classes="panel_title")
        yield Markdown("Analyze target repositories and codebase files using Tree-Sitter.", id="m1_chat_output")
        yield Input(placeholder="Enter GitHub URL or local path...", id="m1_chat_input")
