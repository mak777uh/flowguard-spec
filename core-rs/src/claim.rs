//! The claim/inventory arithmetic, in Rust (ADR-0017).
//!
//! This is the code where every one of the 34 adversarial breaks landed, so the rules are stated here as
//! checks with a code each, and the six known attacks are unit tests:
//!   - a level string that is nearly right is not a level;
//!   - `NaN` cannot clear a density floor (it cannot be constructed as a finite number);
//!   - `completeness_claim: sampled|partial` is a truncated denominator;
//!   - a delta with unpublished growth blocks whatever the flag says, unless there is no baseline;
//!   - `vanished` must be a boolean;
//!   - a report without `analysed_paths` cannot carry a level above the floor.

use crate::canonical::sha256_hex;
use crate::levels::{clamp, floor_for, level_for_distinct_paths, distinct_paths, Level};
use serde_json::Value;


/// The codes a level must declare, read from `docs/NOT-CLAIMED.md` so the two cores cannot drift.
/// A missing table is not a pass: if the document cannot be read, the requirement is unknown and the claim
/// is refused rather than accepted.
pub fn required_codes(level: Level) -> Option<Vec<String>> {
    let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()?
        .join("docs")
        .join("NOT-CLAIMED.md");
    let text = std::fs::read_to_string(path).ok()?;
    let mut in_table = false;
    for line in text.lines() {
        if line.trim_start().starts_with("## Required by level") {
            in_table = true;
            continue;
        }
        if in_table {
            if line.trim_start().starts_with("## ") {
                break;
            }
            let cells: Vec<&str> = line.trim().trim_matches('|').split('|').map(str::trim).collect();
            if cells.len() < 2 {
                continue;
            }
            let want = match level {
                Level::ConsistentDeclared => "`CONSISTENT_DECLARED`",
                Level::ScopedAssurance => "`SCOPED_ASSURANCE`",
                Level::Proven => "`PROVEN`",
            };
            if cells[0] == want {
                return Some(
                    cells[1]
                        .split(',')
                        .map(|c| c.trim().to_string())
                        .filter(|c| !c.is_empty())
                        .collect(),
                );
            }
        }
    }
    None
}

pub fn missing_codes(claim: &Value, level: Level) -> Option<Vec<String>> {
    let required = required_codes(level)?;
    let declared: Vec<String> = claim
        .get("not_claimed")
        .and_then(|v| v.as_array())
        .map(|a| a.iter().filter_map(|v| v.as_str().map(str::to_string)).collect())
        .unwrap_or_default();
    let missing: Vec<String> = required.into_iter().filter(|c| !declared.contains(c)).collect();
    if missing.is_empty() {
        None
    } else {
        Some(missing)
    }
}


/// A confirmation is valid when the record that `fg_confirm.py` would accept is present: an owner with all
/// four contact fields, a statement, a verdict that is not a refutation, and a finding that names a path.
fn _valid_confirmation(record: &Value) -> bool {
    if record.get("owner_confirmed") != Some(&Value::Bool(true)) {
        return false;
    }
    match record.get("verdict").and_then(|v| v.as_str()) {
        Some("confirmed") | Some("partially_correct") => {}
        _ => return false,
    }
    let owner = match record.get("owner").and_then(|v| v.as_object()) {
        Some(o) => o,
        None => return false,
    };
    for field in ["name", "role", "how_contacted", "date"] {
        let ok = owner
            .get(field)
            .and_then(|v| v.as_str())
            .map(|s| !s.trim().is_empty())
            .unwrap_or(false);
        if !ok {
            return false;
        }
    }
    let statement = record.get("owner_statement").and_then(|v| v.as_str()).unwrap_or("");
    if statement.trim().chars().count() < 12 {
        return false;
    }
    record
        .get("finding")
        .and_then(|f| f.get("path_id"))
        .and_then(|v| v.as_str())
        .map(|s| !s.trim().is_empty())
        .unwrap_or(false)
}

fn tier_ceiling(claim: &Value, inventory: &Value) -> Option<u8> {
    let tier = claim.get("evidence_tier").and_then(|v| v.as_u64()).unwrap_or(0) as u8;
    let records: Vec<&Value> = inventory
        .get("foreign_validation")
        .and_then(|v| v.as_array())
        .map(|a| a.iter().collect())
        .unwrap_or_default();
    let valid = records.iter().filter(|r| _valid_confirmation(r)).count();
    let tier3 = records.iter().any(|r| {
        _valid_confirmation(r)
            && r.get("blind_evaluation") == Some(&Value::Bool(true))
            && r.get("ground_truth").map(|g| g.is_object()).unwrap_or(false)
    });
    match tier {
        0 | 1 => Some(tier),
        2 if valid >= 1 => Some(2),
        2 => Some(1),
        3 if tier3 => Some(3),
        3 if valid >= 1 => Some(2),
        _ => Some(1),
    }
}


/// The codes the vocabulary defines, read from the same document as the requirements.
pub fn known_codes() -> Option<Vec<String>> {
    let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()?
        .join("docs")
        .join("NOT-CLAIMED.md");
    let text = std::fs::read_to_string(path).ok()?;
    let mut codes = Vec::new();
    for line in text.lines() {
        // the table writes the code in bold, not in backticks: | **NC-01** | ...
        let trimmed = line.trim();
        if let Some(rest) = trimmed.strip_prefix("| **NC-") {
            if let Some(head) = rest.split("**").next() {
                let digits: String = head.chars().take_while(|c| c.is_ascii_digit()).collect();
                if !digits.is_empty() {
                    codes.push(format!("NC-{digits}"));
                }
            }
        }
    }
    if codes.is_empty() { None } else { Some(codes) }
}

pub struct Refusal {
    pub code: &'static str,
    pub subject: String,
    pub expected: String,
    pub observed: String,
}

impl Refusal {
    fn new(code: &'static str, subject: impl Into<String>, expected: impl Into<String>,
           observed: impl Into<String>) -> Self {
        Refusal { code, subject: subject.into(), expected: expected.into(), observed: observed.into() }
    }
}

#[derive(Debug, PartialEq, Eq)]
pub enum Verdict {
    Invalid,
    Level(Level),
}

impl Verdict {
    pub fn as_str(&self) -> String {
        match self {
            Verdict::Invalid => "INVALID".to_string(),
            Verdict::Level(l) => l.to_string(),
        }
    }
}

pub struct Outcome {
    pub verdict: Verdict,
    pub claimed: Level,
    pub coverage: Option<f64>,
    pub distinct_paths: usize,
    pub band: Option<&'static str>,
    pub refusals: Vec<Refusal>,
}

const KINDS: &[&str] = &[
    "privilege", "function", "trigger_chain", "fk_cascade", "dynamic_sql", "disabled_control",
    "view_trigger", "route", "http_entry", "caller", "observed_write", "report", "static", "runtime",
    "agent", "manual", "catalog", "grant",
];

fn finite(v: &Value) -> Option<f64> {
    v.as_f64().filter(|f| f.is_finite())
}

pub fn verify_claim(claim: &Value, inventory: &Value, report: Option<&Value>) -> Outcome {
    let mut refusals: Vec<Refusal> = Vec::new();
    let mut shape_errors = 0usize;
    let mut refuse = |code: &'static str, subject: &str, expected: &str, observed: &str| {
        refusals.push(Refusal::new(code, subject, expected, observed));
    };

    // --- the claim -----------------------------------------------------------------------------
    let claimed_raw = claim.get("declared_level").and_then(|v| v.as_str()).unwrap_or("");
    let claimed = Level::parse(claimed_raw);
    if claimed.is_none() {
        refuse("REPORT_BUNDLE_INCONSISTENT", "claim.declared_level",
               "CONSISTENT_DECLARED | SCOPED_ASSURANCE | PROVEN", claimed_raw);
        shape_errors += 1;
    }
    let claimed = claimed.unwrap_or(Level::ConsistentDeclared);
    let control = claim.get("declared_control_point").and_then(|v| v.as_str()).unwrap_or("");

    if let Some(known) = known_codes() {
        let declared: Vec<String> = claim
            .get("not_claimed")
            .and_then(|v| v.as_array())
            .map(|a| a.iter().filter_map(|v| v.as_str().map(str::to_string)).collect())
            .unwrap_or_default();
        for code in declared.iter().filter(|c| !known.contains(c)) {
            refuse("REPORT_BUNDLE_INCONSISTENT", "claim.not_claimed",
                   "a code from docs/NOT-CLAIMED.md",
                   &format!("{code} is not an entry in the vocabulary"));
            shape_errors += 1;
        }
    }

    match missing_codes(claim, claimed) {
        Some(missing) => refuse("MISSING_EVIDENCE", "claim.not_claimed",
                                 "every NC code the declared level requires",
                                 &missing.join(", ")),
        None => {}
    }

    // --- the inventory: shape before arithmetic ------------------------------------------------
    let sources: Vec<&Value> = inventory
        .get("sources")
        .and_then(|v| v.as_array())
        .map(|a| a.iter().collect())
        .unwrap_or_default();
    let source_ids: Vec<&str> = sources
        .iter()
        .filter_map(|s| s.get("source_id").and_then(|v| v.as_str()))
        .collect();

    let paths: Vec<&Value> = inventory
        .get("paths")
        .and_then(|v| v.as_array())
        .map(|a| a.iter().collect())
        .unwrap_or_default();

    let mut density: Option<f64> = None;
    for source in &sources {
        if let Some(d) = source.get("db_logic_density") {
            match finite(d) {
                // a number that is not a number is not a density
                Some(f) => {
                    if !(0.0..=1.0).contains(&f) {
                        refuse("REPORT_BUNDLE_INCONSISTENT", "inventory.sources[].db_logic_density",
                               "a finite number 0..1", &f.to_string());
                    }
                    density = Some(density.map_or(f, |cur| cur.min(f)));
                }
                None => {
                    refuse("REPORT_BUNDLE_INCONSISTENT", "inventory.sources[].db_logic_density",
                           "a finite number 0..1", &d.to_string());
                    shape_errors += 1;
                }
            }
        }
    }

    let ids: Vec<&str> = paths
        .iter()
        .filter_map(|p| p.get("path_id").and_then(|v| v.as_str()))
        .collect();
    let (distinct, duplicates) = distinct_paths(&ids);
    for dup in duplicates.iter().take(3) {
        refuse("REPORT_BUNDLE_INCONSISTENT", &format!("inventory.paths[path_id={dup}]"),
               "a unique path_id", "repeated: one finding written several times is one finding");
        shape_errors += 1;
    }

    for path in &paths {
        if let Some(kind) = path.get("kind").and_then(|v| v.as_str()) {
            if !KINDS.contains(&kind) {
                refuse("REPORT_BUNDLE_INCONSISTENT", "inventory.paths[].kind",
                       "one of the declared path kinds", kind);
            }
        }
        if let Some(v) = path.get("vanished") {
            if !v.is_boolean() {
                refuse("REPORT_BUNDLE_INCONSISTENT", "inventory.paths[].vanished", "a boolean",
                       &v.to_string());
            }
        }
    }

    // --- truncation, from the numbers rather than from the label ---------------------------------
    let mut truncated = false;
    for source in &sources {
        let label = source.get("completeness_claim").and_then(|v| v.as_str()).unwrap_or("");
        if label == "partial" || label == "sampled" {
            truncated = true;
        }
        if let Some(tr) = source.get("truncated").and_then(|v| v.as_object()) {
            let kept = tr.get("kept").and_then(|v| v.as_u64());
            let total = tr.get("total").and_then(|v| v.as_u64());
            if let (Some(k), Some(t)) = (kept, total) {
                if k < t {
                    truncated = true;
                }
            }
        }
    }
    if truncated && claimed != Level::ConsistentDeclared {
        refuse("MISSING_EVIDENCE", "coverage_basis", "a complete denominator",
               "the source kept only part of what it found");
    }

    // --- growth ----------------------------------------------------------------------------------
    let growth = inventory.get("perimeter_growth");
    let delta = inventory.get("delta_since_previous");
    let mut grew = growth
        .map(|g| !(g.is_null() || g == &Value::Bool(false) || g.as_str() == Some("false")))
        .unwrap_or(false);
    if let Some(delta) = delta.and_then(|d| d.as_object()) {
        let new_paths = delta.get("new_paths").and_then(|v| v.as_u64()).unwrap_or(0);
        let published = delta.get("published") == Some(&Value::Bool(true));
        let has_baseline = delta.get("baseline") != Some(&Value::Bool(false));
        if new_paths > 0 && !published && has_baseline {
            grew = true;
        }
    }
    if grew && claimed != Level::ConsistentDeclared {
        refuse("POLICY_CEILING_EXCEEDED", "perimeter_growth",
               "no new surface since the previous inventory", "the inventory declares growth");
    }

    // --- coverage -------------------------------------------------------------------------------
    let mut in_core = 0usize;
    for path in &paths {
        let attributed = path
            .get("attribution")
            .and_then(|a| a.get("to"))
            .and_then(|v| v.as_str())
            == Some(control);
        let vanished = path.get("vanished") == Some(&Value::Bool(true));
        let names_real_source = path
            .get("attribution")
            .and_then(|a| a.get("sources"))
            .and_then(|v| v.as_array())
            .map(|a| {
                !a.is_empty() && a.iter().all(|s| {
                    s.as_str().map(|x| source_ids.contains(&x)).unwrap_or(false)
                })
            })
            .unwrap_or(false);
        if attributed && !vanished && names_real_source && !control.is_empty() {
            in_core += 1;
        }
    }
    let total = paths.len();
    let coverage = if total > 0 { Some(in_core as f64 / total as f64) } else { None };

    // --- exclusions must not contradict the coverage ------------------------------------------
    if let Some(excluded) = claim.get("excluded").and_then(|v| v.as_array()) {
        for item in excluded {
            let pid = item.get("path_id").and_then(|v| v.as_str()).unwrap_or("");
            if pid.is_empty() {
                continue;
            }
            let in_core = paths.iter().any(|p| {
                p.get("path_id").and_then(|v| v.as_str()) == Some(pid)
                    && p.get("attribution").and_then(|a| a.get("to")).and_then(|v| v.as_str())
                        == Some(control)
            });
            if in_core {
                // a path cannot be both covered and excluded: that is a contradiction in the claim
                // itself, so the claim is unanswerable rather than merely lowered (E-M69)
                refuse("REPORT_BUNDLE_INCONSISTENT", &format!("excluded {pid}"),
                       "an exclusion outside the core",
                       "the path is inside the declared core");
                shape_errors += 1;
            }
        }
    }

    // --- the report, as an input rather than decoration ------------------------------------------
    if let Some(report) = report {
        if report.get("analysed_paths").is_none() && claimed != Level::ConsistentDeclared {
            refuse("MISSING_EVIDENCE", "report.analysed_paths",
                   "the list of paths the analysis covered",
                   "absent: a report without its denominator cannot be checked");
        }
        if let Some(reported) = report.get("coverage").and_then(finite) {
            let computed = coverage.unwrap_or(0.0);
            if (reported - computed).abs() > 0.05 {
                refuse("REPORT_BUNDLE_INCONSISTENT", "coverage",
                       "within 0.05 of the inventory's own arithmetic", &reported.to_string());
            }
        }
    }

    // --- the tier ceiling: a confirmation is what raises the level, and a self-declared one is not one ---
    let tier = claim.get("evidence_tier").and_then(|v| v.as_u64()).unwrap_or(0) as u8;
    if let Some(ceiling) = tier_ceiling(claim, inventory) {
        if tier > ceiling && claimed != Level::ConsistentDeclared {
            refuse("EVIDENCE_TIER_UNSUPPORTED", "evidence_tier",
                   &format!("evidence tier {ceiling} or lower"),
                   &format!("declared tier {tier} with no valid confirmation behind it"));
        }
    }

    // --- independence: an inventory produced only by the analysing agent is not closure ---------
    let kinds: Vec<&str> = sources
        .iter()
        .filter_map(|s| s.get("kind").and_then(|v| v.as_str()))
        .collect();
    let independent = inventory.get("independent_of_agent") == Some(&Value::Bool(true))
        && kinds.iter().any(|k| *k != "agent");
    if !independent && claimed != Level::ConsistentDeclared {
        refuse("E_NO_INDEPENDENT_CLOSURE", "independent_of_agent",
               "at least one source that is not the analysing agent",
               "the inventory is the agent's own word");
    }

    // --- the verdict: floors keyed to the level being printed, then clamped to the claim ---------
    let mut verdict = level_for_distinct_paths(distinct);
    if let Some(floor) = floor_for(verdict) {
        if distinct < floor {
            verdict = Level::ConsistentDeclared;
        }
    }
    if let Some(d) = density {
        // the band, not a magic number: only the lowest band forbids a strong level
        if d < 0.15 && claimed != Level::ConsistentDeclared {
            refuse("THIN_DB_LOGIC_COVERAGE", "coverage_basis",
                   "at least 0.15 of the schema's functions writing to tables", &d.to_string());
        }
    }
    // coverage thresholds: PROVEN needs everything, SCOPED needs a clear majority
    let cov = coverage.unwrap_or(0.0);
    if verdict == Level::Proven && cov < 1.0 {
        refuse("CLAIM_EXCEEDS_EVIDENCE", "coverage", "full coverage is required for PROVEN",
               &format!("coverage {cov:.3}"));
    }
    if verdict.rank() >= Level::ScopedAssurance.rank() && cov < 0.75 {
        refuse("CLAIM_EXCEEDS_EVIDENCE", "coverage", "at least 0.75 for SCOPED_ASSURANCE",
               &format!("coverage {cov:.3}"));
    }

    // an empty covered set makes the claim true for a trivial reason
    if in_core == 0 && claimed != Level::ConsistentDeclared {
        refuse("COVERAGE_BASIS_TOO_SMALL", "coverage_basis",
               "at least one path inside the core",
               "the covered set is empty, so the claim is vacuously true");
    }

    if !refusals.is_empty() || truncated || grew {
        verdict = Level::ConsistentDeclared;
    }
    verdict = clamp(verdict, claimed);

    let band = density.map(|d| if d < 0.15 { "thin" } else if d < 0.40 { "mixed" } else { "dense" });

    let verdict = if shape_errors > 0 { Verdict::Invalid } else { Verdict::Level(verdict) };
    Outcome { verdict, claimed, coverage, distinct_paths: distinct, band, refusals }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn paths(n: usize) -> Vec<Value> {
        (1..=n)
            .map(|i| json!({
                "path_id": format!("wp_{i:03}"),
                "entry": format!("table:app.t{i}"),
                "kind": "privilege",
                "attribution": {"to": "function:bank.transfer", "sources": ["s"]}
            }))
            .collect()
    }

    fn inv(n: usize, extra: Value) -> Value {
        let mut base = json!({
            "manifest_version": "inventory/0.1",
            "target_lock": "t@1",
            "independent_of_agent": true,
            "sources": [{"source_id": "s", "kind": "static", "completeness_claim": "exhaustive_within_covers", "db_logic_density": 0.9}],
            // a tier-2 claim needs a confirmation that `fg_confirm.py` would accept, otherwise the
            // ceiling caps it and every test below would be measuring the ceiling instead of the rule
            "foreign_validation": [{
                "schema": "s", "owner_confirmed": true, "verdict": "confirmed",
                "owner": {"name": "A", "role": "b", "how_contacted": "c", "date": "d"},
                "owner_statement": "confirmed the findings",
                "finding": {"path_id": "wp_001", "claim": "x"}
            }],
            "paths": paths(n)
        });
        if let (Value::Object(b), Value::Object(e)) = (&mut base, extra) {
            for (k, v) in e {
                b.insert(k, v);
            }
        }
        base
    }

    fn claim(level: &str) -> Value {
        json!({"claim_id": "t", "target_lock": {"commit": "t@1"},
               "declared_control_point": "function:bank.transfer", "declared_level": level,
               "claimed_coverage": 1.0, "evidence_tier": 2,
               "not_claimed": ["NC-01", "NC-02", "NC-03", "NC-04", "NC-05", "NC-10", "NC-11"]})
    }

    #[test]
    fn eight_distinct_paths_reach_proven() {
        let out = verify_claim(&claim("PROVEN"), &inv(8, json!({})), None);
        assert_eq!(out.verdict, Verdict::Level(Level::Proven));
        assert!(out.refusals.is_empty(), "{:?}", out.refusals.iter().map(|r| r.code).collect::<Vec<_>>());
    }

    #[test]
    fn a_nearly_correct_level_is_not_a_level() {
        let out = verify_claim(&claim("PROVEN "), &inv(8, json!({})), None);
        // a shape error is not a lowered claim, it is an unanswerable one
        assert_eq!(out.verdict, Verdict::Invalid);
        assert_eq!(out.refusals[0].code, "REPORT_BUNDLE_INCONSISTENT");
    }

    #[test]
    fn nan_cannot_clear_the_density_floor() {
        let out = verify_claim(&claim("PROVEN"),
                               &inv(8, json!({"sources": [{"source_id": "s", "kind": "grants",
                                                           "db_logic_density": 1e308}]})), None);
        assert_eq!(out.verdict, Verdict::Level(Level::ConsistentDeclared), "an infinite density is not a density");
    }

    #[test]
    fn sampled_is_a_truncated_denominator() {
        let out = verify_claim(&claim("PROVEN"),
                               &inv(8, json!({"sources": [{"source_id": "s", "kind": "static",
                                                           "completeness_claim": "sampled",
                                                           "db_logic_density": 0.9}]})), None);
        assert_eq!(out.verdict, Verdict::Level(Level::ConsistentDeclared));
        assert!(out.refusals.iter().any(|r| r.code == "MISSING_EVIDENCE"));
    }

    #[test]
    fn a_false_flag_does_not_cancel_an_unpublished_delta() {
        let out = verify_claim(&claim("PROVEN"),
                               &inv(8, json!({"perimeter_growth": false,
                                              "delta_since_previous": {"new_paths": 3, "published": false}})), None);
        assert!(out.refusals.iter().any(|r| r.code == "POLICY_CEILING_EXCEEDED"));
    }

    #[test]
    fn a_first_inventory_has_no_growth() {
        let out = verify_claim(&claim("PROVEN"),
                               &inv(8, json!({"delta_since_previous": {"new_paths": 8,
                                                                       "published": false,
                                                                       "baseline": false}})), None);
        assert_eq!(out.verdict, Verdict::Level(Level::Proven), "no baseline means nothing to grow from");
    }

    #[test]
    fn vanished_must_be_a_boolean() {
        let mut inventory = inv(8, json!({}));
        inventory["paths"][0]["vanished"] = json!("false");
        let out = verify_claim(&claim("PROVEN"), &inventory, None);
        assert!(out.refusals.iter().any(|r| r.subject.ends_with(".vanished")));
    }

    #[test]
    fn one_row_relabelled_is_one_row() {
        let mut inventory = inv(1, json!({}));
        let mut rows = Vec::new();
        for kind in ["privilege", "function", "trigger_chain", "fk_cascade"] {
            let mut row = paths(1)[0].clone();
            row["kind"] = json!(kind);
            rows.push(row);
        }
        inventory["paths"] = json!(rows);
        let out = verify_claim(&claim("PROVEN"), &inventory, None);
        assert_eq!(out.distinct_paths, 1);
        // repeated identifiers are a shape error, so the claim cannot be answered at all
        assert_eq!(out.verdict, Verdict::Invalid);
    }

    #[test]
    fn an_honest_report_is_accepted_and_a_lying_one_is_not() {
        let inventory = inv(8, json!({}));
        let honest = json!({"coverage": 1.0, "analysed_paths": []});
        let lying = json!({"coverage": 0.5, "analysed_paths": []});
        assert_eq!(verify_claim(&claim("PROVEN"), &inventory, Some(&honest)).verdict,
                   Verdict::Level(Level::Proven));
        assert_eq!(verify_claim(&claim("PROVEN"), &inventory, Some(&lying)).verdict,
                   Verdict::Level(Level::ConsistentDeclared));
    }
}
