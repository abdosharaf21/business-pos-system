//! Offline RSA-4096 license generator for the Business POS System.
//!
//! This utility is the ONLY component that holds the private key. It runs on
//! the vendor's Windows machine and is never distributed to customers.
//!
//! Usage:
//!   license-gen --generate-keys [--keys-dir <dir>]
//!   license-gen --customer "<Name>" --hwid <hardware-id> [--out <file>]
//!   license-gen --self-check
//!   license-gen --machine-id

use std::path::PathBuf;
use std::process::ExitCode;

use licensing_core::hwid;
use licensing_core::license::{
    sign_payload, validate_against_hardware, verify_signature, License, LicensePayload,
    APP_PRODUCT, LICENSE_SCHEMA,
};
use rsa::pkcs8::{DecodePrivateKey, EncodePrivateKey, EncodePublicKey};
use rsa::rand_core::OsRng;
use rsa::RsaPrivateKey;

const DEFAULT_PRIVATE_KEY: &str = "private_key.pem";
const DEFAULT_PUBLIC_KEY: &str = "public_key.pem";

struct Options {
    keys_dir: PathBuf,
    customer: Option<String>,
    hwid: Option<String>,
    out: Option<String>,
    version: String,
}

fn exe_dir() -> PathBuf {
    std::env::current_exe()
        .ok()
        .and_then(|exe| exe.parent().map(|p| p.to_path_buf()))
        .unwrap_or_else(|| PathBuf::from("."))
}

fn private_key_path(opts: &Options) -> PathBuf {
    opts.keys_dir.join(DEFAULT_PRIVATE_KEY)
}

fn load_private_key(opts: &Options) -> Result<RsaPrivateKey, String> {
    let path = private_key_path(opts);
    if !path.exists() {
        return Err(format!(
            "Private key not found at {}.\nRun `license-gen --generate-keys` first.",
            path.display()
        ));
    }
    let pem =
        std::fs::read_to_string(&path).map_err(|e| format!("Cannot read key file: {}", e))?;
    RsaPrivateKey::from_pkcs8_pem(&pem).map_err(|e| format!("Invalid private key: {}", e))
}

fn generate_keys(opts: &Options) -> Result<(), String> {
    std::fs::create_dir_all(&opts.keys_dir)
        .map_err(|e| format!("Cannot create keys directory: {}", e))?;

    let mut rng = OsRng;
    eprintln!("[license-gen] Generating RSA-4096 keypair (this can take a few seconds)...");
    let private_key =
        RsaPrivateKey::new(&mut rng, 4096).map_err(|e| format!("Key generation failed: {}", e))?;

    let private_pem = private_key
        .to_pkcs8_pem(rsa::pkcs8::LineEnding::LF)
        .map_err(|e| format!("Cannot encode private key: {}", e))?
        .to_string();
    let public_pem = private_key
        .to_public_key()
        .to_public_key_pem(rsa::pkcs8::LineEnding::LF)
        .map_err(|e| format!("Cannot encode public key: {}", e))?;

    std::fs::write(private_key_path(opts), &private_pem)
        .map_err(|e| format!("Cannot write private key: {}", e))?;
    let public_path = opts.keys_dir.join(DEFAULT_PUBLIC_KEY);
    std::fs::write(&public_path, &public_pem)
        .map_err(|e| format!("Cannot write public key: {}", e))?;

    eprintln!(
        "[license-gen] Keys written to:\n  private: {}\n  public:  {}\n\n\
         IMPORTANT:\n  \
         - Keep private_key.pem ONLY on this machine. Never distribute or commit it.\n  \
         - Embed public_key.pem into the application before building it:\n    \
           copy its content to licensing-core/src/license_public_key.pem\n  \
         - Licenses issued with this key are verified with the embedded public key.",
        private_key_path(opts).display(),
        public_path.display()
    );
    Ok(())
}

fn current_timestamp() -> String {
    use std::time::{SystemTime, UNIX_EPOCH};
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default();
    let secs = now.as_secs();
    let days = secs / 86400;
    let (y, m, d) = civil_from_days(days as i64);
    format!("{:04}-{:02}-{:02}T00:00:00+00:00", y, m, d)
}

fn civil_from_days(days: i64) -> (i64, i64, i64) {
    let z = days + 719_468;
    let era = if z >= 0 { z } else { z - 146_096 } / 146_097;
    let doe = (z - era * 146_097) as i64;
    let yoe = (doe - doe / 1460 + doe / 36524 - doe / 146_096) / 365;
    let y = yoe + era * 400;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = doy - (153 * mp + 2) / 5 + 1;
    let m = if mp < 10 { mp + 3 } else { mp - 9 };
    (if m <= 2 { y + 1 } else { y }, m, d)
}

fn build_license(
    private_key: &RsaPrivateKey,
    customer: &str,
    hardware_id: &str,
    version: &str,
) -> Result<License, String> {
    if customer.trim().is_empty() {
        return Err("Customer name cannot be empty.".to_string());
    }
    if hardware_id.trim().is_empty() {
        return Err("Hardware id cannot be empty.".to_string());
    }
    if hardware_id.len() != 64 || !hardware_id.chars().all(|c| c.is_ascii_hexdigit()) {
        return Err("Hardware id must be a 64-character SHA-256 hex digest.".to_string());
    }

    let mut license = License::from_payload(LicensePayload {
        schema: LICENSE_SCHEMA.to_string(),
        customer: customer.trim().to_string(),
        product: APP_PRODUCT.to_string(),
        version: version.to_string(),
        hardware_id: hardware_id.to_string(),
        issued_at: current_timestamp(),
    });
    license.signature = sign_payload(private_key, &license)?;
    Ok(license)
}

fn issue_license(opts: &Options) -> Result<(), String> {
    let customer = opts.customer.as_deref().ok_or("Missing --customer")?;
    let hardware_id = opts.hwid.as_deref().ok_or("Missing --hwid")?;
    let private_key = load_private_key(opts)?;
    let license = build_license(&private_key, customer, hardware_id, &opts.version)?;

    let out_path = opts
        .out
        .as_ref()
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("license.dat"));
    let content =
        serde_json::to_string_pretty(&license).map_err(|e| format!("Cannot serialize license: {}", e))?;
    std::fs::write(&out_path, content).map_err(|e| format!("Cannot write license: {}", e))?;

    eprintln!(
        "[license-gen] License issued.\n  Customer:    {}\n  Hardware ID: {}\n  Product:     {} v{}\n  Issued:      {}\n  Output:      {}\n\n\
         Hand this file to the customer. It is bound to ONE computer.",
        license.customer,
        license.hardware_id,
        license.product,
        license.version,
        license.issued_at,
        out_path.display()
    );
    Ok(())
}

fn print_machine_id() -> Result<(), String> {
    let hardware_id = hwid::get_hardware_id()?;
    println!("{}", hardware_id);
    Ok(())
}

fn self_check(opts: &Options) -> Result<(), String> {
    let hardware_id = hwid::get_hardware_id()?;
    let private_key = load_private_key(opts)?;
    let license = build_license(
        &private_key,
        "Self Check",
        &hardware_id,
        env!("CARGO_PKG_VERSION"),
    )?;

    if !verify_signature(&license) {
        return Err("Self-check failed: signature verification with embedded public key failed."
            .to_string());
    }
    match validate_against_hardware(&license, &hardware_id) {
        Ok(()) => {
            eprintln!("[license-gen] Self-check OK: license verified against this machine.");
            Ok(())
        }
        Err(e) => Err(format!("Self-check failed: {}", e)),
    }
}

fn usage() {
    eprintln!(
        "Business POS System - License Generator (offline, RSA-4096)\n\n\
         USAGE:\n  \
         license-gen --generate-keys [--keys-dir <dir>]\n    \
         Creates a new RSA-4096 keypair. The private key stays ONLY on this machine.\n  \
         license-gen --customer \"<Name>\" --hwid <hardware-id> [--out <license.dat>]\n    \
         Issues a signed license bound to the given hardware id.\n  \
         license-gen --self-check [--keys-dir <dir>]\n    \
         Generates a license for THIS computer and verifies it in memory.\n  \
         license-gen --machine-id\n    \
         Prints the hardware id of the current computer.\n\n\
         OPTIONS:\n  \
         --keys-dir <dir>   Directory holding private_key.pem (default: next to the executable).\n  \
         --out <file>       Output license file (default: ./license.dat).\n  \
         --version <ver>    Product version encoded in the license (default: 0.1.0).\n"
    );
}

fn main() -> ExitCode {
    let mut keys_dir: Option<PathBuf> = None;
    let mut generate = false;
    let mut self_check_flag = false;
    let mut machine_id = false;
    let mut customer: Option<String> = None;
    let mut hwid_arg: Option<String> = None;
    let mut out: Option<String> = None;
    let mut version = "0.1.0".to_string();

    let args: Vec<String> = std::env::args().skip(1).collect();
    let mut i = 0;
    while i < args.len() {
        match args[i].as_str() {
            "--generate-keys" => generate = true,
            "--self-check" => self_check_flag = true,
            "--machine-id" => machine_id = true,
            "--keys-dir" => {
                i += 1;
                if i >= args.len() {
                    usage();
                    return ExitCode::from(2);
                }
                keys_dir = Some(PathBuf::from(&args[i]));
            }
            "--customer" => {
                i += 1;
                if i >= args.len() {
                    usage();
                    return ExitCode::from(2);
                }
                customer = Some(args[i].clone());
            }
            "--hwid" => {
                i += 1;
                if i >= args.len() {
                    usage();
                    return ExitCode::from(2);
                }
                hwid_arg = Some(args[i].clone());
            }
            "--out" => {
                i += 1;
                if i >= args.len() {
                    usage();
                    return ExitCode::from(2);
                }
                out = Some(args[i].clone());
            }
            "--version" => {
                i += 1;
                if i >= args.len() {
                    usage();
                    return ExitCode::from(2);
                }
                version = args[i].clone();
            }
            "--help" | "-h" => {
                usage();
                return ExitCode::SUCCESS;
            }
            other => {
                eprintln!("[license-gen] Unknown argument: {}", other);
                usage();
                return ExitCode::from(2);
            }
        }
        i += 1;
    }

    let opts = Options {
        keys_dir: keys_dir.unwrap_or_else(exe_dir),
        customer,
        hwid: hwid_arg,
        out,
        version,
    };

    let result = if generate {
        generate_keys(&opts)
    } else if self_check_flag {
        self_check(&opts)
    } else if machine_id {
        print_machine_id()
    } else if opts.customer.is_some() && opts.hwid.is_some() {
        issue_license(&opts)
    } else {
        usage();
        return ExitCode::from(2);
    };

    match result {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) => {
            eprintln!("[license-gen] ERROR: {}", e);
            ExitCode::FAILURE
        }
    }
}
