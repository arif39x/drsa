import { A, RouteSectionProps } from "@solidjs/router";
import { createSignal, onMount } from "solid-js";
import { getCurrentWindow } from "@tauri-apps/api/window";
import "./AppShell.css";

/** Left sidebar nav item */
function NavItem(props: { href: string; label: string; iconSvg: any }) {
    return (
        <A
            href={props.href}
            class="nav-item group"
            activeClass="active"
            end={props.href === "/"}
        >
            <span class="nav-icon">{props.iconSvg}</span>
            <span class="nav-label">{props.label}</span>
        </A>
    );
}

export default function AppShell(props: RouteSectionProps) {
    const appWindow = getCurrentWindow();
    const [theme, setTheme] = createSignal<"dark" | "light">("dark");

    onMount(() => {
        const stored = localStorage.getItem("drsa-theme") as "dark" | "light";
        if (stored === "light") {
            setTheme("light");
            document.body.classList.add("light");
        }
    });

    function toggleTheme() {
        if (theme() === "dark") {
            setTheme("light");
            document.body.classList.add("light");
            localStorage.setItem("drsa-theme", "light");
        } else {
            setTheme("dark");
            document.body.classList.remove("light");
            localStorage.setItem("drsa-theme", "dark");
        }
    }

    return (
        <div class="app-wrapper">
            {/* Custom Titlebar */}
            <div class="titlebar" style={{ "pointer-events": "auto", "z-index": 999 }}>
                <div class="titlebar-left" data-tauri-drag-region style={{ "-webkit-app-region": "drag" }}>
                    <span class="titlebar-title" data-tauri-drag-region>// DRSA_KERNEL_v0.1</span>
                </div>
                <div class="titlebar-controls" style={{ "pointer-events": "auto", "-webkit-app-region": "no-drag", "z-index": 1000, position: "relative" }}>
                    <button class="titlebar-btn no-drag" onMouseDown={(e) => { e.stopPropagation(); toggleTheme(); }} onClick={toggleTheme} title="Toggle Theme">
                        {theme() === "dark" ? "☼" : "☾"}
                    </button>
                    <button class="titlebar-btn no-drag" onMouseDown={(e) => { e.stopPropagation(); appWindow.minimize(); }} onClick={() => appWindow.minimize()}>_</button>
                    <button class="titlebar-btn no-drag" onMouseDown={(e) => { e.stopPropagation(); appWindow.toggleMaximize(); }} onClick={() => appWindow.toggleMaximize()}>□</button>
                    <button class="titlebar-btn close no-drag" onMouseDown={(e) => { e.stopPropagation(); appWindow.close(); }} onClick={() => appWindow.close()}>✕</button>
                </div>
            </div>

            <div class="shell">
                {/* Sidebar */}
                <nav class="sidebar glass">
                    <div class="logo-block">
                        <img src="/src/assets/DRSA.png" alt="DRSA Logo" class="logo-img" style={{ width: "24px", height: "24px", "border-radius": "4px", "object-fit": "cover" }} />
                        <span class="logo-name" style={{ "font-family": "monospace", "letter-spacing": "0px" }}>DRSA_</span>
                    </div>

                    <div class="nav-section">
                        <NavItem href="/brain" label="Brain" iconSvg={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" /></svg>} />
                        <NavItem href="/vault" label="Vault" iconSvg={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2" /><line x1="3" y1="9" x2="21" y2="9" /><line x1="9" y1="21" x2="9" y2="9" /></svg>} />
                        <NavItem href="/studio" label="Studio" iconSvg={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 19l7-7 3 3-7 7-3-3z" /><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z" /><path d="M2 2l7.586 7.586" /><circle cx="11" cy="11" r="2" /></svg>} />
                    </div>

                    <div class="nav-bottom">
                        <NavItem href="/settings" label="Settings" iconSvg={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" /></svg>} />
                    </div>
                </nav>

                {/* Main content area */}
                <main class="content anim-fade-in">
                    {props.children}
                </main>
            </div>
        </div >
    );
}
