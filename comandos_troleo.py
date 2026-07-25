# =========================
# COMANDOS — Troleo
# =========================
import random
import discord
from config import bot, FALACIAS_MENSAJES
from storage import shhh_users, repetidor_users, fantasma_users, falacias_users, invertir_users
from logger import log_action
from permisos import is_bot_admin, can_target, no_perms, send_error, ensure_guild_context


def setup():
    @bot.tree.command(name="shhh", description="Borra automáticamente los mensajes de un usuario")
    async def shhh(interaction: discord.Interaction, member: discord.Member):
        if not await ensure_guild_context(interaction): return
        if not is_bot_admin(interaction.guild, interaction.user.id): return await no_perms(interaction)
        if not can_target(interaction.guild, interaction.user.id, member.id):
            return await send_error(interaction, "Objetivo protegido", f"No podés usar el bot contra **{member.display_name}**.")
        if member.id in shhh_users:
            shhh_users.discard(member.id)
            await interaction.response.send_message(f"🔊 {member.mention} ya puede escribir.", ephemeral=True)
        else:
            shhh_users.add(member.id)
            await interaction.response.send_message(f"🤫 {member.mention} ya no puede escribir.", ephemeral=True)
        await log_action(interaction.guild, interaction.user, "shhh", member)

    @bot.tree.command(name="fantasma", description="Roba la identidad de un usuario con webhook")
    async def fantasma(interaction: discord.Interaction, member: discord.Member, nombre: str = None, foto: str = None):
        if not await ensure_guild_context(interaction): return
        if not is_bot_admin(interaction.guild, interaction.user.id): return await no_perms(interaction)
        if not can_target(interaction.guild, interaction.user.id, member.id):
            return await send_error(interaction, "Objetivo protegido", f"No podés usar el bot contra **{member.display_name}**.")
        fantasma_users[member.id] = {
            "name":   nombre or bot.user.name,
            "avatar": foto or str(bot.user.display_avatar.url)
        }
        await interaction.response.send_message(
            f"👻 Modo fantasma activado en {member.mention}\n📛 Nombre: `{fantasma_users[member.id]['name']}`",
            ephemeral=True
        )
        await log_action(interaction.guild, interaction.user, "fantasma", member)

    @bot.tree.command(name="unfantasma", description="Desactiva el modo fantasma de un usuario")
    async def unfantasma(interaction: discord.Interaction, member: discord.Member):
        if not await ensure_guild_context(interaction): return
        if not is_bot_admin(interaction.guild, interaction.user.id): return await no_perms(interaction)
        if not can_target(interaction.guild, interaction.user.id, member.id):
            return await send_error(interaction, "Objetivo protegido", f"No podés usar el bot contra **{member.display_name}**.")
        if member.id not in fantasma_users:
            return await send_error(interaction, "Sin modo fantasma", f"**{member.display_name}** no tiene modo fantasma activo.")
        del fantasma_users[member.id]
        await interaction.response.send_message(f"✅ Modo fantasma desactivado en {member.mention}", ephemeral=True)
        await log_action(interaction.guild, interaction.user, "unfantasma", member)

    @bot.tree.command(name="repetidor", description="El bot repite todo lo que diga el usuario")
    async def repetidor(interaction: discord.Interaction, member: discord.Member):
        if not await ensure_guild_context(interaction): return
        if not is_bot_admin(interaction.guild, interaction.user.id): return await no_perms(interaction)
        if not can_target(interaction.guild, interaction.user.id, member.id):
            return await send_error(interaction, "Objetivo protegido", f"No podés usar el bot contra **{member.display_name}**.")
        if member.id in repetidor_users:
            repetidor_users.discard(member.id)
            await interaction.response.send_message(f"✅ Repetidor desactivado en {member.mention}", ephemeral=True)
        else:
            repetidor_users.add(member.id)
            await interaction.response.send_message(f"🔁 Repetidor activado en {member.mention}", ephemeral=True)
        await log_action(interaction.guild, interaction.user, "repetidor", member)

    @bot.tree.command(name="falacias", description="Manda mensajes raros con la identidad del usuario")
    async def falacias(interaction: discord.Interaction, member: discord.Member):
        if not await ensure_guild_context(interaction): return
        if not is_bot_admin(interaction.guild, interaction.user.id): return await no_perms(interaction)
        if not can_target(interaction.guild, interaction.user.id, member.id):
            return await send_error(interaction, "Objetivo protegido", f"No podés usar el bot contra **{member.display_name}**.")
        if member.id in falacias_users:
            falacias_users.discard(member.id)
            await interaction.response.send_message(f"✅ Falacias desactivado en {member.mention}", ephemeral=True)
        else:
            falacias_users.add(member.id)
            await interaction.response.send_message(f"🌀 Falacias activado en {member.mention}", ephemeral=True)
        await log_action(interaction.guild, interaction.user, "falacias", member)

    @bot.tree.command(name="invertir", description="Invierte el texto de los mensajes del usuario vía webhook")
    async def invertir(interaction: discord.Interaction, member: discord.Member):
        if not await ensure_guild_context(interaction): return
        if not is_bot_admin(interaction.guild, interaction.user.id): return await no_perms(interaction)
        if not can_target(interaction.guild, interaction.user.id, member.id):
            return await send_error(interaction, "Objetivo protegido", f"No podés usar el bot contra **{member.display_name}**.")
        if member.id in invertir_users:
            invertir_users.discard(member.id)
            await interaction.response.send_message(f"✅ Invertir desactivado en {member.mention}", ephemeral=True)
        else:
            invertir_users.add(member.id)
            await interaction.response.send_message(f"🙃 Invertir activado en {member.mention}\n\nAhora cuando escriba, el bot borrará su mensaje y lo reenviará invertido con su misma identidad (nombre y foto).", ephemeral=True)
        await log_action(interaction.guild, interaction.user, "invertir", member)
