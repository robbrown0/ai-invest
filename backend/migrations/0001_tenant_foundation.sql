-- NOT APPLIED. Requires separately provisioned/qualified Percona + pg_tde keys.
-- This migration creates no key, login, credential, tenant data or runtime grant.
-- No plaintext fallback. Actual TDE/WAL/restore/RLS qualification remains required.
BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '30s';

DO $guard$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_extension WHERE extname = 'pg_tde')
       OR NOT EXISTS (SELECT 1 FROM pg_catalog.pg_am WHERE amname = 'tde_heap') THEN
        RAISE EXCEPTION 'qualified_pg_tde_required';
    END IF;
END
$guard$;

CREATE SCHEMA ai_invest;
REVOKE ALL ON SCHEMA ai_invest FROM PUBLIC;

CREATE TABLE ai_invest.tenant (
    id uuid PRIMARY KEY,
    label varchar(120) NOT NULL CHECK (length(label) > 0),
    suspended boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP
) USING tde_heap;

CREATE TABLE ai_invest.brokerage_account (
    tenant_id uuid NOT NULL REFERENCES ai_invest.tenant(id),
    id uuid NOT NULL,
    provider text NOT NULL CHECK (provider = 'alpaca'),
    mode text NOT NULL CHECK (mode = 'PAPER'),
    currency text NOT NULL CHECK (currency = 'USD'),
    stopped boolean NOT NULL DEFAULT true,
    stop_epoch bigint NOT NULL DEFAULT 0 CHECK (stop_epoch >= 0),
    PRIMARY KEY (tenant_id, id)
) USING tde_heap;

CREATE TABLE ai_invest.portfolio (
    tenant_id uuid NOT NULL REFERENCES ai_invest.tenant(id),
    id uuid NOT NULL,
    account_id uuid,
    mode text NOT NULL CHECK (mode IN ('BACKTEST', 'PAPER', 'SHADOW')),
    currency text NOT NULL CHECK (currency = 'USD'),
    virtual_capital numeric NOT NULL CHECK (virtual_capital > 0 AND virtual_capital <= 1000000000 AND scale(virtual_capital) <= 9),
    active boolean NOT NULL DEFAULT false,
    stopped boolean NOT NULL DEFAULT true,
    PRIMARY KEY (tenant_id, id),
    FOREIGN KEY (tenant_id, account_id) REFERENCES ai_invest.brokerage_account(tenant_id, id),
    CHECK ((mode = 'PAPER' AND account_id IS NOT NULL) OR (mode <> 'PAPER' AND account_id IS NULL)),
    UNIQUE (tenant_id, id, account_id)
) USING tde_heap;

CREATE UNIQUE INDEX one_active_paper_portfolio_per_account
    ON ai_invest.portfolio (tenant_id, account_id) WHERE active AND mode = 'PAPER';

CREATE TABLE ai_invest.trade_proposal (
    tenant_id uuid NOT NULL,
    id uuid NOT NULL,
    portfolio_id uuid NOT NULL,
    account_id uuid NOT NULL,
    security_id uuid NOT NULL,
    mode text NOT NULL CHECK (mode = 'PAPER'),
    side text NOT NULL CHECK (side IN ('BUY', 'SELL')),
    quantity numeric NOT NULL CHECK (quantity > 0 AND quantity <= 1000000000 AND scale(quantity) <= 9),
    limit_price numeric NOT NULL CHECK (limit_price > 0 AND limit_price <= 1000000000 AND scale(limit_price) <= 9),
    payload_digest text NOT NULL CHECK (payload_digest ~ '^[0-9a-f]{64}$'),
    created_at timestamptz NOT NULL,
    expires_at timestamptz NOT NULL CHECK (expires_at > created_at),
    PRIMARY KEY (tenant_id, id),
    FOREIGN KEY (tenant_id, portfolio_id, account_id)
        REFERENCES ai_invest.portfolio (tenant_id, id, account_id)
) USING tde_heap;

CREATE TABLE ai_invest.audit_event (
    tenant_id uuid NOT NULL REFERENCES ai_invest.tenant(id),
    id uuid NOT NULL,
    event_type text NOT NULL CHECK (event_type ~ '^[a-z][a-z0-9_]{0,63}$'),
    subject_id uuid NOT NULL,
    subject_digest text NOT NULL CHECK (subject_digest ~ '^[0-9a-f]{64}$'),
    occurred_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (tenant_id, id)
) USING tde_heap;

CREATE FUNCTION ai_invest.reject_mutation() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog AS $immutable$
BEGIN
    RAISE EXCEPTION 'append_only_record';
END
$immutable$;
REVOKE ALL ON FUNCTION ai_invest.reject_mutation() FROM PUBLIC;
CREATE TRIGGER immutable_proposal BEFORE UPDATE OR DELETE ON ai_invest.trade_proposal
    FOR EACH ROW EXECUTE FUNCTION ai_invest.reject_mutation();
CREATE TRIGGER immutable_audit BEFORE UPDATE OR DELETE ON ai_invest.audit_event
    FOR EACH ROW EXECUTE FUNCTION ai_invest.reject_mutation();

-- Intentionally no policies and no runtime grants yet: default deny, not a
-- caller-controlled SET app.tenant_id. Trusted access paths need separate tests.
ALTER TABLE ai_invest.tenant ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_invest.tenant FORCE ROW LEVEL SECURITY;
ALTER TABLE ai_invest.brokerage_account ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_invest.brokerage_account FORCE ROW LEVEL SECURITY;
ALTER TABLE ai_invest.portfolio ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_invest.portfolio FORCE ROW LEVEL SECURITY;
ALTER TABLE ai_invest.trade_proposal ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_invest.trade_proposal FORCE ROW LEVEL SECURITY;
ALTER TABLE ai_invest.audit_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_invest.audit_event FORCE ROW LEVEL SECURITY;
REVOKE ALL ON ALL TABLES IN SCHEMA ai_invest FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA ai_invest FROM PUBLIC;
COMMIT;
