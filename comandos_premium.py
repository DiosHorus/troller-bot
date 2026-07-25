# =========================
# COMANDOS — Sistema Premium y Keys
# =========================
import discord
from config import bot, OWNER_ID
from premium import (
    generate_keys, claim_key, is_premium, get_premium_status,
    get_keys_by_creator, format_duration,
)
from logger import log_action
from permisos import is_owner, send_error, ensure_guild_context


def setup():
    @bot.tree.command(name="claim", description="Activa premium en el servidor con una key")
    async def claim(interaction: discord.Interaction, key: str):
        if not await ensure_guild_context(interaction):
            return

        success, message = claim_key(interaction.guild.id, key)
        if success:
            embed = discord.Embed(
                title="🔑 Premium Activado",
                description=message,
                color=discord.Color.green()
            )
            embed.set_footer(text="Troller Bot — Sistema Premium")
            await interaction.response.send_message(embed=embed, ephemeral=False)
            await log_action(interaction.guild, interaction.user, "claim", details=f"key: {key.strip().upper()}")
        else:
            await send_error(interaction, "Claim fallido", message)

    @bot.tree.command(name="genkey", description="Genera keys de activación premium (solo owner)")
    @discord.app_commands.choices(duracion=[
        discord.app_commands.Choice(name="🕐 7 Días",         value="7d"),
        discord.app_commands.Choice(name="📅 30 Días",        value="30d"),
        discord.app_commands.Choice(name="📆 3 Meses",        value="3m"),
        discord.app_commands.Choice(name="📆 6 Meses",        value="6m"),
        discord.app_commands.Choice(name="🗓️ 1 Año",          value="1y"),
        discord.app_commands.Choice(name="♾️ Permanente",     value="permanent"),
    ])
    async def genkey(
        interaction: discord.Interaction,
        duracion: discord.app_commands.Choice[str],
        cantidad: int = 1
    ):
        if not await ensure_guild_context(interaction):
            return
        if not is_owner(interaction.user.id):
            return await send_error(interaction, "Sin permisos", "Solo el owner del bot puede generar keys.")

        if cantidad < 1 or cantidad > 10:
            return await send_error(
                interaction, "Cantidad inválida",
                "La cantidad debe estar entre **1 y 10** keys por comando."
            )

        try:
            codes = generate_keys(interaction.user.id, duracion.value, cantidad)
        except ValueError as e:
            return await send_error(interaction, "Error generando keys", str(e))

        duration_label = format_duration(duracion.value)

        if cantidad == 1:
            embed = discord.Embed(
                title="🔑 Key Generada",
                description=f"**Duración:** {duration_label}\n**Key:** `{codes[0]}`",
                color=discord.Color.gold()
            )
        else:
            codes_list = "\n".join(f"`{c}`" for c in codes)
            embed = discord.Embed(
                title=f"🔑 {cantidad} Keys Generadas",
                description=f"**Duración:** {duration_label}\n\n{codes_list}",
                color=discord.Color.gold()
            )
        embed.set_footer(text="Troller Bot — Sistema Premium")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await log_action(
            interaction.guild, interaction.user, "genkey",
            details=f"duración: {duracion.value} | cantidad: {cantidad}"
        )

    @bot.tree.command(name="premium", description="Muestra el estado premium del servidor")
    async def premium_cmd(interaction: discord.Interaction):
        if not await ensure_guild_context(interaction):
            return

        status = get_premium_status(interaction.guild.id)

        if status["is_premium"]:
            exp = status["premium_expires"]
            if exp:
                exp_date = exp.replace(" ", " · ")
                exp_text = f"⏰ Expira: **{exp_date}**"
            else:
                exp_text = "♾️ **Premium Permanente**"

            embed = discord.Embed(
                title="🌟 Servidor Premium",
                description=f"Este servidor tiene acceso a **todos los comandos**.\n{exp_text}",
                color=discord.Color.gold()
            )
            if status["claimed_key"]:
                embed.add_field(name="🔑 Key usada", value=f"`{status['claimed_key']}`", inline=True)
            if status["activated_at"]:
                embed.add_field(name="📅 Activado el", value=status["activated_at"], inline=True)
        else:
            embed = discord.Embed(
                title="🆓 Servidor Gratuito",
                description=(
                    "Este servidor usa la versión gratuita con **5 comandos básicos**.\n\n"
                    "Usá `/claim <key>` para activar premium y desbloquear **todos los comandos**."
                ),
                color=discord.Color.light_grey()
            )
        embed.set_footer(text="Troller Bot — Sistema Premium")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="keys", description="Lista las keys que generaste (solo owner)")
    async def keys_cmd(interaction: discord.Interaction):
        if not await ensure_guild_context(interaction):
            return
        if not is_owner(interaction.user.id):
            return await send_error(interaction, "Sin permisos", "Solo el owner del bot puede ver las keys generadas.")

        keys = get_keys_by_creator(interaction.user.id)

        if not keys:
            embed = discord.Embed(
                title="🔑 Tus Keys",
                description="No generaste ninguna key todavía. Usá `/genkey` para crear una.",
                color=discord.Color.blurple()
            )
        else:
            embed = discord.Embed(
                title="🔑 Keys Generadas",
                color=discord.Color.blurple()
            )

            used_count   = sum(1 for k in keys if k["is_used"])
            unused_count = sum(1 for k in keys if not k["is_used"])
            embed.add_field(
                name="📊 Resumen",
                value=f"**{len(keys)}** keys totales\n🟢 {unused_count} sin usar · 🔴 {used_count} usadas",
                inline=False
            )

            # Mostrar últimas 10
            for k in keys[:10]:
                status_icon = "🔴" if k["is_used"] else "🟢"
                claimed_info = f" → Servidor `{k['claimed_by_guild']}`" if k["claimed_by_guild"] else ""
                dur = format_duration(k["duration"])
                value = f"{status_icon} **{dur}**{claimed_info}"
                embed.add_field(
                    name=f"`{k['code']}`",
                    value=value,
                    inline=False
                )

            if len(keys) > 10:
                embed.set_footer(text=f"Mostrando 10 de {len(keys)} keys · Troller Bot")

        embed.set_footer(text="Troller Bot — Sistema Premium")
        await interaction.response.send_message(embed=embed, ephemeral=True)
