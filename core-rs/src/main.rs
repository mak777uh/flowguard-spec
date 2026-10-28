//! fg-core — the verifying core (ADR-0017).
//!
//! `fg-core verify --bundle <dir> [--trusted-keys k1 k2]` prints the verdict as JSON and exits 0 only when the
//! artifact is `SIGNED_AND_CONSISTENT`. It consumes a bundle and nothing else: no database, no repository.

mod bundle;
mod canonical;
mod levels;

use serde_json::json;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::ExitCode;

struct Refusal {
    code: &'static str,
    subject: String,
    expected: String,
    observed: String,
}

fn read_json(path: &Path) -> Result<serde_json::Value, String> {
    let text = fs::read_to_string(path).map_err(|e| format!("cannot read {}: {e}", path.display()))?;
    serde_json::from_str(&text).map_err(|e| format!("{} is not JSON: {e}", path.display()))
}

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args.first().map(String::as_str) != Some("verify") {
        eprintln!("usage: fg-core verify --bundle <dir> [--trusted-keys k1 k2]");
        return ExitCode::from(2);
    }
    let mut dir: Option<PathBuf> = None;
    let mut trusted: Vec<PathBuf> = Vec::new();
    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--bundle" => {
                dir = args.get(i + 1).map(PathBuf::from);
                i += 2;
            }
            "--trusted-keys" => {
                i += 1;
                while i < args.len() && !args[i].starts_with("--") {
                    trusted.push(PathBuf::from(&args[i]));
                    i += 1;
                }
            }
            other => {
                eprintln!("unknown argument: {other}");
                return ExitCode::from(2);
            }
        }
    }
    match dir {
        Some(d) => verify(&d, &trusted),
        None => {
            eprintln!("usage: fg-core verify --bundle <dir> [--trusted-keys k1 k2]");
            ExitCode::from(2)
        }
    }
}

fn verify(dir: &Path, trusted: &[PathBuf]) -> ExitCode {
    let mut errors: Vec<Refusal> = Vec::new();
    let mut checked: Vec<&str> = Vec::new();
    let mut bindings = serde_json::Map::new();

    macro_rules! refuse {
        ($code:expr, $subject:expr, $expected:expr, $observed:expr) => {
            errors.push(Refusal {
                code: $code,
                subject: $subject.to_string(),
                expected: $expected.to_string(),
                observed: $observed.to_string(),
            })
        };
    }

    // 1. the manifest: 64 lowercase hex and one LF, 65 bytes
    let addr_path = dir.join("manifest.sha256");
    let raw = match fs::read(&addr_path) {
        Ok(b) => b,
        Err(_) => {
            refuse!("MISSING_EVIDENCE", "manifest.sha256", "the bundle address", "absent");
            return finish(None, None, bindings, errors, checked);
        }
    };
    let recorded = String::from_utf8_lossy(&raw).trim().to_string();
    if raw.len() != 65 || raw[64] != b'\n' {
        refuse!(
            "REPORT_BUNDLE_INCONSISTENT",
            "manifest.sha256",
            "64 hex characters and one LF (65 bytes)",
            format!("{} bytes", raw.len())
        );
    }
    checked.push("manifest shape");

    // 2. the address recomputed in canonical form
    let bundle = match read_json(&dir.join("bundle.json")) {
        Ok(v) => v,
        Err(e) => {
            refuse!("REPORT_BUNDLE_INCONSISTENT", "bundle.json", "a JSON document", e);
            return finish(Some(recorded), None, bindings, errors, checked);
        }
    };
    let recomputed = canonical::address_of(&bundle).ok();
    match &recomputed {
        Some(addr) if *addr != recorded => {
            let short = |s: &str| s.chars().take(12).collect::<String>();
            refuse!(
                "REPORT_BUNDLE_INCONSISTENT",
                "manifest.sha256",
                format!("address {}", short(addr)),
                format!("recorded {}", short(&recorded))
            );
        }
        Some(_) => {}
        None => refuse!(
            "REPORT_BUNDLE_INCONSISTENT",
            "bundle.json",
            "a canonicalisable document",
            "canonicalisation failed"
        ),
    }
    checked.push("address");

    // 3. a version this core knows
    let version = bundle.get("bundle_version").and_then(|v| v.as_str()).unwrap_or("");
    if version != "fg-bundle/1" && version != "fg-bundle/2" {
        refuse!(
            "REPORT_BUNDLE_INCONSISTENT",
            "bundle_version",
            "fg-bundle/1 or fg-bundle/2",
            version
        );
    }
    checked.push("bundle_version");

    // 4. objects, in both directions
    let obj_dir = dir.join("objects");
    let declared: Vec<String> = bundle
        .get("objects")
        .and_then(|v| v.as_object())
        .map(|m| m.keys().cloned().collect())
        .unwrap_or_default();
    let present: Vec<String> = match fs::read_dir(&obj_dir) {
        Ok(rd) => rd
            .filter_map(|e| e.ok())
            .map(|e| e.file_name().to_string_lossy().to_string())
            .filter(|n| !n.starts_with('.'))
            .collect(),
        Err(_) => Vec::new(),
    };
    let short = |s: &str| s.chars().take(12).collect::<String>();
    for name in &present {
        if !declared.contains(name) {
            refuse!(
                "REPORT_BUNDLE_INCONSISTENT",
                format!("object {}…", short(name)),
                "declared in the manifest",
                "present but undeclared"
            );
        }
    }
    for digest in &declared {
        if !present.contains(digest) {
            refuse!(
                "MISSING_EVIDENCE",
                format!("object {}…", short(digest)),
                "present on disk",
                "declared but absent"
            );
        }
    }
    // an object must hash to its own name: presence is not integrity
    for digest in &declared {
        let path = obj_dir.join(digest);
        if let Ok(bytes) = fs::read(&path) {
            let actual = canonical::sha256_hex(&bytes);
            if actual != *digest {
                refuse!(
                    "REPORT_BUNDLE_INCONSISTENT",
                    format!("object {}…", short(digest)),
                    "a file that hashes to its own name",
                    format!("hashes to {}…", short(&actual))
                );
            }
        }
    }
    checked.push("objects");

    // 5. signatures, and which message form each used
    let sig_dir = dir.join("signatures");
    let mut sigs: Vec<String> = match fs::read_dir(&sig_dir) {
        Ok(rd) => rd
            .filter_map(|e| e.ok())
            .map(|e| e.file_name().to_string_lossy().to_string())
            .filter(|n| n.ends_with(".sig"))
            .collect(),
        Err(_) => Vec::new(),
    };
    sigs.sort();
    // a role without a signature is a claim about a party that nobody signed
    if let Ok(rd) = fs::read_dir(&sig_dir) {
        for entry in rd.filter_map(|e| e.ok()) {
            let name = entry.file_name().to_string_lossy().to_string();
            if let Some(signer) = name.strip_suffix(".role") {
                if !sigs.iter().any(|s| s == &format!("{signer}.sig")) {
                    refuse!(
                        "SIGNATURE_ROLE_UNKNOWN",
                        format!("role {signer}"),
                        "a .sig by the party asserting this role",
                        "unsigned role: nobody signed this assertion"
                    );
                }
            }
        }
    }
    if sigs.is_empty() {
        refuse!("MISSING_EVIDENCE", "signatures", "at least one signature", "none");
    }
    let mut role_asserts: Vec<(String, String, String)> = Vec::new();
    for sig_file in &sigs {
        let signer = sig_file.trim_end_matches(".sig").to_string();
        let pub_pem = match fs::read_to_string(sig_dir.join(format!("{signer}.pub"))) {
            Ok(s) => s,
            Err(_) => {
                refuse!(
                    "MISSING_EVIDENCE",
                    format!("signature {signer}"),
                    "a .pub beside the signature",
                    "absent"
                );
                continue;
            }
        };
        if !trusted.is_empty()
            && !trusted.iter().any(|k| {
                fs::read_to_string(k)
                    .map(|t| t.trim() == pub_pem.trim())
                    .unwrap_or(false)
            })
        {
            refuse!(
                "POLICY_UNTRUSTED",
                format!("signature {signer}"),
                "a key from the trusted set",
                "key is not trusted"
            );
            continue;
        }
        let role = fs::read_to_string(sig_dir.join(format!("{signer}.role")))
            .ok()
            .and_then(|t| serde_json::from_str::<serde_json::Value>(&t).ok());
        let sig_raw = match fs::read_to_string(sig_dir.join(sig_file)) {
            Ok(s) => s,
            Err(_) => continue,
        };
        let key = match bundle::public_key_from_pem(&pub_pem) {
            Ok(k) => k,
            Err(e) => {
                refuse!("MISSING_EVIDENCE", format!("signature {signer}"), "a public key", e);
                continue;
            }
        };
        let sig = match bundle::signature_from_base64(&sig_raw) {
            Ok(s) => s,
            Err(e) => {
                refuse!("MISSING_EVIDENCE", format!("signature {signer}"), "a signature", e);
                continue;
            }
        };
        match bundle::verify_binding(&recorded, &key, &sig, role.as_ref()) {
            None => refuse!(
                "MISSING_EVIDENCE",
                format!("signature {signer}"),
                "a valid signature",
                "verification failed"
            ),
            Some(binding) => {
                bindings.insert(signer.clone(), json!(binding.as_str()));
                if let Some(role) = &role {
                    let asserts = role.get("asserts").and_then(|v| v.as_str()).unwrap_or("");
                    role_asserts.push((signer.clone(), asserts.to_string(), pub_pem.clone()));
                    if asserts == "liability_agreement" {
                        refuse!(
                            "LIABILITY_NOT_A_ROLE",
                            format!("role {signer}"),
                            "no liability role",
                            "liability_agreement"
                        );
                    }
                    if asserts == "risk_acceptance" {
                        let scope = role.get("accepted_scope").and_then(|v| v.as_str());
                        if scope != Some(recorded.as_str()) {
                            refuse!(
                                "RISK_ACCEPTANCE_INCOMPLETE",
                                format!("role {signer}"),
                                "accepted_scope equal to the address",
                                scope.unwrap_or("absent")
                            );
                        }
                        for field in ["residual_risk", "valid_until", "statement"] {
                            if role.get(field).is_none() {
                                refuse!(
                                    "RISK_ACCEPTANCE_INCOMPLETE",
                                    format!("role {signer}"),
                                    field,
                                    "absent"
                                );
                            }
                        }
                        if binding == bundle::Binding::V1Address {
                            refuse!(
                                "RISK_ACCEPTANCE_INCOMPLETE",
                                format!("role {signer}"),
                                "a signature covering the role's terms",
                                "bound to the address alone"
                            );
                        }
                    }
                }
            }
        }
    }
    checked.push("signatures and roles");

    // 6. separation of duties, by public-key bytes
    for (v_signer, v_asserts, v_pem) in &role_asserts {
        for (a_signer, a_asserts, a_pem) in &role_asserts {
            if v_asserts == "consistency_verdict"
                && a_asserts == "risk_acceptance"
                && v_pem.trim() == a_pem.trim()
            {
                refuse!(
                    "SEPARATION_OF_DUTIES_VIOLATED",
                    format!("roles {v_signer} and {a_signer}"),
                    "a different key from the verdict holder",
                    "the same public key holds both"
                );
            }
        }
    }
    checked.push("separation of duties");

    finish(Some(recorded), recomputed, bindings, errors, checked)
}

fn finish(
    recorded: Option<String>,
    recomputed: Option<String>,
    bindings: serde_json::Map<String, serde_json::Value>,
    errors: Vec<Refusal>,
    checked: Vec<&str>,
) -> ExitCode {
    let verdict = if errors.is_empty() {
        "SIGNED_AND_CONSISTENT"
    } else {
        "REFUSED"
    };
    let doc = json!({
        "verdict": verdict,
        "address": {
            "recorded": recorded.clone().unwrap_or_default(),
            "recomputed": recomputed.clone().unwrap_or_default(),
            "match": recorded.is_some() && recorded == recomputed,
        },
        "signature_binding": bindings,
        "errors": errors.iter().map(|e| json!({
            "code": e.code, "subject": e.subject, "expected": e.expected, "observed": e.observed
        })).collect::<Vec<_>>(),
        "checked": checked,
    });
    println!("{}", serde_json::to_string_pretty(&doc).unwrap());
    if errors.is_empty() {
        ExitCode::SUCCESS
    } else {
        ExitCode::FAILURE
    }
}
