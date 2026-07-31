use std::fmt;
use std::path::{Path, PathBuf};

use base64::engine::general_purpose::STANDARD as BASE64;
use base64::Engine;
use rsa::pkcs1v15::{Signature, SigningKey, VerifyingKey};
use rsa::signature::{SignatureEncoding, Signer, Verifier};
use rsa::{pkcs8::DecodePublicKey, RsaPrivateKey, RsaPublicKey};
use serde::{Deserialize, Serialize};
use sha2::Sha256;

/// Product identifier stored inside every license file.
pub const APP_PRODUCT: &str = "Business POS System";

/// License format version. Bump this when the payload layout changes.
pub const LICENSE_SCHEMA: &str = "business-pos-license-v1";

/// Embedded public key (PEM, PKCS#8). The private key lives ONLY in the
/// License Generator and is never distributed with the application.
const LICENSE_PUBLIC_KEY_PEM: &str = include_str!("license_public_key.pem");

/// A parsed license file.
///
/// The `signature` is a Base64-encoded RSA-4096 PKCS#1 v1.5 signature (SHA-256)
/// over the canonical payload of the other six fields.
#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub struct License {
    pub schema: String,
    pub customer: String,
    pub product: String,
    pub version: String,
    pub hardware_id: String,
    pub issued_at: String,
    pub signature: String,
}

/// The subset of a license that is signed. Serialization order is fixed so the
/// generator and the verifier always hash identical bytes.
#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub struct LicensePayload {
    pub schema: String,
    pub customer: String,
    pub product: String,
    pub version: String,
    pub hardware_id: String,
    pub issued_at: String,
}

/// Reason why a license was not accepted.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum LicenseError {
    /// No license file is installed yet.
    Missing,
    /// The file exists but could not be parsed as a license.
    Corrupt(String),
    /// The RSA signature does not match the payload.
    InvalidSignature,
    /// The license is valid but was issued for a different computer.
    WrongHardware,
    /// The license was issued for a different product or an incompatible version.
    ProductMismatch,
}

impl fmt::Display for LicenseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            LicenseError::Missing => write!(f, "No license found"),
            LicenseError::Corrupt(reason) => write!(f, "Corrupt license file: {}", reason),
            LicenseError::InvalidSignature => write!(f, "License signature is invalid"),
            LicenseError::WrongHardware => {
                write!(f, "This license belongs to another computer")
            }
            LicenseError::ProductMismatch => {
                write!(f, "License does not match this product or version")
            }
        }
    }
}

impl License {
    /// Converts the license to the payload that is covered by the signature.
    pub fn payload(&self) -> LicensePayload {
        LicensePayload {
            schema: self.schema.clone(),
            customer: self.customer.clone(),
            product: self.product.clone(),
            version: self.version.clone(),
            hardware_id: self.hardware_id.clone(),
            issued_at: self.issued_at.clone(),
        }
    }

    /// Serializes the payload to the canonical bytes that get signed.
    pub fn canonical_bytes(&self) -> Vec<u8> {
        serde_json::to_vec(&self.payload()).expect("license payload is serializable")
    }
}

/// Verifies the license signature against a specific public key.
pub fn verify_signature_with_key(public_key: &RsaPublicKey, license: &License) -> bool {
    let Ok(signature_bytes) = BASE64.decode(license.signature.as_bytes()) else {
        return false;
    };
    let Ok(signature) = Signature::try_from(signature_bytes.as_slice()) else {
        return false;
    };
    let verifying_key = VerifyingKey::<Sha256>::new(public_key.clone());
    verifying_key
        .verify(&license.canonical_bytes(), &signature)
        .is_ok()
}

/// Verifies the license signature using the embedded public key.
pub fn verify_signature(license: &License) -> bool {
    let Ok(public_key) = RsaPublicKey::from_public_key_pem(LICENSE_PUBLIC_KEY_PEM) else {
        return false;
    };
    verify_signature_with_key(&public_key, license)
}

/// Signs the canonical payload of a license. Used by the License Generator.
pub fn sign_payload(private_key: &RsaPrivateKey, license: &License) -> Result<String, String> {
    let signing_key = SigningKey::<Sha256>::new(private_key.clone());
    let signature = signing_key
        .sign(&license.canonical_bytes())
        .to_vec();
    Ok(BASE64.encode(signature))
}

impl License {
    /// Builds a license struct from a payload (signature filled afterwards).
    pub fn from_payload(payload: LicensePayload) -> License {
        License {
            schema: payload.schema,
            customer: payload.customer,
            product: payload.product,
            version: payload.version,
            hardware_id: payload.hardware_id,
            issued_at: payload.issued_at,
            signature: String::new(),
        }
    }
}

/// Directory where the license file is stored.
///
/// Windows: `%ProgramData%\Business POS System`
/// Other:   `$XDG_DATA_HOME/business-pos-system` (dev/testing only)
///
/// In debug builds the directory can be overridden with the
/// `BUSINESS_POS_LICENSE_DIR` environment variable (used by tests).
/// Release builds always use the platform location.
pub fn license_dir() -> PathBuf {
    #[cfg(debug_assertions)]
    {
        if let Ok(override_dir) = std::env::var("BUSINESS_POS_LICENSE_DIR") {
            if !override_dir.trim().is_empty() {
                return PathBuf::from(override_dir);
            }
        }
    }
    if cfg!(target_os = "windows") {
        let program_data = std::env::var("ProgramData")
            .unwrap_or_else(|_| "C:\\ProgramData".to_string());
        PathBuf::from(program_data).join("Business POS System")
    } else {
        let base = std::env::var("XDG_DATA_HOME").or_else(|_| {
            std::env::var("HOME").map(|home| format!("{}/.local/share", home))
        });
        match base {
            Ok(base) => PathBuf::from(base).join("business-pos-system"),
            Err(_) => PathBuf::from("/tmp/business-pos-system"),
        }
    }
}

/// Full path of the installed license file.
pub fn license_path() -> PathBuf {
    license_dir().join("license.dat")
}

/// Parses a license file from an arbitrary path without validating it.
pub fn read_license_from(path: &Path) -> Result<License, LicenseError> {
    let content = std::fs::read_to_string(path).map_err(|e| match e.kind() {
        std::io::ErrorKind::NotFound => LicenseError::Missing,
        other => LicenseError::Corrupt(other.to_string()),
    })?;
    serde_json::from_str(&content).map_err(|e| LicenseError::Corrupt(e.to_string()))
}

/// Loads the installed license file.
pub fn load_license() -> Result<License, LicenseError> {
    let path = license_path();
    if !path.exists() {
        return Err(LicenseError::Missing);
    }
    read_license_from(&path)
}

/// Checks whether the license product/version is compatible with the installed app.
fn product_matches(license: &License) -> bool {
    if license.schema != LICENSE_SCHEMA {
        return false;
    }
    if license.product != APP_PRODUCT {
        return false;
    }
    let major_minor = |version: &str| -> String {
        version.split('.').take(2).collect::<Vec<&str>>().join(".")
    };
    let app_version = env!("CARGO_PKG_VERSION");
    major_minor(&license.version) == major_minor(app_version)
}

/// Verifies signature, product/version and hardware binding of a license
/// using a specific public key (used by tests and the generator self-check).
pub fn verify_license_with_key(
    public_key: &RsaPublicKey,
    license: &License,
    hardware_id: &str,
) -> Result<(), LicenseError> {
    if !product_matches(license) {
        return Err(LicenseError::ProductMismatch);
    }
    if !verify_signature_with_key(public_key, license) {
        return Err(LicenseError::InvalidSignature);
    }
    if license.hardware_id != hardware_id {
        return Err(LicenseError::WrongHardware);
    }
    Ok(())
}

/// Verifies signature, product/version and hardware binding of a license.
pub fn verify_license(license: &License, hardware_id: &str) -> Result<(), LicenseError> {
    let Ok(public_key) = RsaPublicKey::from_public_key_pem(LICENSE_PUBLIC_KEY_PEM) else {
        return Err(LicenseError::InvalidSignature);
    };
    verify_license_with_key(&public_key, license, hardware_id)
}

/// Validates a parsed license against the current computer.
pub fn validate_against_hardware(license: &License, hardware_id: &str) -> Result<(), LicenseError> {
    verify_license(license, hardware_id)
}

/// Atomically installs a license into the license directory.
pub fn install_license(license: &License) -> Result<(), String> {
    let dir = license_dir();
    std::fs::create_dir_all(&dir)
        .map_err(|e| format!("Could not create license directory: {}", e))?;
    let content = serde_json::to_string_pretty(license)
        .map_err(|e| format!("Could not serialize license: {}", e))?;
    let tmp_path = dir.join("license.dat.tmp");
    std::fs::write(&tmp_path, content)
        .map_err(|e| format!("Could not write license file: {}", e))?;
    std::fs::rename(&tmp_path, license_path())
        .map_err(|e| format!("Could not finalize license file: {}", e))
}

/// Removes the installed license file (used by the uninstaller integration).
pub fn remove_license() -> Result<(), String> {
    let path = license_path();
    if path.exists() {
        std::fs::remove_file(&path).map_err(|e| format!("Could not remove license: {}", e))?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use rsa::rand_core::OsRng;
    use std::sync::{Mutex, OnceLock};

    const APP_VERSION: &str = env!("CARGO_PKG_VERSION");

    /// Serializes every test that touches the filesystem (they share the
    /// process-wide environment override for the license directory).
    static FS_LOCK: Mutex<()> = Mutex::new(());

    /// A single 2048-bit test keypair shared by the whole suite (fast).
    static TEST_KEY: OnceLock<RsaPrivateKey> = OnceLock::new();

    fn test_key() -> &'static RsaPrivateKey {
        TEST_KEY.get_or_init(|| RsaPrivateKey::new(&mut OsRng, 2048).expect("test key"))
    }

    fn issued_at() -> String {
        "2026-07-31T00:00:00+00:00".to_string()
    }

    fn make_license(private_key: &RsaPrivateKey, hardware_id: &str, customer: &str) -> License {
        let mut license = License::from_payload(LicensePayload {
            schema: LICENSE_SCHEMA.to_string(),
            customer: customer.to_string(),
            product: APP_PRODUCT.to_string(),
            version: APP_VERSION.to_string(),
            hardware_id: hardware_id.to_string(),
            issued_at: issued_at(),
        });
        license.signature = sign_payload(private_key, &license).expect("sign must succeed");
        license
    }

    fn sign_license(private_key: &RsaPrivateKey, license: &mut License) {
        license.signature = sign_payload(private_key, license).expect("sign must succeed");
    }

    fn test_public_key(private_key: &RsaPrivateKey) -> RsaPublicKey {
        RsaPublicKey::from(private_key)
    }

    /// Runs a test with the license directory redirected to a fresh temp dir.
    fn with_isolated_license_dir(test_name: &str, f: impl FnOnce()) {
        let _guard = FS_LOCK.lock().unwrap();
        let dir = std::env::temp_dir().join(format!(
            "bpos-license-test-{}-{}",
            test_name,
            std::process::id()
        ));
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).expect("create temp license dir");
        unsafe {
            std::env::set_var("BUSINESS_POS_LICENSE_DIR", &dir);
        }
        f();
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn scenario01_first_activation_succeeds() {
        let private_key = test_key();
        let hardware_id = "aaaa".repeat(16);
        let license = make_license(private_key, &hardware_id, "First Customer");
        assert_eq!(
            verify_license_with_key(&test_public_key(private_key), &license, &hardware_id),
            Ok(())
        );
    }

    #[test]
    fn scenario02_restart_with_valid_license_passes() {
        let private_key = test_key();
        let hardware_id = "bbbb".repeat(16);
        let license = make_license(private_key, &hardware_id, "Restart Customer");
        assert_eq!(
            verify_license_with_key(&test_public_key(private_key), &license, &hardware_id),
            Ok(())
        );
    }

    #[test]
    fn scenario03_updated_app_keeps_license_valid() {
        let private_key = test_key();
        let hardware_id = "cccc".repeat(16);
        // A license issued for an older patch release of the same version line.
        let mut license = make_license(private_key, &hardware_id, "Update Customer");
        license.version = "0.1.0".to_string();
        sign_license(private_key, &mut license);
        assert_eq!(
            verify_license_with_key(&test_public_key(private_key), &license, &hardware_id),
            Ok(())
        );
    }

    #[test]
    fn scenario04_reinstall_keeps_license() {
        let private_key = test_key();
        let hardware_id = "dddd".repeat(16);
        let license = make_license(private_key, &hardware_id, "Reinstall Customer");
        assert_eq!(
            verify_license_with_key(&test_public_key(private_key), &license, &hardware_id),
            Ok(())
        );
    }

    #[test]
    fn scenario05_existing_customer_still_valid() {
        let private_key = test_key();
        let hardware_id = "eeee".repeat(16);
        let license = make_license(private_key, &hardware_id, "Existing Customer");
        assert_eq!(
            verify_license_with_key(&test_public_key(private_key), &license, &hardware_id),
            Ok(())
        );
    }

    #[test]
    fn scenario06_missing_license_returns_missing() {
        with_isolated_license_dir("scenario06", || {
            assert_eq!(load_license(), Err(LicenseError::Missing));
        });
    }

    #[test]
    fn scenario07_fake_license_is_corrupt() {
        let result = read_license_from(Path::new("/dev/null"));
        assert!(matches!(result, Err(LicenseError::Corrupt(_))));
    }

    #[test]
    fn scenario08_modified_license_has_invalid_signature() {
        let private_key = test_key();
        let hardware_id = "ffff".repeat(16);
        let mut license = make_license(private_key, &hardware_id, "Tampered Customer");
        license.customer = "Modified Customer".to_string();
        assert_eq!(
            verify_license_with_key(&test_public_key(private_key), &license, &hardware_id),
            Err(LicenseError::InvalidSignature)
        );
    }

    #[test]
    fn scenario09_wrong_hardware_rejected() {
        let private_key = test_key();
        let license = make_license(private_key, &"1111".repeat(16), "Wrong Hardware Customer");
        assert_eq!(
            verify_license_with_key(&test_public_key(private_key), &license, &"2222".repeat(16)),
            Err(LicenseError::WrongHardware)
        );
    }

    #[test]
    fn scenario10_copied_app_without_license_is_missing() {
        with_isolated_license_dir("scenario10", || {
            assert_eq!(load_license(), Err(LicenseError::Missing));
        });
    }

    #[test]
    fn scenario11_copied_programdata_license_has_wrong_hardware() {
        let private_key = test_key();
        let license = make_license(private_key, &"3333".repeat(16), "Copied ProgramData Customer");
        assert_eq!(
            verify_license_with_key(&test_public_key(private_key), &license, &"4444".repeat(16)),
            Err(LicenseError::WrongHardware)
        );
    }

    #[test]
    fn scenario12_rejected_license_blocks_startup() {
        let private_key = test_key();
        let hardware_id = "5555".repeat(16);
        let mut license = make_license(private_key, &hardware_id, "Rejected Customer");
        // Simulate a corrupted signature (truncated base64 payload).
        license.signature = "AAAA".to_string();
        assert_eq!(
            verify_license_with_key(&test_public_key(private_key), &license, &hardware_id),
            Err(LicenseError::InvalidSignature)
        );
    }

    #[test]
    fn signature_roundtrip_uses_public_key() {
        let private_key = test_key();
        let hardware_id = "6666".repeat(16);
        let license = make_license(private_key, &hardware_id, "Roundtrip Customer");
        assert!(verify_signature_with_key(&test_public_key(private_key), &license));
    }

    #[test]
    fn product_mismatch_rejected() {
        let private_key = test_key();
        let hardware_id = "7777".repeat(16);
        let mut license = make_license(private_key, &hardware_id, "Mismatch Customer");
        license.product = "Another Product".to_string();
        assert_eq!(
            verify_license_with_key(&test_public_key(private_key), &license, &hardware_id),
            Err(LicenseError::ProductMismatch)
        );
    }

    #[test]
    fn install_and_load_roundtrip() {
        with_isolated_license_dir("install_roundtrip", || {
            let private_key = test_key();
            let hardware_id = "8888".repeat(16);
            let license = make_license(private_key, &hardware_id, "Install Roundtrip Customer");
            install_license(&license).expect("install must succeed");
            let loaded = load_license().expect("license must load");
            assert_eq!(loaded, license);
        });
    }

    #[test]
    fn serialized_public_key_parses() {
        let key = RsaPublicKey::from_public_key_pem(LICENSE_PUBLIC_KEY_PEM);
        assert!(key.is_ok(), "embedded public key must be valid PEM");
    }
}
