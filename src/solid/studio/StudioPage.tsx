import MermaidViewer from "./MermaidViewer";
import KnowledgeGraphView from "./KnowledgeGraphView";
import { createSignal } from "solid-js";
import "./StudioPage.css";

export default function StudioPage() {
    const [mermaidCode] = createSignal<string>("graph TD\n  A-->B\n  A-->C");

    return (
        <div class="studio-layout">
            <header class="studio-header">
                <h1 class="studio-title">Studio</h1>
                <p class="studio-subtitle">Handwriting → Diagrams · Artifact Generation · Knowledge Graph</p>
            </header>

            <div class="studio-grid">
                {/* Mermaid viewer (Split Pane) */}
                <section class="studio-card studio-card-wide glass">
                    <h2 class="card-title">Mermaid Diagram</h2>
                    <p class="card-desc">Write your DSL on the left. Watch it render on the right.</p>
                    <MermaidViewer code={mermaidCode()} />
                </section>

                {/* Knowledge graph */}
                <section class="studio-card studio-card-wide glass">
                    <h2 class="card-title">Knowledge Graph</h2>
                    <p class="card-desc">WebGL entity-relation graph extracted by GLiNER + NetworkX + Kuzu DB.</p>
                    <KnowledgeGraphView />
                </section>
            </div>
        </div>
    );
}
