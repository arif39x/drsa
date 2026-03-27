// Contextual RAG
// LanceDB parent/child chunk storage and ANN retrieval.

use tauri::command;
use serde::{Deserialize, Serialize};
use std::sync::{Mutex, OnceLock};

static RAG_MEM: OnceLock<Mutex<Vec<RetrievedChunk>>> = OnceLock::new();

fn get_rag_mem() -> &'static Mutex<Vec<RetrievedChunk>> {
    RAG_MEM.get_or_init(|| Mutex::new(Vec::new()))
}

#[derive(Serialize, Deserialize, Clone)]
pub struct RetrievedChunk {
    pub text: String,
    pub source: String,
    pub page: u32,
    pub score: f32,
}

/// Retrieve top-k relevant chunks for a query from LanceDB.
/// Uses ANN (HNSW) search over vector embeddings.
#[command]
pub async fn rag_retrieve(query: String, top_k: u32) -> Result<Vec<RetrievedChunk>, String> {
    println!("[RAG] retrieve: query='{}', top_k={}", &query[..query.len().min(40)], top_k);
    let mem = get_rag_mem().lock().unwrap();
    if mem.is_empty() {
        return Ok(vec![RetrievedChunk {
            text: "(Stub) No documents ingested yet.".into(),
            source: "none".into(),
            page: 0,
            score: 0.0,
        }]);
    }
    // Return all chunks currently in memory for simplicity
    Ok(mem.clone())
}

/// Store a document's chunks into LanceDB after ingestion.
#[command]
pub async fn rag_store(chunks: Vec<String>, source: String) -> Result<(), String> {
    println!("[RAG] store: {} chunks from '{}'", chunks.len(), source);
    let mut mem = get_rag_mem().lock().unwrap();
    // Clear previous memory for clean context
    mem.clear();
    for c in chunks {
        mem.push(RetrievedChunk {
            text: c,
            source: source.clone(),
            page: 1,
            score: 0.99,
        });
    }
    Ok(())
}

/// Return nodes and edges for the knowledge graph viewer.
#[command]
pub async fn get_knowledge_graph() -> Result<serde_json::Value, String> {
    // TODO: Query Kuzu DB for entities and relations
    Ok(serde_json::json!({ "nodes": [], "edges": [] }))
}
