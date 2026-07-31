#!/usr/bin/env node
"use strict";

/**
 * Pre-build guard for Tauri builds.
 *
 * Guarantees that `frontend/src-tauri/resources/.env` exists before the
 * installer is assembled. If it is missing it is generated from
 * `backend/.env.production` (fallback: repo-root `.env.production`, then the
 * same minimal fallback content used by `scripts/build-desktop.ps1` and
 * `scripts/build-desktop.sh`).
 *
 * Fail-safe: if the file still cannot be created the process exits non-zero,
 * which aborts `tauri build` so a broken installer can never be produced.
 *
 * Wired in via `frontend/package.json` script `ensure-env` and
 * `tauri.conf.json` -> `build.beforeBuildCommand`.
 */

const fs = require("fs");
const path = require("path");

const REPO_ROOT = path.resolve(__dirname, "..");
const RESOURCES_DIR = path.join(REPO_ROOT, "frontend", "src-tauri", "resources");
const ENV_FILE = path.join(RESOURCES_DIR, ".env");
const PROD_ENV = path.join(REPO_ROOT, "backend", ".env.production");
const ROOT_PROD_ENV = path.join(REPO_ROOT, ".env.production");

const FALLBACK_ENV =
  [
    "SECRET_KEY=pos-system-secret-key-2026-production-ready",
    "JWT_SECRET_KEY=pos-system-jwt-secret-key-2026-production-ready",
    "DB_HOST=localhost",
    "DB_PORT=3306",
    "DB_NAME=pos_system",
    "DB_USER=root",
    "DB_PASSWORD=123456",
    "DB_POOL_NAME=pos_pool",
    "DB_POOL_SIZE=5",
    "CORS_ORIGINS=http://localhost:5001",
  ].join("\n") + "\n";

function fail(message) {
  console.error("[ensure-env] ERROR: " + message);
  console.error(
    "[ensure-env] Refusing to continue: a Tauri build without resources/.env " +
      "would produce a broken installer."
  );
  process.exit(1);
}

function main() {
  console.log("[ensure-env] Ensuring resources/.env exists before build...");
  console.log("[ensure-env]   target: " + ENV_FILE);

  if (fs.existsSync(ENV_FILE)) {
    console.log("[ensure-env] resources/.env already exists -> continuing.");
    return;
  }

  console.log("[ensure-env] resources/.env is MISSING -> generating...");
  fs.mkdirSync(RESOURCES_DIR, { recursive: true });

  let source = null;
  if (fs.existsSync(PROD_ENV)) {
    source = PROD_ENV;
  } else if (fs.existsSync(ROOT_PROD_ENV)) {
    source = ROOT_PROD_ENV;
  }

  try {
    if (source) {
      fs.copyFileSync(source, ENV_FILE);
      console.log("[ensure-env] copied " + source + " -> " + ENV_FILE);
    } else {
      fs.writeFileSync(ENV_FILE, FALLBACK_ENV, { encoding: "utf8" });
      console.log("[ensure-env] no .env.production found; wrote fallback .env");
    }
  } catch (err) {
    fail("could not write " + ENV_FILE + ": " + err.message);
  }

  if (!fs.existsSync(ENV_FILE)) {
    fail(ENV_FILE + " still does not exist after generation.");
  }

  console.log("[ensure-env] verified " + ENV_FILE + " exists -> build may continue.");
}

main();
