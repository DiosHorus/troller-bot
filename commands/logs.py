"""
logs.py - Comando de historial de errores del Troller Bot
Comandos slash: /historial
Comandos prefijo: t!historial
Creado por +𝟝𝟠𝓵𝓸𝓬𝓸 (mas_58_loco) y Sandia [🍉] (prushkax)
"""

import discord
from discord import app_commands
from discord.ext import commands
from utils.helpers import (
    is_bot_admin,
    load_logs,
    log_command,
)

# Número de líneas de log por página
LOGS_PER_PAGE = 10


def _build_historial_embed(guild_id: int, pagina: int) -> discord.Embed | None:
    """
    Construye el embed del historial. Retorna None si no hay logs.
    Función compartida entre slash y prefix commands.
    """
    lineas = load_logs(guild_id)
    if not lineas:
        return None

    lineas.reverse()

    total_paginas = (len(lineas) + LOGS_PER_PAGE - 1) // LOGS_PER_PAGE
    if pagina < 1:
        pagina = 1
    if pagina > total_paginas:
        pagina = total_paginas

    inicio = (pagina - 1) * LOGS_PER_PAGE
    fin = inicio + LOGS_PER_PAGE
    pagina_actual = lineas[inicio:fin]

    contenido = ""
    for linea in pagina_actual:
        contenido += f"```{linea.strip()}```\n"

    embed = discord.Embed(
        title="📜 Historial de Errores",
        description=contenido if contenido else "Sin registros.",
        color=discord.Color.orange(),
    )
    embed.set_footer(
        text=f"Página {pagina}/{total_paginas} | Total: {len(lineas)} registro(s)"
    )
    return embed


def setup(
    bot: discord.Client,
    tree: app_commands.CommandTree,
    bot_admins: dict,
):
    """Registra el comando de historial en el árbol de comandos."""

    @tree.command(name="historial", description="📜 Muestra el historial de errores del servidor (paginado).")
    @app_commands.describe(pagina="Número de página (por defecto: 1)")
    async def historial(interaction: discord.Interaction, pagina: int = 1):
        log_command(str(interaction.user), "historial", interaction.guild.name)

        if not is_bot_admin(interaction.user.id, interaction.guild_id, bot_admins):
            await interaction.response.send_message(
                "❌ No tienes permisos para ver el historial.", ephemeral=True
            )
            return

        embed = _build_historial_embed(interaction.guild_id, pagina)
        if embed is None:
            await interaction.response.send_message(
                "📜 No hay errores registrados en este servidor. ¡Todo limpio! ✨",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(embed=embed, ephemeral=True)


def setup_prefix(
    bot: commands.Bot,
    bot_admins: dict,
):
    """Registra el comando de historial con prefijo t!."""

    @bot.command(name="historial", help="📜 Muestra el historial de errores del servidor (paginado).")
    async def historial_prefix(ctx: commands.Context, pagina: int = 1):
        log_command(str(ctx.author), "t!historial", ctx.guild.name)

        if not is_bot_admin(ctx.author.id, ctx.guild.id, bot_admins):
            await ctx.send("❌ No tienes permisos para ver el historial.")
            return

        embed = _build_historial_embed(ctx.guild.id, pagina)
        if embed is None:
            await ctx.send("📜 No hay errores registrados en este servidor. ¡Todo limpio! ✨")
            return

        await ctx.send(embed=embed)
