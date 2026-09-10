"""PostgreSQL ledger access; no connection strings or secret loading.

Accepts an already-authenticated psycopg 3 connection from the protected
runtime. Does not apply migrations or grant privileges.
"""
from contextlib import contextmanager
import json
import re

from .intents import Scope


class DatabaseRefused(RuntimeError):
    def __init__(self):
        super().__init__('database_unavailable_or_unqualified')


class PostgresLedger:
    def __init__(self, connection, scope):
        if type(scope) is not Scope or not connection.autocommit:
            raise DatabaseRefused()
        self.connection, self.scope = connection, scope
        try:
            role = connection.execute('SELECT rolsuper,rolbypassrls,current_user=session_user '
                'FROM pg_catalog.pg_roles WHERE rolname=session_user').fetchone()
            if role != (False, False, True): raise DatabaseRefused()
            if connection.execute('SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_auth_members '
                'WHERE member=(SELECT oid FROM pg_catalog.pg_roles WHERE rolname=session_user))').fetchone()[0]:
                raise DatabaseRefused()
            identity = connection.execute('SELECT tenant_id FROM ai_invest.runtime_identity WHERE database_role=session_user').fetchall()
            if identity != [(scope.tenant_id,)]: raise DatabaseRefused()
            tables = connection.execute("SELECT c.relname,a.amname,c.relrowsecurity,c.relforcerowsecurity,"
                "pg_catalog.pg_get_userbyid(c.relowner)=session_user FROM pg_catalog.pg_class c "
                "JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace JOIN pg_catalog.pg_am a ON a.oid=c.relam "
                "WHERE n.nspname='ai_invest' AND c.relname IN ('runtime_identity','runtime_ledger','runtime_event')").fetchall()
            if len(tables) != 3 or any(row[1:] != ('tde_heap', True, True, False) for row in tables):
                raise DatabaseRefused()
        except Exception:
            raise DatabaseRefused() from None

    def _parameters(self, scope):
        if scope != self.scope: raise DatabaseRefused()
        return (scope.tenant_id, scope.account_id, scope.portfolio_id)

    def read(self, scope):
        try:
            row = self.connection.execute('SELECT body FROM ai_invest.runtime_ledger '
                'WHERE tenant_id=%s AND account_id=%s AND portfolio_id=%s', self._parameters(scope)).fetchone()
            if row is None: raise DatabaseRefused()
            return row[0]
        except Exception:
            raise DatabaseRefused() from None

    def events(self, scope):
        params=self._parameters(scope)
        return self.connection.execute('SELECT revision,kind FROM ai_invest.runtime_event '
            'WHERE tenant_id=%s AND account_id=%s ORDER BY revision',params[:2]).fetchall()

    def close(self):
        self.connection.close()

    @contextmanager
    def transaction(self, scope, event):
        if type(event) is not str or re.fullmatch('[a-z_]{1,40}', event) is None: raise DatabaseRefused()
        params = self._parameters(scope)
        try:
            with self.connection.transaction():
                self.connection.execute("SET LOCAL lock_timeout='5s'")
                self.connection.execute("SET LOCAL statement_timeout='5s'")
                row = self.connection.execute('SELECT revision,body FROM ai_invest.runtime_ledger '
                    'WHERE tenant_id=%s AND account_id=%s AND portfolio_id=%s FOR UPDATE', params).fetchone()
                if row is None: raise DatabaseRefused()
                revision, state = row
                before = json.dumps(state, sort_keys=True)
                yield state
                body = json.dumps(state, sort_keys=True, allow_nan=False)
                if len(body.encode()) > 524288: raise DatabaseRefused()
                if body != before:
                    changed = self.connection.execute('UPDATE ai_invest.runtime_ledger SET revision=%s,body=%s::jsonb '
                        'WHERE tenant_id=%s AND account_id=%s AND portfolio_id=%s AND revision=%s',
                        (revision+1,body,*params,revision))
                    if changed.rowcount != 1: raise DatabaseRefused()
                    self.connection.execute('INSERT INTO ai_invest.runtime_event '
                        '(tenant_id,account_id,revision,kind,body) VALUES (%s,%s,%s,%s,%s::jsonb)',
                        (scope.tenant_id,scope.account_id,revision+1,event,body))
        except Exception:
            raise DatabaseRefused() from None
