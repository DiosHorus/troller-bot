# =========================
# DB — Conexión SQLite y esquema
# =========================
import atexit
import sqlite3
import threading
from pathlib import Path

DB_PATH = Path(__file__).parent / "Base de Datos" / "trollerbot.db"

_connection: sqlite3.Connection | None = None
_lock = threading.Lock()


def get_connection() -> sqlite3.Connection:
    """Devuelve la conexión singleton a la base de datos. Thread-safe."""
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
    """Crea las tablas e índices si no existen. Idempotente."""
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS guild_settings (
            guild_id        INTEGER PRIMARY KEY,
            log_channel_id  INTEGER,
            access_mode     TEXT NOT NULL DEFAULT 'admin_only',
            access_role_id  INTEGER
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            guild_id  INTEGER NOT NULL,
            user_id   INTEGER NOT NULL,
            PRIMARY KEY (guild_id, user_id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS muted (
            guild_id  INTEGER NOT NULL,
            user_id   INTEGER NOT NULL,
            PRIMARY KEY (guild_id, user_id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS deafened (
            guild_id  INTEGER NOT NULL,
            user_id   INTEGER NOT NULL,
            PRIMARY KEY (guild_id, user_id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS voice_banned (
            guild_id  INTEGER NOT NULL,
            user_id   INTEGER NOT NULL,
            PRIMARY KEY (guild_id, user_id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS forced_nicks (
            guild_id  INTEGER NOT NULL,
            user_id   INTEGER NOT NULL,
            nick      TEXT    NOT NULL,
            PRIMARY KEY (guild_id, user_id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS action_logs (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id     INTEGER NOT NULL,
            timestamp    TEXT    NOT NULL,
            actor_name   TEXT    NOT NULL,
            actor_id     INTEGER NOT NULL,
            command      TEXT    NOT NULL,
            target_name  TEXT,
            target_id    INTEGER,
            details      TEXT
        )
    """)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_action_logs_guild  ON action_logs(guild_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_action_logs_target ON action_logs(target_id)")

    conn.commit()


# Cerrar conexión al salir
atexit.register(lambda: _connection.close() if _connection else None)
