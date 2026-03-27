// Layer 2: STUDIO – Artifact Generation
// Spawns Typst or Pandoc subprocess to compile chat/notes to PDF/LaTeX.

use tauri::command;
use std::process::Command;

/// Compile Typst markup to PDF and return the output file path.
#[command]
pub async fn generate_artifact(content: String, format: String) -> Result<String, String> {
    println!("[STUDIO] generate_artifact: format={format}");
    let tmp_input = std::env::temp_dir().join("drsa_artifact.typ");
    std::fs::write(&tmp_input, &content).map_err(|e| e.to_string())?;

    let output_path = std::env::temp_dir().join(format!("drsa_output.{format}"));

    // Try Typst first, fallback to Pandoc
    let status = Command::new("typst")
        .args(["compile", &tmp_input.to_string_lossy(), &output_path.to_string_lossy()])
        .status()
        .or_else(|_| {
            // Pandoc fallback
            Command::new("pandoc")
                .args([&tmp_input.to_string_lossy().to_string(), "-o", &output_path.to_string_lossy()])
                .status()
        })
        .map_err(|e| format!("No compiler found: {e}"))?;

    if status.success() {
        Ok(output_path.to_string_lossy().into())
    } else {
        Err("Compilation failed. Ensure typst or pandoc is installed.".into())
    }
}
