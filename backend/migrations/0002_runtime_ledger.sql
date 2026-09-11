-- UNAPPLIED. No roles/credentials/keys/grants are provisioned here.
-- Tenant login roles, ownership mapping and encrypted runtime require qualification.
BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '30s';

CREATE TABLE ai_invest.runtime_identity (
    database_role name PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES ai_invest.tenant(id)
) USING tde_heap;
ALTER TABLE ai_invest.runtime_identity ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_invest.runtime_identity FORCE ROW LEVEL SECURITY;
CREATE POLICY own_login ON ai_invest.runtime_identity
    FOR SELECT USING (database_role = session_user);

CREATE TABLE ai_invest.runtime_ledger (
    tenant_id uuid NOT NULL,
    account_id uuid NOT NULL,
    portfolio_id uuid NOT NULL,
    revision bigint NOT NULL DEFAULT 0 CHECK (revision >= 0),
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object' AND octet_length(body::text) <= 524288),
    PRIMARY KEY (tenant_id, account_id),
    FOREIGN KEY (tenant_id, portfolio_id, account_id)
        REFERENCES ai_invest.portfolio(tenant_id, id, account_id)
) USING tde_heap;

CREATE TABLE ai_invest.runtime_event (
    tenant_id uuid NOT NULL,
    account_id uuid NOT NULL,
    revision bigint NOT NULL CHECK (revision > 0),
    kind text NOT NULL CHECK (kind ~ '^[a-z_]{1,40}$'),
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object' AND octet_length(body::text) <= 524288),
    recorded_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (tenant_id, account_id, revision),
    FOREIGN KEY (tenant_id, account_id) REFERENCES ai_invest.runtime_ledger(tenant_id, account_id)
) USING tde_heap;
CREATE TRIGGER runtime_event_immutable BEFORE UPDATE OR DELETE ON ai_invest.runtime_event
    FOR EACH ROW EXECUTE FUNCTION ai_invest.reject_mutation();

ALTER TABLE ai_invest.runtime_ledger ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_invest.runtime_ledger FORCE ROW LEVEL SECURITY;
ALTER TABLE ai_invest.runtime_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_invest.runtime_event FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_login ON ai_invest.runtime_ledger
    USING (tenant_id IN (SELECT tenant_id FROM ai_invest.runtime_identity WHERE database_role = session_user))
    WITH CHECK (tenant_id IN (SELECT tenant_id FROM ai_invest.runtime_identity WHERE database_role = session_user));
CREATE POLICY tenant_login ON ai_invest.runtime_event
    USING (tenant_id IN (SELECT tenant_id FROM ai_invest.runtime_identity WHERE database_role = session_user))
    WITH CHECK (tenant_id IN (SELECT tenant_id FROM ai_invest.runtime_identity WHERE database_role = session_user));
REVOKE ALL ON ai_invest.runtime_identity, ai_invest.runtime_ledger, ai_invest.runtime_event FROM PUBLIC;
COMMIT;
