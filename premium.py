# =========================
# PREMIUM — Lógica de servidores premium y sistema de keys
# =========================
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional

import discord
from premium_db import execute, executemany, commit

# =========================
# CACHÉ EN MEMORIA — consultas rápidas sin tocar SQLite cada vez
# =========================
# guild_id -> {"is_premium": bool, "premium_expires": str|None, "claimed_key": str|None}
_premium_cache: dict[int, dict] = {}


def _generate_code() -> str:
    """Genera un código de activación estilo TROLLER-XXXX-XXXX-XXXX."""
    part = lambda: ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    return f"TROLLER-{part()}-{part()}-{part()}"


def parse_duration(raw: str) -> Optional[timedelta]:
    """Convierte una string tipo '7d', '30d', '1m', '1y', 'permanent' a timedelta o None (permanente)."""
    raw = raw.strip().lower()
    if raw in ("permanent", "perm", "permanente", "forever"):
        return None  # None = sin expiración
    import re
    match = re.match(r"^(\d+)\s*(d|m|y|w|h)$", raw)
    if not match:
        return None  # inválido, el caller debe manejar
    num = int(match.group(1))
    unit = match.group(2)
    multipliers = {"h": 1/24, "d": 1, "w": 7, "m": 30, "y": 365}
    return timedelta(days=num * multipliers.get(unit, 1))


def format_duration(raw: str) -> str:
    """Devuelve una representación legible de la duración."""
    raw = raw.strip().lower()
    if raw in ("permanent", "perm", "permanente", "forever"):
        return "Permanente"
    return raw.upper()


# =========================
# GENERACIÓN DE KEYS
# =========================
def generate_keys(creator_id: int, duration_raw: str, count: int = 1) -> list[str]:
    """Genera `count` keys con la duración especificada. Devuelve la lista de códigos."""
    delta = parse_duration(duration_raw)
    if delta is None and duration_raw.lower() not in ("permanent", "perm", "permanente", "forever"):
        raise ValueError(f"Duración inválida: {duration_raw}. Usá ej: 7d, 30d, 1m, 1y, permanent")

    key_expires = None
    if delta is not None:
        key_expires = (datetime.utcnow() + timedelta(days=365*5)).strftime("%Y-%m-%d %H:%M:%S")

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    codes = []
    rows = []
    for _ in range(count):
        code = _generate_code()
        codes.append(code)
        rows.append((code, duration_raw, key_expires, 0, None, None, creator_id, now))

    executemany(
        "INSERT INTO premium_keys (code, duration, key_expires_at, is_used, claimed_by_guild, claimed_at, created_by, created_at) "
        "VALUES (?,?,?,?,?,?,?,?)",
        rows
    )
    commit()
    return codes


# =========================
# CLAIM DE KEY
# =========================
def claim_key(guild_id: int, code: str) -> tuple[bool, str]:
    """
    Intenta activar una key en un servidor.
    Retorna (éxito, mensaje).
    """
    code = code.strip().upper()

    # Buscar la key
    row = execute(
        "SELECT code, duration, key_expires_at, is_used, claimed_by_guild FROM premium_keys WHERE code = ?",
        (code,)
    ).fetchone()

    if row is None:
        return False, "❌ Esa key no existe. Verificá el código e intentá de nuevo."

    db_code, duration_raw, key_expires_at, is_used, claimed_by = row

    if is_used:
        if claimed_by == guild_id:
            return False, "⚠️ Este servidor ya activó esta key anteriormente."
        return False, "❌ Esa key ya fue usada por otro servidor."

    # Verificar si la key en sí expiró (no es lo mismo que la duración del premium)
    if key_expires_at:
        if datetime.utcnow() > datetime.strptime(key_expires_at, "%Y-%m-%d %H:%M:%S"):
            return False, "⏰ Esa key ya expiró y no puede ser activada."

    # Verificar si el server ya tiene premium activo
    existing = execute(
        "SELECT is_premium, premium_expires FROM premium_servers WHERE guild_id = ?",
        (guild_id,)
    ).fetchone()

    if existing and existing[0]:
        if existing[1]:
            exp = datetime.strptime(existing[1], "%Y-%m-%d %H:%M:%S")
            if datetime.utcnow() < exp:
                return False, f"✅ Este servidor ya tiene premium activo hasta **{exp.strftime('%d/%m/%Y')}**."

    # Calcular expiración del premium
    delta = parse_duration(duration_raw)
    premium_expires = None
    if delta is not None:
        premium_expires = (datetime.utcnow() + delta).strftime("%Y-%m-%d %H:%M:%S")

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Marcar key como usada
    execute(
        "UPDATE premium_keys SET is_used = 1, claimed_by_guild = ?, claimed_at = ? WHERE code = ?",
        (guild_id, now, code)
    )

    # Upsert en premium_servers
    execute(
        "INSERT OR REPLACE INTO premium_servers (guild_id, is_premium, premium_expires, claimed_key, activated_at) "
        "VALUES (?, 1, ?, ?, ?)",
        (guild_id, premium_expires, code, now)
    )
    commit()

    # Actualizar caché
    _premium_cache[guild_id] = {
        "is_premium": True,
        "premium_expires": premium_expires,
        "claimed_key": code,
    }

    if premium_expires:
        exp_date = datetime.strptime(premium_expires, "%Y-%m-%d %H:%M:%S")
        return True, f"🎉 ¡Premium activado! Tu servidor tiene acceso a **todos los comandos** hasta **{exp_date.strftime('%d/%m/%Y')}**."
    else:
        return True, "🎉 ¡Premium **permanente** activado! Tu servidor tiene acceso a **todos los comandos** para siempre."


# =========================
# VALIDACIÓN DE PREMIUM
# =========================
def is_premium(guild_id: int) -> bool:
    """Devuelve True si el servidor tiene premium activo (con chequeo de expiración)."""
    # Revisar caché primero
    cached = _premium_cache.get(guild_id)
    if cached is not None and cached.get("is_premium"):
        if cached.get("premium_expires"):
            exp = datetime.strptime(cached["premium_expires"], "%Y-%m-%d %H:%M:%S")
            if datetime.utcnow() >= exp:
                # Expirado — actualizar DB y caché
                execute("UPDATE premium_servers SET is_premium = 0 WHERE guild_id = ?", (guild_id,))
                commit()
                _premium_cache[guild_id] = {"is_premium": False, "premium_expires": None, "claimed_key": None}
                return False
        return True

    # Consultar DB
    row = execute(
        "SELECT is_premium, premium_expires, claimed_key FROM premium_servers WHERE guild_id = ?",
        (guild_id,)
    ).fetchone()

    if row is None or not row[0]:
        _premium_cache[guild_id] = {"is_premium": False, "premium_expires": None, "claimed_key": None}
        return False

    _, premium_expires, claimed_key = row

    if premium_expires:
        exp = datetime.strptime(premium_expires, "%Y-%m-%d %H:%M:%S")
        if datetime.utcnow() >= exp:
            execute("UPDATE premium_servers SET is_premium = 0 WHERE guild_id = ?", (guild_id,))
            commit()
            _premium_cache[guild_id] = {"is_premium": False, "premium_expires": None, "claimed_key": None}
            return False

    _premium_cache[guild_id] = {
        "is_premium": True,
        "premium_expires": premium_expires,
        "claimed_key": claimed_key,
    }
    return True


def get_premium_status(guild_id: int) -> dict:
    """Devuelve el estado premium del servidor."""
    row = execute(
        "SELECT is_premium, premium_expires, claimed_key, activated_at FROM premium_servers WHERE guild_id = ?",
        (guild_id,)
    ).fetchone()

    if row is None or not row[0]:
        return {"is_premium": False, "premium_expires": None, "claimed_key": None, "activated_at": None}

    _, premium_expires, claimed_key, activated_at = row

    # Chequear expiración
    if premium_expires:
        exp = datetime.strptime(premium_expires, "%Y-%m-%d %H:%M:%S")
        if datetime.utcnow() >= exp:
            execute("UPDATE premium_servers SET is_premium = 0 WHERE guild_id = ?", (guild_id,))
            commit()
            return {"is_premium": False, "premium_expires": None, "claimed_key": None, "activated_at": None}

    return {
        "is_premium": True,
        "premium_expires": premium_expires,
        "claimed_key": claimed_key,
        "activated_at": activated_at,
    }


def get_keys_by_creator(creator_id: int) -> list[dict]:
    """Devuelve todas las keys creadas por un usuario."""
    rows = execute(
        "SELECT code, duration, key_expires_at, is_used, claimed_by_guild, claimed_at, created_at "
        "FROM premium_keys WHERE created_by = ? ORDER BY created_at DESC",
        (creator_id,)
    ).fetchall()

    return [
        {
            "code": r[0],
            "duration": r[1],
            "key_expires_at": r[2],
            "is_used": bool(r[3]),
            "claimed_by_guild": r[4],
            "claimed_at": r[5],
            "created_at": r[6],
        }
        for r in rows
    ]


# =========================
# EXPIRACIÓN MASIVA (startup)
# =========================
def check_all_expired() -> int:
    """
    Revisa todos los servidores premium con fecha de expiración
    y desactiva los que ya expiraron. Retorna cuántos expiraron.
    """
    rows = execute(
        "SELECT guild_id, premium_expires FROM premium_servers WHERE is_premium = 1 AND premium_expires IS NOT NULL"
    ).fetchall()

    expired = 0
    now = datetime.utcnow()
    for guild_id, premium_expires in rows:
        exp = datetime.strptime(premium_expires, "%Y-%m-%d %H:%M:%S")
        if now >= exp:
            execute("UPDATE premium_servers SET is_premium = 0 WHERE guild_id = ?", (guild_id,))
            _premium_cache[guild_id] = {"is_premium": False, "premium_expires": None, "claimed_key": None}
            expired += 1

    if expired:
        commit()

    return expired


# =========================
# CARGA INICIAL DEL CACHÉ
# =========================
def load_all_premium():
    """Carga todos los servidores premium al caché de memoria (se llama en on_ready)."""
    rows = execute(
        "SELECT guild_id, is_premium, premium_expires, claimed_key FROM premium_servers WHERE is_premium = 1"
    ).fetchall()

    now = datetime.utcnow()
    for guild_id, _, premium_expires, claimed_key in rows:
        if premium_expires:
            if now >= datetime.strptime(premium_expires, "%Y-%m-%d %H:%M:%S"):
                execute("UPDATE premium_servers SET is_premium = 0 WHERE guild_id = ?", (guild_id,))
                continue
        _premium_cache[guild_id] = {
            "is_premium": True,
            "premium_expires": premium_expires,
            "claimed_key": claimed_key,
        }

    commit()
