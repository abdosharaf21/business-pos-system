use std::net::TcpStream;
use std::process::{Child, Command};
use std::sync::Mutex;
use std::time::Duration;
use tauri::Manager;

const BACKEND_BINARY: &str = "backend-app";

struct BackendProcess(Mutex<Option<Child>>);

impl Drop for BackendProcess {
    fn drop(&mut self) {
        if let Ok(mut guard) = self.0.lock() {
            if let Some(mut child) = guard.take() {
                let _ = child.kill();
                let _ = child.wait();
            }
        }
    }
}

fn wait_for_port(port: u16, timeout_secs: u64) -> Result<(), String> {
    let addr = format!("127.0.0.1:{}", port);
    let start = std::time::Instant::now();
    let timeout = Duration::from_secs(timeout_secs);

    while start.elapsed() < timeout {
        match TcpStream::connect_timeout(&addr.parse().unwrap(), Duration::from_millis(500)) {
            Ok(_) => return Ok(()),
            Err(_) => std::thread::sleep(Duration::from_millis(200)),
        }
    }

    Err(format!(
        "Backend did not start on port {} within {}s",
        port, timeout_secs
    ))
}

fn backend_binary_name() -> String {
    let name = BACKEND_BINARY.to_string();
    if cfg!(target_os = "windows") {
        name + ".exe"
    } else {
        name
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            #[cfg(debug_assertions)]
            {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }

            #[cfg(not(debug_assertions))]
            {
                let resource_dir = app
                    .path()
                    .resource_dir()
                    .map_err(|e| e.to_string())?;

                let flask_path = resource_dir.join("backend").join(backend_binary_name());

                eprintln!(
                    "[tauri] Starting backend from: {}",
                    flask_path.display()
                );

                let child = Command::new(&flask_path)
                    .current_dir(&resource_dir)
                    .env("FLASK_ENV", "production")
                    .env(
                        "FRONTEND_DIST",
                        resource_dir.join("frontend").to_str().unwrap(),
                    )
                    .env("SERVER_PORT", "5001")
                    .env("SERVER_HOST", "127.0.0.1")
                    .spawn()
                    .map_err(|e| format!("Failed to start backend: {}", e))?;

                app.manage(BackendProcess(Mutex::new(Some(child))));

                eprintln!("[tauri] Waiting for backend on port 5001...");
                wait_for_port(5001, 15).map_err(|e| {
                    eprintln!("[tauri] ERROR: {}", e);
                    e
                })?;
                eprintln!("[tauri] Backend is ready");
            }

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
