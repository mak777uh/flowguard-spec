#!/usr/bin/env python3
"""Pinned behaviour for the defect classes this repository lost cards to.

`ADR-0017` lists five breaks that cost a card and a round each. The point of this file is that they
cannot come back quietly: each test below is one of those breaks, written as the smallest document that
used to be accepted and must now be refused.

    1. `"PROVEN "` with a trailing space printed `PROVEN`            -> a level that is not in the enum is INVALID
    2. `NaN` cleared a density floor because `NaN < 0.15` is false    -> a non-finite density is INVALID
    3. `vanished: "false"` counted as coverage because a string is not `true`
                                                                     -> a non-boolean `vanished` is INVALID
    5. duplicate `path_id` inflated a floor                          -> a repeated path_id is INVALID

Break 4 (a report that omits `analysed_paths` skipped a whole check) lives inside `main()`, not in a
function, and is covered by `lab/e-m60-run.py`; it is named here so the list stays complete rather than
looking like a gap.

The coverage invariants are pinned for the same reason: an event the enumeration cannot explain has to be
reported, and free text must never satisfy the enumeration (E-M47).

    python -m unittest discover -s tests -v
"""
import importlib.util
import math
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"


def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


VERIFY = load("fg_verify")
COVERAGE = load("fg_coverage")

CLAIM = {
    "claim_id": "t",
    "target_lock": {"commit": "t@1"},
    "declared_control_point": "function:app.audit",
    "declared_level": "CONSISTENT_DECLARED",
    "claimed_coverage": 0.0,
    "not_claimed": ["NC-01"],
    "excluded": [],
}


def path(**over):
    row = {"path_id": "wp_1", "entry": "table:app.t", "kind": "privilege"}
    row.update(over)
    return row


def inventory(paths=None, sources=None):
    return {
        "manifest_version": "inventory/0.1",
        "target_lock": "t@1",
        "independent_of_agent": True,
        "sources": sources if sources is not None else [{"source_id": "s", "kind": "grants"}],
        "paths": paths if paths is not None else [path()],
    }


def subjects(problems):
    return [p[0] for p in problems]


class RefusedShapes(unittest.TestCase):
    """Each test is a break that used to pass. The refusal is the assertion."""

    def test_level_with_a_trailing_space_is_refused(self):
        problems = VERIFY.validate_shapes(dict(CLAIM, declared_level="PROVEN "), inventory())
        self.assertIn("claim.declared_level", subjects(problems))

    def test_non_finite_density_is_refused(self):
        sources = [{"source_id": "s", "kind": "grants", "db_logic_density": float("nan")}]
        problems = VERIFY.validate_shapes(CLAIM, inventory(sources=sources))
        self.assertIn("inventory.sources[].db_logic_density", subjects(problems))

    def test_infinite_density_is_refused_too(self):
        sources = [{"source_id": "s", "kind": "grants", "db_logic_density": math.inf}]
        problems = VERIFY.validate_shapes(CLAIM, inventory(sources=sources))
        self.assertIn("inventory.sources[].db_logic_density", subjects(problems))

    def test_vanished_as_a_string_is_refused(self):
        problems = VERIFY.validate_shapes(CLAIM, inventory(paths=[path(vanished="false")]))
        self.assertIn("inventory.paths[0].vanished", subjects(problems))

    def test_duplicate_path_id_is_refused(self):
        problems = VERIFY.validate_shapes(CLAIM, inventory(paths=[path(), path()]))
        self.assertIn("inventory.paths[path_id=wp_1]", subjects(problems))

    def test_a_distinct_path_id_is_accepted(self):
        problems = VERIFY.validate_shapes(CLAIM, inventory(paths=[path(), path(path_id="wp_2")]))
        self.assertEqual(problems, [])


class CoverageInvariants(unittest.TestCase):
    """An event the enumeration cannot explain has to be visible."""

    def test_the_three_states_are_distinguished(self):
        # covered = enumerated AND observed; unobserved = enumerated, never seen;
        # unenumerable = seen, absent from the enumeration. The third one is the reason the model exists.
        inv = inventory(paths=[
            path(entry="stmt:INSERT table:app.t"),
            path(path_id="wp_2", kind="observed_write", entry="stmt:INSERT table:app.t"),
            path(path_id="wp_3", kind="observed_write", entry="stmt:DELETE table:app.t"),
        ])
        states = COVERAGE.states(inv)
        self.assertEqual(states["covered"], ["INSERT"])
        self.assertEqual(states["unobserved"], [])
        self.assertEqual(states["unenumerable"], ["DELETE"])

    def test_enumerated_but_never_observed_is_unobserved(self):
        inv = inventory(paths=[path(entry="stmt:INSERT table:app.t")])
        states = COVERAGE.states(inv)
        self.assertEqual(states["covered"], [])
        self.assertEqual(states["unobserved"], ["INSERT"])
        self.assertEqual(states["unenumerable"], [])

    def test_free_text_detail_never_satisfies_the_enumeration(self):
        # E-M47: typing DELETE into `detail` made an unexplained event look catalogued
        inv = inventory(paths=[
            path(entry="table:app.t", detail="DELETE"),
            path(path_id="wp_2", kind="observed_write", entry="stmt:DELETE table:app.t"),
        ])
        self.assertEqual(COVERAGE.states(inv)["unenumerable"], ["DELETE"])

    def test_observed_write_paths_are_not_part_of_the_catalogue(self):
        inv = inventory(paths=[path(kind="observed_write", entry="stmt:UPDATE table:app.t")])
        states = COVERAGE.states(inv)
        self.assertEqual(states["covered"], [])
        self.assertEqual(states["unenumerable"], ["UPDATE"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
