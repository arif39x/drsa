// Layer 2: STUDIO – Audio Summaries
// Spawns Kokoro/Piper TTS process and returns audio file path.

use tauri::command;
use std::process::Command;

/// Synthesise a text summary to audio using Kokoro TTS (or Piper fallback).
/// Returns the path to the generated WAV/MP3 file.
#[command]
pub async fn generate_audio_summary(text: String) -> Result<String, String> {
    println!("[STUDIO] generate_audio_summary: {} chars", text.len());
    let output_path = std::env::temp_dir().join("drsa_summary.wav");

    // Try kokoro-tts CLI, fallback to piper
    let status = Command::new("kokoro-tts")
        .args(["--text", &text, "--output", &output_path.to_string_lossy()])
        .status()
        .or_else(|_| {
            Command::new("piper")
                .args(["--text", &text, "--output_file", &output_path.to_string_lossy()])
                .status()
        })
        .map_err(|e| format!("No TTS engine found: {e}"))?;

    if status.success() {
        Ok(output_path.to_string_lossy().into())
    } else {
        Err("TTS synthesis failed. Install kokoro-tts or piper.".into())
    }
}
