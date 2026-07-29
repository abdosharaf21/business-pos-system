#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

log() { echo "[build-desktop] $*"; }

# 1. Build frontend (React → dist/)
log "Building frontend..."
cd frontend
npm run build
cd "$PROJECT_ROOT"

# 2. Build backend with PyInstaller
log "Building backend (PyInstaller)..."
python3 backend/build.py

# 3. Prepare resources directory for Tauri
RESOURCES_DIR="frontend/src-tauri/resources"
log "Preparing resources in $RESOURCES_DIR..."

rm -rf "$RESOURCES_DIR"
mkdir -p "$RESOURCES_DIR"

# 3a. Copy PyInstaller output
cp -r backend/dist/backend-app "$RESOURCES_DIR/backend"

# 3b. Copy frontend dist (so Flask can serve it)
mkdir -p "$RESOURCES_DIR/frontend"
cp -r frontend/dist/* "$RESOURCES_DIR/frontend/"

# 3c. Copy .env for production
if [ -f backend/.env.production ]; then
    cp backend/.env.production "$RESOURCES_DIR/.env"
    log "Using .env.production"
elif [ -f .env.production ]; then
    cp .env.production "$RESOURCES_DIR/.env"
    log "Using .env.production from project root"
else
    log "WARNING: No .env.production found; creating minimal .env"
    cat > "$RESOURCES_DIR/.env" <<-EOF
SECRET_KEY=pos-system-secret-key-2026-production-ready
JWT_SECRET_KEY=pos-system-jwt-secret-key-2026-production-ready
DB_HOST=localhost
DB_PORT=3306
DB_NAME=pos_system
DB_USER=root
DB_PASSWORD=123456
DB_POOL_NAME=pos_pool
DB_POOL_SIZE=5
CORS_ORIGINS=http://localhost:5001
EOF
fi

log "Resources prepared:"
find "$RESOURCES_DIR" -type f | head -20

# 4. Run tauri build
log "Running tauri build..."
cd frontend
npm run tauri build
