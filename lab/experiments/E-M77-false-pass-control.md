---
id: E-M77
hypothesis: H-M77
status: completed
base_commit: "c06d28b"
started: "2026-10-29T21:25:00+03:00"
finished: "2026-10-29T21:40:00+03:00"
environment: "Windows, CPython 3.13.11, bash"
command: "bash lab/selftest-guards.sh   # three times, then per-control"
threshold: "Pre-registered: a negative control passes only if its own plant is what turns the guard red. A control that goes green because the tree is already dirty is a false pass and must be found, not counted."
result: "The line-endings control was a false pass. It passed on the first run and failed on every run after the tree was cleaned, because the guard reads `git ls-files` and the planted CRLF file was never added to the repository: the only reason it had ever 'caught' anything was that `.github/workflows/guards.yml` and `lab/selftest-guards.sh` themselves carried CRLF at that moment. It now stages its plant, exactly like the secrets control does, and the reason is written in the control. The other two new controls were checked separately: the metric-digest control fails on the planted row for the right reason (`999 (line 150): 000000000000… matches no file in lab/logs/`), and the refusal-coverage control generates its code at run time so no carrier can contain it. Controls: 11, all passing, each for its own reason."
verdict: refutes
---

# E-M77 — the control that was green for the wrong reason

## What happened

After `E-M76` added three negative controls, the suite reported 11/0 in my shell and 10/1 inside the ritual. The
same command, two answers — and the difference was the tree, not the code.

The line-endings guard scans `git ls-files`. My control wrote the planted file into a staged copy and never
committed it, so the guard could not see it. The control passed the first time because **the real tree was dirty**:
`.github/workflows/guards.yml` and `lab/selftest-guards.sh` had CRLF from my edits, so the guard was red for a
reason unrelated to the plant. Once the tree was clean, the control failed — correctly, because it had been
measuring nothing.

That is the same class as `E-M45` (a test measuring its fixture) and `E-M67` (a test measuring the ceiling), and it
is the third instance in this repository. The general form is worth writing down:

> a negative control must be red **because of its plant**, and the only way to know is to run it on a clean tree.

## The fix

```bash
printf '#!/usr/bin/env bash\r\necho hi\r\n' > "$TMP/repo/lab/_negative_crlf.sh"
( cd "$TMP/repo" && git add -A && git -c user.email=t@t -c user.name=t commit -qm plant )
```

with the reason in the control itself, so the next person does not "simplify" the commit away.

## The other two, checked individually

- **metric digests**: the control's plant is a row with a 64-zero digest. Run alone, the guard exits 1 and says
  `999 (line 150): 000000000000… matches no file in lab/logs/` — the plant, named.
- **refusal coverage**: the control builds the code at run time (`SYNTHETIC_$(date +%s)_UNRAISED`), because a
  literal in `lab/selftest-guards.sh` is inside a carrier and the guard counted its own plant as exercised.

## What this changes in the ritual

The suite is now honest about three guards that previously had no control at all, and about one control that had a
control-shaped hole. It also means `bash lab/selftest-guards.sh` must be run on a **clean tree** to mean anything —
which is true of the ritual by construction, since the ritual runs after `git add -A`.

## What this does not do

- It does not prove the other eight controls are free of the same defect. They stage their plants, which is
  necessary and not sufficient: the sufficient test is "clean tree, plant, red, remove, green", and only this suite
  running on a clean tree each time keeps that true.
- It does not touch the product. It is a control about controls, which is where the last two days of external
  findings keep landing.
