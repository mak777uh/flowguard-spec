-- A bypass that is not listed anywhere: the grant is on a VIEW, the write lands on the TABLE.
-- A reader of the catalogue sees "GRANT UPDATE ON accounts_v TO app_rw" and must infer that accounts_v is
-- updatable and that its updatable-ness reaches accounts. Nothing in the migration says so directly.

CREATE TABLE sample2.accounts (
    id      bigserial PRIMARY KEY,
    balance numeric NOT NULL DEFAULT 0
);

CREATE VIEW sample2.accounts_v AS SELECT id, balance FROM sample2.accounts;

-- an INSTEAD OF trigger makes the view writable, and its body writes the table
CREATE OR REPLACE FUNCTION sample2.accounts_v_update()
RETURNS trigger AS $$
BEGIN
    UPDATE sample2.accounts SET balance = NEW.balance WHERE id = NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER accounts_v_write
    INSTEAD OF UPDATE ON sample2.accounts_v
    FOR EACH ROW EXECUTE FUNCTION sample2.accounts_v_update();

-- the privilege is granted on the view, not on the table
GRANT SELECT, UPDATE ON sample2.accounts_v TO app_rw;

-- and a SECURITY DEFINER function: the caller writes the table without holding any grant on it
CREATE OR REPLACE FUNCTION sample2.set_balance(p_id bigint, p_amount numeric)
RETURNS void AS $$
BEGIN
    UPDATE sample2.accounts SET balance = p_amount WHERE id = p_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION sample2.set_balance(bigint, numeric) TO app_rw;
