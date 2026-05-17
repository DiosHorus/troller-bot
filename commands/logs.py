"""
logs.py - Comando de historial de errores del Troller Bot
Comando: /historial (paginado)
Creado por +𝟝𝟠𝓵𝓸𝓬𝓸 (mas_58_loco) y Sandia [🍉] (prushkax)
"""

import discord
from discord import app_commands
from utils.helpers import (
    is_bot_admin,
    load_logs,
    log_command,
)

# Número de líneas de log por página
LOGS_PER_PAGE = 10


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

        # Solo admins pueden ver el historial
        if not is_bot_admin(interaction.user.id, interaction.guild_id, bot_admins):
            await interaction.response.send_message(
                "❌ No tienes permisos para ver el historial.", ephemeral=True
            )
            return

        guild_id = interaction.guild_id
        lineas = load_logs(guild_id)

        if not lineas:
            await interaction.response.send_message(
                "📜 No hay errores registrados en este servidor. ¡Todo limpio! ✨",
                ephemeral=True,
            )
            return

        # Invertir para mostrar los más recientes primero
        lineas.reverse()

        # Calcular paginación
        total_paginas = (len(lineas) + LOGS_PER_PAGE - 1) // LOGS_PER_PAGE
        if pagina < 1:
            pagina = 1
        if pagina > total_paginas:
            pagina = total_paginas

        inicio = (pagina - 1) * LOGS_PER_PAGE
        fin = inicio + LOGS_PER_PAGE
        pagina_actual = lineas[inicio:fin]

        # Construir el embed
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

        await interaction.response.send_message(embed=embed, ephemeral=True)
