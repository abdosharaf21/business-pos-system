use std::net::TcpStream;
use std::path::PathBuf;
use std::process::{Child, Command};
use std::sync::Mutex;
use std::time::Duration;
use tauri::Manager;

const BACKEND_BINARY: &str = "backend-app";
const BACKEND_PORT: u16 = 5001;
#[cfg(target_os = "windows")]
const CREATE_NO_WINDOW: u32 = 0x0800_0000;

struct BackendProcess(Mutex<Option<Child>>);

impl BackendProcess {
    fn stop(&self) {
        if let Ok(mut guard) = self.0.lock() {
            if let Some(mut child) = guard.take() {
                let _ = child.kill();
                let _ = child.wait();
            }
        }
    }
}

impl Drop for BackendProcess {
    fn drop(&mut self) {
        self.stop();
    }
}

fn kill_backend(app_handle: &tauri::AppHandle) {
    if let Some(state) = app_handle.try_state::<BackendProcess>() {
        state.stop();
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

fn normalize_path(path: &PathBuf) -> PathBuf {
    let s = path.to_string_lossy().to_string();
    if cfg!(target_os = "windows") && s.starts_with("\\\\?\\") {
        PathBuf::from(&s[4..])
    } else {
        path.clone()
    }
}

fn app_resource_dir(app: &tauri::App) -> Result<PathBuf, String> {
    let dir = app.path().resource_dir().map_err(|e| e.to_string())?;
    if cfg!(debug_assertions) {
        Ok(dir)
    } else {
        Ok(normalize_path(&dir))
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let app = tauri::Builder::default()
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::Destroyed = event {
                kill_backend(window.app_handle());
            }
        })
        .setup(|app| {
            #[cfg(debug_assertions)]
            {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }

            let resource_dir = app_resource_dir(app)?;
            let resources_dir = resource_dir.join("resources");
            let backend_dir = resources_dir.join("backend");
            let frontend_dir = resources_dir.join("frontend");
            let env_file = resources_dir.join(".env");
            let flask_path = backend_dir.join(backend_binary_name());

            eprintln!(
                "[tauri] Starting backend from: {}",
                flask_path.display()
            );

            let mut cmd = Command::new(&flask_path);
            cmd.current_dir(&resource_dir)
                .env("FLASK_ENV", "production")
                .env("FRONTEND_DIST", frontend_dir.to_str().unwrap())
                .env("SERVER_PORT", BACKEND_PORT.to_string())
                .env("SERVER_HOST", "127.0.0.1")
                .env("ENV_FILE", env_file.to_str().unwrap());

            #[cfg(target_os = "windows")]
            {
                use std::os::windows::process::CommandExt;
                cmd.creation_flags(CREATE_NO_WINDOW);
            }

            let child = cmd
                .spawn()
                .map_err(|e| format!("Failed to start backend: {}", e))?;

            app.manage(BackendProcess(Mutex::new(Some(child))));

            let handle = app.handle().clone();
            std::thread::spawn(move || {
                eprintln!("[tauri] Waiting for backend on port {}...", BACKEND_PORT);
                match wait_for_port(BACKEND_PORT, 30) {
                    Ok(_) => {
                        eprintln!("[tauri] Backend is ready, navigating to frontend...");
                        if let Some(window) = handle.get_webview_window("main") {
                            let url =
                                url::Url::parse(&format!("http://localhost:{}", BACKEND_PORT))
                                    .unwrap();
                            let _ = window.navigate(url);
                        }
                    }
                    Err(e) => eprintln!("[tauri] Backend startup warning: {}", e),
                }
            });

            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building tauri application");

    app.run(|app_handle, event| {
        if let tauri::RunEvent::ExitRequested { .. } = event {
            kill_backend(app_handle);
        }
    });
}
