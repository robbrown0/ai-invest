-- Execution-owned, tenant-scoped PAPER connection metadata; never credential bytes.
BEGIN;
CREATE TABLE ai_invest.web_connection (
    tenant_id uuid NOT NULL REFERENCES ai_invest.tenant(id),
    id uuid NOT NULL,
    broker_account_id uuid NOT NULL UNIQUE,
    mode text NOT NULL DEFAULT 'PAPER' CHECK (mode='PAPER'),
    state text NOT NULL CHECK (state IN ('CONNECTED','DISCONNECTED')),
    credential_version uuid,
    snapshot jsonb NOT NULL DEFAULT '{}' CHECK (octet_length(snapshot::text)<=262144),
    updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (tenant_id,id),
    CHECK ((state='CONNECTED')=(credential_version IS NOT NULL))
) USING tde_heap;
CREATE TABLE ai_invest.web_event (
    tenant_id uuid NOT NULL REFERENCES ai_invest.tenant(id),
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    connection_id uuid NOT NULL,
    actor text NOT NULL CHECK (actor ~ '^[a-f0-9]{64}$'),
    kind text NOT NULL CHECK (kind IN ('connected','replaced','disconnected','refreshed')),
    recorded_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (tenant_id,id),
    FOREIGN KEY (tenant_id,connection_id) REFERENCES ai_invest.web_connection(tenant_id,id)
) USING tde_heap;
CREATE TRIGGER web_event_immutable BEFORE UPDATE OR DELETE ON ai_invest.web_event
    FOR EACH ROW EXECUTE FUNCTION ai_invest.reject_mutation();
ALTER TABLE ai_invest.web_connection ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_invest.web_connection FORCE ROW LEVEL SECURITY;
ALTER TABLE ai_invest.web_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_invest.web_event FORCE ROW LEVEL SECURITY;
CREATE POLICY web_tenant ON ai_invest.web_connection
    USING (tenant_id IN (SELECT tenant_id FROM ai_invest.runtime_identity WHERE database_role=session_user))
    WITH CHECK (tenant_id IN (SELECT tenant_id FROM ai_invest.runtime_identity WHERE database_role=session_user));
CREATE POLICY web_tenant ON ai_invest.web_event
    USING (tenant_id IN (SELECT tenant_id FROM ai_invest.runtime_identity WHERE database_role=session_user))
    WITH CHECK (tenant_id IN (SELECT tenant_id FROM ai_invest.runtime_identity WHERE database_role=session_user));
REVOKE ALL ON ai_invest.web_connection,ai_invest.web_event FROM PUBLIC;
-- Fixed execution service identity; future tenants use distinct peer roles/processes.
CREATE ROLE ai_web_a LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
GRANT CONNECT ON DATABASE ai_invest TO ai_web_a;
GRANT USAGE ON SCHEMA ai_invest TO ai_web_a;
GRANT SELECT ON ai_invest.runtime_identity TO ai_web_a;
GRANT SELECT,INSERT,UPDATE ON ai_invest.web_connection TO ai_web_a;
GRANT SELECT,INSERT ON ai_invest.web_event TO ai_web_a;
WITH t AS (INSERT INTO ai_invest.tenant(id,label) VALUES(gen_random_uuid(),'Private PAPER web tenant') RETURNING id)
INSERT INTO ai_invest.runtime_identity SELECT 'ai_web_a',id FROM t;
COMMIT;
