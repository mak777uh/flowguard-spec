//! Canonical JSON and the address.
//!
//! The rules are the ones a rebuilder had to guess and nobody should have to guess again:
//! recursive code-point key order, `,`/`:` separators, no trailing newline, UTF-8 without \u escapes.

use serde_json::Value;
use sha2::{Digest, Sha256};

pub fn sha256_hex(bytes: &[u8]) -> String {
    let mut h = Sha256::new();
    h.update(bytes);
    format!("{:x}", h.finalize())
}

fn escape(s: &str) -> String {
    let mut out = String::with_capacity(s.len() + 2);
    out.push('"');
    for ch in s.chars() {
        match ch {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            '\u{08}' => out.push_str("\\b"),
            '\u{0c}' => out.push_str("\\f"),
            c if (c as u32) < 0x20 => out.push_str(&format!("\\u{:04x}", c as u32)),
            c => out.push(c),
        }
    }
    out.push('"');
    out
}

/// ECMAScript `Number::toString` — the rule RFC 8785 §3.2.2.3 points at (ADR-0018).
///
/// Python and Rust both print a shortest round-trip mantissa, but lay it out differently: Rust never uses an
/// exponent in `Display` and writes `0.0` where the rule wants `0`. `{:e}` gives the shortest mantissa and a
/// decimal exponent, and the layout is then decided once, here.
fn es_number(f: f64) -> Option<String> {
    if !f.is_finite() {
        return None;
    }
    if f == 0.0 {
        return Some("0".to_string());
    }
    let negative = f < 0.0;
    let text = format!("{:e}", f.abs());
    let (mantissa, exp) = text.split_once('e')?;
    let exp10: i32 = exp.parse().ok()?;
    let digits: String = mantissa.chars().filter(|c| *c != '.').collect();
    let digits = digits.trim_end_matches('0').to_string();
    let digits = if digits.is_empty() { "0".to_string() } else { digits };

    let n = digits.len() as i32;
    let k = exp10 + 1; // position of the decimal point relative to the digits

    let body = if k >= n && k <= 21 {
        format!("{}{}", digits, "0".repeat((k - n) as usize))
    } else if k > 0 && k <= 21 {
        format!("{}.{}", &digits[..k as usize], &digits[k as usize..])
    } else if k > -6 && k <= 0 {
        format!("0.{}{}", "0".repeat((-k) as usize), digits)
    } else {
        let (head, tail) = digits.split_at(1);
        let fraction = if tail.is_empty() { String::new() } else { format!(".{}", tail) };
        let e = k - 1;
        format!("{}{}e{}{}", head, fraction, if e >= 0 { "+" } else { "-" }, e.abs())
    };
    Some(if negative { format!("-{}", body) } else { body })
}

/// Canonicalise a JSON value. Keys are sorted by Unicode code point at every level.
pub fn canonical(v: &Value) -> Result<String, String> {
    let mut out = String::new();
    write_value(v, &mut out)?;
    Ok(out)
}

fn write_value(v: &Value, out: &mut String) -> Result<(), String> {
    match v {
        Value::Null => out.push_str("null"),
        Value::Bool(b) => out.push_str(if *b { "true" } else { "false" }),
        Value::Number(n) => {
            if n.is_f64() {
                let f = n.as_f64().unwrap();
                match es_number(f) {
                    Some(s) => out.push_str(&s),
                    None => return Err("non-finite number in a document that must be canonical".into()),
                }
            } else {
                out.push_str(&n.to_string());
            }
        }
        Value::String(s) => out.push_str(&escape(s)),
        Value::Array(a) => {
            out.push('[');
            for (i, item) in a.iter().enumerate() {
                if i > 0 {
                    out.push(',');
                }
                write_value(item, out)?;
            }
            out.push(']');
        }
        Value::Object(map) => {
            let mut keys: Vec<&String> = map.keys().collect();
            keys.sort(); // String ordering is code-point ordering
            out.push('{');
            for (i, k) in keys.iter().enumerate() {
                if i > 0 {
                    out.push(',');
                }
                out.push_str(&escape(k));
                out.push(':');
                write_value(&map[*k], out)?;
            }
            out.push('}');
        }
    }
    Ok(())
}

pub fn address_of(bundle: &Value) -> Result<String, String> {
    Ok(sha256_hex(canonical(bundle)?.as_bytes()))
}


#[cfg(test)]
mod tests {
    use super::canonical;
    use serde_json::json;

    /// The published number cases, the same file the Python side asserts (ADR-0018). Two implementations
    /// that pass the same table cannot disagree about a float without one of them failing here.
    #[test]
    fn rfc8785_number_vectors() {
        let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("../lab/vectors/rfc8785-numbers.json");
        let text = std::fs::read_to_string(&path).expect("the published vectors must be readable");
        let doc: serde_json::Value = serde_json::from_str(&text).unwrap();
        for case in doc["vectors"].as_array().unwrap() {
            let input = case["input"].as_str().unwrap();
            let expected = case["expected"].as_str().unwrap();
            let value: serde_json::Value = serde_json::from_str(input).unwrap();
            let got = canonical(&json!({ "n": value })).unwrap();
            assert_eq!(got, format!("{{\"n\":{}}}", expected), "case {input}");
        }
    }
}
