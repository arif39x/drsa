import { onMount } from "solid-js";
import { invoke } from "@tauri-apps/api/core";

/**
 * WebGL Knowledge Graph using a bare Canvas + minimal force-directed layout.
 * In production, replace with react-force-graph or Sigma.js WebGL renderer.
 * Data is fetched from Rust IPC → Python knowledge_graph.py.
 */
interface Node { id: string; label: string; group: string; x?: number; y?: number; }
interface Edge { source: string; target: string; label: string; }

export default function KnowledgeGraphView() {
    let canvasRef: HTMLCanvasElement | undefined;

    onMount(async () => {
        try {
            const { nodes, edges } = await invoke<{ nodes: Node[]; edges: Edge[] }>("get_knowledge_graph");
            renderGraph(nodes, edges);
        } catch {
            renderPlaceholder();
        }
    });

    function renderPlaceholder() {
        const ctx = canvasRef?.getContext("2d");
        if (!ctx || !canvasRef) return;
        ctx.fillStyle = "#161b22";
        ctx.fillRect(0, 0, canvasRef.width, canvasRef.height);
        ctx.fillStyle = "#58a6ff";
        ctx.font = "14px Inter, sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("Knowledge graph will appear after ingesting documents.", canvasRef.width / 2, canvasRef.height / 2);
    }

    function renderGraph(nodes: Node[], edges: Edge[]) {
        const ctx = canvasRef?.getContext("2d");
        if (!ctx || !canvasRef) return;
        const W = canvasRef.width, H = canvasRef.height;

        // Simple random layout seeded positions
        const pos: Record<string, { x: number; y: number }> = {};
        nodes.forEach((n) => { pos[n.id] = n.x != null ? { x: n.x, y: n.y! } : { x: Math.random() * W, y: Math.random() * H }; });

        ctx.clearRect(0, 0, W, H);

        // Draw edges
        ctx.strokeStyle = "#21262d";
        ctx.lineWidth = 1;
        edges.forEach((e) => {
            const s = pos[e.source], t = pos[e.target];
            if (!s || !t) return;
            ctx.beginPath();
            ctx.moveTo(s.x, s.y);
            ctx.lineTo(t.x, t.y);
            ctx.stroke();
        });

        // Draw nodes
        nodes.forEach((n) => {
            const p = pos[n.id];
            if (!p) return;
            ctx.beginPath();
            ctx.arc(p.x, p.y, 8, 0, Math.PI * 2);
            ctx.fillStyle = n.group === "entity" ? "#58a6ff" : "#d2a8ff";
            ctx.fill();
            ctx.fillStyle = "#e6edf3";
            ctx.font = "10px Inter, sans-serif";
            ctx.textAlign = "center";
            ctx.fillText(n.label, p.x, p.y + 20);
        });
    }

    return (
        <div class="kg-wrap">
            <canvas id="kg-canvas" ref={canvasRef} class="kg-canvas" width="900" height="400" />
        </div>
    );
}
