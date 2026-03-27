// Receives files from frontend, saves to temp, dispatches to Python pipeline.

use pyo3::prelude::*;
use tauri::command;
use std::fs;
use std::path::PathBuf;
use crate::rust::brain::rag_contextual::rag_store;

/// Accept a file from the frontend (as raw bytes) and trigger Python ingestion.
#[command]
pub async fn ingest_file(file_name: String, bytes: Vec<u8>) -> Result<String, String> {
    println!("[VAULT] ingest_file: {} ({} bytes)", file_name, bytes.len());

    // Write bytes to temp path
    let tmp_path: PathBuf = std::env::temp_dir().join(&file_name);
    fs::write(&tmp_path, &bytes).map_err(|e| e.to_string())?;
    let path_str = tmp_path.to_string_lossy().to_string();

    // Call Python multi_modal_ingestion pipeline
    let result = Python::with_gil(|py| -> PyResult<String> {
        let sys = py.import_bound("sys")?;
        let path: pyo3::Bound<'_, pyo3::types::PyList> = sys.getattr("path")?.downcast_into()?;
        path.insert(0, "src/python")?;
        let module = py.import_bound("vault.multi_modal_ingestion")?;
        let ingest_fn = module.getattr("ingest")?;
        ingest_fn.call1((path_str.as_str(),))?.extract()
    });

    let text = result.map_err(|e| format!("Ingestion error: {e}"))?;

    // Store the extracted text in RAG memory
    rag_store(vec![text.clone()], file_name).await.map_err(|e| format!("RAG store error: {e}"))?;

    Ok(text)
}
