-- A three-path migration used by the ritual: one function that writes, one trigger that fires, one grant.
-- Not a real schema; it exists so the migrations enumerator is exercised without a database.

CREATE TABLE IF NOT EXISTS sample.accounts (
    id          bigserial PRIMARY KEY,
    balance     numeric NOT NULL DEFAULT 0,
    updated_at  timestamptz NOT NULL DEFAULT now()
);

CREATE OR REPLACE FUNCTION sample.update_updated_at_column()
RETURNS trigger AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sample_accounts_updated_at
    BEFORE UPDATE ON sample.accounts
    FOR EACH ROW EXECUTE FUNCTION sample.update_updated_at_column();

CREATE OR REPLACE FUNCTION sample.apply_transfer(p_from bigint, p_to bigint, p_amount numeric)
RETURNS void AS $$
BEGIN
    UPDATE sample.accounts SET balance = balance - p_amount WHERE id = p_from;
    UPDATE sample.accounts SET balance = balance + p_amount WHERE id = p_to;
END;
$$ LANGUAGE plpgsql;

GRANT INSERT, UPDATE ON sample.accounts TO app_rw;
