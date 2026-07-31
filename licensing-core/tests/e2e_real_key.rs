//! End-to-end test using the REAL vendor private key and the embedded public key.
//!
//! This test proves that a license issued by the License Generator is accepted
//! by the application-side verification pipeline. It is skipped when the
//! private key is not available (e.g. on machines that never hold it).

use std::path::PathBuf;
use std::sync::Mutex;

use licensing_core::hwid;
use licensing_core::license::{
    install_license, license_dir, load_license, sign_payload, validate_against_hardware,
    verify_signature, License, LicensePayload, APP_PRODUCT, LICENSE_SCHEMA,
};
use rsa::pkcs8::DecodePrivateKey;
use rsa::RsaPrivateKey;

static FS_LOCK: Mutex<()> = Mutex::new(());

fn private_key_path() -> PathBuf {
    if let Ok(path) = std::env::var("BUSINESS_POS_PRIVATE_KEY") {
        return PathBuf::from(path);
    }
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../licensing-tools/license-gen/keys/private_key.pem")
}

fn load_private_key() -> Option<RsaPrivateKey> {
    let path = private_key_path();
    if !path.exists() {
        return None;
    }
    let pem = std::fs::read_to_string(&path).ok()?;
    RsaPrivateKey::from_pkcs8_pem(&pem).ok()
}

#[test]
fn e2e_real_license_passes_embedded_key_verification() {
    let Some(private_key) = load_private_key() else {
        eprintln!("SKIP: private key not found at {}", private_key_path().display());
        return;
    };

    let hardware_id = hwid::get_hardware_id().expect("hardware id must be computable");
    let mut license = License::from_payload(LicensePayload {
        schema: LICENSE_SCHEMA.to_string(),
        customer: "End To End Customer".to_string(),
        product: APP_PRODUCT.to_string(),
        version: env!("CARGO_PKG_VERSION").to_string(),
        hardware_id: hardware_id.clone(),
        issued_at: "2026-07-31T00:00:00+00:00".to_string(),
    });
    license.signature = sign_payload(&private_key, &license).expect("signing must succeed");

    assert!(
        verify_signature(&license),
        "real signature must verify with the embedded public key"
    );
    assert_eq!(
        validate_against_hardware(&license, &hardware_id),
        Ok(()),
        "validated against the current machine"
    );

    // Install and reload through the exact production code paths.
    let _guard = FS_LOCK.lock().unwrap();
    let temp_dir = std::env::temp_dir().join(format!("bpos-e2e-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&temp_dir);
    std::fs::create_dir_all(&temp_dir).expect("create temp dir");
    unsafe {
        std::env::set_var("BUSINESS_POS_LICENSE_DIR", &temp_dir);
    }
    install_license(&license).expect("install must succeed");
    let loaded = load_license().expect("license must load from the install location");
    assert_eq!(loaded, license, "installed license round-trips byte for byte");
    assert_eq!(
        validate_against_hardware(&loaded, &hardware_id),
        Ok(()),
        "loaded license still validates"
    );
    let _ = std::fs::remove_dir_all(&temp_dir);
    let _ = license_dir();
}
