from textual.widgets import Vertical, Static, Button
from textual.containers import Container

class VaultView(Vertical):
    """Document Vault & RAG Interface."""
    def compose(self):
        yield Static("Document Vault & RAG", classes="title")
        yield Static("Upload and index documents for deep research.", classes="panel")
        yield Button("Scan Local Vault", variant="success", id="scan_btn")
        yield Static(id="vault_status", classes="panel")
