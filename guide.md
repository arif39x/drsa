# DRSA Quick Start Guide

Welcome to the **Definitive Research & Studio Assistant (DRSA)**.

DRSA is designed as a local-first, zero-lag agentic environment using a 4-layer architecture:
1. **The Glass (SolidJS)**: High-performance, reactive UI.
2. **The Micro-Kernel (Rust/Tauri)**: System integration, headless state, and fast native execution.
3. **The Embedded ML Engine (Python)**: Zero-copy python pipeline embedded within the Rust kernel via PyO3.
4. **External Services (Docker)**: Privacy-first localized instances like SearXNG.

---

## 🚀 How to Run

Use the included helper script to start the local environment and launch the desktop application:

```bash
./run.sh
```

**What this script does:**
1. Starts the SearXNG Docker container (backgrounds it).
2. Sets the `PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1` flag to satisfy the Python 3.14 / PyO3 v0.22 ABI.
3. Launches the Tauri development window using `npm run tauri dev`.

---

## 🛠️ Configuration & Workflow

### 1. The Brain
The Brain tab integrates Local GGUF models via `llama-cpp-rs` or API-based endpoints.
- If using API models (OpenAI, Anthropic), provide your key in **Settings > Bring Your Own Key (BYOK)**. The key is stored locally in your OS keychain.

### 2. The Vault
File ingestions (PDF, URL scraping) are mapped to LanceDB parent/child structures using `rust/brain/rag_contextual.rs`.
- Place your PDF extractors (`docling` or `marker-pdf`) into your Python environment if you aren't using the cloud fallbacks.

### 3. The Studio
The Studio leverages `typst` and `kokoro-tts` for immediate artifact compilation.
- Ensure the `typst` CLI and `piper` or `kokoro-tts` are installed on your host system if you intend to use the artifact generators natively.

## Next Steps for Development
Look into `src-tauri/src/lib.rs` and the corresponding modules in `src-tauri/src/rust/` to implement individual command logic. The UI endpoints in `src/solid/` are pre-wired.
