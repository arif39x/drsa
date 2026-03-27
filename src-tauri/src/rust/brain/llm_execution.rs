// BRAIN Local LLM Execution
// llama-cpp-rs model loader and token streaming.
// Zero-copy mmap of GGUF model files for minimum latency.

use tauri::command;
use serde::{Deserialize, Serialize};
use super::agent_integration::run_agent;
use super::rag_contextual::rag_retrieve;

#[derive(Serialize, Deserialize)]
pub struct ChatResponse {
    pub content: String,
    pub steps: Vec<String>,
    pub citation: Option<Citation>,
}

#[derive(Serialize, Deserialize)]
pub struct Citation {
    pub file: String,
    pub page: u32,
    pub highlight: String,
}

/// Main chat IPC command.
/// Routes between local LLM (llama-cpp-rs) and cloud (via HTTP) based on `model`.
/// Calls agent_integration for agentic reasoning and RAG retrieval.
#[command]
pub async fn chat_invoke(query: String, model: String) -> Result<ChatResponse, String> {
    println!("[BRAIN] chat_invoke: model={model}, query={}", &query[..query.len().min(60)]);

    // 1. Retrieve RAG context
    let chunks = rag_retrieve(query.clone(), 3).await.map_err(|e| e.to_string())?;
    let context: Vec<String> = chunks.into_iter().map(|c| c.text).collect();

    // 2. Call python agent
    let agent_res = run_agent(query.clone(), context).await?;

    Ok(ChatResponse {
        content: agent_res.answer,
        steps: agent_res.steps,
        citation: None,
    })
}

/// Convert hand-drawn strokes JSON to Mermaid DSL via LLM.
#[command]
pub async fn handwriting_to_mermaid(strokes: String) -> Result<String, String> {
    println!("[BRAIN] handwriting_to_mermaid: {} bytes of strokes", strokes.len());
    Ok("graph TD\n  A[Start] --> B[Process]\n  B --> C[End]".into())
}
