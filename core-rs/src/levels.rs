//! The verdict ladder as a closed type.
//!
//! In Python this was a string, and `"PROVEN "` with one trailing space printed PROVEN with exit 0 and no
//! errors (E-M42 B1). Here an unknown level is a parse failure, and every comparison is a function of an enum.

use std::fmt;

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum Level {
    ConsistentDeclared,
    ScopedAssurance,
    Proven,
}

impl Level {
    pub fn parse(raw: &str) -> Option<Level> {
        match raw {
            "CONSISTENT_DECLARED" => Some(Level::ConsistentDeclared),
            "SCOPED_ASSURANCE" => Some(Level::ScopedAssurance),
            "PROVEN" => Some(Level::Proven),
            _ => None,
        }
    }

    pub fn rank(self) -> u8 {
        match self {
            Level::ConsistentDeclared => 0,
            Level::ScopedAssurance => 1,
            Level::Proven => 2,
        }
    }
}

impl fmt::Display for Level {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(match self {
            Level::ConsistentDeclared => "CONSISTENT_DECLARED",
            Level::ScopedAssurance => "SCOPED_ASSURANCE",
            Level::Proven => "PROVEN",
        })
    }
}

/// The verdict may never exceed the claimed level — the type-level version of E-M42 B1.
pub fn clamp(computed: Level, claimed: Level) -> Level {
    if computed.rank() <= claimed.rank() {
        computed
    } else {
        claimed
    }
}

pub fn min_level(a: Level, b: Level) -> Level {
    if a.rank() <= b.rank() {
        a
    } else {
        b
    }
}

/// Floors are keyed to the level being printed, not to the level the caller asked for (E-M42 B2).
pub fn floor_for(level: Level) -> Option<usize> {
    match level {
        Level::ConsistentDeclared => None,
        Level::ScopedAssurance => Some(3),
        Level::Proven => Some(8),
    }
}

pub fn level_for_distinct_paths(count: usize) -> Level {
    if count >= floor_for(Level::Proven).unwrap() {
        Level::Proven
    } else if count >= floor_for(Level::ScopedAssurance).unwrap() {
        Level::ScopedAssurance
    } else {
        Level::ConsistentDeclared
    }
}

/// Distinct means distinct rows, not distinct labels: one path relabelled eight ways passed an eight-path
/// floor twice (E-M47 #2, E-M50 B1).
pub fn distinct_paths(ids: &[&str]) -> (usize, Vec<String>) {
    let mut seen: std::collections::HashSet<&str> = std::collections::HashSet::new();
    let mut dupes: Vec<String> = Vec::new();
    for id in ids {
        if id.is_empty() {
            continue;
        }
        if !seen.insert(id) {
            dupes.push((*id).to_string());
        }
    }
    (seen.len(), dupes)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_nearly_correct_level_is_not_a_level() {
        assert_eq!(Level::parse("PROVEN"), Some(Level::Proven));
        assert_eq!(Level::parse("PROVEN "), None, "a trailing space is not PROVEN");
        assert_eq!(Level::parse("proven"), None);
        assert_eq!(Level::parse("PROVEN\u{200b}"), None);
    }

    #[test]
    fn the_verdict_never_exceeds_the_claim() {
        for computed in [Level::ConsistentDeclared, Level::ScopedAssurance, Level::Proven] {
            for claimed in [Level::ConsistentDeclared, Level::ScopedAssurance, Level::Proven] {
                assert!(clamp(computed, claimed).rank() <= claimed.rank());
            }
        }
        assert_eq!(clamp(Level::Proven, Level::ScopedAssurance), Level::ScopedAssurance);
    }

    #[test]
    fn floors_are_monotone_in_distinct_paths() {
        let mut previous = 0;
        for n in 0..20 {
            let r = level_for_distinct_paths(n).rank();
            assert!(r >= previous, "the level must not fall when paths are added");
            previous = r;
        }
        assert_eq!(level_for_distinct_paths(2), Level::ConsistentDeclared);
        assert_eq!(level_for_distinct_paths(3), Level::ScopedAssurance);
        assert_eq!(level_for_distinct_paths(8), Level::Proven);
    }

    #[test]
    fn one_row_is_one_row_however_it_is_labelled() {
        let (distinct, dupes) = distinct_paths(&["wp_1", "wp_1", "wp_1", "wp_1"]);
        assert_eq!(distinct, 1);
        assert_eq!(dupes.len(), 3);
    }
}
