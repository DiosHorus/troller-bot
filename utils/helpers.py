"""
helpers.py - Funciones auxiliares para el Troller Bot
Incluye: logging en consola con colores, verificaciones de permisos, registro de errores.
Creado por +𝟝𝟠𝓵𝓸𝓬𝓸 (mas_58_loco) y Sandia [🍉] (prushkax)
"""

import os
import discord
from datetime import datetime
from colorama import Fore, Style, init

# Inicializar colorama
init(autoreset=True)

# ─────────────────────────────────────────────
# Constantes
# ─────────────────────────────────────────────
OWNER_ID = 1060078154141679667
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
LOGS_DIR = os.path.join(DATA_DIR, "logs")
ADMINS_DIR = os.path.join(DATA_DIR, "admins")

# Variable global para controlar si se muestran los logs de comandos en consola
SHOW_COMMAND_LOGS = True


# ─────────────────────────────────────────────
# Funciones de logging en consola con colores
# ─────────────────────────────────────────────

def _timestamp() -> str:
    """Retorna la marca de tiempo actual formateada."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log_info(mensaje: str) -> None:
    """Imprime un mensaje informativo en consola (azul)."""
    print(f"{Fore.CYAN}[{_timestamp()}] ℹ️  {mensaje}{Style.RESET_ALL}")


def log_success(mensaje: str) -> None:
    """Imprime un mensaje de éxito en consola (verde)."""
    print(f"{Fore.GREEN}[{_timestamp()}] ✅ {mensaje}{Style.RESET_ALL}")


def log_warning(mensaje: str) -> None:
    """Imprime un mensaje de advertencia en consola (amarillo)."""
    print(f"{Fore.YELLOW}[{_timestamp()}] ⚠️  {mensaje}{Style.RESET_ALL}")


def log_error_console(mensaje: str) -> None:
    """Imprime un mensaje de error en consola (rojo)."""
    print(f"{Fore.RED}[{_timestamp()}] ❌ {mensaje}{Style.RESET_ALL}")


def log_command(usuario: str, comando: str, servidor: str) -> None:
    """Imprime el uso de un comando en consola (magenta). Respeta SHOW_COMMAND_LOGS."""
    if SHOW_COMMAND_LOGS:
        print(
            f"{Fore.MAGENTA}[{_timestamp()}] 🔧 "
            f"Comando: /{comando} | Usuario: {usuario} | Servidor: {servidor}"
            f"{Style.RESET_ALL}"
        )


def log_bot_ready(bot_user: str, servidores: int) -> None:
    """Imprime el banner de inicio del bot."""
    banner = f"""
{Fore.GREEN}{'═' * 50}
  🤖 Troller Bot está en línea
  👤 Conectado como: {bot_user}
  🌐 Servidores: {servidores}
  📅 {_timestamp()}
{'═' * 50}{Style.RESET_ALL}"""
    print(banner)


# ─────────────────────────────────────────────
# Registro de errores en archivo
# ─────────────────────────────────────────────

def log_error(guild_id: int, comando: str, error: str) -> None:
    """
    Guarda un error en el archivo de logs del servidor correspondiente.
    Formato: [timestamp] Comando: /comando | Error: descripción
    """
    os.makedirs(LOGS_DIR, exist_ok=True)
    archivo = os.path.join(LOGS_DIR, f"{guild_id}.txt")
    linea = f"[{_timestamp()}] Comando: /{comando} | Error: {error}\n"
    try:
        with open(archivo, "a", encoding="utf-8") as f:
            f.write(linea)
        log_warning(f"Error registrado en logs del servidor {guild_id}")
    except Exception as e:
        log_error_console(f"No se pudo guardar el log: {e}")


def load_logs(guild_id: int) -> list[str]:
    """Carga las líneas de log de un servidor. Retorna lista vacía si no hay."""
    archivo = os.path.join(LOGS_DIR, f"{guild_id}.txt")
    if not os.path.exists(archivo):
        return []
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            return f.readlines()
    except Exception:
        return []


# ─────────────────────────────────────────────
# Verificaciones de permisos
# ─────────────────────────────────────────────

def is_owner(user_id: int) -> bool:
    """Verifica si el usuario es el dueño del bot."""
    return user_id == OWNER_ID


def is_bot_admin(user_id: int, guild_id: int, bot_admins: dict) -> bool:
    """
    Verifica si el usuario es admin del bot en el servidor dado.
    El dueño siempre es admin.
    bot_admins: dict[guild_id] -> set de user_ids
    """
    if is_owner(user_id):
        return True
    return user_id in bot_admins.get(guild_id, set())


def can_target(
    interaction_or_ctx,
    target: discord.Member,
    bot_admins: dict,
) -> tuple[bool, str]:
    """
    Verifica si el ejecutor puede aplicar acciones sobre el objetivo.
    Acepta tanto discord.Interaction (slash) como commands.Context (prefijo).
    Reglas:
      - No puedes actuar sobre ti mismo.
      - No puedes actuar sobre el dueño del bot.
      - No puedes actuar sobre otros admins del bot (a menos que seas el dueño).
      - No puedes actuar sobre alguien con rol igual o superior al tuyo.
    Retorna (puede_actuar, razón_si_no).
    """
    # Soportar tanto Interaction como Context
    if isinstance(interaction_or_ctx, discord.Interaction):
        ejecutor = interaction_or_ctx.user
        guild_id = interaction_or_ctx.guild_id
    else:
        # commands.Context
        ejecutor = interaction_or_ctx.author
        guild_id = interaction_or_ctx.guild.id

    if target.id == ejecutor.id:
        return False, "❌ No puedes aplicar esta acción sobre ti mismo."

    if is_owner(target.id):
        return False, "❌ No puedes aplicar esta acción sobre el dueño del bot."

    # Solo el dueño puede actuar sobre otros admins
    if is_bot_admin(target.id, guild_id, bot_admins) and not is_owner(ejecutor.id):
        return False, "❌ No puedes aplicar esta acción sobre otro admin del bot."

    # Verificar jerarquía de roles de Discord
    if isinstance(ejecutor, discord.Member) and isinstance(target, discord.Member):
        if target.top_role >= ejecutor.top_role and not is_owner(ejecutor.id):
            return False, "❌ No puedes aplicar esta acción sobre alguien con un rol igual o superior al tuyo."

    return True, ""
