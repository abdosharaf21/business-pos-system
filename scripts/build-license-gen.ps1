# Build the License Generator for Windows (PowerShell)
# The generator is the ONLY component that holds the RSA-4096 private key.
# Run this on the vendor's Windows machine, keep the keys private.
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location "$ProjectRoot\licensing-tools\license-gen"

Write-Host "[license-gen] Building release binary..."
cargo build --release
if ($LASTEXITCODE -ne 0) { throw "cargo build failed" }

$exe = Join-Path $ProjectRoot "licensing-tools\license-gen\target\release\license-gen.exe"
Write-Host "[license-gen] Done: $exe"
Write-Host "[license-gen] Next:"
Write-Host "   1. Run:  license-gen.exe --generate-keys"
Write-Host "   2. Copy public_key.pem content into licensing-core\src\license_public_key.pem"
Write-Host "   3. Rebuild the application with scripts\build-desktop.ps1"
Write-Host "   4. Issue licenses with:  license-gen.exe --customer ""Name"" --hwid <64-hex-id>"
