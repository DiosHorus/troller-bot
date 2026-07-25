# =========================
# COMANDOS — Nicks
# =========================
import random
import asyncio
import discord
from config import bot, RANDOM_NICKS
from storage import (
    random_nick_users,
    load_forced_nicks, save_forced_nicks,
)
from logger import log_action
from permisos import is_bot_admin, can_target, no_perms, send_error, handle_forbidden, ensure_guild_context


def setup():
    @bot.tree.command(name="forcenick", description="Fuerza un nick y lo reaplica si lo cambian")
    async def forcenick(interaction: discord.Interaction, member: discord.Member, nick: str):
        if not await ensure_guild_context(interaction): return
        if not is_bot_admin(interaction.guild, interaction.user.id): return await no_perms(interaction)
        if not can_target(interaction.guild, interaction.user.id, member.id):
            return await send_error(interaction, "Objetivo protegido", f"No podés usar el bot contra **{member.display_name}**.")
        nick = nick.strip()
        if not nick or len(nick) > 32:
            return await send_error(interaction, "Nick inválido", "El nick debe tener entre 1 y 32 caracteres.")
        forced_nicks = load_forced_nicks(interaction.guild)
        forced_nicks[member.id] = nick
        save_forced_nicks(interaction.guild, forced_nicks)
        try:
            await member.edit(nick=nick)
        except discord.Forbidden:
            return await handle_forbidden(interaction, "nick", member)
        await interaction.response.send_message(f"✅ Nick forzado: `{nick}`", ephemeral=True)
        await log_action(interaction.guild, interaction.user, "forcenick", member, f"nick: {nick}")

    @bot.tree.command(name="unforcenick", description="Quita el nick forzado")
    async def unforcenick(interaction: discord.Interaction, member: discord.Member):
        if not await ensure_guild_context(interaction): return
        if not is_bot_admin(interaction.guild, interaction.user.id): return await no_perms(interaction)
        if not can_target(interaction.guild, interaction.user.id, member.id):
            return await send_error(interaction, "Objetivo protegido", f"No podés usar el bot contra **{member.display_name}**.")
        forced_nicks = load_forced_nicks(interaction.guild)
        if member.id not in forced_nicks:
            return await send_error(interaction, "Sin nick forzado", f"**{member.display_name}** no tiene nick forzado activo.")
        old_nick = forced_nicks.pop(member.id)
        save_forced_nicks(interaction.guild, forced_nicks)
        await interaction.response.send_message("✅ Nick forzado quitado.", ephemeral=True)
        await log_action(interaction.guild, interaction.user, "unforcenick", member, f"nick anterior: {old_nick}")

    @bot.tree.command(name="randomnick", description="Cambia el nick aleatoriamente cada 5 minutos")
    async def randomnick(interaction: discord.Interaction, member: discord.Member):
        if not await ensure_guild_context(interaction): return
        if not is_bot_admin(interaction.guild, interaction.user.id): return await no_perms(interaction)
        if not can_target(interaction.guild, interaction.user.id, member.id):
            return await send_error(interaction, "Objetivo protegido", f"No podés usar el bot contra **{member.display_name}**.")
        if member.id in random_nick_users:
            random_nick_users.discard(member.id)
            return await interaction.response.send_message(f"✅ Random nick desactivado en {member.mention}", ephemeral=True)
        random_nick_users.add(member.id)
        await interaction.response.send_message(f"🎲 Random nick activado en {member.mention}", ephemeral=True)
        await log_action(interaction.guild, interaction.user, "randomnick", member)
        async def nick_loop():
            while member.id in random_nick_users:
                try:
                    await member.edit(nick=random.choice(RANDOM_NICKS))
                except Exception:
                    pass
                await asyncio.sleep(300)
        asyncio.create_task(nick_loop())

    @bot.tree.command(name="nickspam", description="Cambia el nick frenéticamente por un tiempo")
    async def nickspam(interaction: discord.Interaction, member: discord.Member, segundos: int = 30):
        if not await ensure_guild_context(interaction): return
        if not is_bot_admin(interaction.guild, interaction.user.id): return await no_perms(interaction)
        if not can_target(interaction.guild, interaction.user.id, member.id):
            return await send_error(interaction, "Objetivo protegido", f"No podés usar el bot contra **{member.display_name}**.")
        await interaction.response.send_message(f"🔥 Nickspam activado en {member.mention}", ephemeral=True)
        await log_action(interaction.guild, interaction.user, "nickspam", member, f"duración: {segundos}s")
        async def nsp_loop():
            end_time = asyncio.get_event_loop().time() + segundos
            while asyncio.get_event_loop().time() < end_time:
                try:
                    await member.edit(nick=random.choice(RANDOM_NICKS))
                except Exception:
                    break
                await asyncio.sleep(0.8)
        asyncio.create_task(nsp_loop())
