# =========================
# COMANDOS — Moderación
# =========================
import asyncio
import discord
from config import bot, PUNISH_ROLE_NAME
from storage import (
    load_muted, save_muted,
    load_deafened, save_deafened,
    load_voice_banned, save_voice_banned,
)
from logger import log_action
from permisos import is_bot_admin, can_target, no_perms, send_error, handle_forbidden, ensure_guild_context
from roles import get_or_create_punish_role


def setup():
    @bot.tree.command(name="silenciar", description="Silencia a un usuario en voz")
    async def silenciar(interaction: discord.Interaction, member: discord.Member):
        if not await ensure_guild_context(interaction): return
        if not is_bot_admin(interaction.guild, interaction.user.id): return await no_perms(interaction)
        if not can_target(interaction.guild, interaction.user.id, member.id):
            return await send_error(interaction, "Objetivo protegido", f"No podés usar el bot contra **{member.display_name}**.")
        muted = load_muted(interaction.guild)
        muted.add(member.id)
        save_muted(interaction.guild, muted)
        if member.voice:
            try:
                await member.edit(mute=True)
            except discord.Forbidden:
                return await handle_forbidden(interaction, "silenciar", member)
        await interaction.response.send_message("✅ Usuario silenciado.", ephemeral=True)
        await log_action(interaction.guild, interaction.user, "silenciar", member)

    @bot.tree.command(name="ensordecer", description="Ensordece a un usuario en voz")
    async def ensordecer(interaction: discord.Interaction, member: discord.Member):
        if not await ensure_guild_context(interaction): return
        if not is_bot_admin(interaction.guild, interaction.user.id): return await no_perms(interaction)
        if not can_target(interaction.guild, interaction.user.id, member.id):
            return await send_error(interaction, "Objetivo protegido", f"No podés usar el bot contra **{member.display_name}**.")
        deafened = load_deafened(interaction.guild)
        deafened.add(member.id)
        save_deafened(interaction.guild, deafened)
        if member.voice:
            try:
                await member.edit(deafen=True)
            except discord.Forbidden:
                return await handle_forbidden(interaction, "ensordecer", member)
        await interaction.response.send_message("✅ Usuario ensordecido.", ephemeral=True)
        await log_action(interaction.guild, interaction.user, "ensordecer", member)

    @bot.tree.command(name="castigar", description="Silencia, ensordece, bloquea voz y aplica rol Troleado")
    async def castigar(interaction: discord.Interaction, member: discord.Member):
        if not await ensure_guild_context(interaction): return
        if not is_bot_admin(interaction.guild, interaction.user.id): return await no_perms(interaction)
        if not can_target(interaction.guild, interaction.user.id, member.id):
            return await send_error(interaction, "Objetivo protegido", f"No podés castigar a **{member.display_name}**.")
        muted = load_muted(interaction.guild); muted.add(member.id); save_muted(interaction.guild, muted)
        deafened = load_deafened(interaction.guild); deafened.add(member.id); save_deafened(interaction.guild, deafened)
        voice_banned = load_voice_banned(interaction.guild); voice_banned.add(member.id); save_voice_banned(interaction.guild, voice_banned)
        role = await get_or_create_punish_role(interaction.guild)
        if role:
            try:
                await member.add_roles(role)
            except Exception:
                pass
        if member.voice:
            try:
                await member.edit(mute=True, deafen=True)
                await asyncio.sleep(0.5)
                await member.move_to(None)
            except discord.Forbidden:
                return await handle_forbidden(interaction, "silenciar", member)
        await interaction.response.send_message(f"✅ {member.name} ha sido castigado.", ephemeral=True)
        await log_action(interaction.guild, interaction.user, "castigar", member)

    @bot.tree.command(name="liberar", description="Quita mute, deafen, bloqueo de voz y rol Troleado")
    async def liberar(interaction: discord.Interaction, member: discord.Member):
        if not await ensure_guild_context(interaction): return
        if not is_bot_admin(interaction.guild, interaction.user.id): return await no_perms(interaction)
        if not can_target(interaction.guild, interaction.user.id, member.id):
            return await send_error(interaction, "Objetivo protegido", f"No podés liberar a **{member.display_name}**.")
        m = load_muted(interaction.guild); m.discard(member.id); save_muted(interaction.guild, m)
        d = load_deafened(interaction.guild); d.discard(member.id); save_deafened(interaction.guild, d)
        v = load_voice_banned(interaction.guild); v.discard(member.id); save_voice_banned(interaction.guild, v)
        role = discord.utils.get(interaction.guild.roles, name=PUNISH_ROLE_NAME)
        if role:
            try:
                await member.remove_roles(role)
            except Exception:
                pass
        if member.voice:
            try:
                await member.edit(mute=False, deafen=False)
            except Exception:
                pass
        await interaction.response.send_message(f"✅ {member.name} ha sido liberado.", ephemeral=True)
        await log_action(interaction.guild, interaction.user, "liberar", member)

    @bot.tree.command(name="expulsar", description="Expulsa a un usuario del servidor")
    async def expulsar(interaction: discord.Interaction, member: discord.Member, razon: str = "Sin razón"):
        if not await ensure_guild_context(interaction): return
        if not is_bot_admin(interaction.guild, interaction.user.id): return await no_perms(interaction)
        if not can_target(interaction.guild, interaction.user.id, member.id):
            return await send_error(interaction, "Objetivo protegido", f"No podés expulsar a **{member.display_name}**.")
        try:
            await member.kick(reason=razon)
        except discord.Forbidden:
            return await handle_forbidden(interaction, "expulsar", member)
        await interaction.response.send_message("✅ Usuario expulsado.", ephemeral=True)
        await log_action(interaction.guild, interaction.user, "expulsar", member, f"razón: {razon}")

    @bot.tree.command(name="fakeban", description="Simula un baneo quitando acceso a todos los canales")
    async def fakeban(interaction: discord.Interaction, member: discord.Member, razon: str = "Violación de los términos de servicio"):
        if not await ensure_guild_context(interaction): return
        if not is_bot_admin(interaction.guild, interaction.user.id): return await no_perms(interaction)
        if not can_target(interaction.guild, interaction.user.id, member.id):
            return await send_error(interaction, "Objetivo protegido", f"No podés fakebanear a **{member.display_name}**.")
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        ban_channel = discord.utils.get(guild.text_channels, name="fuiste-baneado")
        if not ban_channel:
            try:
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    member:             discord.PermissionOverwrite(view_channel=True, send_messages=False),
                    guild.me:           discord.PermissionOverwrite(view_channel=True, send_messages=True)
                }
                ban_channel = await guild.create_text_channel("fuiste-baneado", overwrites=overwrites)
            except discord.Forbidden:
                return await handle_forbidden(interaction, "canal")
        try:
            for channel in guild.channels:
                if channel.id == ban_channel.id:
                    continue
                try:
                    await channel.set_permissions(member, view_channel=False)
                except Exception:
                    pass
            await ban_channel.set_permissions(member, view_channel=True, send_messages=False)
        except Exception as e:
            print(f"❌ Error en fakeban: {e}")
        embed = discord.Embed(
            title="🔨 Has sido baneado de este servidor",
            description=f"**Usuario:** {member.mention}\n**Razón:** {razon}\n\nContactá a un administrador si creés que es un error.",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text="Discord — Sistema de moderación automática")
        try:
            await ban_channel.send(f"{member.mention}", embed=embed)
        except Exception:
            pass
        await interaction.followup.send(f"🔨 Fakeban aplicado a {member.mention}", ephemeral=True)
        await log_action(guild, interaction.user, "fakeban", member, f"razón: {razon}")

    @bot.tree.command(name="unfakeban", description="Quita el fakeban y restaura acceso a los canales")
    async def unfakeban(interaction: discord.Interaction, member: discord.Member):
        if not await ensure_guild_context(interaction): return
        if not is_bot_admin(interaction.guild, interaction.user.id): return await no_perms(interaction)
        await interaction.response.defer(ephemeral=True)
        try:
            for channel in interaction.guild.channels:
                try:
                    await channel.set_permissions(member, overwrite=None)
                except Exception:
                    pass
        except Exception as e:
            print(f"❌ Error quitando fakeban: {e}")
        await interaction.followup.send(f"✅ Fakeban quitado a {member.mention}", ephemeral=True)
        await log_action(interaction.guild, interaction.user, "unfakeban", member)
