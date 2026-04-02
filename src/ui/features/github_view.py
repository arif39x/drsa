from textual.widgets import Vertical, Static, Input, Button
from textual.containers import Container

class GitHubView(Vertical):
    """GitHub Repository Analysis Interface."""
    def compose(self):
        yield Static("GitHub Repository Analysis", classes="title")
        yield Input(placeholder="Enter Repository URL...", id="repo_input")
        yield Button("Analyze Repository", variant="primary", id="analyze_btn")
        yield Static(id="index_status", classes="panel")
