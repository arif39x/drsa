// Layer 2: BRAIN – Agent Integration
// PyO3 bridge: calls Python agentic_reasoning.py with query + context.

use pyo3::prelude::*;
use tauri::command;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct AgentResult {
    pub answer: String,
    pub steps: Vec<String>,
}

/// Call Python LangGraph agent via PyO3.
/// Passes query and retrieved context; returns answer + reasoning steps.
#[command]
pub async fn run_agent(query: String, context: Vec<String>) -> Result<AgentResult, String> {
    println!("[AGENT] run_agent: query='{}'", &query[..query.len().min(40)]);

    let result = Python::with_gil(|py| -> PyResult<AgentResult> {
        // Import the agentic_reasoning Python module
        let sys = py.import_bound("sys")?;
        let path: pyo3::Bound<'_, pyo3::types::PyList> = sys.getattr("path")?.downcast_into()?;
        // Add src/python to sys.path so our modules are importable
        path.insert(0, "src/python")?;

        let module = py.import_bound("brain.agentic_reasoning")?;
        let run_fn = module.getattr("run_agent")?;
        let ctx_str = context.join("\n\n");
        let result: String = run_fn.call1((query.as_str(), ctx_str.as_str()))?.extract()?;

        Ok(AgentResult {
            answer: result,
            steps: vec!["Python LangGraph agent invoked".into()],
        })
    });

    result.map_err(|e| format!("PyO3 error: {e}"))
}
