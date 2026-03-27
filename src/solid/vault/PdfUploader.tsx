import { createSignal } from "solid-js";
import { invoke } from "@tauri-apps/api/core";
import "./vault-shared.css";

export default function PdfUploader() {
    const [dragging, setDragging] = createSignal(false);
    const [progress, setProgress] = createSignal<number | null>(null);
    const [fileName, setFileName] = createSignal<string | null>(null);
    const [status, setStatus] = createSignal<"idle" | "processing" | "done" | "error">("idle");

    async function processFile(file: File) {
        setFileName(file.name);
        setStatus("processing");
        setProgress(0);

        // Simulate progress ticks while awaiting Rust IPC
        const tick = setInterval(() => setProgress((p) => Math.min((p ?? 0) + 10, 90)), 300);

        try {
            // Read file as ArrayBuffer → pass bytes to Rust ingestion_handler
            const buffer = await file.arrayBuffer();
            const bytes = new Uint8Array(buffer);
            await invoke("ingest_file", { fileName: file.name, bytes });
            clearInterval(tick);
            setProgress(100);
            setStatus("done");
        } catch (e) {
            clearInterval(tick);
            setStatus("error");
            console.error("Ingestion error:", e);
        }
    }

    function onDrop(e: DragEvent) {
        e.preventDefault();
        setDragging(false);
        const file = e.dataTransfer?.files[0];
        if (file) processFile(file);
    }

    return (
        <div class="uploader-wrap">
            <div
                id="pdf-drop-zone"
                class={`drop-zone ${dragging() ? "dragging" : ""} ${status()}`}
                onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={onDrop}
                onClick={() => document.getElementById("file-input")?.click()}
            >
                <input
                    id="file-input"
                    type="file"
                    accept=".pdf,.mp4,.mp3,.wav,.md,.txt"
                    style="display:none"
                    onChange={(e) => { const f = e.currentTarget.files?.[0]; if (f) processFile(f); }}
                />
                {status() === "idle" && <div style={{ "font-family": "monospace" }}>
                    <span class="drop-icon">↓</span>
                    <p class="drop-text">{"// Initialize data transfer..."}</p>
                    <p class="drop-hint">[BROWSE_FS]</p>
                </div>}
                {status() === "processing" && <div style={{ "font-family": "monospace" }}>
                    <span class="drop-icon spin">O</span>
                    <p class="drop-text">[RUN] Parsing <strong>{fileName()}</strong>...</p>
                    <div class="progress-bar"><div class="progress-fill" style={{ width: `${progress()}%` }} /></div>
                </div>}
                {status() === "done" && <div style={{ "font-family": "monospace" }}>
                    <span class="drop-icon">✓</span>
                    <p class="drop-text">[OK] <strong>{fileName()}</strong> ingested.</p>
                    <button class="reset-btn" onClick={(e) => { e.stopPropagation(); setStatus("idle"); setProgress(null); }}>[RESTART_INGEST]</button>
                </div>}
                {status() === "error" && <div style={{ "font-family": "monospace" }}>
                    <span class="drop-icon">✕</span>
                    <p class="drop-text">ERR: Ingestion failed. Check format.</p>
                    <button class="reset-btn" onClick={(e) => { e.stopPropagation(); setStatus("idle"); }}>[RETRY]</button>
                </div>}
            </div>
        </div>
    );
}
