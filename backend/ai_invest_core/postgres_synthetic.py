"""Disconnected broker fixture with durable PostgreSQL state; no networking.

Uses a separate connection/transaction from the application's order ledger so
acceptance survives a client process crash, as an independent broker would.
"""
from contextlib import contextmanager
import json

from .postgres import PostgresLedger, DatabaseRefused
from .synthetic import SyntheticBroker, SCOPES


class PostgresSyntheticBroker(SyntheticBroker):
    def __init__(self, connection, scope):
        if scope not in SCOPES: raise DatabaseRefused()
        self.ledger=PostgresLedger(connection,scope)
        self.connection=connection
        self.scope=scope
        self.partial=self.timeout=False
        row=connection.execute("SELECT a.amname,c.relrowsecurity,c.relforcerowsecurity,"
            "pg_get_userbyid(c.relowner)=session_user FROM pg_class c JOIN pg_am a ON c.relam=a.oid "
            "WHERE c.oid='ai_invest.synthetic_broker'::regclass").fetchone()
        if row!=('tde_heap',True,True,False): raise DatabaseRefused()

    def snapshot(self,scope):
        params=self.ledger._parameters(scope)
        row=self.connection.execute('SELECT body FROM ai_invest.synthetic_broker '
            'WHERE tenant_id=%s AND account_id=%s',params[:2]).fetchone()
        if row is None: raise DatabaseRefused()
        return row[0]

    @contextmanager
    def _change(self,scope):
        params=self.ledger._parameters(scope)
        with self.connection.transaction():
            self.connection.execute("SET LOCAL lock_timeout='5s'")
            self.connection.execute("SET LOCAL statement_timeout='5s'")
            row=self.connection.execute('SELECT body FROM ai_invest.synthetic_broker '
                'WHERE tenant_id=%s AND account_id=%s FOR UPDATE',params[:2]).fetchone()
            if row is None: raise DatabaseRefused()
            state=row[0]
            yield state
            body=json.dumps(state,allow_nan=False)
            if len(body.encode())>524288: raise DatabaseRefused()
            changed=self.connection.execute('UPDATE ai_invest.synthetic_broker SET body=%s::jsonb '
                'WHERE tenant_id=%s AND account_id=%s',(body,*params[:2]))
            if changed.rowcount!=1: raise DatabaseRefused()

    def close(self):
        self.connection.close()
