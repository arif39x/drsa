import { createSignal, For } from "solid-js";
import "./AgentThinkingDropdown.css";

interface Props {
    steps: string[];
}

export default function AgentThinkingDropdown(props: Props) {
    const [open, setOpen] = createSignal(false);

    return (
        <div class="agent-dropdown glass">
            <button class="agent-toggle" id="agent-toggle-btn" onClick={() => setOpen((o) => !o)}>
                <span class="agent-icon" style={{ "font-size": "12px", "font-weight": "bold" }}>LOG</span>
                <span>Agent Reasoning</span>
                <span class="agent-chevron" classList={{ rotated: open() }}>▾</span>
            </button>
            <div class="agent-steps" classList={{ visible: open() }}>
                <For each={props.steps}>
                    {(step, i) => (
                        <div class="agent-step anim-fade-in">
                            <span class="step-num">{i() + 1}</span>
                            <span class="step-text">{step}</span>
                        </div>
                    )}
                </For>
            </div>
        </div>
    );
}
