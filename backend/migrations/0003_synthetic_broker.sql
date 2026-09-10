-- Durable DISCONNECTED broker fixture; never used for brokerage account data.
BEGIN;
CREATE TABLE ai_invest.synthetic_broker (
    tenant_id uuid NOT NULL,
    account_id uuid NOT NULL,
    body jsonb NOT NULL CHECK (jsonb_typeof(body)='object' AND octet_length(body::text)<=524288),
    PRIMARY KEY (tenant_id,account_id),
    FOREIGN KEY (tenant_id,account_id) REFERENCES ai_invest.runtime_ledger(tenant_id,account_id)
) USING tde_heap;
ALTER TABLE ai_invest.synthetic_broker ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_invest.synthetic_broker FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_login ON ai_invest.synthetic_broker
    USING (tenant_id IN (SELECT tenant_id FROM ai_invest.runtime_identity WHERE database_role=session_user))
    WITH CHECK (tenant_id IN (SELECT tenant_id FROM ai_invest.runtime_identity WHERE database_role=session_user));
REVOKE ALL ON ai_invest.synthetic_broker FROM PUBLIC;
COMMIT;
