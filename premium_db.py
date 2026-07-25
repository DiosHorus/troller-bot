# =========================
# PREMIUM_DB — Base de datos de keys y servidores premium
# =========================
import atexit
import sqlite3
import threading
from pathlib import Path

DB_PATH = Path(__file__).parent / "Base de Datos" / "premium.db"

_connection: sqlite3.Connection | None = None
_lock = threading.Lock()


def get_connection() -> sqlite3.Connection:
    """Devuelve la conexión singleton a la base de datos premium. Thread-safe."""
    global _connection
    if _connection is None:
        with _lock:
            if _connection is None:
                _connection = sqlite3.connect(str(DB_PATH), check_same_thread=False)
                _connection.execute("PRAGMA journal_mode=WAL")
                _connection.execute("PRAGMA foreign_keys=OFF")
                init_db()
    return _connection


def execute(sql: str, params: tuple = ()):
    """Ejecuta una sentencia SQL y devuelve el cursor."""
    conn = get_connection()
    return conn.execute(sql, params)


def executemany(sql: str, seq: list):
    """Ejecuta una sentencia SQL con múltiples parámetros."""
    conn = get_connection()
    return conn.executemany(sql, seq)


def commit():
    """Commit manual de la conexión."""
    if _connection:
        _connection.commit()


def init_db():
    """Crea las tablas si no existen. Idempotente."""
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS premium_keys (
            code              TEXT PRIMARY KEY,
            duration          TEXT NOT NULL,
            key_expires_at    TEXT,
            is_used           INTEGER NOT NULL DEFAULT 0,
            claimed_by_guild  INTEGER,
            claimed_at        TEXT,
            created_by        INTEGER NOT NULL,
            created_at        TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS premium_servers (
            guild_id         INTEGER PRIMARY KEY,
            is_premium       INTEGER NOT NULL DEFAULT 0,
            premium_expires  TEXT,
            claimed_key      TEXT,
            activated_at     TEXT
        )
    """)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_premium_keys_used  ON premium_keys(is_used)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_premium_keys_guild ON premium_keys(claimed_by_guild)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_premium_servers_exp ON premium_servers(premium_expires)")

    conn.commit()


# Cerrar conexión al salir
atexit.register(lambda: _connection.close() if _connection else None)
