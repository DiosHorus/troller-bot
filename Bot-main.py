"""
Bot-main.py - Punto de entrada principal del Troller Bot
Un bot de moderación/troll para Discord.
Creado por +𝟝𝟠𝓵𝓸𝓬𝓸 (mas_58_loco) y Sandia [🍉] (prushkax)

Uso:
  1. Copia .env.example a .env y coloca tu token
  2. Instala dependencias: pip install -r requirements.txt
  3. Ejecuta: python Bot-main.py
"""

import os
import sys
import asyncio
import threading
import discord
from discord import app_commands
from dotenv import load_dotenv
from colorama import Fore, Style, init as colorama_init

# Inicializar colorama
colorama_init(autoreset=True)

# Cargar variables de entorno desde .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print(f"{Fore.RED}❌ Error: No se encontró DISCORD_TOKEN en el archivo .env{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}💡 Copia .env.example a .env y coloca tu token de Discord.{Style.RESET_ALL}")
    sys.exit(1)

# ─────────────────────────────────────────────
# Importar módulos propios
# ─────────────────────────────────────────────
from utils.helpers import (
    log_info,
    log_success,
    log_warning,
    log_error_console,
    log_bot_ready,
    OWNER_ID,
)
from commands import admin as admin_module
from commands import moderation as moderation_module
from commands import logs as logs_module
from commands import audio as audio_module

# ─────────────────────────────────────────────
# Configuración del bot
# ─────────────────────────────────────────────

# Toggle para mostrar/ocultar logs de uso de comandos en consola
SHOW_COMMAND_LOGS = True

# Configurar intents
intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.message_content = True

# Crear el cliente del bot
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# ─────────────────────────────────────────────
# Estructuras de datos globales (por servidor)
# dict[guild_id] -> set de user_ids
# ─────────────────────────────────────────────
muted_users: dict[int, set] = {}
deafened_users: dict[int, set] = {}
voice_banned_users: dict[int, set] = {}
bot_admins: dict[int, set] = {}

# ─────────────────────────────────────────────
# Aplicar el toggle de SHOW_COMMAND_LOGS a helpers
# ─────────────────────────────────────────────
import utils.helpers as helpers_mod
helpers_mod.SHOW_COMMAND_LOGS = SHOW_COMMAND_LOGS


# ─────────────────────────────────────────────
# Eventos del bot
# ─────────────────────────────────────────────

@bot.event
async def on_ready():
    """Se ejecuta cuando el bot está listo y conectado."""
    global bot_admins

    # Cargar admins de todos los servidores
    bot_admins.update(admin_module.load_all_admins(bot))

    # Asegurar que el dueño esté en la lista de admins de cada servidor
    for guild in bot.guilds:
        if guild.id not in bot_admins:
            bot_admins[guild.id] = {OWNER_ID}
        else:
            bot_admins[guild.id].add(OWNER_ID)

    # Registrar comandos de cada módulo
    moderation_module.setup(bot, tree, muted_users, deafened_users, voice_banned_users, bot_admins)
    admin_module.setup(bot, tree, bot_admins)
    logs_module.setup(bot, tree, bot_admins)
    audio_module.setup(bot, tree, bot_admins)

    # Sincronizar el árbol de comandos con Discord
    try:
        synced = await tree.sync()
        log_success(f"Se sincronizaron {len(synced)} comando(s) slash.")
    except Exception as e:
        log_error_console(f"Error sincronizando comandos: {e}")

    # Mostrar banner de inicio
    log_bot_ready(str(bot.user), len(bot.guilds))

    # Iniciar la consola interactiva en un hilo separado
    threading.Thread(target=_console_input, daemon=True).start()


@bot.event
async def on_voice_state_update(
    member: discord.Member,
    before: discord.VoiceState,
    after: discord.VoiceState,
):
    """
    Evento que se dispara cuando un usuario cambia su estado de voz.
    Se usa para:
      - Re-mutear usuarios que intentan desmutear
      - Re-ensordecer usuarios que intentan desensordecerse
      - Desconectar usuarios con ban de voz
    """
    guild_id = member.guild.id

    # ─── Voice ban: desconectar si entra a un canal ───
    if member.id in voice_banned_users.get(guild_id, set()):
        if after.channel is not None:
            try:
                await member.move_to(None, reason="Ban de voz activo - Troller Bot")
                log_warning(f"🚫 {member} intentó unirse a voz pero tiene ban de voz en {member.guild.name}")
            except discord.Forbidden:
                log_error_console(f"Sin permisos para desconectar a {member} (voice ban)")
            return

    # ─── Re-mute: si el usuario está en la lista y se desmutea ───
    if member.id in muted_users.get(guild_id, set()):
        if after.channel is not None and not after.mute:
            try:
                await member.edit(mute=True, reason="Re-mute automático - Troller Bot")
                log_warning(f"🔇 {member} intentó desmutear pero fue re-muteado en {member.guild.name}")
            except discord.Forbidden:
                log_error_console(f"Sin permisos para re-mutear a {member}")

    # ─── Re-deafen: si el usuario está en la lista y se desensordece ───
    if member.id in deafened_users.get(guild_id, set()):
        if after.channel is not None and not after.deaf:
            try:
                await member.edit(deafen=True, reason="Re-deafen automático - Troller Bot")
                log_warning(f"🔈 {member} intentó desensordecerse pero fue re-ensordecido en {member.guild.name}")
            except discord.Forbidden:
                log_error_console(f"Sin permisos para re-ensordecer a {member}")


# ─────────────────────────────────────────────
# Consola interactiva (/test desde terminal)
# ─────────────────────────────────────────────

def _console_input():
    """
    Hilo que escucha comandos desde la consola de Python.
    Soporta:
      /test  - Verificar que el bot está funcionando
      /stats - Mostrar estadísticas del bot
      /quit  - Apagar el bot
    """
    while True:
        try:
            entrada = input()
            if entrada.strip().lower() == "/test":
                print(
                    f"\n{Fore.GREEN}{'─' * 40}\n"
                    f"  ✅ El bot está funcionando correctamente\n"
                    f"  🤖 Usuario: {bot.user}\n"
                    f"  🌐 Servidores: {len(bot.guilds)}\n"
                    f"  📡 Latencia: {round(bot.latency * 1000)}ms\n"
                    f"  🔇 Usuarios muteados: {sum(len(s) for s in muted_users.values())}\n"
                    f"  🔈 Usuarios ensordecidos: {sum(len(s) for s in deafened_users.values())}\n"
                    f"  🚫 Usuarios con ban de voz: {sum(len(s) for s in voice_banned_users.values())}\n"
                    f"{'─' * 40}{Style.RESET_ALL}\n"
                )
            elif entrada.strip().lower() == "/stats":
                print(
                    f"\n{Fore.CYAN}{'─' * 40}\n"
                    f"  📊 Estadísticas del Troller Bot\n"
                    f"  🌐 Servidores: {len(bot.guilds)}\n"
                    f"  👥 Usuarios totales: {sum(g.member_count or 0 for g in bot.guilds)}\n"
                    f"  👑 Admins totales: {sum(len(s) for s in bot_admins.values())}\n"
                    f"{'─' * 40}{Style.RESET_ALL}\n"
                )
            elif entrada.strip().lower() == "/quit":
                print(f"{Fore.YELLOW}⏏️  Apagando el bot...{Style.RESET_ALL}")
                asyncio.run_coroutine_threadsafe(bot.close(), bot.loop)
            elif entrada.strip():
                print(
                    f"{Fore.YELLOW}⚠️  Comando no reconocido. "
                    f"Comandos disponibles: /test, /stats, /quit{Style.RESET_ALL}"
                )
        except (EOFError, KeyboardInterrupt):
            break


# ─────────────────────────────────────────────
# Iniciar el bot
# ─────────────────────────────────────────────

if __name__ == "__main__":
    log_info("🚀 Iniciando Troller Bot...")
    log_info(f"📂 Directorio de trabajo: {os.path.dirname(os.path.abspath(__file__))}")

    try:
        bot.run(TOKEN, log_handler=None)
    except discord.LoginFailure:
        log_error_console("❌ Token inválido. Verifica tu DISCORD_TOKEN en el archivo .env")
        sys.exit(1)
    except KeyboardInterrupt:
        log_info("⏏️  Bot detenido por el usuario.")
    except Exception as e:
        log_error_console(f"❌ Error fatal: {e}")
        sys.exit(1)
