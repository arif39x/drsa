import { createSignal } from "solid-js";
import { invoke } from "@tauri-apps/api/core";

export default function GithubLinkInput() {
    const [url, setUrl] = createSignal("");
    const [status, setStatus] = createSignal<"idle" | "loading" | "done" | "error">("idle");
    const [summary, setSummary] = createSignal("");

    async function analyze() {
        const lines = url().split("\n").map(l => l.trim()).filter(Boolean);
        if (lines.length === 0) return;
        setStatus("loading");
        setSummary("");
        try {
            let combined = "";
            for (const u of lines) {
                const result = await invoke<string>("analyze_github_repo", { url: u });
                combined += `--- Analysis for ${u} ---\n${result}\n\n`;
            }
            setSummary(combined);
            setStatus("done");
        } catch (e) {
            setSummary(String(e));
            setStatus("error");
        }
    }

    return (
        <div class="github-wrap">
            <div class="input-row" style={{ "align-items": "flex-start" }}>
                <textarea
                    id="github-url-input"
                    class="vault-input multi-line"
                    placeholder="git_uri_1...&#10;git_uri_2..."
                    rows={3}
                    value={url()}
                    onInput={(e) => setUrl(e.currentTarget.value)}
                    onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); analyze(); } }}
                    style={{ "font-family": "monospace" }}
                />
                <button id="github-analyze-btn" class="vault-btn" onClick={analyze} disabled={status() === "loading"} style={{ "font-family": "monospace", "font-weight": "bold" }}>
                    {status() === "loading" ? "[WAIT]" : "FETCH_ALL"}
                </button>
            </div>
            {summary() && (
                <pre class={`vault-result ${status()}`}>{summary()}</pre>
            )}
        </div>
    );
}
