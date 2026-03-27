import PdfUploader from "./PdfUploader";
import GithubLinkInput from "./GithubLinkInput";
import SearchInput from "./SearchInput";
import "./VaultPage.css";

export default function VaultPage() {
    return (
        <div class="vault-layout">
            <header class="vault-header">
                <h1 class="vault-title" style={{ "font-family": "monospace" }}>VAULT_CORE</h1>
                <p class="vault-subtitle" style={{ "font-family": "monospace" }}>// Ingest vectors, repos, and targets.</p>
            </header>

            <div class="vault-grid">
                {/* PDF / Multi-modal ingestion */}
                <section class="vault-card glass">
                    <h2 class="card-title" style={{ "font-family": "monospace" }}>DATA_INGEST_PIPELINE</h2>
                    <p class="card-desc">Targets: PDF, MP4, MP3, WAV, MD, TXT</p>
                    <PdfUploader />
                </section>

                {/* GitHub */}
                <section class="vault-card glass">
                    <h2 class="card-title" style={{ "font-family": "monospace" }}>GIT_SYNC_MODULE</h2>
                    <p class="card-desc">Parse public/private repositories via tree-sitter AST.</p>
                    <GithubLinkInput />
                </section>

                {/* Metasearch */}
                <section class="vault-card glass">
                    <h2 class="card-title" style={{ "font-family": "monospace" }}>NET_SEARCH_ROUTINE</h2>
                    <p class="card-desc">Concurrent privacy-first metasearch via SearXNG kernel.</p>
                    <SearchInput />
                </section>
            </div>
        </div>
    );
}
