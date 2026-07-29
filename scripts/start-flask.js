const { spawn } = require("child_process");
const path = require("path");

const isWin = process.platform === "win32";
const python = isWin ? "python" : "python3";
const backendDir = path.resolve(__dirname, "..", "backend");
const env = { ...process.env, FLASK_ENV: "desktop" };

const proc = spawn(python, ["app.py"], {
  cwd: backendDir,
  env,
  stdio: "inherit",
  shell: isWin,
});

process.on("exit", () => {
  proc.kill();
});

proc.on("exit", (code) => {
  process.exit(code ?? 0);
});
