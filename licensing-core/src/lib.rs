//! Shared offline licensing logic for the Business POS System.
//!
//! This crate is used by both the desktop application (to verify licenses at
//! startup) and the License Generator (to create signed licenses). Because both
//! sides share the exact same payload, signature and key formats, a license
//! produced by the generator is guaranteed to verify in the application.

pub mod hwid;
pub mod license;

pub use license::{
    install_license, license_dir, license_path, load_license, read_license_from,
    validate_against_hardware, verify_license, License, LicenseError, APP_PRODUCT,
    LICENSE_SCHEMA,
};
