import { createSignal, For, Show } from "solid-js";
import { invoke } from "@tauri-apps/api/core";
import AgentThinkingDropdown from "./AgentThinkingDropdown";
import CitationViewer from "./CitationViewer";
import "./ChatWindow.css";

interface Message {
    id: number;
    role: "user" | "assistant";
    content: string;
    steps?: string[];
    citation?: { file: string; page: number; highlight: string };
}

export default function ChatWindow() {
    const [messages, setMessages] = createSignal<Message[]>([]);
    const [input, setInput] = createSignal("");
    const [loading, setLoading] = createSignal(false);
    const [model, setModel] = createSignal("local");
    const [activeCitation, setActiveCitation] = createSignal<Message["citation"] | null>(null);
    let msgEnd: HTMLDivElement | undefined;

    async function send() {
        const text = input().trim();
        if (!text || loading()) return;

        const userMsg: Message = { id: Date.now(), role: "user", content: text };
        setMessages((m) => [...m, userMsg]);
        setInput("");
        setLoading(true);

        try {
            // IPC call to Rust brain/agent_integration → Python agentic_reasoning
            const response = await invoke<{ content: string; steps: string[]; citation?: Message["citation"] }>(
                "chat_invoke",
                { query: text, model: model() }
            );
            const assistantMsg: Message = {
                id: Date.now() + 1,
                role: "assistant",
                content: response.content,
                steps: response.steps,
                citation: response.citation,
            };
            setMessages((m) => [...m, assistantMsg]);
            if (response.citation) setActiveCitation(response.citation);
        } catch (e) {
            setMessages((m) => [
                ...m,
                { id: Date.now() + 1, role: "assistant", content: `Error: ${e}` },
            ]);
        } finally {
            setLoading(false);
            msgEnd?.scrollIntoView({ behavior: "smooth" });
        }
    }

    return (
        <div class={`chat-layout ${activeCitation() ? "with-citation" : ""}`}>
            {/* Message pane */}
            <div class="chat-pane">
                {/* Model selector */}
                <div class="model-bar glass">
                    <label class="model-label">Model</label>
                    <select id="model-select" class="model-select" value={model()} onChange={(e) => setModel(e.currentTarget.value)}>
                        <option value="local">Local GGUF (llama.cpp)</option>
                        <option value="openai">OpenAI</option>
                        <option value="anthropic">Anthropic Claude</option>
                        <option value="gemini">Google Gemini</option>
                        <option value="groq">Groq</option>
                    </select>
                </div>

                {/* Messages */}
                <div class="messages">
                    <Show when={messages().length === 0}>
                        <div class="chat-empty" style={{ "font-family": "monospace" }}>
                            <p>{">> SYSTEM IDLE. AWAITING QUERY."}</p>
                        </div>
                    </Show>
                    <For each={messages()}>
                        {(msg) => (
                            <div class={`message ${msg.role} anim-fade-in`}>
                                <Show when={msg.role === "assistant" && msg.steps?.length}>
                                    <AgentThinkingDropdown steps={msg.steps!} />
                                </Show>
                                <div class="bubble">{msg.content}</div>
                                <Show when={msg.citation}>
                                    <div class="msg-citation" onClick={() => setActiveCitation(msg.citation!)}>
                                        Source: {msg.citation!.file} p.{msg.citation!.page}
                                    </div>
                                </Show>
                            </div>
                        )}
                    </For>
                    <Show when={loading()}>
                        <div class="message assistant anim-fade-in">
                            <div class="bubble loading-bubble">
                                <span class="dot" /><span class="dot" /><span class="dot" />
                            </div>
                        </div>
                    </Show>
                    <div ref={msgEnd} />
                </div>

                {/* Input bar */}
                <form class="input-bar glass" onSubmit={(e) => { e.preventDefault(); send(); }}>
                    <textarea
                        id="chat-input"
                        class="chat-input multi-line"
                        rows={1}
                        placeholder="// Input command... (Shift+Enter for newline)"
                        value={input()}
                        onInput={(e) => {
                            setInput(e.currentTarget.value);
                            e.currentTarget.style.height = 'auto';
                            e.currentTarget.style.height = (e.currentTarget.scrollHeight < 120 ? e.currentTarget.scrollHeight : 120) + 'px';
                        }}
                        onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
                        style={{ "font-family": "monospace" }}
                    />
                    <button id="chat-send" class="send-btn" type="submit" disabled={loading()} style={{ "font-family": "monospace", "font-weight": "bold" }}>
                        {loading() ? "[...]" : "EXEC"}
                    </button>
                </form>
            </div>

            {/* Citation split-pane */}
            <Show when={activeCitation()}>
                <CitationViewer
                    citation={activeCitation()!}
                    onClose={() => setActiveCitation(null)}
                />
            </Show>
        </div>
    );
}
