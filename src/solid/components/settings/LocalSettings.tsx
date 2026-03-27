import { createSignal } from "solid-js";
import { invoke } from "@tauri-apps/api/core";
import "./LocalSettings.css";

export default function LocalSettings() {
    const [modelPath, setModelPath] = createSignal("");
    const [apiKey, setApiKey] = createSignal("");
    const [mode, setMode] = createSignal<"local" | "cloud">("local");
    const [saved, setSaved] = createSignal(false);

    async function save() {
        await invoke("save_settings", {
            modelPath: modelPath(),
            apiKey: apiKey(),
            mode: mode(), // mode now stores the specific provider id
        });
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
    }

    return (
        <div class="settings-layout">
            <header class="settings-header">
                <h1 class="settings-title">Settings</h1>
                <p class="settings-sub">Configure local LLM and cloud API keys.</p>
            </header>

            <div class="settings-section glass">
                <h2 class="section-heading">LLM Provider</h2>
                <select id="llm-provider-select" class="settings-input" value={mode()} onChange={(e) => setMode(e.currentTarget.value as any)}>
                    <option value="local">Local GGUF (llama.cpp)</option>
                    <option value="openai">OpenAI</option>
                    <option value="anthropic">Anthropic Claude</option>
                    <option value="gemini">Google Gemini</option>
                    <option value="groq">Groq</option>
                </select>
            </div>

            {mode() === "local" && (
                <div class="settings-section glass">
                    <h2 class="section-heading">Local Model Path</h2>
                    <p class="section-desc">Path to your GGUF model file (e.g., Mistral-7B-Q4.gguf)</p>
                    <input
                        id="model-path-input"
                        class="settings-input"
                        placeholder="/home/user/models/model.gguf"
                        value={modelPath()}
                        onInput={(e) => setModelPath(e.currentTarget.value)}
                    />
                </div>
            )}

            {mode() !== "local" && (
                <div class="settings-section glass">
                    <h2 class="section-heading">BYOK API Key ({mode().toUpperCase()})</h2>
                    <p class="section-desc">Stored securely in your OS keychain. Never leaves your device.</p>
                    <input
                        id="api-key-input"
                        class="settings-input"
                        type="password"
                        placeholder="sk-..."
                        value={apiKey()}
                        onInput={(e) => setApiKey(e.currentTarget.value)}
                    />
                </div>
            )}

            <button
                id="settings-save-btn"
                class={`save-btn ${saved() ? "saved" : ""}`}
                onClick={save}
            >
                {saved() ? "Saved." : "Save Settings"}
            </button>
        </div>
    );
}
