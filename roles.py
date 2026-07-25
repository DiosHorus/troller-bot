# =========================
# ROLES — Gestión de roles del bot
# =========================
import discord
from config import BOT_ROLE_NAME, PUNISH_ROLE_NAME, bot

# =========================
# ROLES
# =========================
async def ensure_bot_role(guild: discord.Guild):
    role = discord.utils.get(guild.roles, name=BOT_ROLE_NAME)
    if not role:
        try:
            role = await guild.create_role(
                name=BOT_ROLE_NAME,
                color=discord.Color.dark_red(),
                reason="Rol de identidad del Troller Bot"
            )
            print(f"🆕 Rol '{BOT_ROLE_NAME}' creado en {guild.name}")
        except discord.Forbidden:
            print(f"⚠️ No pude crear el rol '{BOT_ROLE_NAME}' en {guild.name}")
            return
    bot_member = guild.get_member(bot.user.id)
    if bot_member and role not in bot_member.roles:
        try:
            await bot_member.add_roles(role)
        except discord.Forbidden:
            print(f"⚠️ No pude ponerme el rol '{BOT_ROLE_NAME}' en {guild.name}")

async def get_or_create_punish_role(guild: discord.Guild):
    role = discord.utils.get(guild.roles, name=PUNISH_ROLE_NAME)
    if role:
        return role
    try:
        return await guild.create_role(
            name=PUNISH_ROLE_NAME,
            color=discord.Color.greyple(),
            reason="Rol de castigo del Troller Bot"
        )
    except discord.Forbidden:
        return None
