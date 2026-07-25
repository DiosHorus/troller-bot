# =========================
# MAIN — Entry point del bot
# =========================
import discord
from discord import app_commands
from config import bot, TOKEN, BASIC_COMMANDS, OWNER_ID
import storage
import roles

# Registrar eventos
import eventos
eventos.register_events()

# Registrar comandos
import comandos_admin
import comandos_mod
import comandos_nick
import comandos_troleo
import comandos_voz
import comandos_util
import comandos_premium

comandos_admin.setup()
comandos_mod.setup()
comandos_nick.setup()
comandos_troleo.setup()
comandos_voz.setup()
comandos_util.setup()
comandos_premium.setup()

# =========================
# SISTEMA PREMIUM
# =========================
import premium
from permisos import send_error


@bot.tree.interaction_check
async def premium_check(interaction: discord.Interaction) -> bool:
    """Valida acceso premium antes de ejecutar cualquier comando slash."""
    # En DM no aplica
    if interaction.guild is None:
        return True

    cmd_name = interaction.command.name if interaction.command else None
    if cmd_name is None:
        return True

    # Comandos básicos: siempre permitidos (sin premium)
    if cmd_name in BASIC_COMMANDS:
        return True

    # Owner siempre tiene acceso total
    if interaction.user.id == OWNER_ID:
        return True

    # Verificar premium
    if premium.is_premium(interaction.guild.id):
        return True

    # Rechazado — no tiene premium
    embed = discord.Embed(
        title="🔒 Comando Premium",
        description=(
            f"El comando **`/{cmd_name}`** requiere **premium**.\n\n"
            "Tu servidor está en modo gratuito con solo **5 comandos básicos**.\n"
            "Usá **`/claim <key>`** para desbloquear todos los comandos.\n"
            "Usá **`/premium`** para ver el estado actual."
        ),
        color=discord.Color.gold()
    )
    embed.set_footer(text="Troller Bot — Sistema Premium")
    try:
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception:
        pass
    return False


# =========================
# ERRORES GLOBALES
# =========================
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    print(f"❌ Error en comando: {error}")
    if isinstance(error, app_commands.MissingPermissions):
        await send_error(interaction, "Sin permisos de Discord", "No tenés los permisos de Discord necesarios para usar este comando.")
    elif isinstance(error, app_commands.BotMissingPermissions):
        await send_error(interaction, "Bot sin permisos", f"Al bot le faltan permisos: `{error.missing_permissions}`",
                         "Andá a **Configuración del servidor → Roles → Troller Bot** y activá los permisos necesarios.")
    elif isinstance(error, app_commands.CommandOnCooldown):
        await send_error(interaction, "Cooldown", f"Esperá `{error.retry_after:.1f}s` antes de usar este comando de nuevo.")
    else:
        await send_error(interaction, "Error inesperado", str(error))


# =========================
# READY
# =========================
@bot.event
async def on_ready():
    print(f"✅ Bot listo: {bot.user}")

    # Migrar datos viejos de txt a SQLite (one-time)
    if storage.run_migration(bot):
        print("✅ Migración de txt a SQLite completada")

    # Cargar estado premium y limpiar expirados
    premium.load_all_premium()
    expired = premium.check_all_expired()
    if expired:
        print(f"⏰ {expired} servidores premium expiraron y fueron desactivados")

    print("📋 Servidores:")
    for guild in bot.guilds:
        print(f"   - {guild.name} | ID: {guild.id}")
        storage.load_admins(guild)
        storage.load_muted(guild)
        storage.load_deafened(guild)
        storage.load_voice_banned(guild)
        storage.load_forced_nicks(guild)
        storage.load_access_config(guild)
        await roles.ensure_bot_role(guild)
        try:
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"✅ Comandos en '{guild.name}': {[cmd.name for cmd in synced]}")
        except Exception as e:
            print(f"❌ Error sincronizando en '{guild.name}': {e}")

bot.run(TOKEN)
