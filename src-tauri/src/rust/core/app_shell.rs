// Layer 2: CORE – App Shell
// Handles OS-level Tauri management: window state, system tray, drag regions.

use tauri::{App, Manager};

/// Initialise OS-level shell features: system tray, window decorations.
pub fn setup(app: &mut App) -> Result<(), Box<dyn std::error::Error>> {
    let window = app.get_webview_window("main").unwrap();
    window.set_decorations(false)?;   // Frameless glass window
    window.set_shadow(true)?;
    Ok(())
}
