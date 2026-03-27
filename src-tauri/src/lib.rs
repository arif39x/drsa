// DRSA – Tauri Micro-Kernel Entry Point
// Registers all IPC commands from the 4 architectural layers.

mod rust {
    pub mod core {
        pub mod app_shell;
        pub mod public_scaling;
    }
    pub mod brain {
        pub mod llm_execution;
        pub mod rag_contextual;
        pub mod agent_integration;
    }
    pub mod vault {
        pub mod ingestion_handler;
        pub mod github_arch;
    }
    pub mod studio {
        pub mod artifact_generation;
        pub mod audio_summaries;
    }
}

use rust::{
    brain::{
        agent_integration::run_agent,
        llm_execution::{chat_invoke, handwriting_to_mermaid},
        rag_contextual::{get_knowledge_graph, rag_retrieve, rag_store},
    },
    core::public_scaling::{get_api_key, save_settings},
    studio::{
        artifact_generation::generate_artifact,
        audio_summaries::generate_audio_summary,
    },
    vault::{
        github_arch::analyze_github_repo,
        ingestion_handler::ingest_file,
    },
};

/// Metasearch via local SearXNG Docker container.
#[tauri::command]
async fn metasearch_query(query: String) -> Result<serde_json::Value, String> {
    let url = format!(
        "http://localhost:8080/search?q={}&format=json",
        urlencoding::encode(&query)
    );
    let resp = reqwest::get(&url)
        .await
        .map_err(|e| format!("SearXNG unreachable: {e}"))?
        .json::<serde_json::Value>()
        .await
        .map_err(|e| e.to_string())?;
    Ok(resp)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .setup(|app| {
            rust::core::app_shell::setup(app)?;
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            // Core
            save_settings,
            get_api_key,
            // Brain
            chat_invoke,
            handwriting_to_mermaid,
            run_agent,
            rag_retrieve,
            rag_store,
            get_knowledge_graph,
            // Vault
            ingest_file,
            analyze_github_repo,
            metasearch_query,
            // Studio
            generate_artifact,
            generate_audio_summary,
        ])
        .run(tauri::generate_context!())
        .expect("error while running DRSA");
}
