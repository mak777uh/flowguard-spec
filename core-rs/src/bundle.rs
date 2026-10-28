//! Address and role-bound signatures (ADR-0016, fg-bundle/2), plus the v1 forms for older artifacts.
//!
//!   address     = sha256( canonical(bundle.json) )
//!   role_digest = sha256( canonical(role document) )                     every term, scope included
//!   payload_v2  = sha256( "fg-bundle/2|" + address + "|" + role_digest + "|" + scope )  as 64 ASCII hex
//!   signature   = Ed25519(payload_v2)
//!
//!   payload_v1  = address + "\nrole:" + digest(role document WITHOUT accepted_scope)
//!   payload_v1a = address                    (the weakest form: provenance only)

use crate::canonical::{canonical, sha256_hex};
use base64::Engine;
use ed25519_dalek::{Signature, Verifier, VerifyingKey};
use serde_json::Value;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Binding {
    V2,
    V1Role,
    V1Address,
}

impl Binding {
    pub fn as_str(self) -> &'static str {
        match self {
            Binding::V2 => "v2",
            Binding::V1Role => "v1-role",
            Binding::V1Address => "v1-address",
        }
    }
}

pub fn role_digest(role: &Value) -> Result<String, String> {
    Ok(sha256_hex(canonical(role)?.as_bytes()))
}

pub fn payload_v2(address: &str, role: &Value) -> Result<String, String> {
    let scope = role
        .get("accepted_scope")
        .and_then(|v| v.as_str())
        .unwrap_or("");
    Ok(sha256_hex(
        format!("fg-bundle/2|{address}|{}|{scope}", role_digest(role)?).as_bytes(),
    ))
}

pub fn payload_v1_role(address: &str, role: &Value) -> Result<String, String> {
    let mut bounded = role.clone();
    if let Value::Object(map) = &mut bounded {
        map.remove("accepted_scope");
    }
    Ok(format!(
        "{address}\nrole:{}",
        sha256_hex(canonical(&bounded)?.as_bytes())
    ))
}

/// Ed25519 public key from a PEM SubjectPublicKeyInfo: the last 32 bytes of the DER are the raw key.
/// Parsed here rather than through a PEM crate so the core has no dependency it does not use elsewhere.
pub fn public_key_from_pem(pem: &str) -> Result<VerifyingKey, String> {
    let body: String = pem
        .lines()
        .filter(|l| !l.starts_with("-----"))
        .collect::<Vec<_>>()
        .join("");
    let der = base64::engine::general_purpose::STANDARD
        .decode(body.trim())
        .map_err(|e| format!("public key is not base64: {e}"))?;
    if der.len() < 32 {
        return Err("public key is too short to be an Ed25519 SubjectPublicKeyInfo".into());
    }
    let raw: [u8; 32] = der[der.len() - 32..]
        .try_into()
        .map_err(|_| "public key is not 32 bytes".to_string())?;
    VerifyingKey::from_bytes(&raw).map_err(|e| format!("not an Ed25519 public key: {e}"))
}

pub fn signature_from_base64(raw: &str) -> Result<Signature, String> {
    let bytes = base64::engine::general_purpose::STANDARD
        .decode(raw.trim())
        .map_err(|e| format!("signature is not base64: {e}"))?;
    Signature::from_slice(&bytes).map_err(|e| format!("signature is not 64 bytes: {e}"))
}

pub fn verify_binding(
    address: &str,
    key: &VerifyingKey,
    sig: &Signature,
    role: Option<&Value>,
) -> Option<Binding> {
    if let Some(role) = role {
        if let Ok(msg) = payload_v2(address, role) {
            if key.verify(msg.as_bytes(), sig).is_ok() {
                return Some(Binding::V2);
            }
        }
        if let Ok(msg) = payload_v1_role(address, role) {
            if key.verify(msg.as_bytes(), sig).is_ok() {
                return Some(Binding::V1Role);
            }
        }
    }
    if key.verify(address.as_bytes(), sig).is_ok() {
        return Some(Binding::V1Address);
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn scope_is_inside_the_v2_role_digest() {
        let a = json!({"asserts": "risk_acceptance", "issuer": "x", "accepted_scope": "aa"});
        let b = json!({"asserts": "risk_acceptance", "issuer": "x", "accepted_scope": "bb"});
        assert_ne!(role_digest(&a).unwrap(), role_digest(&b).unwrap());
    }

    #[test]
    fn the_v1_message_excludes_the_scope() {
        let a = json!({"asserts": "risk_acceptance", "issuer": "x", "accepted_scope": "aa"});
        let b = json!({"asserts": "risk_acceptance", "issuer": "x", "accepted_scope": "bb"});
        assert_eq!(
            payload_v1_role("addr", &a).unwrap(),
            payload_v1_role("addr", &b).unwrap(),
            "v1 could not see the scope, which is why it was replaced"
        );
    }
}
