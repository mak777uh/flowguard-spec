"""Systematic mutators for the differential (E-M58): every field, every file, every format knob."""
import json
from pathlib import Path


def _edit_json(path: Path, fn):
    doc = json.loads(path.read_text(encoding="utf-8"))
    fn(doc)
    path.write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")


def _reformat_json(path: Path, **kw):
    doc = json.loads(path.read_text(encoding="utf-8"))
    path.write_text(json.dumps(doc, **kw), encoding="utf-8")


def build():
    """Return a list of (name, mutation) pairs. A mutation that must NOT change the verdict is
    marked with a leading '+' so the harness can assert acceptance instead of refusal."""
    m = []

    # ---- formatting changes that must be harmless (the address is canonical, not textual)
    m.append(("+bundle.json reformatted with indent=4",
              lambda d: _reformat_json(d / "bundle.json", indent=4, sort_keys=True)))
    m.append(("+bundle.json compacted",
              lambda d: _reformat_json(d / "bundle.json", separators=(",", ":"))))
    m.append(("+bundle.json key order shuffled",
              lambda d: _reformat_json(d / "bundle.json", indent=1, sort_keys=False)))

    def swap_keys(d):
        p = d / "bundle.json"
        doc = json.loads(p.read_text(encoding="utf-8"))
        items = list(doc.items())[::-1]
        p.write_text(json.dumps(dict(items), indent=1, ensure_ascii=False), encoding="utf-8")

    m.append(("+bundle.json top-level keys reversed", swap_keys))

    # ---- claim field edits: the address must change, so the manifest no longer matches
    for field, value in (("claim_id", "x"), ("declared_level", "PROVEN"),
                         ("claimed_coverage", 0.99), ("declared_control_point", "function:other")):
        m.append((f"claim.{field} changed",
                  (lambda f, v: (lambda d: _edit_json(d / "bundle.json", lambda doc: doc["claim"].__setitem__(f, v))))(field, value)))

    # ---- manifest.sha256 damage
    m.append(("manifest.sha256 uppercased",
              lambda d: (d / "manifest.sha256").write_text(
                  (d / "manifest.sha256").read_text().strip().upper() + "\n")))
    m.append(("manifest.sha256 without LF",
              lambda d: (d / "manifest.sha256").write_text(
                  (d / "manifest.sha256").read_text().strip())))
    m.append(("manifest.sha256 with CRLF",
              lambda d: (d / "manifest.sha256").write_bytes(
                  (d / "manifest.sha256").read_text().strip().encode() + b"\r\n")))
    m.append(("manifest.sha256 truncated",
              lambda d: (d / "manifest.sha256").write_text(
                  (d / "manifest.sha256").read_text().strip()[:-1] + "\n")))

    # ---- signature files damaged in every way that should be caught
    m.append(("owner.sig base64 corrupted",
              lambda d: (d / "signatures" / "owner.sig").write_text("A" * 88 + "\n")))
    m.append(("owner.sig truncated",
              lambda d: (d / "signatures" / "owner.sig").write_text(
                  (d / "signatures" / "owner.sig").read_text().strip()[:44] + "\n")))
    m.append(("owner.sig empty", lambda d: (d / "signatures" / "owner.sig").write_text("")))
    m.append(("owner.pub replaced by demo.pub",
              lambda d: (d / "signatures" / "owner.pub").write_bytes(
                  (d / "signatures" / "demo.pub").read_bytes())))
    m.append(("demo.pub truncated",
              lambda d: (d / "signatures" / "demo.pub").write_bytes(
                  (d / "signatures" / "demo.pub").read_bytes()[:100])))
    m.append(("owner.role not JSON",
              lambda d: (d / "signatures" / "owner.role").write_text("{not json")))

    # ---- role document edits
    for field, value in (("issuer", "someone-else"), ("valid_until", "1999-01-01"),
                         ("residual_risk", ["NC-99"]), ("asserts", "analysis_provenance")):
        m.append((f"owner.role {field} changed",
                  (lambda f, v: (lambda d: _edit_json(d / "signatures" / "owner.role",
                                                      lambda doc: doc.__setitem__(f, v))))(field, value)))
    m.append(("owner.role extra key added",
              lambda d: _edit_json(d / "signatures" / "owner.role",
                                   lambda doc: doc.__setitem__("note", "extra"))))
    m.append(("owner.role accepted_scope deleted",
              lambda d: _edit_json(d / "signatures" / "owner.role",
                                   lambda doc: doc.pop("accepted_scope", None))))
    m.append(("owner.role accepted_scope null",
              lambda d: _edit_json(d / "signatures" / "owner.role",
                                   lambda doc: doc.__setitem__("accepted_scope", None))))
    m.append(("+owner.role reformatted (must stay valid)",
              lambda d: _reformat_json(d / "signatures" / "owner.role", indent=4, sort_keys=True)))
    m.append(("+owner.role compacted (must stay valid)",
              lambda d: _reformat_json(d / "signatures" / "owner.role", separators=(",", ":"))))

    # ---- objects and directory structure
    m.append(("object renamed to its wrong digest",
              lambda d: (sorted((d / "objects").glob("*"))[0].rename(
                  d / "objects" / ("f" * 64)))))
    m.append(("signatures directory emptied",
              lambda d: [f.unlink() for f in (d / "signatures").glob("*")]))
    m.append(("objects directory emptied",
              lambda d: [f.unlink() for f in (d / "objects").glob("*")]))
    m.append(("bundle.json deleted", lambda d: (d / "bundle.json").unlink()))
    m.append(("manifest.sha256 deleted", lambda d: (d / "manifest.sha256").unlink()))

    def duplicate_sig(d):
        src = d / "signatures" / "demo.sig"
        (d / "signatures" / "demo-copy.sig").write_bytes(src.read_bytes())

    m.append(("an extra signature copy added", duplicate_sig))

    def same_key_two_roles(d):
        # the same key signing both roles must violate separation of duties
        (d / "signatures" / "owner.pub").write_bytes((d / "signatures" / "demo.pub").read_bytes())

    m.append(("same key holds both roles", same_key_two_roles))

    return m
