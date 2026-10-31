# NNN — one sentence that says what was checked

**Verdict:** could not tell

## Claim

What was done, in the words of the person who did it. One paragraph. If the claim needs a qualifier, the
qualifier belongs here and not in `Limits`.

## Evidence

Links with what each one proves: a transaction hash, a pinned commit, a log digest, a file in this folder. Name
the artifact and then say what a reader should conclude from it — a link without a sentence is a bookmark.

## Reproduce

The exact commands, in order, with the environment they assume. If a step needs a live database, say which and
say the port. A reader who cannot run it should learn that here, not after twenty minutes.

## Verdict

One of `confirmed`, `not confirmed`, `could not tell`, and the sentence that decides it. For `not confirmed`,
say which part was wrong: the claim, the method, or the tool.

## Limits

What this case does not establish. Always at least one line. For a case written by the person who wrote the
tool, the first line here is: *author-side run; does not count toward P1.*
