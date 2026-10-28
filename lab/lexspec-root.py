"""F-3-1 reproduction: the same bytes pass or fail depending on whether the tree carries a repository marker."""

import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(os.environ.get("LEXSPEC_DIR",
                                   pathlib.Path(__file__).resolve().parents[2] / "lexspec-review"))
TOOL = REPO / "tools" / "lexcheck.py"


def run(tool, statement, tag):
    r = subprocess.run([sys.executable, str(tool), str(statement), "--json"],
                       capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except Exception:  # noqa: BLE001
        print("  %-38s NO-JSON (exit %s)" % (tag, r.returncode))
        return
    codes = [f["code"] for f in d.get("findings", [])][:2]
    print("  %-38s %-18s coverage=%s  %s" % (tag, d["verdict"], d["coverage"], codes))


def main():
    if not TOOL.exists():
        print("clone LexSpec first, or set LEXSPEC_DIR (looked in %s)" % REPO)
        return 2
    work = pathlib.Path(tempfile.mkdtemp(prefix="lexprobe-"))
    for sub in ("corpus", "examples"):
        shutil.copytree(REPO / sub, work / sub)
    statement = work / "examples" / "01-delivery-ok.lex.json"
    print("statement and corpus are byte-identical in all three runs\n")
    run(TOOL, statement, "tree as copied (no marker)")
    (work / ".git").mkdir()
    run(TOOL, statement, "after mkdir .git")
    (work / "docs").mkdir()
    (work / "docs" / "10-SPEC-v0.1.md").write_text("marker", encoding="utf-8")
    (work / ".git").rmdir()
    run(TOOL, statement, "after adding the spec marker instead")
    return 0


if __name__ == "__main__":
    sys.exit(main())
