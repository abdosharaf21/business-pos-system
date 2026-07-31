# Licensing System — Business POS System

Offline, hardware-locked, RSA-4096 license management.

## Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `licensing-core` | `licensing-core/` | Shared library: hardware ID, license format, RSA verify/sign. Used by both the app and the generator so payloads are byte-identical. |
| License Generator | `licensing-tools/license-gen/` | **Vendor-only** Windows utility. Holds the RSA-4096 private key and issues `license.dat` files. |
| Application gate | `frontend/src-tauri/src/` | Verifies the license at every startup. Without a valid license the backend never starts and an activation window is shown. |
| Activation window | `frontend/src-tauri/loading/activation/` | Native activation UI (dark). |
| Uninstall hook | `frontend/src-tauri/nsis/uninstaller.nsh` | Asks whether to remove the license during uninstall (default: NO). |

## License file

Stored at `%ProgramData%\Business POS System\license.dat` (Windows). It contains:

- `schema` — `business-pos-license-v1`
- `customer` — licensee name
- `product` — `Business POS System`
- `version` — product version the license was issued for
- `hardware_id` — SHA-256 of `MachineGuid|MotherboardUUID|CPUId` (64 hex chars)
- `issued_at` — issue date (RFC 3339)
- `signature` — RSA-4096 PKCS#1 v1.5 (SHA-256) signature over the other fields

The private key exists **only** in the License Generator. The app embeds the
public key (`licensing-core/src/license_public_key.pem`) at build time.

## Vendor workflow (first-time setup, Windows)

```powershell
# 1. Build the generator
.\scripts\build-license-gen.ps1

# 2. Generate the keypair ONCE (a few seconds). Keep the keys secret.
licensing-tools\license-gen\target\release\license-gen.exe --generate-keys
#    -> writes private_key.pem + public_key.pem next to license-gen.exe

# 3. Embed the public key into the app, then rebuild the installer
Copy-Item licensing-tools\license-gen\target\release\public_key.pem `
          licensing-core\src\license_public_key.pem -Force
.\scripts\build-desktop.ps1
```

> If you regenerate the keypair after shipping, all previously issued licenses
> become invalid. Only regenerate when you intend to re-issue everything.

## Issuing a license

```powershell
# Ask the customer for their hardware id (shown in the activation window, 64 hex chars)
license-gen.exe --machine-id

# Issue a license bound to that machine
license-gen.exe --customer "Acme Corp" --hwid <64-hex-id> --out license.dat
```

Send `license.dat` to the customer. It is valid for exactly one computer.

## Security rules

- The private key must never leave the vendor machine, never be committed,
  never be logged. It is excluded by `.gitignore`
  (`licensing-tools/license-gen/keys/`).
- Raw hardware identifiers are never logged or transmitted — only the SHA-256
  hash is shown.
- The application never contains the private key, only the public key.
- Licenses are verified locally (no network call). Copying the app, the
  installer, the database or a license file to another computer is detected by
  the hardware binding and blocks startup.

## Testing

- Cross-platform unit + scenario tests:
  ```bash
  cd licensing-core && cargo test
  ```
- Real-key end-to-end (auto-skips if the private key is absent):
  ```bash
  cd licensing-core && cargo test --test e2e_real_key
  ```
- Windows GUI harness (after installing the NSIS package):
  ```powershell
  .\licensing-tools\test-license.ps1
  ```
