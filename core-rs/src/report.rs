//! One self-contained HTML page for a bundle, in Rust (ADR-0017: the product's checkable surface is Rust).
//!
//! The page is deliberately plain: no script, no external link, no build. It must be readable by a stranger
//! offline, and re-generating it from the same bundle must give the same bytes. Parity with the Python generator
//! (`tools/fg_report_html.py`) is checked by `lab/e-m83-run.py`, because two generators that disagree are two
//! answers to "what does this bundle say".

use crate::bundle::{public_key_from_pem, signature_from_base64, verify_binding};
use crate::canonical::address_of;
use crate::claim::{verify_claim, Verdict};
use serde_json::{json, Value};
use std::fs;
use std::path::Path;

pub const CSS: &str = "\
:root { color-scheme: light dark; --fg:#111; --bg:#fff; --mute:#555; --line:#ddd; --ok:#0a7; --bad:#b00; }
@media (prefers-color-scheme: dark) { :root { --fg:#eee; --bg:#111; --mute:#aaa; --line:#333; } }
body { font: 15px/1.5 -apple-system, Segoe UI, Roboto, sans-serif; margin: 2rem auto; max-width: 60rem;
       padding: 0 1rem; color: var(--fg); background: var(--bg); }
h1 { font-size: 1.4rem; margin-bottom: .2rem; }
h2 { font-size: 1.05rem; margin-top: 2rem; border-bottom: 1px solid var(--line); padding-bottom: .2rem; }
.mono { font-family: ui-monospace, Consolas, monospace; font-size: .9em; }
.mute { color: var(--mute); }
table { border-collapse: collapse; width: 100%; margin: .6rem 0; }
th, td { text-align: left; padding: .3rem .5rem; border-bottom: 1px solid var(--line); vertical-align: top; }
.ok { color: var(--ok); font-weight: 600; }
.bad { color: var(--bad); font-weight: 600; }
code { background: rgba(127,127,127,.15); padding: 0 .25em; border-radius: 3px; }
";

fn esc(s: &str) -> String {
    s.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
}

pub struct ReportInputs {
    pub bundle: Value,
    pub claim: Option<Value>,
    pub inventory: Option<Value>,
    pub address: String,
    pub verdict: String,
    pub errors: Vec<Value>,
    pub binding: Vec<(String, String)>,
}

pub fn read_bundle(dir: &Path) -> Result<ReportInputs, String> {
    let bundle_path = dir.join("bundle.json");
    let bundle: Value = serde_json::from_str(
        &fs::read_to_string(&bundle_path).map_err(|e| format!("cannot read bundle.json: {e}"))?,
    )
    .map_err(|e| format!("bundle.json is not JSON: {e}"))?;

    let addr_path = dir.join("manifest.sha256");
    let address = fs::read_to_string(&addr_path)
        .map(|s| s.trim().to_string())
        .unwrap_or_default();
    let recomputed = address_of(&bundle).unwrap_or_default();

    // objects -> claim and inventory
    let mut claim = None;
    let mut inventory = None;
    if let Some(objs) = bundle.get("objects").and_then(|v| v.as_object()) {
        for digest in objs.keys() {
            let p = dir.join("objects").join(digest);
            if let Ok(text) = fs::read_to_string(&p) {
                if let Ok(doc) = serde_json::from_str::<Value>(&text) {
                    if doc.get("declared_level").is_some() {
                        claim = Some(doc);
                    } else if doc.get("paths").is_some() {
                        inventory = Some(doc);
                    }
                }
            }
        }
    }

    // signatures: which form each one used
    let mut binding = Vec::new();
    let sig_dir = dir.join("signatures");
    if let Ok(rd) = fs::read_dir(&sig_dir) {
        let mut names: Vec<String> = rd
            .filter_map(|e| e.ok())
            .map(|e| e.file_name().to_string_lossy().to_string())
            .filter(|n| n.ends_with(".sig"))
            .collect();
        names.sort();
        for sig_file in names {
            let signer = sig_file.trim_end_matches(".sig").to_string();
            let pub_pem = fs::read_to_string(sig_dir.join(format!("{signer}.pub"))).ok();
            let role: Option<Value> = fs::read_to_string(sig_dir.join(format!("{signer}.role")))
                .ok()
                .and_then(|t| serde_json::from_str(&t).ok());
            let sig_raw = fs::read_to_string(sig_dir.join(&sig_file)).unwrap_or_default();
            let key = match pub_pem {
                Some(pem) => public_key_from_pem(&pem).ok(),
                None => None,
            };
            if let (Some(key), Ok(sig)) = (key, signature_from_base64(&sig_raw)) {
                if let Some(b) = verify_binding(&address, &key, &sig, role.as_ref()) {
                    binding.push((signer, b.as_str().to_string()));
                }
            }
        }
    }

    // the claim arithmetic, when both halves are present
    let mut errors: Vec<Value> = Vec::new();
    let mut verdict = "SIGNED_AND_CONSISTENT".to_string();
    if let (Some(c), Some(i)) = (claim.as_ref(), inventory.as_ref()) {
        let out = verify_claim(c, i, None);
        verdict = match &out.verdict {
            Verdict::Invalid => "INVALID".to_string(),
            Verdict::Level(l) => l.to_string(),
        };
        for r in &out.refusals {
            errors.push(json!({
                "code": r.code, "subject": r.subject, "expected": r.expected, "observed": r.observed
            }));
        }
    }
    if recomputed != address {
        verdict = "REPORT_BUNDLE_INCONSISTENT".to_string();
        errors.push(json!({"code": "REPORT_BUNDLE_INCONSISTENT", "subject": "manifest.sha256",
                           "expected": format!("{}…", &recomputed[..12.min(recomputed.len())]),
                           "observed": format!("recorded {}…", &address[..12.min(address.len())])}));
    }

    Ok(ReportInputs { bundle, claim, inventory, address, verdict, errors, binding })
}

pub fn render(inp: &ReportInputs) -> String {
    let version = inp.bundle.get("bundle_version").and_then(|v| v.as_str()).unwrap_or("—");
    let paths: Vec<&Value> = inp
        .inventory
        .as_ref()
        .and_then(|i| i.get("paths"))
        .and_then(|v| v.as_array())
        .map(|a| a.iter().collect())
        .unwrap_or_default();
    let attributed = paths
        .iter()
        .filter(|p| p.get("attribution").and_then(|a| a.get("to")).and_then(|v| v.as_str()).is_some())
        .count();
    let coverage = if paths.is_empty() { 0.0 } else { attributed as f64 / paths.len() as f64 };

    let cls = if inp.verdict == "SIGNED_AND_CONSISTENT" { "ok" } else { "bad" };

    let mut rows = String::new();
    for p in &paths {
        let pid = p.get("path_id").and_then(|v| v.as_str()).unwrap_or("");
        let kind = p.get("kind").and_then(|v| v.as_str()).unwrap_or("");
        let entry = p.get("entry").and_then(|v| v.as_str()).unwrap_or("");
        let target = p.get("target").and_then(|v| v.as_str()).unwrap_or("");
        let attr = p
            .get("attribution")
            .and_then(|a| a.get("to"))
            .and_then(|v| v.as_str())
            .unwrap_or("none");
        let cell_cls = if attr == "none" { "bad" } else { "ok" };
        rows.push_str(&format!(
            "<tr><td class='mono'>{}</td><td>{}</td><td class='mono'>{}</td>\
             <td class='mono'>{}</td><td class='{}'>{}</td></tr>",
            esc(pid), esc(kind), esc(entry), esc(target), cell_cls, esc(attr)
        ));
    }
    let paths_html = if rows.is_empty() {
        "<p class='mute'>no paths in this inventory</p>".to_string()
    } else {
        format!(
            "<table><tr><th>path</th><th>kind</th><th>entry</th><th>target</th>\
             <th>attributed to</th></tr>{rows}</table>"
        )
    };

    let claim_html = inp
        .claim
        .as_ref()
        .map(|c| {
            let level = c.get("declared_level").and_then(|v| v.as_str()).unwrap_or("—");
            let cp = c.get("declared_control_point").and_then(|v| v.as_str()).unwrap_or("—");
            let tier = c.get("evidence_tier").map(|v| v.to_string()).unwrap_or("—".into());
            let nc = c
                .get("not_claimed")
                .and_then(|v| v.as_array())
                .map(|a| a.iter().filter_map(|x| x.as_str()).collect::<Vec<_>>().join(", "))
                .unwrap_or_else(|| "—".into());
            format!(
                "<h2>What it claims, and what it refuses to claim</h2><table>\
                 <tr><th>declared level</th><td class='mono'>{}</td></tr>\
                 <tr><th>control point</th><td class='mono'>{}</td></tr>\
                 <tr><th>evidence tier</th><td class='mono'>{}</td></tr>\
                 <tr><th>not claimed</th><td class='mono'>{}</td></tr></table>",
                esc(level), esc(cp), esc(&tier), esc(&nc)
            )
        })
        .unwrap_or_default();

    let err_html = if inp.errors.is_empty() {
        "<p class='ok'>no refusals</p>".to_string()
    } else {
        let mut body = String::from("<table><tr><th>code</th><th>subject</th><th>expected</th>\
                                     <th>observed</th></tr>");
        for e in &inp.errors {
            body.push_str(&format!(
                "<tr><td class='mono'>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>",
                esc(e.get("code").and_then(|v| v.as_str()).unwrap_or("")),
                esc(e.get("subject").and_then(|v| v.as_str()).unwrap_or("")),
                esc(e.get("expected").and_then(|v| v.as_str()).unwrap_or("")),
                esc(e.get("observed").and_then(|v| v.as_str()).unwrap_or(""))
            ));
        }
        body.push_str("</table>");
        body
    };

    let binding = inp
        .binding
        .iter()
        .map(|(k, v)| format!("{k}: {v}"))
        .collect::<Vec<_>>()
        .join(", ");

    format!(
        "<!doctype html>\n<meta charset=\"utf-8\">\n<title>FlowGuard — {verdict}</title>\n\
         <style>{css}</style>\n<h1>FlowGuard report</h1>\n\
         <p class=\"mute mono\">bundle {addr} · format {version} · signatures {binding}</p>\n\
         <p>Verdict: <span class=\"{cls}\">{verdict}</span>\n  \
         <span class=\"mute\">— a statement about this document, not about the system it describes</span></p>\n\
         <h2>The paths, first</h2>\n\
         <p>{n} paths enumerated, <b>{attr}</b> attributed to the declared control point\n   \
         (coverage <span class=\"mono\">{cov:.2}</span>). Every row below is a way the target can be written.</p>\n\
         {paths}\n{claim}\n<h2>Refusals</h2>\n{errors}\n\
         <h2>What this page cannot tell you</h2>\n<ul>\n  \
         <li>Whether the inventory is complete. A path that no enumerator saw is not on this page (<code>NC-01</code>).</li>\n  \
         <li>Whether anything outside the declared scope is safe (<code>NC-02</code>).</li>\n  \
         <li>Whether the parties whose signatures are attached had authority to attach them.</li>\n</ul>\n\
         <p class=\"mute\">Generated by <code>fg-core report</code> from the bundle alone — no network, no build \
         step, no JavaScript. Re-generate it from the same bundle and you must get the same bytes.</p>\n",
        verdict = esc(&inp.verdict),
        css = CSS,
        addr = esc(&inp.address),
        version = esc(version),
        binding = esc(&binding),
        cls = cls,
        n = paths.len(),
        attr = attributed,
        cov = coverage,
        paths = paths_html,
        claim = claim_html,
        errors = err_html,
    )
}
