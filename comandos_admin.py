# =========================
# COMANDOS — Sistema de Admin
# =========================
import discord
from config import bot, OWNER_ID
from storage import (
    ACCESS_MODES, ACCESS_ROLES,
    load_admins, save_admins,
    save_log_channel_id,
    save_access_config,
)
from logger import log_action
from permisos import is_owner, is_bot_admin, no_perms, send_error, ensure_guild_context


def setup():
    @bot.tree.command(name="addadmin", description="Añade un admin del bot (solo owner)")
    async def addadmin(interaction: discord.Interaction, member: discord.Member):
        if not await ensure_guild_context(interaction): return
        if not is_owner(interaction.user.id):
            return await no_perms(interaction)
        if member.id == OWNER_ID:
            return await send_error(interaction, "Acción inválida", "Vos ya sos el owner, no necesitás agregarte.")
        admins = load_admins(interaction.guild)
        admins.add(member.id)
        save_admins(interaction.guild, admins)
        embed = discord.Embed(title="🛡️ Admin agregado", color=discord.Color.green())
        embed.add_field(name="Usuario", value=f"{member.mention} (`{member.id}`)")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await log_action(interaction.guild, interaction.user, "addadmin", member)

    @bot.tree.command(name="removeadmin", description="Quita un admin del bot (solo owner)")
    async def removeadmin(interaction: discord.Interaction, member: discord.Member):
        if not await ensure_guild_context(interaction): return
        if not is_owner(interaction.user.id):
            return await no_perms(interaction)
        if member.id == OWNER_ID:
            return await send_error(interaction, "Acción inválida", "No podés quitarte a vos mismo como owner.")
        admins = load_admins(interaction.guild)
        admins.discard(member.id)
        save_admins(interaction.guild, admins)
        embed = discord.Embed(title="❌ Admin removido", color=discord.Color.red())
        embed.add_field(name="Usuario", value=f"{member.mention} (`{member.id}`)")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await log_action(interaction.guild, interaction.user, "removeadmin", member)

    @bot.tree.command(name="admins", description="Muestra los admins y el modo de acceso del bot")
    async def admins_cmd(interaction: discord.Interaction):
        if not await ensure_guild_context(interaction): return
        if not is_bot_admin(interaction.guild, interaction.user.id):
            return await no_perms(interaction)
        admins_set = load_admins(interaction.guild)
        mode    = ACCESS_MODES.get(interaction.guild.id, "admin_only")
        role_id = ACCESS_ROLES.get(interaction.guild.id)
        role    = interaction.guild.get_role(role_id) if role_id else None
        mode_text = {
            "admin_only": "🔒 Solo admins del bot",
            "role":       f"🎭 Rol requerido: {role.mention if role else '`no configurado`'}",
            "everyone":   "🌐 Cualquier persona",
        }
        embed = discord.Embed(title="🛡️ Sistema de Admins — Troller Bot", color=discord.Color.blurple())
        embed.add_field(name="⚙️ Modo de acceso", value=mode_text.get(mode, mode), inline=False)
        lines = []
        for uid in sorted(admins_set):
            m = interaction.guild.get_member(uid)
            shown = m.mention if m else f"`{uid}`"
            lines.append(f"👑 {shown} — owner" if uid == OWNER_ID else f"🛡️ {shown}")
        embed.add_field(name="Admins registrados", value="\n".join(lines) if lines else "Ninguno", inline=False)
        embed.set_footer(text="Troller Bot — Sistema de permisos")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="accessmode", description="Cambia quién puede usar el bot (solo owner)")
    @discord.app_commands.choices(modo=[
        discord.app_commands.Choice(name="🔒 Solo admins del bot",           value="admin_only"),
        discord.app_commands.Choice(name="🎭 Cualquiera con un rol",         value="role"),
        discord.app_commands.Choice(name="🌐 Cualquier persona del servidor", value="everyone"),
    ])
    async def accessmode(interaction: discord.Interaction, modo: discord.app_commands.Choice[str], rol: discord.Role = None):
        if not await ensure_guild_context(interaction): return
        if not is_owner(interaction.user.id):
            return await no_perms(interaction)
        if modo.value == "role" and not rol:
            return await send_error(
                interaction, "Falta el rol",
                "Tenés que especificar un rol cuando usás el modo `rol`.",
                "Ejemplo: `/accessmode modo:rol rol:@Moderadores`"
            )
        ACCESS_MODES[interaction.guild.id] = modo.value
        ACCESS_ROLES[interaction.guild.id] = rol.id if rol else None
        save_access_config(interaction.guild)
        descriptions = {
            "admin_only": "🔒 Solo admins del bot pueden usar los comandos.",
            "role":       f"🎭 Cualquiera con el rol {rol.mention if rol else ''} puede usar los comandos.",
            "everyone":   "🌐 Cualquier persona del servidor puede usar los comandos.",
        }
        embed = discord.Embed(title="⚙️ Modo de acceso actualizado", description=descriptions[modo.value], color=discord.Color.yellow())
        embed.set_footer(text="Troller Bot — Sistema de permisos")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await log_action(interaction.guild, interaction.user, "accessmode",
                         details=f"modo: {modo.value}" + (f" | rol: {rol.name}" if rol else ""))

    @bot.tree.command(name="log", description="Configura el canal de logs (solo owner)")
    async def log_cmd(interaction: discord.Interaction, canal: discord.TextChannel):
        if not await ensure_guild_context(interaction): return
        if not is_owner(interaction.user.id):
            return await no_perms(interaction)
        save_log_channel_id(interaction.guild, canal.id)
        embed = discord.Embed(title="📋 Canal de logs configurado", color=discord.Color.blurple())
        embed.add_field(name="Canal", value=canal.mention)
        embed.add_field(name="Base de datos", value="`trollerbot.db`")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await log_action(interaction.guild, interaction.user, "log", details=f"canal: #{canal.name}")
