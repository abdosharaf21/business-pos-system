"""First-run database setup server for the Business POS System.

The desktop shell starts this small server (instead of the main
application) whenever MySQL cannot be reached or the stored credentials
are rejected. It serves a self-contained dark-themed setup wizard and a
tiny JSON API so the user can enter database credentials and launch the
application without ever editing configuration files by hand.

Security:
    * The database password is never logged and never prefilled.
    * Credentials are sent over localhost in the request body only.
    * The password is written to the ``.env`` file only after a
      successful connection test.
"""

import html
import logging
import os
import re

import mysql.connector

from flask import Flask, Response, jsonify, request

from backend.database.bootstrap import BootstrapError, ensure_database_ready
from backend.database.config import DatabaseConfig

logger = logging.getLogger(__name__)

_ENV_KEY_RE = re.compile(r"^([A-Za-z0-9_]+)\s*=")


def _resolve_env_file(env_file: str) -> str:
    """Resolve the target ``.env`` path for saving settings.

    Args:
        env_file: Path passed by the desktop shell, if any.

    Returns:
        The absolute path to the ``.env`` file to update.
    """
    if env_file:
        return env_file
    candidates = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.getcwd(), "resources", ".env"),
    ]
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
    return os.path.join(os.getcwd(), "resources", ".env")


def _existing_env(env_file: str) -> dict:
    """Read the current ``.env`` values for prefilling the wizard.

    Args:
        env_file: Path to the ``.env`` file.

    Returns:
        Dictionary of key/value pairs found in the file.
    """
    result = {}
    if not os.path.isfile(env_file):
        return result
    with open(env_file, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = _ENV_KEY_RE.match(line)
            if match:
                value = line.split("=", 1)[1].strip().strip("\"'")
                result[match.group(1)] = value
    return result


def _encode_value(value) -> str:
    """Sanitize a value for storage in a ``.env`` file.

    Args:
        value: Raw value.

    Returns:
        Value safe to write as ``KEY=VALUE``, quoted when needed.
    """
    value = str(value).strip().strip("\"'")
    value = value.replace("\r", "").replace("\n", "")
    if re.search(r"[\s#\"'\\]", value):
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return value


def _write_env_file(env_file: str, values: dict) -> None:
    """Write database settings into the ``.env`` file atomically.

    Existing keys are updated in place and unrelated settings are
    preserved verbatim.

    Args:
        env_file: Path to the ``.env`` file.
        values: Database settings to write.
    """
    if os.path.isfile(env_file):
        with open(env_file, "r", encoding="utf-8-sig") as f:
            lines = f.read().splitlines()
    else:
        lines = []
    new_lines = []
    updated = set()
    for line in lines:
        match = _ENV_KEY_RE.match(line.strip())
        if match and match.group(1) in values:
            new_lines.append(f"{match.group(1)}={_encode_value(values[match.group(1)])}")
            updated.add(match.group(1))
        else:
            new_lines.append(line)
    for key, value in values.items():
        if key not in updated:
            new_lines.append(f"{key}={_encode_value(value)}")
    content = "\n".join(new_lines) + "\n"
    target = env_file + ".tmp"
    with open(target, "w", encoding="utf-8") as f:
        f.write(content)
    os.replace(target, env_file)


def _map_error_message(error: mysql.connector.Error, host: str, port: int) -> str:
    """Turn a connection error into a precise, user-friendly message.

    Args:
        error: The mysql.connector error raised while connecting.
        host: Database host being tested.
        port: Database port being tested.

    Returns:
        Short explanation of the failure.
    """
    if error.errno in (2002, 2003, 2005, 2006):
        return f"MySQL server is not reachable at {host}:{port} (errno {error.errno})."
    if error.errno == 1045:
        return "MySQL rejected the username or password (errno 1045 - access denied)."
    return f"Unexpected MySQL error: {error}"


def _validate_payload(payload: dict) -> tuple:
    """Validate the values submitted by the wizard.

    Args:
        payload: Parsed JSON request body.

    Returns:
        Tuple of (validated_values or None, error_message or None).
    """
    host = str(payload.get("host") or "localhost").strip() or "localhost"
    port_raw = str(payload.get("port") or "3306").strip() or "3306"
    user = str(payload.get("user") or "root").strip() or "root"
    password = str(payload.get("password") or "")
    database = str(payload.get("database") or "pos_system").strip() or "pos_system"
    try:
        port = int(port_raw)
    except ValueError:
        return None, "Port must be a number between 1 and 65535."
    if not (1 <= port <= 65535):
        return None, "Port must be between 1 and 65535."
    if not re.match(r"^[A-Za-z0-9_]+$", database):
        return None, "Database name may only contain letters, numbers and underscores."
    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
    }, None


def _test_connection(values: dict) -> tuple:
    """Try to connect to the MySQL server with the submitted values.

    The connection is made without selecting a database so that a
    missing database (which the bootstrap will create) is not an error.

    Args:
        values: Validated host/port/user/password values.

    Returns:
        Tuple of (success bool, message string).
    """
    try:
        conn = mysql.connector.connect(
            host=values["host"],
            port=values["port"],
            user=values["user"],
            password=values["password"],
            connection_timeout=6,
            autocommit=True,
        )
    except mysql.connector.Error as e:
        return False, _map_error_message(e, values["host"], values["port"])
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
    finally:
        conn.close()
    return True, "Connection successful"


def _env_values(values: dict) -> dict:
    """Convert validated values into ``.env`` database settings.

    Args:
        values: Validated host/port/user/password/database values.

    Returns:
        Dictionary of DB_* environment settings.
    """
    return {
        "DB_HOST": values["host"],
        "DB_PORT": str(values["port"]),
        "DB_NAME": values["database"],
        "DB_USER": values["user"],
        "DB_PASSWORD": values["password"],
    }


def _render_wizard(env_file: str) -> str:
    """Render the setup wizard with current values prefilled.

    Args:
        env_file: Path to the ``.env`` file.

    Returns:
        Complete HTML document for the setup window.
    """
    existing = _existing_env(env_file)
    return (
        SETUP_WIZARD_HTML
        .replace("__HOST__", html.escape(existing.get("DB_HOST", "localhost")))
        .replace("__PORT__", html.escape(existing.get("DB_PORT", "3306")))
        .replace("__DB_NAME__", html.escape(existing.get("DB_NAME", "pos_system")))
        .replace("__DB_USER__", html.escape(existing.get("DB_USER", "root")))
    )


def create_setup_app(env_file: str = None) -> Flask:
    """Create the Flask app that serves the setup wizard and its API.

    Args:
        env_file: Path to the ``.env`` file to update on save; when
            None the standard search paths are used.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)
    target_env = _resolve_env_file(env_file)
    wizard_page = _render_wizard(target_env)

    @app.get("/")
    def wizard():
        """Serve the setup wizard page."""
        return Response(wizard_page, mimetype="text/html")

    @app.get("/api/setup/status")
    def setup_status():
        """Tell the desktop shell that database setup is required."""
        return jsonify({"success": True, "setup_required": True})

    @app.post("/api/test-connection")
    def test_connection():
        """Test the submitted database connection settings."""
        values, error = _validate_payload(request.get_json(silent=True) or {})
        if error:
            return jsonify({"success": False, "message": error}), 400
        ok, message = _test_connection(values)
        return jsonify({"success": ok, "message": message}), (200 if ok else 400)

    @app.post("/api/save-config")
    def save_config():
        """Validate, persist and bootstrap the database settings."""
        values, error = _validate_payload(request.get_json(silent=True) or {})
        if error:
            return jsonify({"success": False, "message": error}), 400
        ok, message = _test_connection(values)
        if not ok:
            return jsonify({"success": False, "message": message}), 400
        _write_env_file(target_env, _env_values(values))
        logger.info(
            "Database settings saved to %s (host=%s port=%s db=%s user=%s)",
            target_env,
            values["host"],
            values["port"],
            values["database"],
            values["user"],
        )
        try:
            config = DatabaseConfig(
                host=values["host"],
                port=values["port"],
                name=values["database"],
                user=values["user"],
                password=values["password"],
            )
            result = ensure_database_ready(config)
        except BootstrapError as bootstrap_error:
            logger.error("Database setup failed: %s", bootstrap_error.message)
            return jsonify({"success": False, "message": bootstrap_error.message}), 400
        logger.info("Database setup complete: %s", result)
        return jsonify({
            "success": True,
            "message": "Database is ready. Starting the application...",
            "data": result,
        })

    return app


SETUP_WIZARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="color-scheme" content="dark">
<title>Business POS System - Database Setup</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { min-height: 100%; }
  body {
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, Arial, sans-serif;
    background: #0f172a; color: #e2e8f0;
  }
  .wrap { max-width: 600px; margin: 0 auto; padding: 34px 32px 26px; }
  .logo { display: flex; align-items: center; gap: 12px; }
  .logo-dot {
    width: 34px; height: 34px; border-radius: 9px;
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-weight: 700; font-size: 16px;
    box-shadow: 0 6px 16px -4px rgba(59, 130, 246, 0.5);
  }
  h1 { font-size: 20px; font-weight: 600; letter-spacing: 0.2px; }
  .sub { color: #94a3b8; font-size: 13px; margin: 6px 0 22px; line-height: 1.5; }
  .card {
    background: #1e293b; border: 1px solid #334155; border-radius: 14px;
    padding: 22px; box-shadow: 0 12px 28px -8px rgba(0, 0, 0, 0.45);
  }
  .row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
  .field { margin-bottom: 13px; }
  label {
    display: block; font-size: 11px; font-weight: 600; color: #94a3b8;
    text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 6px;
  }
  input {
    width: 100%; padding: 10px 12px; border-radius: 8px;
    border: 1px solid #334155; background: #0f172a; color: #e2e8f0;
    font-size: 14px; outline: none;
    transition: border-color 0.15s, box-shadow 0.15s;
  }
  input::placeholder { color: #475569; }
  input:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25); }
  .actions { display: flex; gap: 10px; margin-top: 4px; }
  button {
    cursor: pointer; border: none; border-radius: 8px;
    font-size: 14px; font-weight: 600; padding: 10px 16px;
    transition: background 0.15s, opacity 0.15s;
  }
  .btn-secondary { background: transparent; color: #94a3b8; border: 1px solid #334155; }
  .btn-secondary:hover { color: #e2e8f0; border-color: #475569; }
  .btn-primary { background: #2563eb; color: #fff; }
  .btn-primary:hover { background: #1d4ed8; }
  .btn-primary:disabled { opacity: 0.45; cursor: not-allowed; }
  .btn-block { width: 100%; margin-top: 16px; padding: 12px; font-size: 15px; }
  .test-status {
    display: none; align-items: center; gap: 10px;
    margin-top: 14px; font-size: 13px; padding: 10px 12px; border-radius: 8px;
  }
  .test-status.ok { display: flex; background: rgba(34, 197, 94, 0.12); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.35); }
  .test-status.err { display: flex; background: rgba(239, 68, 68, 0.12); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.35); }
  .test-status.info { display: flex; background: rgba(59, 130, 246, 0.12); color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.35); }
  .spinner {
    display: none; width: 15px; height: 15px; flex: 0 0 auto;
    border: 2px solid rgba(59, 130, 246, 0.3); border-top-color: #3b82f6;
    border-radius: 50%; animation: spin 0.7s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .hint { color: #64748b; font-size: 12px; margin-top: 16px; line-height: 1.6; }
  .hint b { color: #94a3b8; font-weight: 600; }
</style>
</head>
<body>
  <div class="wrap">
    <div class="logo">
      <div class="logo-dot">P</div>
      <h1>Business POS System</h1>
    </div>
    <p class="sub">To connect the application to its database, provide the connection details for your MySQL Server.</p>

    <div class="card">
      <form id="wizard-form" onsubmit="event.preventDefault(); testConnection();">
        <div class="row">
          <div class="field">
            <label for="host">Host</label>
            <input id="host" type="text" value="__HOST__" spellcheck="false" autocomplete="off">
          </div>
          <div class="field">
            <label for="port">Port</label>
            <input id="port" type="text" inputmode="numeric" value="__PORT__" spellcheck="false" autocomplete="off">
          </div>
        </div>
        <div class="row">
          <div class="field">
            <label for="database">Database Name</label>
            <input id="database" type="text" value="__DB_NAME__" spellcheck="false" autocomplete="off">
          </div>
          <div class="field">
            <label for="user">Username</label>
            <input id="user" type="text" value="__DB_USER__" spellcheck="false" autocomplete="off">
          </div>
        </div>
        <div class="field">
          <label for="password">Password</label>
          <input id="password" type="password" placeholder="Enter MySQL password" autocomplete="new-password">
        </div>
        <div class="actions">
          <button class="btn-secondary" type="button" onclick="cancel()">Cancel</button>
          <button class="btn-primary" id="test-btn" type="submit">Test Connection</button>
        </div>
        <div id="status" class="test-status"><span class="spinner" id="spinner"></span><span id="status-text"></span></div>
        <button class="btn-primary btn-block" id="save-btn" type="button" disabled onclick="saveAndLaunch()">Save &amp; Launch Application</button>
      </form>
    </div>

    <p class="hint">
      The application creates the database automatically if it does not exist and never
      modifies an existing database.<br>
      <b>First-time login after setup:</b> admin@pos.com &middot; password 123456
    </p>
  </div>

<script>
  function $(id) { return document.getElementById(id); }
  var tested = null;

  function values() {
    return {
      host: $('host').value.trim() || 'localhost',
      port: ($('port').value.trim() || '3306').replace(/^0+/, '') || '3306',
      user: $('user').value.trim() || 'root',
      password: $('password').value,
      database: $('database').value.trim() || 'pos_system'
    };
  }
  function currentKey() { return JSON.stringify(values()); }
  function setStatus(text, kind) {
    $('status').className = 'test-status ' + (kind || '');
    $('status-text').textContent = text || '';
  }
  function setTesting(on) {
    $('spinner').style.display = on ? 'block' : 'none';
    $('test-btn').disabled = on;
    $('save-btn').disabled = true;
  }
  function refreshSave() {
    $('save-btn').disabled = tested !== currentKey();
  }

  ['host', 'port', 'user', 'password', 'database'].forEach(function (id) {
    $(id).addEventListener('input', function () {
      tested = null;
      setStatus('', '');
      refreshSave();
    });
  });

  function testConnection() {
    var v = values();
    setTesting(true);
    setStatus('Testing connection...', 'info');
    fetch('/api/test-connection', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(v)
    }).then(function (res) {
      return res.json();
    }).then(function (data) {
      if (data.success) {
        tested = currentKey();
        setStatus('Connection successful', 'ok');
      } else {
        tested = null;
        setStatus(data.message || 'Connection failed', 'err');
      }
    }).catch(function () {
      tested = null;
      setStatus('Could not reach the setup service. Please try again.', 'err');
    }).finally(function () {
      $('spinner').style.display = 'none';
      $('test-btn').disabled = false;
      refreshSave();
    });
  }

  function saveAndLaunch() {
    var v = values();
    setTesting(true);
    setStatus('Saving settings...', 'info');
    fetch('/api/save-config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(v)
    }).then(function (res) {
      return res.json();
    }).then(function (data) {
      if (!data.success) {
        tested = null;
        setStatus(data.message || 'Could not save the settings.', 'err');
        $('spinner').style.display = 'none';
        $('test-btn').disabled = false;
        refreshSave();
        return;
      }
      $('password').value = '';
      setStatus(data.message || 'Database is ready. Starting the application...', 'ok');
      if (window.__TAURI__ && window.__TAURI__.core) {
        return window.__TAURI__.core.invoke('restart_backend').catch(function () {
          setStatus('Settings saved, but the application could not restart. Please close and reopen it.', 'err');
        });
      }
      setStatus('Settings saved. Please close this window and reopen the application.', 'ok');
    }).catch(function () {
      tested = null;
      setStatus('Could not save the settings. Please try again.', 'err');
      $('spinner').style.display = 'none';
      $('test-btn').disabled = false;
      refreshSave();
    });
  }

  function cancel() {
    if (window.__TAURI__ && window.__TAURI__.core) {
      window.__TAURI__.core.invoke('cancel_setup');
    } else if (window.close) {
      window.close();
    }
  }
</script>
</body>
</html>"""
