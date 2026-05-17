"""
admin.py - Sistema de administradores del Troller Bot
Comandos: /addadmin, /removeadmin, /admins, /sync
Solo el dueño del bot puede gestionar admins.
Creado por +𝟝𝟠𝓵𝓸𝓬𝓸 (mas_58_loco) y Sandia [🍉] (prushkax)
"""

import os
import discord
from discord import app_commands
from utils.helpers import (
    is_owner,
    OWNER_ID,
    ADMINS_DIR,
    log_command,
    log_success,
    log_warning,
    log_error,
    log_error_console,
)


# ─────────────────────────────────────────────
# Funciones de persistencia de admins
# ─────────────────────────────────────────────

def get_admin_file(guild_id: int) -> str:
    """Retorna la ruta del archivo de admins para un servidor."""
    os.makedirs(ADMINS_DIR, exist_ok=True)
    return os.path.join(ADMINS_DIR, f"{guild_id}.txt")


def load_admins(guild_id: int) -> set:
    """Carga la lista de admins de un servidor desde archivo."""
    archivo = get_admin_file(guild_id)
    admins = set()
    if os.path.exists(archivo):
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                for linea in f:
                    linea = linea.strip()
                    if linea.isdigit():
                        admins.add(int(linea))
        except Exception as e:
            log_error_console(f"Error cargando admins del servidor {guild_id}: {e}")
    # El dueño siempre es admin
    admins.add(OWNER_ID)
    return admins


def save_admins(guild_id: int, admins: set) -> None:
    """Guarda la lista de admins de un servidor en archivo."""
    archivo = get_admin_file(guild_id)
    try:
        with open(archivo, "w", encoding="utf-8") as f:
            for admin_id in admins:
                f.write(f"{admin_id}\n")
        log_success(f"Lista de admins guardada para servidor {guild_id}")
    except Exception as e:
        log_error_console(f"Error guardando admins del servidor {guild_id}: {e}")


def load_all_admins(bot: discord.Client) -> dict:
    """
    Carga los admins de todos los servidores al iniciar el bot.
    Retorna dict[guild_id] -> set de user_ids
    """
    bot_admins = {}
    os.makedirs(ADMINS_DIR, exist_ok=True)
    for archivo in os.listdir(ADMINS_DIR):
        if archivo.endswith(".txt"):
            try:
                guild_id = int(archivo.replace(".txt", ""))
                bot_admins[guild_id] = load_admins(guild_id)
            except ValueError:
                continue
    return bot_admins


# ─────────────────────────────────────────────
# Registro de comandos
# ─────────────────────────────────────────────

def setup(
    bot: discord.Client,
    tree: app_commands.CommandTree,
    bot_admins: dict,
):
    """Registra los comandos de administración en el árbol de comandos."""

    # ─────────────────────────────────────────
    # /addadmin - Agregar un admin (solo dueño)
    # ─────────────────────────────────────────
    @tree.command(name="addadmin", description="👑 Agrega un administrador del bot (solo dueño).")
    @app_commands.describe(usuario="El usuario a agregar como admin")
    async def addadmin(interaction: discord.Interaction, usuario: discord.Member):
        log_command(str(interaction.user), "addadmin", interaction.guild.name)

        if not is_owner(interaction.user.id):
            await interaction.response.send_message(
                "❌ Solo el dueño del bot puede usar este comando.", ephemeral=True
            )
            return

        guild_id = interaction.guild_id

        # Inicializar la lista si no existe
        if guild_id not in bot_admins:
            bot_admins[guild_id] = {OWNER_ID}

        if usuario.id in bot_admins[guild_id]:
            await interaction.response.send_message(
                f"⚠️ **{usuario.display_name}** ya es admin del bot.", ephemeral=True
            )
            return

        bot_admins[guild_id].add(usuario.id)
        save_admins(guild_id, bot_admins[guild_id])

        await interaction.response.send_message(
            f"👑 **{usuario.display_name}** ha sido agregado como admin del bot.", ephemeral=True
        )
        log_success(f"{usuario} fue agregado como admin en {interaction.guild.name}")

    # ─────────────────────────────────────────
    # /removeadmin - Quitar un admin (solo dueño)
    # ─────────────────────────────────────────
    @tree.command(name="removeadmin", description="🚫 Quita un administrador del bot (solo dueño).")
    @app_commands.describe(usuario="El usuario a quitar como admin")
    async def removeadmin(interaction: discord.Interaction, usuario: discord.Member):
        log_command(str(interaction.user), "removeadmin", interaction.guild.name)

        if not is_owner(interaction.user.id):
            await interaction.response.send_message(
                "❌ Solo el dueño del bot puede usar este comando.", ephemeral=True
            )
            return

        guild_id = interaction.guild_id

        # No se puede remover al dueño
        if is_owner(usuario.id):
            await interaction.response.send_message(
                "❌ No puedes quitar al dueño del bot como admin.", ephemeral=True
            )
            return

        if usuario.id not in bot_admins.get(guild_id, set()):
            await interaction.response.send_message(
                f"⚠️ **{usuario.display_name}** no es admin del bot.", ephemeral=True
            )
            return

        bot_admins[guild_id].discard(usuario.id)
        save_admins(guild_id, bot_admins[guild_id])

        await interaction.response.send_message(
            f"🚫 **{usuario.display_name}** ha sido removido como admin del bot.", ephemeral=True
        )
        log_success(f"{usuario} fue removido como admin en {interaction.guild.name}")

    # ─────────────────────────────────────────
    # /admins - Mostrar la lista de admins
    # ─────────────────────────────────────────
    @tree.command(name="admins", description="📋 Muestra la lista de administradores del bot (solo dueño).")
    async def admins(interaction: discord.Interaction):
        log_command(str(interaction.user), "admins", interaction.guild.name)

        if not is_owner(interaction.user.id):
            await interaction.response.send_message(
                "❌ Solo el dueño del bot puede usar este comando.", ephemeral=True
            )
            return

        guild_id = interaction.guild_id
        admin_ids = bot_admins.get(guild_id, {OWNER_ID})

        if not admin_ids:
            await interaction.response.send_message(
                "📋 No hay administradores configurados.", ephemeral=True
            )
            return

        # Construir la lista de admins con nombres
        lineas = []
        for i, admin_id in enumerate(admin_ids, 1):
            miembro = interaction.guild.get_member(admin_id)
            if miembro:
                nombre = miembro.display_name
                es_owner = " 👑 (Dueño)" if is_owner(admin_id) else ""
                lineas.append(f"**{i}.** {nombre} (`{admin_id}`){es_owner}")
            else:
                lineas.append(f"**{i}.** ID: `{admin_id}` (no encontrado en el servidor)")

        embed = discord.Embed(
            title="📋 Administradores del Bot",
            description="\n".join(lineas),
            color=discord.Color.gold(),
        )
        embed.set_footer(text=f"Total: {len(admin_ids)} admin(s)")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ─────────────────────────────────────────
    # /sync - Sincronizar comandos (solo dueño)
    # ─────────────────────────────────────────
    @tree.command(name="sync", description="🔄 Fuerza la sincronización de comandos en este servidor (solo dueño).")
    async def sync(interaction: discord.Interaction):
        log_command(str(interaction.user), "sync", interaction.guild.name)

        if not is_owner(interaction.user.id):
            await interaction.response.send_message(
                "❌ Solo el dueño del bot puede usar este comando.", ephemeral=True
            )
            return

        try:
            await interaction.response.defer(ephemeral=True)
            synced = await bot.tree.sync(guild=interaction.guild)
            await interaction.followup.send(
                f"✅ Se sincronizaron **{len(synced)}** comando(s) en **{interaction.guild.name}**.",
                ephemeral=True,
            )
            log_success(f"Sincronizados {len(synced)} comandos en {interaction.guild.name}")
        except Exception as e:
            log_error_console(f"Error sincronizando comandos: {e}")
            await interaction.followup.send(
                f"❌ Error al sincronizar comandos: {e}", ephemeral=True
            )
