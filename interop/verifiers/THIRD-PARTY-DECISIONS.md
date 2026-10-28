# Places where the README did not tell me what to do

Every entry: what I had to decide, what I chose, and the README line I based it
on — or **no line, I guessed**. Line numbers are from
`sample-bundle/README.md` as shipped.

Numbering matches the `DECISION n` comments in `verify_bundle.py`.

---

## D1 — The manifest's required fields are never enumerated

§6b line 120 says `MISSING_EVIDENCE` fires when "the manifest lacks a required
field", and no list of required fields appears anywhere on the page.

I required `bundle_version`, `subjects`, `objects`, `claim`, `inventory_digest`,
plus `claim.target_lock` and `claim.not_claimed`. **No line lists these** — I
chose every field the page itself *reads* somewhere (§2, §5, §8b). A bundle
missing, say, `plaintext_notified` is not refused by me, and nothing on the page
says whether it should be.

## D2 — Object byte-length mismatch: which code?

Line 82 (`bytes` must equal the file's length) mandates the check; line 119
assigns `REPORT_BUNDLE_INCONSISTENT` to "the objects map, the directory and a
subject disagree" — which does not literally cover a length mismatch.

I chose `REPORT_BUNDLE_INCONSISTENT`. **Partly guessed**: length is a map-vs-file
disagreement, but `MISSING_EVIDENCE` is defensible.

## D3 — Object whose bytes no longer hash to its own name: which code?

Line 79 says the file name *is* the SHA-256 of its bytes. Line 119 covers
map/dir/subject disagreement; line 120 covers "a declared object is absent".

I chose `REPORT_BUNDLE_INCONSISTENT`. **No line covers the present-but-wrong-hash
state.** One can argue the object *with that digest* is absent, which would make
`MISSING_EVIDENCE` correct instead. This is tampering case (a) and the ambiguity
is real: both rows describe the state.

## D4 — `asserts` missing entirely

Line 121: `SIGNATURE_ROLE_UNKNOWN` when "`asserts` is not one of §8's roles".
A document with no `asserts` key at all is not obviously that.

I chose `SIGNATURE_ROLE_UNKNOWN`. **Guessed** (closest row; a role document with
no role is not a role).

## D5 — Missing required field on a non-`risk_acceptance` role

Line 123 gives `RISK_ACCEPTANCE_INCOMPLETE` for the risk role's missing fields.
§8's table requires `issuer` for all roles and `policy_digest` for
`consistency_verdict`, but §6b assigns **no** code for those being absent.

I chose `MISSING_EVIDENCE`. **Guessed.**

## D6 — The contents of `not_a_role` are not given

Line 122 says `LIABILITY_NOT_A_ROLE` fires for "`liability_agreement` or another
key in `not_a_role`". `not_a_role` is defined nowhere on the page; line 161 names
only `liability_agreement`.

I hard-coded `{"liability_agreement"}`. **Unavoidable guess**: a bundle asserting
some other non-role (e.g. `warranty`) gets `SIGNATURE_ROLE_UNKNOWN` from me, and
I cannot tell from this page whether that is what was intended.

## D7 — "the key is deleted" is top-level only

Explicit at line 71 ("The deletion is top-level only"). **Not a guess**, recorded
only because it is easy to get wrong.

## D8 — `target_lock` equality: the shapes do not match (§8b defect)

Line 170: `bundle.claim.target_lock` equals the inventory's `target_lock`. In the
artifact `claim.target_lock` is an **object** `{"commit": "flowguard-sample@2026-10-27"}`
(bundle.json lines 46–48) and the inventory's `target_lock` is the **bare string**
`"flowguard-sample@2026-10-27"`. A literal `==` is `False`.

I normalised a one-key `{"commit": ...}` object down to its string before
comparing. **No line says to do this — I guessed**, and I believe this is a
description defect, not a bundle defect: implemented literally, §8b refuses the
one artifact the page says is valid. This is the only place where the page, read
literally, produces a false refusal on its own example.

## D9 — Which address goes into the signed message when the two differ

Line 57 says `address_hex`; line 171 speaks of "the recorded address". When
`manifest.sha256` and the canonical `bundle.json` disagree, the address check has
already refused, but the signature check still needs one.

I use the **recorded** value when it is well-formed, else the recomputed one.
**Guessed** (line 171 leans "recorded", but nothing states it).

## D10 — Inventory that does not parse as JSON

§8b needs the inventory parsed to read `target_lock`. Unparseable inventory means
that check cannot run.

I refuse `MISSING_EVIDENCE`. **No line** — `REPORT_BUNDLE_INCONSISTENT` is
defensible too.

## D11 — `claim.target_lock` vs inventory `target_lock` mismatch: which code?

Lines 168–170 mandate the check and say "a mismatch is a refusal", assigning **no
code**. Line 125 defines `TARGET_MISMATCH` as the claim's `target_lock` versus
"the expected target supplied by the verifier" — a *different* comparison, which
may be absent.

I reused `TARGET_MISMATCH`. **Guessed.** Tension worth naming: line 114 says "a
verifier that invents a code is not conforming", so the only conforming move is to
reuse one of the eight; this is the closest.

## D12 — `issuer` disagrees with the file stem: which code?

Lines 148–149 mandate the check ("a document whose `issuer` disagrees with its own
file name is ambiguous about who asserted it") and assign **no code**.

I chose `MISSING_EVIDENCE`. **Guessed.**

## D13 — `residual_risk` ≠ `claim.not_claimed`: which code?

Line 172 mandates it ("`residual_risk` equals the claim's `not_claimed` set, as
sets") and assigns **no code**.

I chose `RISK_ACCEPTANCE_INCOMPLETE`. **Guessed.**

D11, D12 and D13 together are the sharpest gap: §8b mandates three cross-file
checks and §6b gives a code for **none** of them, while line 114 forbids inventing
one.

## D14 — How many signers must a bundle carry?

Nothing on the page says. `SIGNED_AND_CONSISTENT` (line 93) is a claim about
signing, and line 94 forbids printing a success that is not supported, so a bundle
with zero verifying signatures must not pass — but there is no code for "no
signatures at all".

I refuse `MISSING_EVIDENCE` when no signer produced any binding. **Guessed**,
licensed by line 94. Without this guard a bundle with `signatures/` emptied passes,
which is plainly a false success.

## D15 — Is `risk_acceptance` or `consistency_verdict` mandatory?

Not stated. §8b and §7 only describe what to check *if* they exist.

I emit a **note**, not a refusal, when either is absent. **Guessed** (deliberately
permissive: refusing would invent a requirement).

## D16 — Malformed `manifest.sha256`

Line 17 fixes the format (64 lowercase hex + one LF, 65 bytes); §6b has no row for
a malformed manifest.

I refuse `REPORT_BUNDLE_INCONSISTENT`. **Guessed.**

## D17 — Malformed `.sig` (bad base64, wrong decoded length, interior whitespace)

Lines 27–30 say to decode tolerantly, that interior whitespace "should be
refused", and that both files are 88 base64 chars + LF — but no code is named for
a `.sig` that cannot be decoded.

I refuse `MISSING_EVIDENCE` (it cannot verify over any message form). **Guessed.**

## D18 — `.sig` present without `.pub`

Line 121 covers the reverse direction only (a `.role` without a `.sig` or `.pub`).

I refuse `MISSING_EVIDENCE`. **Guessed.**

## D19 — Stray files under `signatures/`

Lines 83–84 impose "nothing declared but absent, or present but undeclared" for
`objects/` only; no equivalent rule is stated for `signatures/`.

I ignore a lone `.pub` with no `.sig`/`.role`, and check once per file stem.
**Guessed.**

## D20 — Role file that is not a JSON object, or does not parse

I refuse `SIGNATURE_ROLE_UNKNOWN`. **No line.**

## D21 — How many refusals may one run produce?

Line 93 offers "One of: `SIGNED_AND_CONSISTENT`, or **a** refusal" (singular),
but several checks can fail at once — editing `bundle.json` breaks both
`bundle_version` and the address.

I report **all** failures, each with its own code and its own
expected/observed/next-action, and call the verdict `REFUSED` if any exists.
**Guessed**, on the strength of line 94 ("a failed check must produce a refusal
with a code — never an omission"): collapsing to one would omit failures.

## D22 — Pairing `.role`/`.sig`/`.pub` into "the same party"

Line 121 says "from the same party". §8 lines 148–149 say the file stem "names the
party everywhere else".

I pair by file stem. **Grounded** on line 148.

## D23 — `accepted_scope` present but not a string

Explicit at line 123 ("or `accepted_scope` is not a string") →
`RISK_ACCEPTANCE_INCOMPLETE`. Checked with `null` (case `m_scope_null`). **Not a
guess.**

---

## Things the page asserts that I could not check

- **`accepted_scope` bound as `"address"` must be refused for `risk_acceptance`**
  (lines 52, 105–106). Unenforceable as written: with no `.role` file there is no
  `asserts` field, so nothing in the bundle says the signer intended
  `risk_acceptance`. A verifier cannot distinguish "role-less signer that happens
  to be the acceptor" from any other role-less signer. I report the binding as
  `"address"` and can refuse only if the operator supplies the role assignment out
  of band, which the page never defines.
- **`policy_digest`** (lines 163–164) is an external reference; not checkable. I
  emit a note so silence is not read as a pass.
- **`NC-01`…`NC-11`** (lines 186–188): meanings unavailable; I compare them as
  opaque identifiers only.
- **`ensure_ascii=False`** (lines 192–193) — admitted untestable; both settings
  give identical bytes here. My implementation uses `False` as instructed.
- **Float rendering** (lines 194–198) — admitted unspecified. `0.133` round-trips
  under `repr`; `1.0`, `1e-7`, `-0.0` would be undecidable. My implementation
  relies on Python's shortest-round-trip `repr`.
- **`.role` trailing newline** (lines 199–201) — stated irrelevant, untested by
  the artifact. I parse JSON and re-canonicalise, so it is irrelevant in my code
  by construction.
