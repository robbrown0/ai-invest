-- No tenant/account access; unauthenticated LAN sees service health only.
BEGIN;
CREATE ROLE ai_lan_status LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS CONNECTION LIMIT 2;
GRANT CONNECT ON DATABASE ai_invest TO ai_lan_status;
ALTER ROLE ai_lan_status SET statement_timeout='2s';
ALTER ROLE ai_lan_status SET idle_in_transaction_session_timeout='2s';
ALTER ROLE ai_lan_status SET default_transaction_read_only=on;
COMMIT;
