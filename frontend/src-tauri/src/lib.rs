use std::io::{Read, Write};
use std::net::TcpStream;
use std::path::PathBuf;
use std::process::{Child, Command};
use std::sync::Mutex;
use std::time::Duration;
use tauri::{Manager, WebviewUrl, WebviewWindowBuilder};

const BACKEND_BINARY: &str = "backend-app";
const BACKEND_PORT: u16 = 5001;
const SETUP_WINDOW_LABEL: &str = "setup";
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

struct SetupComplete(Mutex<bool>);

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

fn app_resource_dir(app_handle: &tauri::AppHandle) -> Result<PathBuf, String> {
    let dir = app_handle.path().resource_dir().map_err(|e| e.to_string())?;
    if cfg!(debug_assertions) {
        Ok(dir)
    } else {
        Ok(normalize_path(&dir))
    }
}

fn spawn_backend(resource_dir: &PathBuf) -> Result<Child, String> {
    let resources_dir = resource_dir.join("resources");
    let backend_dir = resources_dir.join("backend");
    let frontend_dir = resources_dir.join("frontend");
    let env_file = resources_dir.join(".env");
    let flask_path = backend_dir.join(backend_binary_name());

    eprintln!("[tauri] Starting backend from: {}", flask_path.display());

    let mut cmd = Command::new(&flask_path);
    cmd.current_dir(resource_dir)
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

    cmd.spawn().map_err(|e| format!("Failed to start backend: {}", e))
}

fn http_get_json(path: &str) -> Option<serde_json::Value> {
    let addr = format!("127.0.0.1:{}", BACKEND_PORT);
    let mut stream =
        TcpStream::connect_timeout(&addr.parse().ok()?, Duration::from_millis(1500)).ok()?;
    let request = format!(
        "GET {path} HTTP/1.1\r\nHost: {addr}\r\nConnection: close\r\n\r\n"
    );
    stream.write_all(request.as_bytes()).ok()?;
    let mut buf = Vec::new();
    stream.read_to_end(&mut buf).ok()?;
    let body = String::from_utf8_lossy(&buf).to_string();
    let body = body.split("\r\n\r\n").nth(1).unwrap_or("");
    serde_json::from_str(body).ok()
}

fn backend_requires_setup() -> bool {
    for _ in 0..5 {
        if let Some(value) = http_get_json("/api/setup/status") {
            return value
                .get("setup_required")
                .and_then(|v| v.as_bool())
                .unwrap_or(false);
        }
        std::thread::sleep(Duration::from_millis(300));
    }
    false
}

fn navigate_main(handle: &tauri::AppHandle) {
    if let Some(window) = handle.get_webview_window("main") {
        let url = url::Url::parse(&format!("http://localhost:{}", BACKEND_PORT)).unwrap();
        let _ = window.navigate(url);
    }
}

fn open_setup_window(handle: &tauri::AppHandle) -> Result<(), String> {
    if handle.get_webview_window(SETUP_WINDOW_LABEL).is_some() {
        return Ok(());
    }
    let url = url::Url::parse(&format!("http://localhost:{}", BACKEND_PORT)).unwrap();
    WebviewWindowBuilder::new(handle, SETUP_WINDOW_LABEL, WebviewUrl::External(url))
        .title("Business POS System - Database Setup")
        .inner_size(660.0, 780.0)
        .min_inner_size(660.0, 780.0)
        .resizable(false)
        .maximizable(false)
        .center()
        .build()
        .map(|_| ())
        .map_err(|e| e.to_string())
}

#[tauri::command]
fn restart_backend(app_handle: tauri::AppHandle) -> Result<(), String> {
    if let Some(state) = app_handle.try_state::<BackendProcess>() {
        state.stop();
    }
    let resource_dir = app_resource_dir(&app_handle)?;
    let child = spawn_backend(&resource_dir)?;
    match app_handle.try_state::<BackendProcess>() {
        Some(state) => {
            if let Ok(mut guard) = state.0.lock() {
                *guard = Some(child);
            }
        }
        None => {
            app_handle.manage(BackendProcess(Mutex::new(Some(child))));
        }
    }
    eprintln!("[tauri] Backend restarted after database setup");
    if let Some(state) = app_handle.try_state::<SetupComplete>() {
        if let Ok(mut guard) = state.0.lock() {
            *guard = true;
        }
    }
    let handle = app_handle.clone();
    std::thread::spawn(move || match wait_for_port(BACKEND_PORT, 30) {
        Ok(_) => {
            eprintln!("[tauri] Backend is ready, opening application...");
            navigate_main(&handle);
            if let Some(window) = handle.get_webview_window(SETUP_WINDOW_LABEL) {
                let _ = window.close();
            }
        }
        Err(e) => eprintln!("[tauri] Backend restart warning: {}", e),
    });
    Ok(())
}

#[tauri::command]
fn cancel_setup(app_handle: tauri::AppHandle) {
    eprintln!("[tauri] Database setup cancelled, exiting...");
    app_handle.exit(0);
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let app = tauri::Builder::default()
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::Destroyed = event {
                let app_handle = window.app_handle();
                if window.label() == "main" {
                    kill_backend(app_handle);
                    app_handle.exit(0);
                } else if window.label() == SETUP_WINDOW_LABEL {
                    let done = app_handle
                        .state::<SetupComplete>()
                        .0
                        .lock()
                        .map(|guard| *guard)
                        .unwrap_or(false);
                    if !done {
                        app_handle.exit(0);
                    }
                }
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

            app.manage(SetupComplete(Mutex::new(false)));

            let resource_dir = app_resource_dir(app.handle())?;
            let child = spawn_backend(&resource_dir)?;
            app.manage(BackendProcess(Mutex::new(Some(child))));

            let handle = app.handle().clone();
            std::thread::spawn(move || {
                eprintln!("[tauri] Waiting for backend on port {}...", BACKEND_PORT);
                match wait_for_port(BACKEND_PORT, 30) {
                    Ok(_) => {
                        if backend_requires_setup() {
                            eprintln!("[tauri] Database setup required, opening setup wizard...");
                            if let Err(e) = open_setup_window(&handle) {
                                eprintln!("[tauri] Could not open setup window: {}", e);
                            }
                        } else {
                            eprintln!("[tauri] Backend is ready, navigating to frontend...");
                            navigate_main(&handle);
                        }
                    }
                    Err(e) => eprintln!("[tauri] Backend startup warning: {}", e),
                }
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![restart_backend, cancel_setup])
        .build(tauri::generate_context!())
        .expect("error while building tauri application");

    app.run(|app_handle, event| {
        if let tauri::RunEvent::ExitRequested { .. } = event {
            kill_backend(app_handle);
        }
    });
}
