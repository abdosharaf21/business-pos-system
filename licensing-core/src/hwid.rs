use sha2::{Digest, Sha256};

/// Collects the machine identifiers used to build the hardware hash.
///
/// The raw identifiers (Machine GUID, motherboard UUID, CPU ID) are never
/// logged, never returned to the frontend and never persisted. Only the final
/// SHA-256 hash derived from them is exposed to the rest of the application.
#[cfg(target_os = "windows")]
fn raw_identifiers() -> Vec<String> {
    windows::raw_identifiers()
}

#[cfg(not(target_os = "windows"))]
fn raw_identifiers() -> Vec<String> {
    unix::raw_identifiers()
}

/// Computes the hardware ID of the current computer.
///
/// The hardware ID is the lowercase hex SHA-256 digest of the combined machine
/// identifiers, joined with the `|` separator:
///
/// `MachineGuid|MotherboardUUID|CPUId`
///
/// Returns `Err` only when no identifier at all could be collected.
pub fn get_hardware_id() -> Result<String, String> {
    let parts = raw_identifiers();
    if parts.is_empty() {
        return Err("Could not collect any hardware identifier".to_string());
    }

    let mut hasher = Sha256::new();
    for (index, part) in parts.iter().enumerate() {
        if index > 0 {
            hasher.update(b"|");
        }
        hasher.update(part.as_bytes());
    }

    Ok(format!("{:x}", hasher.finalize()))
}

#[cfg(target_os = "windows")]
mod windows {
    use serde::Deserialize;
    use winreg::enums::HKEY_LOCAL_MACHINE;
    use winreg::RegKey;
    use wmi::{COMLibrary, WMIConnection};

    const MACHINE_GUID_KEY: &str = r"SOFTWARE\Microsoft\Cryptography";
    const MACHINE_GUID_VALUE: &str = "MachineGuid";

    /// Reads `HKLM\SOFTWARE\Microsoft\Cryptography\MachineGuid`.
    fn machine_guid() -> Option<String> {
        let hklm = RegKey::predef(HKEY_LOCAL_MACHINE);
        let cryptography = hklm.open_subkey(MACHINE_GUID_KEY).ok()?;
        cryptography
            .get_value::<String, _>(MACHINE_GUID_VALUE)
            .ok()
            .filter(|value| !value.trim().is_empty())
    }

    /// Reads the motherboard UUID from `Win32_ComputerSystemProduct`.
    ///
    /// The struct must be named after the WMI class so the wmi crate can build
    /// the corresponding query.
    #[derive(Deserialize)]
    struct Win32_ComputerSystemProduct {
        #[serde(rename = "UUID")]
        uuid: Option<String>,
    }

    fn motherboard_uuid() -> Option<String> {
        let com_library = COMLibrary::new().ok()?;
        let connection = WMIConnection::new(com_library).ok()?;
        let products: Vec<Win32_ComputerSystemProduct> = connection.query().ok()?;
        products
            .into_iter()
            .find_map(|product| product.uuid.filter(|value| !value.trim().is_empty()))
    }

    /// Reads the CPU identifier from `Win32_Processor`.
    #[derive(Deserialize)]
    struct Win32_Processor {
        #[serde(rename = "ProcessorId")]
        processor_id: Option<String>,
    }

    fn cpu_id() -> Option<String> {
        let com_library = COMLibrary::new().ok()?;
        let connection = WMIConnection::new(com_library).ok()?;
        let processors: Vec<Win32_Processor> = connection.query().ok()?;
        processors
            .into_iter()
            .find_map(|processor| {
                processor
                    .processor_id
                    .filter(|value| !value.trim().is_empty())
            })
    }

    /// Collects the three Windows machine identifiers.
    pub fn raw_identifiers() -> Vec<String> {
        let mut parts = Vec::new();
        if let Some(value) = machine_guid() {
            parts.push(value);
        }
        if let Some(value) = motherboard_uuid() {
            parts.push(value);
        }
        if let Some(value) = cpu_id() {
            parts.push(value);
        }
        parts
    }
}

#[cfg(not(target_os = "windows"))]
mod unix {
    use std::fs;

    /// Reads a file, trimming trailing whitespace.
    fn read_trimmed(path: &str) -> Option<String> {
        fs::read_to_string(path)
            .ok()
            .map(|content| content.trim().to_string())
            .filter(|content| !content.is_empty())
    }

    /// Linux machine id used for the development/testing fallback.
    fn machine_guid() -> Option<String> {
        read_trimmed("/etc/machine-id")
            .or_else(|| read_trimmed("/var/lib/dbus/machine-id"))
    }

    /// Motherboard product UUID exposed by the DMI/SMBIOS interface.
    fn motherboard_uuid() -> Option<String> {
        read_trimmed("/sys/class/dmi/id/product_uuid")
    }

    /// First CPU hardware id reported by the kernel.
    fn cpu_id() -> Option<String> {
        let cpuinfo = fs::read_to_string("/proc/cpuinfo").ok()?;
        for line in cpuinfo.lines() {
            if let Some(rest) = line.strip_prefix("cpu id") {
                return Some(rest.trim_start_matches(':').trim().to_string());
            }
        }
        None
    }

    /// Collects the three Linux machine identifiers for development/testing.
    pub fn raw_identifiers() -> Vec<String> {
        let mut parts = Vec::new();
        if let Some(value) = machine_guid() {
            parts.push(value);
        }
        if let Some(value) = motherboard_uuid() {
            parts.push(value);
        }
        if let Some(value) = cpu_id() {
            parts.push(value);
        }
        parts
    }
}

#[cfg(test)]
mod tests {
    use super::get_hardware_id;

    #[test]
    fn hardware_id_is_a_sha256_hex_digest() {
        let hardware_id = get_hardware_id().expect("hardware id must be computable");
        assert_eq!(hardware_id.len(), 64);
        assert!(hardware_id.chars().all(|c| c.is_ascii_hexdigit()));
    }

    #[test]
    fn hardware_id_is_deterministic() {
        let first = get_hardware_id().expect("hardware id must be computable");
        let second = get_hardware_id().expect("hardware id must be computable");
        assert_eq!(first, second);
    }
}
