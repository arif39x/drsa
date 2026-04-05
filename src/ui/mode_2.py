from textual.containers import Vertical
from textual.widgets import Static, Markdown, Input

class Mode2DocumentVault(Vertical):
    def compose(self):
        yield Static("MODE 2: DOCUMENT VAULT", classes="panel_title")
        yield Markdown("Parse and ingest technical PDFs and research material.", id="m2_chat_output")
        yield Input(placeholder="Enter document path...", id="m2_chat_input")
