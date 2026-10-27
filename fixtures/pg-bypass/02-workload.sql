-- A workload with a known set of writes to bank.accounts.
-- Two of them pass through the control point, three do not. A runtime source that watches the
-- server log must see five distinct writes; a catalogue source cannot tell them apart by execution.

-- through the control point (legitimate)
SELECT bank.transfer(1, 2, 10);
SELECT bank.transfer_via_api(1, 2, 5);

-- direct, each a different shape
INSERT INTO bank.accounts(id, balance) VALUES (901, 0);
UPDATE bank.accounts SET balance = 0 WHERE id = 901;
DELETE FROM bank.accounts WHERE id = 901;
