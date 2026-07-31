//! Tauri commands backing the license activation window.

use std::path::PathBuf;

use licensing_core::hwid::get_hardware_id as compute_hardware_id;
use licensing_core::license::{
    install_license, load_license, read_license_from, validate_against_hardware, LicenseError,
};
use serde::Serialize;
use tauri::AppHandle;

/// Snapshot of the current activation state shown by the activation window.
#[derive(Serialize)]
pub struct ActivationStatus {
    pub status: String,
    pub message: String,
    pub customer: Option<String>,
    pub hardware_id: String,
}

#[tauri::command]
pub fn get_hardware_id() -> Result<String, String> {
    compute_hardware_id()
}

#[tauri::command]
pub fn get_activation_status() -> ActivationStatus {
    let hardware_id = match compute_hardware_id() {
        Ok(id) => id,
        Err(_) => "unavailable".to_string(),
    };

    match load_license() {
        Ok(license) => {
            let customer = Some(license.customer.clone());
            match validate_against_hardware(&license, &hardware_id) {
                Ok(()) => ActivationStatus {
                    status: "valid".to_string(),
                    message: "Licensed".to_string(),
                    customer,
                    hardware_id,
                },
                Err(LicenseError::WrongHardware) => ActivationStatus {
                    status: "wrong_hardware".to_string(),
                    message: "This license belongs to another computer. Please contact the software provider."
                        .to_string(),
                    customer,
                    hardware_id,
                },
                Err(_) => ActivationStatus {
                    status: "invalid".to_string(),
                    message: "The installed license is invalid or damaged. Please contact the software provider."
                        .to_string(),
                    customer,
                    hardware_id,
                },
            }
        }
        Err(_) => ActivationStatus {
            status: "missing".to_string(),
            message: "No license detected. Activate the software to continue.".to_string(),
            customer: None,
            hardware_id,
        },
    }
}

#[tauri::command]
pub fn pick_license_file() -> Option<String> {
    rfd::FileDialog::new()
        .add_filter("License file", &["dat", "json"])
        .set_title("Select your license file")
        .pick_file()
        .map(|path| path.to_string_lossy().to_string())
}

/// Validates and installs the selected license, then restarts the app so it
/// boots into the normal licensed flow. `AppHandle::restart()` diverges, so
/// this command only returns when something goes wrong.
#[tauri::command]
pub fn activate_license(path: String, app_handle: AppHandle) -> Result<(), String> {
    let hardware_id = compute_hardware_id()?;
    let license = read_license_from(&PathBuf::from(&path)).map_err(|e| e.to_string())?;
    validate_against_hardware(&license, &hardware_id).map_err(|e| e.to_string())?;
    install_license(&license)?;

    eprintln!("[tauri] License activated, restarting application...");
    app_handle.restart();
}

#[tauri::command]
pub fn cancel_activation(app_handle: AppHandle) {
    eprintln!("[tauri] Activation cancelled, exiting...");
    app_handle.exit(0);
}

/// Returns whether the license gate passed for the current machine without
/// logging any hardware details (used only to decide which window to show).
pub fn license_gate_passed() -> bool {
    let Ok(hardware_id) = compute_hardware_id() else {
        return false;
    };
    match load_license() {
        Ok(license) => validate_against_hardware(&license, &hardware_id).is_ok(),
        Err(_) => false,
    }
}
