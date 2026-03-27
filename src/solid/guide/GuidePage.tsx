import "./GuidePage.css";

export default function GuidePage() {
    return (
        <div class="guide-layout">
            <header class="guide-header">
                <h1 class="guide-title" style={{ "font-family": "monospace" }}>// DRSA_DOCUMENTATION</h1>
                <p class="guide-subtitle" style={{ "font-family": "monospace" }}>Definitive Research & Studio Assistant v0.1</p>
            </header>

            <div class="guide-content glass">
                <h2 style={{ "font-family": "monospace" }}>[SYSTEM] Architecture</h2>
                <p>DRSA is a zero-lag agentic environment using a 4-layer stack:</p>
                <ul>
                    <li><strong>The Glass (SolidJS)</strong>: High-performance, reactive UI.</li>
                    <li><strong>The Micro-Kernel (Rust/Tauri)</strong>: System integration, headless state, fast I/O.</li>
                    <li><strong>Embedded ML (Python)</strong>: Zero-copy pipeline via PyO3.</li>
                    <li><strong>External Services (Docker)</strong>: Privacy-first instances like SearXNG.</li>
                </ul>

                <hr class="guide-divider" />

                <h2 style={{ "font-family": "monospace" }}>[RUN] Execution Pipeline</h2>
                <pre class="guide-code">./run.sh</pre>
                <p><strong>Operations:</strong></p>
                <ol>
                    <li>Boots SearXNG container (background).</li>
                    <li>Sets <code>PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1</code>.</li>
                    <li>Compiles and launches Tauri kernel.</li>
                </ol>

                <hr class="guide-divider" />

                <h2 style={{ "font-family": "monospace" }}>[CONF] Subsystems</h2>
                <h3>1. BRAIN</h3>
                <p>Integrates Local GGUF models via <code>llama-cpp-rs</code> or BYOK Cloud API endpoints. Keys are stored securely in the OS keychain.</p>

                <h3>2. VAULT</h3>
                <p>File ingestions (PDF, Web, Git) mapped to LanceDB parent/child structures. Ensure <code>docling</code> and <code>tree-sitter</code> are in path.</p>

                <h3>3. STUDIO</h3>
                <p>Uses <code>typst</code>, Mermaid, and Kuzu DB for localized artifacts and Knowledge Graph processing.</p>
            </div>
        </div>
    );
}
