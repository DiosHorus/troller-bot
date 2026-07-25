# =========================
# COMANDOS — Utilidades (sugerencias, historial, help)
# =========================
from datetime import datetime
import discord
from config import bot, OWNER_ID, SUGGEST_FILE
from db import execute
from logger import log_action
from permisos import is_bot_admin, no_perms, send_error, ensure_guild_context


def setup():
    # =========================
    # SUGERENCIAS
    # =========================
    @bot.tree.command(name="suggest", description="Envía una sugerencia al Troller Bot")
    async def suggest(interaction: discord.Interaction, sugerencia: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {interaction.user} ({interaction.user.id})"
        if interaction.guild:
            line += f" en '{interaction.guild.name}'"
        line += f": {sugerencia}\n"
        try:
            with open(SUGGEST_FILE, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception as e:
            print(f"❌ Error guardando sugerencia: {e}")

        dm_enviado = False
        try:
            owner = await bot.fetch_user(OWNER_ID)
            embed = discord.Embed(
                title="💡 Nueva sugerencia para Troller Bot",
                description=f">>> {sugerencia}",
                color=discord.Color.blurple(),
                timestamp=datetime.now()
            )
            embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
            embed.add_field(name="Usuario", value=f"{interaction.user.mention} (`{interaction.user.id}`)", inline=True)
            if interaction.guild:
                embed.add_field(name="Servidor", value=interaction.guild.name, inline=True)
            embed.set_footer(text="Troller Bot — Sistema de sugerencias")
            await owner.send(embed=embed)
            dm_enviado = True
        except discord.Forbidden:
            print("⚠️ No se pudo enviar MD al owner (DMs cerrados)")
        except Exception as e:
            print(f"❌ Error enviando MD: {e}")

        msg = "✅ ¡Sugerencia enviada! El dueño la recibirá por MD." if dm_enviado else "✅ ¡Sugerencia guardada!"
        await interaction.response.send_message(msg, ephemeral=True)
        if interaction.guild:
            await log_action(interaction.guild, interaction.user, "suggest", details=sugerencia[:80])

    # =========================
    # HISTORIAL
    # =========================
    @bot.tree.command(name="historial", description="Muestra el historial de acciones de un usuario")
    async def historial(interaction: discord.Interaction, member: discord.Member):
        if not await ensure_guild_context(interaction): return
        if not is_bot_admin(interaction.guild, interaction.user.id): return await no_perms(interaction)

        guild_id = interaction.guild.id

        # Acciones CONTRA este usuario (últimas 5)
        contra_rows = execute(
            "SELECT timestamp, actor_name, command, details FROM action_logs "
            "WHERE guild_id=? AND target_id=? ORDER BY id DESC LIMIT 5",
            (guild_id, member.id)
        ).fetchall()

        # Acciones DICTADAS por este usuario (últimas 5)
        dictadas_rows = execute(
            "SELECT timestamp, target_name, command, details FROM action_logs "
            "WHERE guild_id=? AND actor_id=? ORDER BY id DESC LIMIT 5",
            (guild_id, member.id)
        ).fetchall()

        # Conteo total
        total_contra = execute(
            "SELECT COUNT(*) FROM action_logs WHERE guild_id=? AND target_id=?",
            (guild_id, member.id)
        ).fetchone()[0]

        total_dictadas = execute(
            "SELECT COUNT(*) FROM action_logs WHERE guild_id=? AND actor_id=?",
            (guild_id, member.id)
        ).fetchone()[0]

        def format_rows(rows):
            if not rows:
                return ["`Sin registros`"]
            chunks = []
            for ts, name, cmd, details in rows:
                entry = f"{name} — /{cmd}"
                if details:
                    entry += f" | {details}"
                entry = entry[:150] + ("…" if len(entry) > 150 else "")
                chunks.append(f"• `{entry}`")
            return chunks

        contra_text   = "\n".join(format_rows(contra_rows))
        dictadas_text = "\n".join(format_rows(dictadas_rows))

        contra_text   = contra_text[:1020]   + ("…" if len(contra_text)   > 1020 else "")
        dictadas_text = dictadas_text[:1020] + ("…" if len(dictadas_text) > 1020 else "")

        embed = discord.Embed(
            title=f"📋 Historial de {member.display_name}",
            color=discord.Color.blurple(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(
            name=f"⚔️ Acciones contra este usuario ({total_contra} total)",
            value=contra_text,
            inline=False
        )
        embed.add_field(
            name=f"🛡️ Acciones dictadas por este usuario ({total_dictadas} total)",
            value=dictadas_text,
            inline=False
        )
        embed.set_footer(text="Mostrando últimas 5 por categoría • Troller Bot")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # =========================
    # HELP
    # =========================
    @bot.tree.command(name="help", description="Muestra todos los comandos del bot")
    async def help_cmd(interaction: discord.Interaction):
        if not await ensure_guild_context(interaction): return

        embeds = []

        # ── Embed 1: Portada
        e0 = discord.Embed(
            title="🤖 Troller Bot — Ayuda",
            description=(
                "**34 comandos** para administrar, moderar y trolear.\n"
                "Todos los comandos usan `/` y se ejecutan con parámetros integrados de Discord.\n\n"
                "### ⭐ Sistema Premium\n"
                "Servidores **gratuitos**: 7 comandos básicos.\n"
                "Servidores **premium**: todos los comandos desbloqueados.\n"
                "Usá `/premium` para ver tu estado y `/claim <key>` para activar.\n\n"
                "### Leyenda\n"
                "🔒 Solo el **owner** del bot\n"
                "🛡️ Requiere ser **admin** del bot\n"
                "🌟 Requiere **premium** en el servidor (o ser owner)\n"
                "👤 Cualquiera puede usarlo\n"
                "↻ Se activa/desactiva al volver a usarlo sobre el mismo usuario"
            ),
            color=discord.Color.blurple()
        )
        e0.set_footer(text="Troller Bot • /help — Página 1/8")
        embeds.append(e0)

        # ── Embed 2: Admin (5 comandos)
        e1 = discord.Embed(title="⚙️ Admin", description="Gestión de admins, acceso y logs del bot.", color=discord.Color.yellow())
        e1.add_field(name="🔒 `/addadmin <@usuario>`",
                     value="Agrega un admin al bot.", inline=True)
        e1.add_field(name="🔒 `/removeadmin <@usuario>`",
                     value="Quita un admin del bot.", inline=True)
        e1.add_field(name="🛡️ `/admins`",
                     value="Lista los admins y el modo de acceso actual.", inline=True)
        e1.add_field(name="🔒 `/accessmode <modo> [@rol]`",
                     value="Cambia quién puede usar el bot.\n**Modos:** `admin_only` · `role` · `everyone`\nSi usás `role`, especificá el rol.", inline=False)
        e1.add_field(name="🔒 `/log <#canal>`",
                     value="Configura el canal donde se envían los logs de acciones.", inline=False)
        e1.set_footer(text="Troller Bot • Admin — Página 2/8")
        embeds.append(e1)

        # ── Embed 3: Premium (4 comandos)
        e_premium = discord.Embed(title="⭐ Premium", description="Sistema de keys y activación de premium.", color=discord.Color.gold())
        e_premium.add_field(name="👤 `/claim <key>`",
                            value="Activa premium en este servidor usando una key.\nFormato: `TROLLER-XXXX-XXXX-XXXX`", inline=False)
        e_premium.add_field(name="👤 `/premium`",
                            value="Muestra el estado premium actual del servidor (gratuito o premium, fecha de expiración).", inline=False)
        e_premium.add_field(name="🔒 `/genkey <duración> [cantidad]`",
                            value="Genera keys de activación. Duraciones: `7d`, `30d`, `3m`, `6m`, `1y`, `permanent`.\nMáx 10 por uso.", inline=False)
        e_premium.add_field(name="🔒 `/keys`",
                            value="Lista todas las keys que generaste y su estado (usada / sin usar).", inline=False)
        e_premium.set_footer(text="Troller Bot • Premium — Página 3/8")
        embeds.append(e_premium)

        # ── Embed 4: Moderación (7 comandos)
        e2 = discord.Embed(title="🛡️ Moderación", description="Silenciar, ensordecer, castigar y expulsar.", color=discord.Color.orange())
        e2.add_field(name="🌟🛡️ `/silenciar <@usuario>`",
                     value="Silencia en voz. Se reaplica si intenta activar el micrófono.", inline=True)
        e2.add_field(name="🌟🛡️ `/ensordecer <@usuario>`",
                     value="Ensordece en voz. Se reaplica si intenta quitar el deafen.", inline=True)
        e2.add_field(name="🌟🛡️ `/castigar <@usuario>`",
                     value="Aplica **todo junto**: mute + deafen + bloqueo de voz + rol @Troleado.", inline=False)
        e2.add_field(name="🌟🛡️ `/liberar <@usuario>`",
                     value="Quita **todos** los castigos activos del usuario.", inline=True)
        e2.add_field(name="🌟🛡️ `/expulsar <@usuario> [razón]`",
                     value="Expulsa (kick) al usuario del servidor.", inline=True)
        e2.add_field(name="🌟🛡️ `/fakeban <@usuario> [razón]`",
                     value="Simula un baneo: oculta todos los canales y crea #fuiste-baneado.", inline=False)
        e2.add_field(name="🌟🛡️ `/unfakeban <@usuario>`",
                     value="Restaura el acceso a canales tras un fakeban.", inline=True)
        e2.set_footer(text="Troller Bot • Moderación — Página 4/8")
        embeds.append(e2)

        # ── Embed 5: Nicks (4 comandos)
        e3 = discord.Embed(title="📛 Nicks", description="Control de apodos forzados y aleatorios.", color=discord.Color.blue())
        e3.add_field(name="🌟🛡️ `/forcenick <@usuario> <nick>`",
                     value="Fuerza un apodo. Se reaplica automáticamente si el usuario lo cambia o se reconecta.", inline=False)
        e3.add_field(name="🌟🛡️ `/unforcenick <@usuario>`",
                     value="Quita el nick forzado y deja que el usuario elija.", inline=True)
        e3.add_field(name="🌟🛡️ ↻ `/randomnick <@usuario>`",
                     value="Cambia el nick aleatoriamente **cada 5 minutos**. Usalo de nuevo para desactivar.", inline=False)
        e3.add_field(name="🌟🛡️ `/nickspam <@usuario> [segundos]`",
                     value="Cambia el nick frenéticamente cada 0.8s durante el tiempo indicado (def: 30s).", inline=False)
        e3.set_footer(text="Troller Bot • Nicks — Página 5/8")
        embeds.append(e3)

        # ── Embed 6: Troleo (6 comandos)
        e4 = discord.Embed(title="😈 Troleo", description="Efectos sobre mensajes: borrar, suplantar, repetir, invertir.", color=discord.Color.purple())
        e4.add_field(name="🌟🛡️ ↻ `/shhh <@usuario>`",
                     value="Borra **todos** sus mensajes automáticamente. Toggle.", inline=True)
        e4.add_field(name="🌟🛡️ ↻ `/fantasma <@usuario> [nombre] [url-foto]`",
                     value="Suplanta su identidad vía webhook. Sus mensajes salen con otro nombre/foto. Toggle.", inline=False)
        e4.add_field(name="🌟🛡️ `/unfantasma <@usuario>`",
                     value="Desactiva el modo fantasma.", inline=True)
        e4.add_field(name="🌟🛡️ ↻ `/repetidor <@usuario>`",
                     value="El bot repite en el canal todo lo que escriba. Toggle.", inline=False)
        e4.add_field(name="🌟🛡️ ↻ `/falacias <@usuario>`",
                     value="40% de probabilidad de reemplazar su mensaje por una frase aleatoria rara. Toggle.", inline=False)
        e4.add_field(name="🌟🛡️ ↻ `/invertir <@usuario>`",
                     value="Invierte el texto de sus mensajes (∀ʇxǝʇ oʇɹǝʌuı). Toggle.", inline=False)
        e4.set_footer(text="Troller Bot • Troleo — Página 6/8")
        embeds.append(e4)

        # ── Embed 7: Voz & Sonido (5 comandos)
        e5 = discord.Embed(title="🎙️ Voz & Sonido", description="Troleo en canales de voz y reproducción de audio.", color=discord.Color.teal())
        e5.add_field(name="🌟🛡️ ↻ `/spamcall <@usuario> [segundos]`",
                     value="Mueve al usuario aleatoriamente entre canales de voz cada 0.3s (def: 30s). Usalo de nuevo para detener.", inline=False)
        e5.add_field(name="🌟🛡️ `/lobotomy <@usuario> [segundos]`",
                     value="Alterna mute/deafen rápidamente para simular lag extremo (def: 20s).", inline=False)
        e5.add_field(name="🌟🛡️ `/sound <url-de-youtube>`",
                     value="Descarga y reproduce el audio del video en tu canal de voz.\n⚠️ Requiere FFmpeg. Si YouTube bloquea, ejecutá `export_cookies.py`.", inline=False)
        e5.add_field(name="🛡️ `/stop`",
                     value="Detiene la reproducción y desconecta al bot del canal de voz.", inline=True)
        e5.add_field(name="🌟🛡️ `/paranoia <@usuario> [mensajes]`",
                     value="Envía frases perturbadoras por MD cada 1-5 min (def: 5 mensajes).", inline=False)
        e5.set_footer(text="Troller Bot • Voz & Sonido — Página 7/8")
        embeds.append(e5)

        # ── Embed 8: Utilidades (3 comandos)
        e6 = discord.Embed(title="🧰 Utilidades", description="Sugerencias, historial y ayuda.", color=discord.Color.dark_purple())
        e6.add_field(name="👤 `/suggest <texto>`",
                     value="Envía una sugerencia al dueño del bot por MD.", inline=True)
        e6.add_field(name="🛡️ `/historial <@usuario>`",
                     value="Muestra las últimas 5 acciones **contra** y **dictadas por** ese usuario.", inline=False)
        e6.add_field(name="👤 `/help`",
                     value="Muestra este menú de ayuda.", inline=True)
        e6.set_footer(text="Troller Bot • Utilidades — Página 8/8")
        embeds.append(e6)

        await interaction.response.send_message(embeds=embeds, ephemeral=True)
