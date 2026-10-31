import importlib.util
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("fgc", ROOT / "tools" / "fg_canonical.py")
CANON = importlib.util.module_from_spec(spec)
sys.modules["fgc"] = CANON
spec.loader.exec_module(CANON)


class Rfc8785Numbers(unittest.TestCase):
    """The published number cases. Acceptance is the vector, not our opinion."""

    def setUp(self):
        self.vectors = json.loads((ROOT / "lab" / "vectors" / "rfc8785-numbers.json")
                                  .read_text(encoding="utf-8"))["vectors"]

    def test_every_published_number_case(self):
        for case in self.vectors:
            with self.subTest(case["input"]):
                got = CANON.canonical_bytes({"n": json.loads(case["input"])}).decode()
                self.assertEqual('{"n":' + case["expected"] + "}", got, case["why"])

    def test_non_finite_is_refused(self):
        for bad in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(repr(bad)):
                with self.assertRaises(ValueError):
                    CANON.canonical_bytes({"n": bad})

    def test_booleans_are_not_numbers(self):
        self.assertEqual(CANON.canonical_bytes({"a": True, "b": 1}), b'{"a":true,"b":1}')

    def test_keys_sort_by_code_point_and_strings_keep_utf8(self):
        doc = {"b": "é", "a": {"z": 1, "y": [1, 2]}}
        self.assertEqual(CANON.canonical_bytes(doc), '{"a":{"y":[1,2],"z":1},"b":"é"}'.encode())


if __name__ == "__main__":
    unittest.main(verbosity=2)
