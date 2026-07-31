# Build Desktop — Windows (PowerShell)
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

function Log { Write-Host "[build-desktop] $args" }

# 1. Build frontend (React -> dist/)
Log "Building frontend..."
Set-Location frontend
npm run build
Set-Location $ProjectRoot

# 2. Build backend with PyInstaller
Log "Building backend (PyInstaller)..."
python backend/build.py

# 3. Prepare resources directory for Tauri
$ResourcesDir = "frontend\src-tauri\resources"
Log "Preparing resources in $ResourcesDir..."

if (Test-Path $ResourcesDir) { Remove-Item -Recurse -Force $ResourcesDir }
New-Item -ItemType Directory -Force -Path $ResourcesDir | Out-Null

# 3a. Copy PyInstaller output
Copy-Item -Recurse "backend\dist\backend-app" "$ResourcesDir\backend"

# 3b. Copy frontend dist (so Flask can serve it)
New-Item -ItemType Directory -Force -Path "$ResourcesDir\frontend" | Out-Null
Copy-Item -Recurse "frontend\dist\*" "$ResourcesDir\frontend\"

# 3c. Copy .env for production
if (Test-Path "backend\.env.production") {
    Copy-Item "backend\.env.production" "$ResourcesDir\.env"
    Log "Using .env.production"
} elseif (Test-Path ".env.production") {
    Copy-Item ".env.production" "$ResourcesDir\.env"
    Log "Using .env.production from project root"
} else {
    Log "WARNING: No .env.production found; creating minimal .env"
@"
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
        "@ | Out-File -Encoding ascii "$ResourcesDir\.env"
}

Log "Resources prepared:"
Get-ChildItem -Recurse -File $ResourcesDir | Select-Object -First 20 | ForEach-Object { $_.FullName }

# 4. Run tauri build
Log "Running tauri build..."
Set-Location frontend
npm run tauri build
