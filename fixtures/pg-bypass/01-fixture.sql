-- Fixture: a small "bank" with one declared control point and eight planted bypasses.
--
-- The declared contract of this system, as its own documentation would state it:
--   "All writes to bank.accounts go through bank.transfer()."
-- Every plant below violates that statement in a different way, so that an enumerator can be
-- measured against a known ground truth instead of against its own imagination.
--
-- Plant list (see expected.json for ids and classes):
--   P1  direct UPDATE grant to the application role
--   P2  direct INSERT grant to the application role
--   P3  SECURITY DEFINER function that writes accounts
--   P4  plain function with no permission check that writes accounts
--   P5  audit trigger that exists and is DISABLED
--   P6  view with an INSTEAD OF trigger that writes accounts
--   P7  function that writes accounts through dynamic SQL
--   P8  trigger on another table that writes accounts (indirect chain)

DROP SCHEMA IF EXISTS bank CASCADE;
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_rw') THEN
    EXECUTE 'DROP OWNED BY app_rw';
    EXECUTE 'DROP ROLE app_rw';
  END IF;
END $$;
CREATE SCHEMA bank;

CREATE ROLE app_rw LOGIN PASSWORD 'app_rw';

CREATE TABLE bank.accounts (
  id      integer PRIMARY KEY,
  balance numeric NOT NULL DEFAULT 0
);

CREATE TABLE bank.audit_events (
  id      bigserial PRIMARY KEY,
  note    text
);

-- The declared control point.
CREATE FUNCTION bank.transfer(src integer, dst integer, amt numeric)
RETURNS void LANGUAGE plpgsql AS $$
BEGIN
  IF amt <= 0 THEN RAISE EXCEPTION 'amount must be positive'; END IF;
  UPDATE bank.accounts SET balance = balance - amt WHERE id = src;
  UPDATE bank.accounts SET balance = balance + amt WHERE id = dst;
END $$;

GRANT USAGE ON SCHEMA bank TO app_rw;
GRANT EXECUTE ON FUNCTION bank.transfer(integer, integer, numeric) TO app_rw;

-- P1 / P2: direct table privileges, which bypass transfer() entirely.
GRANT UPDATE ON bank.accounts TO app_rw;   -- P1
GRANT INSERT ON bank.accounts TO app_rw;   -- P2

-- P3: a SECURITY DEFINER writer — runs with the owner's rights and reaches the table directly.
CREATE FUNCTION bank.credit_direct(acct integer, amt numeric)
RETURNS void LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
  UPDATE bank.accounts SET balance = balance + amt WHERE id = acct;
END $$;
GRANT EXECUTE ON FUNCTION bank.credit_direct(integer, numeric) TO app_rw;

-- P4: an ordinary function that writes the table with no check at all.
CREATE FUNCTION bank.set_balance(acct integer, amt numeric)
RETURNS void LANGUAGE plpgsql AS $$
BEGIN
  UPDATE bank.accounts SET balance = amt WHERE id = acct;
END $$;
GRANT EXECUTE ON FUNCTION bank.set_balance(integer, numeric) TO app_rw;

-- P5: a control that exists in the catalogue but is switched off.
CREATE FUNCTION bank.audit_accounts()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO bank.audit_events(note) VALUES ('accounts changed');
  RETURN NEW;
END $$;
CREATE TRIGGER accounts_audit BEFORE UPDATE ON bank.accounts
  FOR EACH ROW EXECUTE FUNCTION bank.audit_accounts();
ALTER TABLE bank.accounts DISABLE TRIGGER accounts_audit;   -- P5

-- P6: a view whose INSTEAD OF trigger writes the table.
CREATE VIEW bank.v_accounts AS SELECT id, balance FROM bank.accounts;
CREATE FUNCTION bank.v_accounts_write()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  UPDATE bank.accounts SET balance = NEW.balance WHERE id = NEW.id;
  RETURN NEW;
END $$;
CREATE TRIGGER v_accounts_ins INSTEAD OF UPDATE ON bank.v_accounts
  FOR EACH ROW EXECUTE FUNCTION bank.v_accounts_write();
GRANT UPDATE ON bank.v_accounts TO app_rw;

-- P7: dynamic SQL — visible only if the enumerator searches function bodies as text.
CREATE FUNCTION bank.adjust_dynamic(acct integer, amt numeric)
RETURNS void LANGUAGE plpgsql AS $$
BEGIN
  EXECUTE format('UPDATE bank.accounts SET balance = balance + %s WHERE id = %s', amt, acct);
END $$;
GRANT EXECUTE ON FUNCTION bank.adjust_dynamic(integer, numeric) TO app_rw;

-- P8: an indirect chain — writing one table causes a write to accounts.
CREATE FUNCTION bank.audit_to_accounts()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  UPDATE bank.accounts SET balance = balance + 1 WHERE id = 1;
  RETURN NEW;
END $$;
CREATE TRIGGER audit_events_write AFTER INSERT ON bank.audit_events
  FOR EACH ROW EXECUTE FUNCTION bank.audit_to_accounts();
GRANT INSERT ON bank.audit_events TO app_rw;

INSERT INTO bank.accounts(id, balance) VALUES (1, 1000), (2, 500);

-- ---------------------------------------------------------------------------
-- Legitimate callers: paths that DO pass through the declared control point.
-- Attribution is what these exist to test: a call-graph enumerator must mark
-- them as inside the core, and must not be fooled by names.
-- ---------------------------------------------------------------------------

CREATE FUNCTION bank.transfer_via_api(src integer, dst integer, amt numeric)
RETURNS void LANGUAGE plpgsql AS $$
BEGIN
  PERFORM bank.transfer(src, dst, amt);
END $$;
GRANT EXECUTE ON FUNCTION bank.transfer_via_api(integer, integer, numeric) TO app_rw;

CREATE FUNCTION bank.transfer_batch(ids integer[], amt numeric)
RETURNS void LANGUAGE plpgsql AS $$
DECLARE i integer;
BEGIN
  FOR i IN 1 .. array_length(ids, 1) - 1 LOOP
    PERFORM bank.transfer_via_api(ids[i], ids[i+1], amt);
  END LOOP;
END $$;
GRANT EXECUTE ON FUNCTION bank.transfer_batch(integer[], numeric) TO app_rw;

-- Decoy: named as if it were a transfer, writes the table directly.
CREATE FUNCTION bank.transfer_fast(acct integer, amt numeric)
RETURNS void LANGUAGE plpgsql AS $$
BEGIN
  UPDATE bank.accounts SET balance = balance + amt WHERE id = acct;
END $$;
GRANT EXECUTE ON FUNCTION bank.transfer_fast(integer, numeric) TO app_rw;

-- A cascade INTO the target: deleting a branch deletes its accounts. Invisible to grants, function
-- bodies and triggers; the enumerator missed this class entirely on a production schema (E-M41).
CREATE TABLE bank.branches (id integer PRIMARY KEY, name text);
ALTER TABLE bank.accounts ADD COLUMN IF NOT EXISTS branch_id integer
  REFERENCES bank.branches(id) ON DELETE CASCADE;
