from textual.widgets import Vertical, Static, Markdown, Input
from textual.containers import Container

class StudioView(Vertical):
    # Research Studio Interface.
    def compose(self):
        yield Static("Research Studio (LaTeX & Diagrams)", classes="title")
        yield Markdown("")
        yield Input(placeholder="Add research note...", id="studio_input")
