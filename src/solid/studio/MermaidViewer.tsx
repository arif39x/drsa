import { createEffect, createSignal } from "solid-js";
import mermaid from "mermaid";

interface Props { code: string; }

let idCounter = 0;

export default function MermaidViewer(props: Props) {
    const [edited, setEdited] = createSignal(props.code);
    const [svgHtml, setSvgHtml] = createSignal("");
    const [error, setError] = createSignal("");
    const id = `mermaid-${idCounter++}`;

    // Sync edited when parent sends new code
    createEffect(() => setEdited(props.code));

    async function render(code: string) {
        if (!code.trim()) { setSvgHtml(""); setError(""); return; }
        try {
            mermaid.initialize({ startOnLoad: false, theme: "dark" });
            const { svg } = await mermaid.render(id, code);
            setSvgHtml(svg);
            setError("");
        } catch (e: any) {
            setError(String(e.message ?? e));
        }
    }

    // Re-render on edits (debounced)
    let timer: number;
    const debounceRender = (code: string) => {
        clearTimeout(timer);
        timer = window.setTimeout(() => render(code), 600);
    };

    createEffect(() => { const c = edited(); debounceRender(c); });

    return (
        <div class="mermaid-wrap">
            <div class="mermaid-split">
                <div class="mermaid-editor-pane">
                    <textarea
                        id="mermaid-textarea"
                        class="mermaid-textarea"
                        placeholder="graph TD&#10;  A-->B"
                        value={edited()}
                        onInput={(e) => setEdited(e.currentTarget.value)}
                    />
                </div>
                <div class="mermaid-preview-pane">
                    {error() && <p class="mermaid-error">Error: {error()}</p>}
                    <div class="mermaid-preview" innerHTML={svgHtml()} />
                </div>
            </div>
        </div>
    );
}
