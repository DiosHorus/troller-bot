# =========================
# LOGGER — Sistema de logs con embeds + archivos
# =========================
from datetime import datetime
from pathlib import Path
import discord
from storage import load_log_channel_id
from db import execute, commit

# =========================
# LOGS EN ARCHIVO
# =========================
LOG_DIR = Path(__file__).parent / "logs"
PREMIUM_LOG = LOG_DIR / "premium.log"
COMMANDS_LOG = LOG_DIR / "commands.log"

# Comandos del sistema premium (se muestran en consola + premium.log)
PREMIUM_COMMANDS = {"claim", "genkey", "premium", "keys"}


def _write_log(filepath: Path, line: str):
    """Escribe una línea a un archivo de log. Crea el directorio si no existe."""
    try:
        LOG_DIR.mkdir(exist_ok=True)
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"❌ Error escribiendo log en {filepath}: {e}")


# =========================
# LOGS CON EMBED
# =========================
LOG_COLORS = {
    "silenciar": discord.Color.orange(),    "ensordecer": discord.Color.orange(),
    "castigar":  discord.Color.red(),       "liberar":    discord.Color.green(),
    "expulsar":  discord.Color.dark_red(),  "fakeban":    discord.Color.dark_red(),
    "unfakeban": discord.Color.green(),     "forcenick":  discord.Color.blue(),
    "unforcenick": discord.Color.blue(),    "randomnick": discord.Color.blue(),
    "nickspam":  discord.Color.blue(),      "shhh":       discord.Color.greyple(),
    "fantasma":  discord.Color.purple(),    "unfantasma": discord.Color.purple(),
    "repetidor": discord.Color.gold(),      "falacias":   discord.Color.gold(),
    "invertir":  discord.Color.gold(),      "spamcall":   discord.Color.teal(),
    "lobotomy":  discord.Color.teal(),      "paranoia":   discord.Color.dark_purple(),
    "addadmin":  discord.Color.brand_green(), "removeadmin": discord.Color.brand_red(),
    "suggest":   discord.Color.blurple(),   "log":        discord.Color.blurple(),
    "accessmode": discord.Color.yellow(),
    "sound":      discord.Color.green(),      "stop":       discord.Color.red(),
    "claim":      discord.Color.gold(),       "genkey":     discord.Color.gold(),
}

LOG_EMOJIS = {
    "silenciar": "🔇", "ensordecer": "🔕", "castigar": "⛓️",  "liberar": "🔓",
    "expulsar":  "👢", "fakeban":    "🔨", "unfakeban": "✅",  "forcenick": "📛",
    "unforcenick": "📛", "randomnick": "🎲", "nickspam": "🔥", "shhh": "🤫",
    "fantasma":  "👻", "unfantasma": "👻", "repetidor": "🔁", "falacias": "🌀",
    "invertir":  "🙃", "spamcall":   "📞", "lobotomy":  "🧠", "paranoia": "👁️",
    "addadmin":  "🛡️", "removeadmin": "❌", "suggest":  "💡", "log": "📋",
    "accessmode": "⚙️",
    "sound":      "🔊",      "stop":       "⏹️",
    "claim":      "🔑",      "genkey":     "🔑",
}


async def log_action(guild: discord.Guild, actor, command_name: str, target=None, details=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    emoji = LOG_EMOJIS.get(command_name, "⚡")
    color = LOG_COLORS.get(command_name, discord.Color.blurple())

    # ── Archivo: commands.log (TODOS los comandos, sin consola) ──
    target_str = f"{target} ({target.id})" if target else "-"
    details_str = f" | {details}" if details else ""
    log_line = f"[{timestamp}] {guild.name} | {actor} | /{command_name} | Target: {target_str}{details_str}"
    _write_log(COMMANDS_LOG, log_line)

    # ── Consola + premium.log (solo comandos premium) ──
    if command_name in PREMIUM_COMMANDS:
        premium_line = f"🔑 [{timestamp}] {guild.name} | {actor} | /{command_name} | Target: {target_str}{details_str}"
        print(premium_line)
        _write_log(PREMIUM_LOG, premium_line)

    # Insertar en base de datos
    try:
        execute(
            "INSERT INTO action_logs (guild_id, timestamp, actor_name, actor_id, command, target_name, target_id, details) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (guild.id, timestamp, str(actor), actor.id, command_name,
             str(target) if target else None,
             target.id if target else None,
             details)
        )
        commit()
    except Exception as e:
        print(f"❌ Error guardando log en DB: {e}")

    # Embed al canal de logs
    channel_id = load_log_channel_id(guild)
    if not channel_id:
        return
    channel = guild.get_channel(channel_id)
    if not isinstance(channel, discord.TextChannel):
        return

    embed = discord.Embed(title=f"{emoji} /{command_name}", color=color, timestamp=datetime.now())
    embed.add_field(
        name="👤 Ejecutado por",
        value=f"{actor.mention}\n`{actor} ({actor.id})`",
        inline=True
    )
    if target:
        embed.add_field(
            name="🎯 Objetivo",
            value=f"{target.mention}\n`{target} ({target.id})`",
            inline=True
        )
    if details:
        embed.add_field(name="📝 Detalles", value=details, inline=False)
    embed.set_footer(
        text=f"Troller Bot • {guild.name}",
        icon_url=guild.icon.url if guild.icon else None
    )
    if actor.display_avatar:
        embed.set_thumbnail(url=actor.display_avatar.url)

    try:
        await channel.send(embed=embed)
    except Exception as e:
        print(f"❌ Error enviando log embed: {e}")
