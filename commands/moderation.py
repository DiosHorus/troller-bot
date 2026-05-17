"""
moderation.py - Comandos de moderación del Troller Bot
Comandos slash: /silenciar, /ensordecer, /expulsar, /castigar, /liberar
Comandos prefijo: t!silenciar, t!ensordecer, t!expulsar, t!castigar, t!liberar
Creado por +𝟝𝟠𝓵𝓸𝓬𝓸 (mas_58_loco) y Sandia [🍉] (prushkax)
"""

import discord
from discord import app_commands
from discord.ext import commands
from utils.helpers import (
    is_bot_admin,
    can_target,
    log_error,
    log_command,
    log_success,
    log_error_console,
)


def setup(
    bot: discord.Client,
    tree: app_commands.CommandTree,
    muted_users: dict,
    deafened_users: dict,
    voice_banned_users: dict,
    bot_admins: dict,
):
    """Registra los comandos de moderación en el árbol de comandos."""

    # ─────────────────────────────────────────
    # /silenciar - Mutear a un usuario en voz
    # ─────────────────────────────────────────
    @tree.command(name="silenciar", description="🔇 Silencia (mutea) a un usuario en el canal de voz.")
    @app_commands.describe(usuario="El usuario a silenciar")
    async def silenciar(interaction: discord.Interaction, usuario: discord.Member):
        log_command(str(interaction.user), "silenciar", interaction.guild.name)

        # Verificar que el ejecutor es admin del bot
        if not is_bot_admin(interaction.user.id, interaction.guild_id, bot_admins):
            await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
            return

        # Verificar que se puede actuar sobre el objetivo
        puede, razon = can_target(interaction, usuario, bot_admins)
        if not puede:
            await interaction.response.send_message(razon, ephemeral=True)
            return

        try:
            # Agregar a la lista de muteados del servidor
            guild_id = interaction.guild_id
            if guild_id not in muted_users:
                muted_users[guild_id] = set()
            muted_users[guild_id].add(usuario.id)

            # Si está en un canal de voz, mutearlo
            if usuario.voice and usuario.voice.channel:
                await usuario.edit(mute=True, reason=f"Silenciado por {interaction.user}")

            await interaction.response.send_message(
                f"🔇 **{usuario.display_name}** ha sido silenciado.", ephemeral=True
            )
            log_success(f"{usuario} fue silenciado por {interaction.user} en {interaction.guild.name}")

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos suficientes para silenciar a este usuario.", ephemeral=True
            )
            log_error(interaction.guild_id, "silenciar", f"Sin permisos para silenciar a {usuario}")
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Ocurrió un error: {e}", ephemeral=True
            )
            log_error(interaction.guild_id, "silenciar", str(e))

    # ─────────────────────────────────────────
    # /ensordecer - Ensordecer a un usuario
    # ─────────────────────────────────────────
    @tree.command(name="ensordecer", description="🔈 Ensordece a un usuario en el canal de voz.")
    @app_commands.describe(usuario="El usuario a ensordecer")
    async def ensordecer(interaction: discord.Interaction, usuario: discord.Member):
        log_command(str(interaction.user), "ensordecer", interaction.guild.name)

        if not is_bot_admin(interaction.user.id, interaction.guild_id, bot_admins):
            await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
            return

        puede, razon = can_target(interaction, usuario, bot_admins)
        if not puede:
            await interaction.response.send_message(razon, ephemeral=True)
            return

        try:
            guild_id = interaction.guild_id
            if guild_id not in deafened_users:
                deafened_users[guild_id] = set()
            deafened_users[guild_id].add(usuario.id)

            if usuario.voice and usuario.voice.channel:
                await usuario.edit(deafen=True, reason=f"Ensordecido por {interaction.user}")

            await interaction.response.send_message(
                f"🔈 **{usuario.display_name}** ha sido ensordecido.", ephemeral=True
            )
            log_success(f"{usuario} fue ensordecido por {interaction.user} en {interaction.guild.name}")

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos suficientes para ensordecer a este usuario.", ephemeral=True
            )
            log_error(interaction.guild_id, "ensordecer", f"Sin permisos para ensordecer a {usuario}")
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Ocurrió un error: {e}", ephemeral=True
            )
            log_error(interaction.guild_id, "ensordecer", str(e))

    # ─────────────────────────────────────────
    # /expulsar - Desconectar a un usuario del canal de voz
    # ─────────────────────────────────────────
    @tree.command(name="expulsar", description="👢 Expulsa (desconecta) a un usuario del canal de voz.")
    @app_commands.describe(usuario="El usuario a expulsar del canal de voz")
    async def expulsar(interaction: discord.Interaction, usuario: discord.Member):
        log_command(str(interaction.user), "expulsar", interaction.guild.name)

        if not is_bot_admin(interaction.user.id, interaction.guild_id, bot_admins):
            await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
            return

        puede, razon = can_target(interaction, usuario, bot_admins)
        if not puede:
            await interaction.response.send_message(razon, ephemeral=True)
            return

        try:
            if not usuario.voice or not usuario.voice.channel:
                await interaction.response.send_message(
                    "❌ El usuario no está en un canal de voz.", ephemeral=True
                )
                return

            await usuario.move_to(None, reason=f"Expulsado del canal de voz por {interaction.user}")
            await interaction.response.send_message(
                f"👢 **{usuario.display_name}** ha sido expulsado del canal de voz.", ephemeral=True
            )
            log_success(f"{usuario} fue expulsado del canal de voz por {interaction.user} en {interaction.guild.name}")

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos suficientes para expulsar a este usuario.", ephemeral=True
            )
            log_error(interaction.guild_id, "expulsar", f"Sin permisos para expulsar a {usuario}")
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Ocurrió un error: {e}", ephemeral=True
            )
            log_error(interaction.guild_id, "expulsar", str(e))

    # ─────────────────────────────────────────
    # /castigar - Castigo completo: mute + deafen + voice ban + desconectar
    # ─────────────────────────────────────────
    @tree.command(
        name="castigar",
        description="💀 Castiga a un usuario: silenciar + ensordecer + ban de voz + desconectar."
    )
    @app_commands.describe(usuario="El usuario a castigar")
    async def castigar(interaction: discord.Interaction, usuario: discord.Member):
        log_command(str(interaction.user), "castigar", interaction.guild.name)

        if not is_bot_admin(interaction.user.id, interaction.guild_id, bot_admins):
            await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
            return

        puede, razon = can_target(interaction, usuario, bot_admins)
        if not puede:
            await interaction.response.send_message(razon, ephemeral=True)
            return

        try:
            guild_id = interaction.guild_id

            # Agregar a todas las listas de castigo
            if guild_id not in muted_users:
                muted_users[guild_id] = set()
            if guild_id not in deafened_users:
                deafened_users[guild_id] = set()
            if guild_id not in voice_banned_users:
                voice_banned_users[guild_id] = set()

            muted_users[guild_id].add(usuario.id)
            deafened_users[guild_id].add(usuario.id)
            voice_banned_users[guild_id].add(usuario.id)

            # Aplicar mute y deafen si está en voz
            if usuario.voice and usuario.voice.channel:
                await usuario.edit(
                    mute=True,
                    deafen=True,
                    reason=f"Castigado por {interaction.user}"
                )
                # Desconectar del canal de voz
                await usuario.move_to(None, reason=f"Castigado por {interaction.user}")

            await interaction.response.send_message(
                f"💀 **{usuario.display_name}** ha sido castigado completamente.\n"
                f"🔇 Silenciado | 🔈 Ensordecido | 🚫 Ban de voz | 👢 Desconectado",
                ephemeral=True,
            )
            log_success(f"{usuario} fue castigado por {interaction.user} en {interaction.guild.name}")

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos suficientes para castigar a este usuario.", ephemeral=True
            )
            log_error(interaction.guild_id, "castigar", f"Sin permisos para castigar a {usuario}")
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Ocurrió un error: {e}", ephemeral=True
            )
            log_error(interaction.guild_id, "castigar", str(e))

    # ─────────────────────────────────────────
    # /liberar - Quitar todos los castigos
    # ─────────────────────────────────────────
    @tree.command(name="liberar", description="✅ Libera a un usuario de todos los castigos.")
    @app_commands.describe(usuario="El usuario a liberar")
    async def liberar(interaction: discord.Interaction, usuario: discord.Member):
        log_command(str(interaction.user), "liberar", interaction.guild.name)

        if not is_bot_admin(interaction.user.id, interaction.guild_id, bot_admins):
            await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
            return

        puede, razon = can_target(interaction, usuario, bot_admins)
        if not puede:
            await interaction.response.send_message(razon, ephemeral=True)
            return

        try:
            guild_id = interaction.guild_id

            # Remover de todas las listas de castigo
            muted_users.get(guild_id, set()).discard(usuario.id)
            deafened_users.get(guild_id, set()).discard(usuario.id)
            voice_banned_users.get(guild_id, set()).discard(usuario.id)

            # Quitar mute y deafen si está en voz
            if usuario.voice and usuario.voice.channel:
                await usuario.edit(
                    mute=False,
                    deafen=False,
                    reason=f"Liberado por {interaction.user}"
                )

            await interaction.response.send_message(
                f"✅ **{usuario.display_name}** ha sido liberado de todos los castigos.",
                ephemeral=True,
            )
            log_success(f"{usuario} fue liberado por {interaction.user} en {interaction.guild.name}")

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos suficientes para liberar a este usuario.", ephemeral=True
            )
            log_error(interaction.guild_id, "liberar", f"Sin permisos para liberar a {usuario}")
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Ocurrió un error: {e}", ephemeral=True
            )
            log_error(interaction.guild_id, "liberar", str(e))


# ─────────────────────────────────────────────────
# Comandos con prefijo (t!)
# ─────────────────────────────────────────────────

def setup_prefix(
    bot: commands.Bot,
    muted_users: dict,
    deafened_users: dict,
    voice_banned_users: dict,
    bot_admins: dict,
):
    """Registra los comandos de moderación con prefijo t!."""

    @bot.command(name="silenciar", help="🔇 Silencia (mutea) a un usuario en el canal de voz.")
    async def silenciar_prefix(ctx: commands.Context, usuario: discord.Member):
        log_command(str(ctx.author), "t!silenciar", ctx.guild.name)

        if not is_bot_admin(ctx.author.id, ctx.guild.id, bot_admins):
            await ctx.send("❌ No tienes permisos para usar este comando.")
            return

        puede, razon = can_target(ctx, usuario, bot_admins)
        if not puede:
            await ctx.send(razon)
            return

        try:
            guild_id = ctx.guild.id
            if guild_id not in muted_users:
                muted_users[guild_id] = set()
            muted_users[guild_id].add(usuario.id)

            if usuario.voice and usuario.voice.channel:
                await usuario.edit(mute=True, reason=f"Silenciado por {ctx.author}")

            await ctx.send(f"🔇 **{usuario.display_name}** ha sido silenciado.")
            log_success(f"{usuario} fue silenciado por {ctx.author} en {ctx.guild.name}")

        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos suficientes para silenciar a este usuario.")
            log_error(ctx.guild.id, "silenciar", f"Sin permisos para silenciar a {usuario}")
        except Exception as e:
            await ctx.send(f"❌ Ocurrió un error: {e}")
            log_error(ctx.guild.id, "silenciar", str(e))

    @bot.command(name="ensordecer", help="🔈 Ensordece a un usuario en el canal de voz.")
    async def ensordecer_prefix(ctx: commands.Context, usuario: discord.Member):
        log_command(str(ctx.author), "t!ensordecer", ctx.guild.name)

        if not is_bot_admin(ctx.author.id, ctx.guild.id, bot_admins):
            await ctx.send("❌ No tienes permisos para usar este comando.")
            return

        puede, razon = can_target(ctx, usuario, bot_admins)
        if not puede:
            await ctx.send(razon)
            return

        try:
            guild_id = ctx.guild.id
            if guild_id not in deafened_users:
                deafened_users[guild_id] = set()
            deafened_users[guild_id].add(usuario.id)

            if usuario.voice and usuario.voice.channel:
                await usuario.edit(deafen=True, reason=f"Ensordecido por {ctx.author}")

            await ctx.send(f"🔈 **{usuario.display_name}** ha sido ensordecido.")
            log_success(f"{usuario} fue ensordecido por {ctx.author} en {ctx.guild.name}")

        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos suficientes para ensordecer a este usuario.")
            log_error(ctx.guild.id, "ensordecer", f"Sin permisos para ensordecer a {usuario}")
        except Exception as e:
            await ctx.send(f"❌ Ocurrió un error: {e}")
            log_error(ctx.guild.id, "ensordecer", str(e))

    @bot.command(name="expulsar", help="👢 Expulsa (desconecta) a un usuario del canal de voz.")
    async def expulsar_prefix(ctx: commands.Context, usuario: discord.Member):
        log_command(str(ctx.author), "t!expulsar", ctx.guild.name)

        if not is_bot_admin(ctx.author.id, ctx.guild.id, bot_admins):
            await ctx.send("❌ No tienes permisos para usar este comando.")
            return

        puede, razon = can_target(ctx, usuario, bot_admins)
        if not puede:
            await ctx.send(razon)
            return

        try:
            if not usuario.voice or not usuario.voice.channel:
                await ctx.send("❌ El usuario no está en un canal de voz.")
                return

            await usuario.move_to(None, reason=f"Expulsado del canal de voz por {ctx.author}")
            await ctx.send(f"👢 **{usuario.display_name}** ha sido expulsado del canal de voz.")
            log_success(f"{usuario} fue expulsado del canal de voz por {ctx.author} en {ctx.guild.name}")

        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos suficientes para expulsar a este usuario.")
            log_error(ctx.guild.id, "expulsar", f"Sin permisos para expulsar a {usuario}")
        except Exception as e:
            await ctx.send(f"❌ Ocurrió un error: {e}")
            log_error(ctx.guild.id, "expulsar", str(e))

    @bot.command(name="castigar", help="💀 Castiga a un usuario: silenciar + ensordecer + ban de voz + desconectar.")
    async def castigar_prefix(ctx: commands.Context, usuario: discord.Member):
        log_command(str(ctx.author), "t!castigar", ctx.guild.name)

        if not is_bot_admin(ctx.author.id, ctx.guild.id, bot_admins):
            await ctx.send("❌ No tienes permisos para usar este comando.")
            return

        puede, razon = can_target(ctx, usuario, bot_admins)
        if not puede:
            await ctx.send(razon)
            return

        try:
            guild_id = ctx.guild.id

            if guild_id not in muted_users:
                muted_users[guild_id] = set()
            if guild_id not in deafened_users:
                deafened_users[guild_id] = set()
            if guild_id not in voice_banned_users:
                voice_banned_users[guild_id] = set()

            muted_users[guild_id].add(usuario.id)
            deafened_users[guild_id].add(usuario.id)
            voice_banned_users[guild_id].add(usuario.id)

            if usuario.voice and usuario.voice.channel:
                await usuario.edit(mute=True, deafen=True, reason=f"Castigado por {ctx.author}")
                await usuario.move_to(None, reason=f"Castigado por {ctx.author}")

            await ctx.send(
                f"💀 **{usuario.display_name}** ha sido castigado completamente.\n"
                f"🔇 Silenciado | 🔈 Ensordecido | 🚫 Ban de voz | 👢 Desconectado"
            )
            log_success(f"{usuario} fue castigado por {ctx.author} en {ctx.guild.name}")

        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos suficientes para castigar a este usuario.")
            log_error(ctx.guild.id, "castigar", f"Sin permisos para castigar a {usuario}")
        except Exception as e:
            await ctx.send(f"❌ Ocurrió un error: {e}")
            log_error(ctx.guild.id, "castigar", str(e))

    @bot.command(name="liberar", help="✅ Libera a un usuario de todos los castigos.")
    async def liberar_prefix(ctx: commands.Context, usuario: discord.Member):
        log_command(str(ctx.author), "t!liberar", ctx.guild.name)

        if not is_bot_admin(ctx.author.id, ctx.guild.id, bot_admins):
            await ctx.send("❌ No tienes permisos para usar este comando.")
            return

        puede, razon = can_target(ctx, usuario, bot_admins)
        if not puede:
            await ctx.send(razon)
            return

        try:
            guild_id = ctx.guild.id

            muted_users.get(guild_id, set()).discard(usuario.id)
            deafened_users.get(guild_id, set()).discard(usuario.id)
            voice_banned_users.get(guild_id, set()).discard(usuario.id)

            if usuario.voice and usuario.voice.channel:
                await usuario.edit(mute=False, deafen=False, reason=f"Liberado por {ctx.author}")

            await ctx.send(f"✅ **{usuario.display_name}** ha sido liberado de todos los castigos.")
            log_success(f"{usuario} fue liberado por {ctx.author} en {ctx.guild.name}")

        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos suficientes para liberar a este usuario.")
            log_error(ctx.guild.id, "liberar", f"Sin permisos para liberar a {usuario}")
        except Exception as e:
            await ctx.send(f"❌ Ocurrió un error: {e}")
            log_error(ctx.guild.id, "liberar", str(e))
