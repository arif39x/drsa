// Layer 2: CORE – Public Scaling
// Supabase JWT auth and OS keychain storage for BYOK API keys.

use tauri::command;

/// Save an API key to the OS keychain via keyring crate (stub).
#[command]
pub async fn save_settings(model_path: String, api_key: String, mode: String) -> Result<String, String> {
    // TODO: Use `keyring` crate to persist api_key into OS secret store.
    // TODO: Write model_path to app config file via tauri::api::path.
    println!("[CORE] save_settings: mode={mode}, model_path={model_path}");
    Ok("Settings saved.".into())
}

/// Retrieve the stored API key from the OS keychain (stub).
#[command]
pub async fn get_api_key() -> Result<String, String> {
    // TODO: Retrieve from OS keychain.
    Ok(String::new())
}
