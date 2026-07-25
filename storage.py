# =========================
# STORAGE — Estado en memoria y persistencia en SQLite
# =========================
import re
from pathlib import Path
import discord
from config import OWNER_ID
from db import execute, executemany, commit

# =========================
# VARIABLES EN MEMORIA (sesión — no persisten)
# =========================
shhh_users:        set[int]        = set()
repetidor_users:   set[int]        = set()
fantasma_users:    dict[int, dict] = {}
random_nick_users: set[int]        = set()
spam_call_users:   set[int]        = set()
falacias_users:    set[int]        = set()
invertir_users:    set[int]        = set()
ACCESS_MODES:      dict[int, str]  = {}   # guild_id -> "admin_only" | "role" | "everyone"
ACCESS_ROLES:      dict[int, int]  = {}   # guild_id -> role_id

# =========================
# UTILIDADES (solo para migración)
# =========================
def sanitize_name(name: str) -> str:
    name = name.strip().replace(" ", "_")
    name = re.sub(r"[^\w\-]", "", name, flags=re.UNICODE)
    return name[:60] if name else "Servidor"


# =========================
# ADMINS
# =========================
def load_admins(guild: discord.Guild) -> set:
    rows = execute("SELECT user_id FROM admins WHERE guild_id=?", (guild.id,)).fetchall()
    admins = {row[0] for row in rows}
    admins.add(OWNER_ID)
    return admins


def save_admins(guild: discord.Guild, admins: set):
    execute("BEGIN IMMEDIATE")
    execute("DELETE FROM admins WHERE guild_id=?", (guild.id,))
    data = [(guild.id, uid) for uid in admins if uid != OWNER_ID]
    if data:
        executemany("INSERT INTO admins (guild_id, user_id) VALUES (?,?)", data)
    commit()


# =========================
# MUTED
# =========================
def load_muted(guild: discord.Guild) -> set:
    rows = execute("SELECT user_id FROM muted WHERE guild_id=?", (guild.id,)).fetchall()
    return {row[0] for row in rows}


def save_muted(guild: discord.Guild, data: set):
    execute("BEGIN IMMEDIATE")
    execute("DELETE FROM muted WHERE guild_id=?", (guild.id,))
    if data:
        executemany("INSERT INTO muted (guild_id, user_id) VALUES (?,?)",
                     [(guild.id, uid) for uid in data])
    commit()


# =========================
# DEAFENED
# =========================
def load_deafened(guild: discord.Guild) -> set:
    rows = execute("SELECT user_id FROM deafened WHERE guild_id=?", (guild.id,)).fetchall()
    return {row[0] for row in rows}


def save_deafened(guild: discord.Guild, data: set):
    execute("BEGIN IMMEDIATE")
    execute("DELETE FROM deafened WHERE guild_id=?", (guild.id,))
    if data:
        executemany("INSERT INTO deafened (guild_id, user_id) VALUES (?,?)",
                     [(guild.id, uid) for uid in data])
    commit()


# =========================
# VOICE BANNED
# =========================
def load_voice_banned(guild: discord.Guild) -> set:
    rows = execute("SELECT user_id FROM voice_banned WHERE guild_id=?", (guild.id,)).fetchall()
    return {row[0] for row in rows}


def save_voice_banned(guild: discord.Guild, data: set):
    execute("BEGIN IMMEDIATE")
    execute("DELETE FROM voice_banned WHERE guild_id=?", (guild.id,))
    if data:
        executemany("INSERT INTO voice_banned (guild_id, user_id) VALUES (?,?)",
                     [(guild.id, uid) for uid in data])
    commit()


# =========================
# FORCED NICKS
# =========================
def load_forced_nicks(guild: discord.Guild) -> dict:
    rows = execute(
        "SELECT user_id, nick FROM forced_nicks WHERE guild_id=?", (guild.id,)
    ).fetchall()
    return {row[0]: row[1] for row in rows}


def save_forced_nicks(guild: discord.Guild, data: dict):
    execute("BEGIN IMMEDIATE")
    execute("DELETE FROM forced_nicks WHERE guild_id=?", (guild.id,))
    if data:
        executemany("INSERT INTO forced_nicks (guild_id, user_id, nick) VALUES (?,?,?)",
                     [(guild.id, uid, nick) for uid, nick in sorted(data.items())])
    commit()


# =========================
# LOG CHANNEL
# =========================
def load_log_channel_id(guild: discord.Guild):
    row = execute(
        "SELECT log_channel_id FROM guild_settings WHERE guild_id=?", (guild.id,)
    ).fetchone()
    return row[0] if row else None


def save_log_channel_id(guild: discord.Guild, channel_id: int):
    execute(
        "INSERT INTO guild_settings (guild_id, log_channel_id) VALUES (?,?) "
        "ON CONFLICT(guild_id) DO UPDATE SET log_channel_id=excluded.log_channel_id",
        (guild.id, channel_id)
    )
    commit()


# =========================
# ACCESS CONFIG
# =========================
def load_access_config(guild: discord.Guild):
    row = execute(
        "SELECT access_mode, access_role_id FROM guild_settings WHERE guild_id=?",
        (guild.id,)
    ).fetchone()
    if row:
        ACCESS_MODES[guild.id] = row[0]
        ACCESS_ROLES[guild.id] = row[1]
    else:
        ACCESS_MODES[guild.id] = "admin_only"
        ACCESS_ROLES[guild.id] = None
        execute(
            "INSERT OR IGNORE INTO guild_settings (guild_id) VALUES (?)",
            (guild.id,)
        )
        commit()


def save_access_config(guild: discord.Guild):
    mode = ACCESS_MODES.get(guild.id, "admin_only")
    role_id = ACCESS_ROLES.get(guild.id)
    execute(
        "INSERT INTO guild_settings (guild_id, access_mode, access_role_id) VALUES (?,?,?) "
        "ON CONFLICT(guild_id) DO UPDATE SET access_mode=excluded.access_mode, access_role_id=excluded.access_role_id",
        (guild.id, mode, role_id)
    )
    commit()


# =========================
# MIGRACIÓN — one-time: txt → SQLite
# =========================
_LOG_LINE_RE = re.compile(
    r"^\[(.+?)\] (.+?) \((\d+)\) usó /(\S+?)(?: contra (.+?) \((\d+)\))?(?:\s*\|\s*(.*))?$"
)


def _migrate_id_set(guild_id: int, file_path: Path, table: str):
    """Lee un archivo de IDs (uno por línea) y los inserta en la tabla dada."""
    if not file_path.exists():
        return 0
    count = 0
    try:
        for line in file_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.isdigit():
                execute(f"INSERT OR IGNORE INTO {table} (guild_id, user_id) VALUES (?,?)",
                        (guild_id, int(line)))
                count += 1
    except Exception as e:
        print(f"❌ Error migrando {file_path.name}: {e}")
    return count


def _migrate_forced_nicks(guild_id: int, file_path: Path):
    """Lee forced_nicks (uid|nick por línea) e inserta en la tabla."""
    if not file_path.exists():
        return 0
    count = 0
    try:
        for line in file_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or "|" not in line:
                continue
            user_id_str, nick = line.split("|", 1)
            if user_id_str.isdigit():
                execute(
                    "INSERT OR IGNORE INTO forced_nicks (guild_id, user_id, nick) VALUES (?,?,?)",
                    (guild_id, int(user_id_str), nick)
                )
                count += 1
    except Exception as e:
        print(f"❌ Error migrando {file_path.name}: {e}")
    return count


def _migrate_log_channel(guild_id: int, file_path: Path):
    """Lee log_channel (un solo integer) y hace upsert en guild_settings."""
    if not file_path.exists():
        return False
    try:
        value = file_path.read_text(encoding="utf-8").strip()
        if value.isdigit():
            execute(
                "INSERT INTO guild_settings (guild_id, log_channel_id) VALUES (?,?) "
                "ON CONFLICT(guild_id) DO UPDATE SET log_channel_id=excluded.log_channel_id",
                (guild_id, int(value))
            )
            return True
    except Exception as e:
        print(f"❌ Error migrando {file_path.name}: {e}")
    return False


def _migrate_access_config(guild_id: int, file_path: Path):
    """Lee access_config (modo en línea 1, role_id opcional en línea 2)."""
    if not file_path.exists():
        return False
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
        mode = lines[0].strip() if lines else "admin_only"
        role_id = int(lines[1].strip()) if len(lines) > 1 and lines[1].strip().isdigit() else None
        execute(
            "INSERT INTO guild_settings (guild_id, access_mode, access_role_id) VALUES (?,?,?) "
            "ON CONFLICT(guild_id) DO UPDATE SET access_mode=excluded.access_mode, access_role_id=excluded.access_role_id",
            (guild_id, mode, role_id)
        )
        return True
    except Exception as e:
        print(f"❌ Error migrando {file_path.name}: {e}")
    return False


def _migrate_action_logs(guild_id: int, file_path: Path):
    """Parsea log-{guild}.txt e inserta cada línea en action_logs."""
    if not file_path.exists():
        return 0
    count = 0
    try:
        for line in file_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            m = _LOG_LINE_RE.match(line)
            if not m:
                continue
            timestamp, actor_name, actor_id, command = m.group(1), m.group(2), int(m.group(3)), m.group(4)
            target_name = m.group(5) if m.group(5) else None
            target_id   = int(m.group(6)) if m.group(6) else None
            details     = m.group(7).strip() if m.group(7) else None

            execute(
                "INSERT INTO action_logs (guild_id, timestamp, actor_name, actor_id, command, target_name, target_id, details) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (guild_id, timestamp, actor_name, actor_id, command, target_name, target_id, details)
            )
            count += 1
    except Exception as e:
        print(f"❌ Error migrando {file_path.name}: {e}")
    return count


def run_migration(bot) -> bool:
    """
    Migra datos de archivos txt viejos a SQLite (one-time).
    Retorna True si se ejecutó la migración, False si ya estaba hecha o no había datos.
    """
    # Verificar si ya hay datos migrados
    row = execute("SELECT COUNT(*) FROM action_logs").fetchone()
    if row and row[0] > 0:
        return False  # Ya migrado

    # Verificar si hay al menos algún archivo txt que migrar
    has_files = (
        list(Path(".").glob("admins_*.txt"))
        or list(Path(".").glob("muted_*.txt"))
        or list(Path(".").glob("log-*.txt"))
    )
    if not has_files:
        return False

    print("🔄 Iniciando migración de txt a SQLite...")
    migrated_anything = False
    cleaned_files = set()

    for guild in bot.guilds:
        safe_name = sanitize_name(guild.name)
        guild_id = guild.id

        # Mapeo: categoría → (tabla, función migradora)
        categories = [
            ("admins",       "admins",        _migrate_id_set),
            ("muted",        "muted",         _migrate_id_set),
            ("deafened",     "deafened",      _migrate_id_set),
            ("voice_banned", "voice_banned",  _migrate_id_set),
        ]

        for cat_name, table, func in categories:
            fp = Path(f"{cat_name}_{safe_name}.txt")
            if fp.exists():
                n = func(guild_id, fp, table)
                if n:
                    print(f"   ✅ {fp.name}: {n} registros → {table}")
                    migrated_anything = True
                cleaned_files.add(fp)

        # Forced nicks
        fp_nicks = Path(f"forced_nicks_{safe_name}.txt")
        if fp_nicks.exists():
            n = _migrate_forced_nicks(guild_id, fp_nicks)
            if n:
                print(f"   ✅ {fp_nicks.name}: {n} nicks → forced_nicks")
                migrated_anything = True
            cleaned_files.add(fp_nicks)

        # Log channel
        fp_lc = Path(f"log_channel_{safe_name}.txt")
        if fp_lc.exists():
            if _migrate_log_channel(guild_id, fp_lc):
                print(f"   ✅ {fp_lc.name} → guild_settings.log_channel_id")
                migrated_anything = True
            cleaned_files.add(fp_lc)

        # Access config
        fp_ac = Path(f"access_config_{safe_name}.txt")
        if fp_ac.exists():
            if _migrate_access_config(guild_id, fp_ac):
                print(f"   ✅ {fp_ac.name} → guild_settings")
                migrated_anything = True
            cleaned_files.add(fp_ac)

        # Action logs
        fp_log = Path(f"log-{safe_name}.txt")
        if fp_log.exists():
            n = _migrate_action_logs(guild_id, fp_log)
            if n:
                print(f"   ✅ {fp_log.name}: {n} líneas → action_logs")
                migrated_anything = True
            cleaned_files.add(fp_log)

    if migrated_anything:
        commit()
        # Borrar archivos migrados
        for fp in cleaned_files:
            try:
                fp.unlink()
            except Exception as e:
                print(f"⚠️ No se pudo borrar {fp.name}: {e}")
        print("✅ Migración completada. Archivos txt eliminados.")
    else:
        print("ℹ️  No se encontraron datos para migrar.")

    return migrated_anything
