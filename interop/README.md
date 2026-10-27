# interop — notes between the repositories

The channel between `flowguard-spec`, `VecDHT` and `-`. Not a chat, not a task, not an obligation: **notes**.

## Protocol

1. One note, one file: `interop/YYYY-MM-DD-<from>-<to>.md`.
2. A published note is **never edited**. If it was wrong, the next note says so.
3. The header always carries: the commit the note was written from, and the commit it addresses. Without both,
   a note is an opinion.
4. Each repository keeps its own language (`VecDHT` in Russian, `flowguard-spec` in English). The sender archives
   its own translation and links the original.
5. No reply is required. Reply only when there is something to say.
6. **Nothing but files under `interop/`** ever goes into another repository: no edits, no dependencies, no
   refactoring requests.

## Why notes instead of a chat

A note is pinned to a commit, so in a month it is still clear which state of the code was being discussed.
A conversation does not survive that, and memory does not either.

## Index

| date | from | to | about |
|---|---|---|---|
| 2026-10-27 | flowguard-spec | VecDHT | first compatibility pass: the M1–M7 method kit, what we take, what we give, what we do not ask for |
| 2026-10-27 | flowguard-spec | VecDHT | corrections to myself after reading their lab/: their claim map is a different dimension rather than a missing registry; M7 protocol draft; two questions on gives and 	argets |
