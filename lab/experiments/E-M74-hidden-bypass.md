---
id: E-M74
hypothesis: H-M74
status: completed
base_commit: "cbc601b"
started: "2026-10-29T00:50:00+03:00"
finished: "2026-10-29T01:20:00+03:00"
environment: "Windows, CPython 3.13.11; fixture written to hide a bypass rather than list it"
command: "python enumerators/migrations/fg_enum_migrations.py --dir fixtures/hidden-bypass --schema sample2 --control function:sample2.review_transfer --out inbox/hidden.json --target-lock hidden@1"
threshold: "Pre-registered, from E-M73's next experiment: a bypass that exists only because two facts must be combined - a grant on a VIEW over a table, and a SECURITY DEFINER function - must appear in the inventory as a path whose target is the TABLE. If the enumerator only lists the view grant, the hidden bypass is not surfaced and the answer to 'what did the pair add' is 'nothing'."
result: "The fixture found three defects, one of them the point of the experiment. (1) A grant on a view was recorded against the VIEW, so the write to the base table was invisible: the inventory said 'role:app_rw -> table:sample2.accounts_v' and a reader had to know that the view is writable and writes accounts. Now the enumerator resolves CREATE VIEW ... AS SELECT ... FROM <table> and emits a view_trigger path whose target is the base table, with the how-field naming the mechanism. (2) SECURITY DEFINER was not flagged at all, although it is precisely how a caller writes a table it holds no grant on; now it is a field. (3) A keyword leaked into a table position ('public.GRANT') and a word from a comment became a target ('public.without'); targets are now restricted to identifiers the file itself creates. Regressions: the earlier corpus and both cores are unchanged (E-M70 still passes)."
verdict: supports
---

# E-M74 — the hidden bypass: what the fixture found in my own enumerator

## The fixture

`fixtures/hidden-bypass/V1__hidden.sql` is written to hide a path rather than list it:

```sql
CREATE VIEW sample2.accounts_v AS SELECT id, balance FROM sample2.accounts;
CREATE TRIGGER accounts_v_write INSTEAD OF UPDATE ON sample2.accounts_v
    FOR EACH ROW EXECUTE FUNCTION sample2.accounts_v_update();   -- the body UPDATEs accounts
GRANT SELECT, UPDATE ON sample2.accounts_v TO app_rw;             -- the grant is on the VIEW
GRANT EXECUTE ON FUNCTION sample2.set_balance(...) TO app_rw;     -- SECURITY DEFINER writes accounts
```

A reader of the catalogue sees a grant on a view and a function they may not look into. Neither line says
"`app_rw` can rewrite `accounts.balance`".

## What was wrong before the fix

```
privilege      role:app_rw        target=table:sample2.accounts_v     ← the view, not the table
function       ...accounts_v_update  target=public.GRANT              ← a keyword as a table
function       ...accounts_v_update  target=public.without            ← a word from a comment
```

So the inventory was **correct about paths and wrong about targets**: the write it named landed on a view whose
writability the consumer had to infer, and one function's target was a word from a prose comment. A consumer
reading the inventory would not learn that `app_rw` can rewrite balances.

## After the three fixes

```
function       function:sample2.accounts_v_update  target=sample2.accounts
function       function:sample2.set_balance        target=sample2.accounts   security_definer=true
trigger_chain  trigger:accounts_v_write            target=table:sample2.accounts_v
view_trigger   role:app_rw                         target=table:sample2.accounts
      how: GRANT SELECT, UPDATE ON view sample2.accounts_v TO app_rw; the view is writable and its write
           lands on sample2.accounts
observed_write stmt:UPDATE sample2.accounts        target=table:sample2.accounts
```

1. **View → base table.** `CREATE VIEW ... AS SELECT ... FROM <table>` is parsed, and a grant on a view produces
   a `view_trigger` path whose target is the table, with the mechanism in `how`. This is the experiment's point.
2. **`security_definer`** is now a field. A definer function writes a table the caller holds no grant on, which is
   the second way in that the catalogue hides.
3. **Targets are restricted to identifiers the file creates.** A word after `FROM` in a comment is not a table.

## What this says about E-M73's open question

`E-M73` concluded that our artifact made an answer auditable but not better, and named this experiment as the one
that could show a real recall gain. The fixture shows the mechanism now exists in the enumerator — but it also
shows why the earlier paired evaluation could not have shown a gain: **the schema it used had every path listed in
the catalogue**. A measurement can only distinguish the arms if the catalogue is insufficient, and my first
fixture was not.

## What this still does not do

- It does not run the paired evaluation on this fixture. That is the next step, and the pre-registered threshold is
  the same: arm B must find strictly more true bypasses, no more false ones.
- It does not resolve nests: a view over a view over a table, or a definer function that calls another definer
  function. One level is handled; more is not, and the source note should say so.
- It does not change the ceiling. A hidden bypass surfaced by the tool is still a claim about a document.
