"""Do our two canonicalisers produce the same bytes?

Two projects in one family, each with its own canonical form, both claiming that the byte form is the contract
between implementations. If they disagree on any document, then a digest produced by one is meaningless to the
other - and the exchange of signed artifacts between them would fail silently.

This is the first entry in the cross-repo registry: a styk, not a project.
"""
import hashlib
import importlib.util
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ours() -> "callable":
    """FlowGuard's canonical form: fg_bundle.canonical_bytes."""
    mod = load(ROOT / "tools" / "fg_bundle.py", "fgb")
    for candidate in ("canon", "canonical_bytes", "canonical", "_canonical"):
        fn = getattr(mod, candidate, None)
        if fn is not None:
            def call(doc, _fn=fn):
                out = _fn(doc)
                return out if isinstance(out, bytes) else out.encode("utf-8")
            return call
    raise SystemExit("no canonical function found in tools/fg_bundle.py")


def theirs() -> "callable":
    """LexSpec's canonical form: lexcheck.canonical_text."""
    repo = pathlib.Path(__import__("os").environ.get(
        "LEXSPEC_DIR", ROOT.parent / "lexspec-review"))
    mod = load(repo / "tools" / "lexcheck.py", "lexcheck")
    return lambda doc: mod.canonical_text(doc).encode("utf-8")


DOCS = {
    "empty object": {},
    "flat": {"b": 1, "a": 2},
    "nested keys": {"z": {"b": [1, 2], "a": {"y": None, "x": True}}},
    "cyrillic": {"термин": "поставщик", "atom": "a1"},
    "combining marks (NFC)": {"t": "и\u0306"},          # и + breve
    "astral plane": {"emoji": "🙂", "k": "𝕏"},
    "control char": {"c": "a\u0001b"},
    "line separators": {"s": "a\u2028b\u2029c"},
    "quote and backslash": {"q": 'a"b\\c'},
    "empty containers": {"a": [], "b": {}},
    "integers large": {"n": 2**63 - 1, "m": 0},
    "array order kept": {"a": [3, 1, 2]},
    "duplicate-at-top": {"a": 1},
    "key ordering unicode": {"Z": 1, "a": 2, "А": 3, "а": 4},
}


def main() -> int:
    o, t = ours(), theirs()
    bad = 0
    print(f"{'document':28} {'same bytes':10} our digest  their digest")
    for name, doc in DOCS.items():
        try:
            ob = o(doc)
        except Exception as e:  # noqa: BLE001
            ob = f"ERROR {type(e).__name__}: {e}".encode()
        try:
            tb = t(doc)
        except Exception as e:  # noqa: BLE001
            tb = f"ERROR {type(e).__name__}: {e}".encode()
        same = ob == tb
        bad += 0 if same else 1
        od = hashlib.sha256(ob).hexdigest()[:12] if not ob.startswith(b"ERROR") else "error"
        td = hashlib.sha256(tb).hexdigest()[:12] if not tb.startswith(b"ERROR") else "error"
        print(f"{name:28} {str(same):10} {od}  {td}")
        if not same:
            print(f"    ours:  {ob[:120]!r}")
            print(f"    their: {tb[:120]!r}")
    # floats: one side must refuse them, and it should be both
    for name, doc in (("float 1.0", {"n": 1.0}), ("float 0.5", {"n": 0.5})):
        try:
            ob = o(doc)
        except Exception as e:  # noqa: BLE001
            ob = f"REFUSED {type(e).__name__}".encode()
        try:
            tb = t(doc)
        except Exception as e:  # noqa: BLE001
            tb = f"REFUSED {type(e).__name__}".encode()
        print(f"{name:28} ours={ob[:40]!r} their={tb[:40]!r}")
    print(f"\ndocuments: {len(DOCS)}, byte disagreements: {bad}")
    print("RESULT:", "PASS" if not bad else "FAIL")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
