"""
Utility per gestione database - supporta PostgreSQL e SQLite
"""
import os

# Importa driver database appropriati
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

import sqlite3

# Configurazione database
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    USE_POSTGRES = True
    DATABASE = None
else:
    USE_POSTGRES = False
    DATABASE = 'piattaforma.db'


def get_db():
    """Connessione al database - supporta PostgreSQL e SQLite"""
    if USE_POSTGRES:
        if not POSTGRES_AVAILABLE:
            raise RuntimeError("psycopg2 non installato ma DATABASE_URL configurato")
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn


def execute_query(conn, query, params=None, fetch_one=False, fetch_all=False):
    """Helper per eseguire query con supporto PostgreSQL/SQLite"""
    if USE_POSTGRES:
        # PostgreSQL usa %s come placeholder
        query = query.replace('?', '%s')
        cursor = conn.cursor(cursor_factory=RealDictCursor)
    else:
        # SQLite usa ?
        cursor = conn.cursor()

    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)

    if fetch_one:
        result = cursor.fetchone()
        cursor.close()
        return result
    elif fetch_all:
        result = cursor.fetchall()
        cursor.close()
        return result
    else:
        return cursor
