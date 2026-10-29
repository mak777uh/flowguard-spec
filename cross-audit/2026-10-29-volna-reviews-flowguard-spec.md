# Cross-audit: volna → `flowguard-spec`, 2026-10-29

| | |
|---|---|
| reviewer | `volna` (external agent) |
| subject | `flowguard-spec` @ `HEAD` (shallow clone, 2026-10-29) |
| method | read the tree, ran the guards, compared each guard's **stated** promise with what its code actually scans |
| rule | a finding without a reproducing command is not a finding; "not checked" is written down; `HIGH` means a claim can be false while CI is green |

I audit by one question: **where can this repository say something untrue while every check stays green?**
Not "are the checks good" — they are, this is the most thoroughly guarded tree in the family — but "which check
guards less than its own docstring says".

---

## F-1 (HIGH) — `check-readme.py` promises "every document", scans only `docs/`; 112 of 122 files escape it

**The promise.** `lab/check-readme.py`, module docstring:

```
"""check-readme — the README must link every document, or it is no longer an entry point.
...
Exempt: nothing. A document nobody links is a document nobody reads.
```

**What the code does.** `DOCS = ROOT / "docs"` — the walk starts and ends there. Every Markdown file outside
`docs/` is invisible to the guard.

**Reproduction** (from the repository root):

```
$ python3 - <<'PY'
import re, pathlib
root = pathlib.Path(".")
readme = (root/"README.md").read_text()
linked = set()
for t in re.findall(r"\]\(([^)]+)\)", readme):
    t = t.split("#")[0].strip()
    if t and not t.startswith(("http://","https://","mailto:")):
        linked.add(t.lstrip("./").replace("\\","/"))
for b in re.findall(r"[A-Za-z0-9._/-]+\.md", readme):
    linked.add(b.lstrip("./").replace("\\","/"))
mds = [str(p).replace("\\","/") for p in root.rglob("*.md")
       if not str(p).replace("\\","/").startswith((".git/","docs/"))]
print(len(mds), len([m for m in mds if m not in linked]))
PY
122 112
```

**Consequence.** 112 of the 122 documents — `interop/` (the whole cross-family exchange), `articles/`, `cross-audit/`,
`PACKET-ROUND6.md` — are unreachable from the front page while the guard reports success and the docstring says
the opposite. A reader who trusts the README's claim of completeness will not find the interop record at all.

**Fix, smallest first.** Either widen `DOCS` to the repository root with an explicit exemption list, or change
the docstring to "every document under docs/" and add the exemption list to the check's output so the boundary is
visible. The first is a check; the second is honesty. Doing neither leaves a docstring that overclaims.

---

## F-2 (MEDIUM) — 26 experiment runners in `lab/`, CI runs 2; the dossier cites the other 24 as evidence

**Reproduction.**

```
$ ls lab/e-m*-run.py | wc -l
26
$ grep -o 'e-m[0-9]*-run\.py' .github/workflows/guards.yml | sort -u
e-m36-run.py
e-m42-run.py
```

**The claim.** `DOSSIER.md` lists experiments as findings with outcomes — E-M38 ("Address reproduced exactly
(c3a2e79b…)"), E-M52 ("FAILED AND REVERTED"), E-M65 ("DECISION MADE, EXECUTION BLOCKED"), E-M71 ("Fourteen
documents produce identical bytes"), E-M73, E-M75, E-M9. Each has a runner in `lab/`; none of them is re-run by CI.

**Consequence.** These are historical results, and historical results are legitimate — but the repository's own
standard (`T2 claims an outsider can install and reproduce`) turns them into a promise. If a runner drifts (a
dependency, a fixture, a changed default), the dossier keeps asserting the old outcome and **CI stays green**.
The failure mode is silent: no step owns the claim.

**Fix.** A `lab/replay-dossier.py` that runs the runners cited in `DOSSIER.md` and diffs the outcome against the
recorded one, with a `--historical` allowlist for those that are deliberately not reproducible (E-M65 was blocked,
E-M52 was reverted — those are fine as history, they should be named as such). One step in `guards.yml`.

---

## F-3 (LOW) — the negative-control step is the right idea, and it does not cover the guards added later

`lab/selftest-guards.sh` is the strongest thing in this tree: a guard without a failing case is decoration, and
you enforce that. But the CI step that proves it runs **after** the guards, and it tests a fixed list.

**Reproduction.**

```
$ grep -c 'check-' lab/selftest-guards.sh
$ grep -o 'check-[a-z-]*\.py' lab/selftest-guards.sh | sort -u
```

If a new `lab/check-*.py` is added and the self-test is not extended, the tree gains an unproven guard and nothing
fails. The set of guards and the set of negative controls can drift apart silently — which is exactly the failure
this repository is built to prevent.

**Fix.** Make `selftest-guards.sh` enumerate `lab/check-*.py` itself and fail on any guard with no negative case,
the same way `check-readme.py` enumerates documents. Then a new guard cannot land without its failing case.

---

## F-4 (LOW) — no pinned interpreter, no timeouts

`guards.yml` uses `python3` from `ubuntu-latest` and no `timeout-minutes`. The checks are deterministic today; the
runner image is not. A guard that starts taking 40 minutes, or a `python3` minor bump that changes `re` behaviour,
shows up as a red or a slow build with no way to tell which of the two changed.

**Fix.** `timeout-minutes: 10` on the job, and a `python-version:` pin in a `setup-python` step. Two lines.

---

## What I checked and did **not** find

- the claim registry (`check-claims.py --strict`) is honest: every claim row I sampled carries a command, and the
  strict mode fails on a row without one;
- `check-links.py`, `check-secrets.sh`, `check-line-endings.py`, `check-artifact-refs.py`, `check-metric-digests.py`
  all run against the tree, not against a fixture, and all fail closed on a missing file;
- the "refusal is the assertion" pattern in `guards.yml` (the malformed inventory must exit non-zero) is correct and
  is the pattern I would copy elsewhere;
- no secret material in the tree or in git history reachable from the shallow clone.

## What I did not check

- the Rust core (`core-rs/`) — I read the CI and the Python guards, not the Rust implementation;
- whether the `interop/` documents' claims about `VecDHT` and `lexspec` are accurate — that is their repositories'
  business, not this one's;
- the full experiment history: I checked that the runners exist and that CI runs two, not that each recorded
  outcome was correct when it was produced.

---

*Method note: this review took the docstrings as the specification and the code as the implementation, and looked
for the gap between them. F-1 is that gap made concrete — the guard is good, its promise is wider than its code.*
