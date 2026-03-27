import { createSignal, For } from "solid-js";
import { invoke } from "@tauri-apps/api/core";

interface SearchResult {
    title: string;
    url: string;
    snippet: string;
}

export default function SearchInput() {
    const [query, setQuery] = createSignal("");
    const [results, setResults] = createSignal<SearchResult[]>([]);
    const [loading, setLoading] = createSignal(false);

    async function search() {
        const lines = query().split("\n").map(l => l.trim()).filter(Boolean);
        if (lines.length === 0) return;
        setLoading(true);
        setResults([]);
        try {
            let allResults: SearchResult[] = [];
            for (const q of lines) {
                const res = await invoke<SearchResult[]>("metasearch_query", { query: q });
                allResults = [...allResults, ...res];
            }
            // Simple deduplication
            const unique = Array.from(new Map(allResults.map(item => [item.url, item])).values());
            setResults(unique);
        } catch (e) {
            console.error("Search error:", e);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div class="search-wrap">
            <div class="input-row" style={{ "align-items": "flex-start" }}>
                <textarea
                    id="search-query-input"
                    class="vault-input multi-line"
                    placeholder="/search querystring_1...&#10;/search querystring_2..."
                    rows={3}
                    value={query()}
                    onInput={(e) => setQuery(e.currentTarget.value)}
                    onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); search(); } }}
                    style={{ "font-family": "monospace" }}
                />
                <button id="search-btn" class="vault-btn" onClick={search} disabled={loading()} style={{ "font-family": "monospace", "font-weight": "bold" }}>
                    {loading() ? "[WAIT]" : "EXEC_SEARCH"}
                </button>
            </div>
            <div class="search-results">
                <For each={results()}>
                    {(r) => (
                        <div class="search-result-item">
                            <a class="result-title" href={r.url} target="_blank">{r.title}</a>
                            <p class="result-snippet">{r.snippet}</p>
                        </div>
                    )}
                </For>
            </div>
        </div>
    );
}
