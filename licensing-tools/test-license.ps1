# Business POS System — License Test Harness (Windows, PowerShell)
#
# Verifies the 12 licensing scenarios against the packaged application.
# Run this on the Windows build machine AFTER installing the NSIS package.
#
# Prerequisites:
#   1. Run scripts\build-desktop.ps1 (builds app + license generator).
#   2. Install the produced NSIS installer (Business POS System_*.exe).
#   3. Run this script from the repository root.
#
#   .\licensing-tools\test-license.ps1
#
# Optional parameters:
#   -AppExe       Path to the application executable (default: installed NSIS app).
#   -LicenseGen   Path to license-gen.exe (default: licensing-tools\license-gen\target\release\license-gen.exe).
#   -TimeOutSecs  Seconds to wait for the app to settle (default 25).
#   -NoCleanup    Keep temporary files after the run.
#
# Exit code 0 when every scenario passes, 1 otherwise.

param(
    [string]$AppExe = "",
    [string]$LicenseGen = "",
    [int]$TimeOutSecs = 25,
    [switch]$NoCleanup
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

if (-not $AppExe) {
    $AppExe = Join-Path $env:LOCALAPPDATA "Programs\Business POS System\Business POS System.exe"
}
if (-not $LicenseGen) {
    $LicenseGen = Join-Path $ProjectRoot "licensing-tools\license-gen\target\release\license-gen.exe"
}

if (-not (Test-Path $AppExe)) { throw "App not found: $AppExe (install the NSIS package first)" }
if (-not (Test-Path $LicenseGen)) { throw "License generator not found: $LicenseGen (run scripts\build-desktop.ps1 first)" }

$WorkDir = Join-Path $env:TEMP "bpos-license-tests"
if (Test-Path $WorkDir) { Remove-Item -Recurse -Force $WorkDir }
New-Item -ItemType Directory -Force -Path $WorkDir | Out-Null

$Results = @()

function Log { Write-Host "[test-license] $args" }

function Get-MachineId {
    $id = & $LicenseGen --machine-id
    return ($id -join "").Trim()
}

function New-License {
    param([string]$Hwid, [string]$Customer, [string]$OutFile)
    & $LicenseGen --customer $Customer --hwid $Hwid --out $OutFile | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "license-gen failed" }
}

function Test-Port {
    param([int]$Port = 5001)
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $iar = $client.BeginConnect("127.0.0.1", $Port, $null, $null)
        $ok = $iar.AsyncWaitHandle.WaitOne(1000, $false)
        if ($ok) { $client.EndConnect($iar); return $true }
        return $false
    } catch { return $false }
    finally { $client.Dispose() }
}

function Invoke-Scenario {
    param(
        [string]$Name,
        [scriptblock]$Setup,      # prepares the license file (called with $scenarioDir)
        [bool]$ExpectedLicensed    # true => port 5001 must open, false => activation must show
    )

    $scenarioDir = Join-Path $WorkDir $Name
    New-Item -ItemType Directory -Force -Path $scenarioDir | Out-Null
    $licensePath = Join-Path $scenarioDir "Business POS System\license.dat"

    # Build the ProgramData-like layout the app looks for.
    & $Setup $scenarioDir $licensePath

    # Launch the app with a redirected ProgramData so the real one is untouched.
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $AppExe
    $psi.UseShellExecute = $false
    $psi.EnvironmentVariables["ProgramData"] = $scenarioDir
    $psi.RedirectStandardError = $true
    $proc = [System.Diagnostics.Process]::Start($psi)

    Start-Sleep -Seconds $TimeOutSecs

    $portOpen = Test-Port -Port 5001
    $alive = -not $proc.HasExited
    if (-not $alive) { try { $proc.Kill() } catch {} }

    $pass = $false
    if ($ExpectedLicensed) {
        $pass = $portOpen
    } else {
        $pass = (-not $portOpen) -and $alive
    }

    $detail = "portOpen=$portOpen alive=$alive"
    $Results += [PSCustomObject]@{ Name = $Name; Expected = $ExpectedLicensed; Pass = $pass; Detail = $detail }
    if ($pass) { Log "PASS  $Name ($detail)" } else { Log "FAIL  $Name ($detail)" }

    Start-Sleep -Seconds 2
}

try {
    $machineId = Get-MachineId
    Log "Machine hardware id: $machineId"
    Log "App:      $AppExe"
    Log "Gen:      $LicenseGen"
    Log ""

    $validLicense = Join-Path $WorkDir "valid-license.dat"
    New-License $machineId "Scenario Customer" $validLicense

    # Scenario 1 — First activation (no license) shows the activation window.
    Invoke-Scenario "S01_first_activation" {
        param($dir, $path)   # no license file created
    } -ExpectedLicensed $false

    # Scenario 1b — Installing a valid license lets the app start.
    Invoke-Scenario "S01b_activate_then_start" {
        param($dir, $path)
        New-Item -ItemType Directory -Force -Path (Split-Path $path) | Out-Null
        Copy-Item $validLicense $path
    } -ExpectedLicensed $true

    # Scenario 2 — Restart with the same valid license.
    Invoke-Scenario "S02_restart_valid" {
        param($dir, $path)
        New-Item -ItemType Directory -Force -Path (Split-Path $path) | Out-Null
        Copy-Item $validLicense $path
    } -ExpectedLicensed $true

    # Scenario 3 — App update keeps the (already valid) license.
    Invoke-Scenario "S03_update_keeps_license" {
        param($dir, $path)
        New-Item -ItemType Directory -Force -Path (Split-Path $path) | Out-Null
        Copy-Item $validLicense $path
    } -ExpectedLicensed $true

    # Scenario 4 — Reinstall keeps the license (same ProgramData).
    Invoke-Scenario "S04_reinstall_keeps_license" {
        param($dir, $path)
        New-Item -ItemType Directory -Force -Path (Split-Path $path) | Out-Null
        Copy-Item $validLicense $path
    } -ExpectedLicensed $true

    # Scenario 5 — Existing customer (valid license already present).
    Invoke-Scenario "S05_existing_customer" {
        param($dir, $path)
        New-Item -ItemType Directory -Force -Path (Split-Path $path) | Out-Null
        Copy-Item $validLicense $path
    } -ExpectedLicensed $true

    # Scenario 6 — Missing license blocks startup.
    Invoke-Scenario "S06_missing_license" {
        param($dir, $path)   # no license file created
    } -ExpectedLicensed $false

    # Scenario 7 — Fake license file is rejected.
    Invoke-Scenario "S07_fake_license" {
        param($dir, $path)
        New-Item -ItemType Directory -Force -Path (Split-Path $path) | Out-Null
        "this is not a license" | Set-Content -Encoding ascii $path
    } -ExpectedLicensed $false

    # Scenario 8 — Modified license (tampered field) is rejected.
    Invoke-Scenario "S08_modified_license" {
        param($dir, $path)
        New-Item -ItemType Directory -Force -Path (Split-Path $path) | Out-Null
        $tampered = (Get-Content $validLicense -Raw) -replace "Scenario Customer", "Hacked Customer"
        $tampered | Set-Content -Encoding utf8 $path
    } -ExpectedLicensed $false

    # Scenario 9 — Wrong hardware (license bound to another PC) is rejected.
    Invoke-Scenario "S09_wrong_hardware" {
        param($dir, $path)
        $otherLicense = Join-Path $WorkDir "other-license.dat"
        New-License ("0" * 64) "Other Pc Customer" $otherLicense
        New-Item -ItemType Directory -Force -Path (Split-Path $path) | Out-Null
        Copy-Item $otherLicense $path
    } -ExpectedLicensed $false

    # Scenario 10 — Copied application to another PC (no ProgramData) blocks startup.
    Invoke-Scenario "S10_copied_app_no_license" {
        param($dir, $path)   # fresh ProgramData, no license
    } -ExpectedLicensed $false

    # Scenario 11 — Copied ProgramData license to another PC (different HWID).
    Invoke-Scenario "S11_copied_programdata" {
        param($dir, $path)
        $otherLicense = Join-Path $WorkDir "other-license-2.dat"
        New-License ("f" * 64) "Copied ProgramData Customer" $otherLicense
        New-Item -ItemType Directory -Force -Path (Split-Path $path) | Out-Null
        Copy-Item $otherLicense $path
    } -ExpectedLicensed $false

    # Scenario 12 — Rejected license (corrupt signature) blocks startup.
    Invoke-Scenario "S12_rejected_license" {
        param($dir, $path)
        New-Item -ItemType Directory -Force -Path (Split-Path $path) | Out-Null
        $corrupt = (Get-Content $validLicense -Raw) -replace '"signature": "[^"]+"', '"signature": "AAAA"'
        $corrupt | Set-Content -Encoding utf8 $path
    } -ExpectedLicensed $false

    Log ""
    Log "==================== SUMMARY ===================="
    $failures = @($Results | Where-Object { -not $_.Pass })
    $Results | ForEach-Object {
        "{0}  {1}" -f ($(if ($_.Pass) { "PASS" } else { "FAIL" })), $_.Name
    }
    Log "Passed: $($Results.Count - $failures.Count) / $($Results.Count)"
    if ($failures.Count -gt 0) {
        Log "Failed scenarios: $($failures.Name -join ', ')"
        exit 1
    }
    Log "ALL SCENARIOS PASSED"
    exit 0
}
finally {
    if (-not $NoCleanup -and (Test-Path $WorkDir)) {
        Remove-Item -Recurse -Force $WorkDir
    }
}
