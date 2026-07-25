# =========================
# COMANDOS — Voz / Psicológico / Sonido
# =========================
import os
import random
import asyncio
import tempfile
import discord
from config import bot
from storage import spam_call_users
from logger import log_action
from permisos import is_bot_admin, can_target, no_perms, send_error, ensure_guild_context


def setup():
    @bot.tree.command(name="sound", description="Reproduce el audio de un video de YouTube en tu canal de voz")
    async def sound(interaction: discord.Interaction, url: str):
        if not await ensure_guild_context(interaction):
            return
        if not is_bot_admin(interaction.guild, interaction.user.id):
            return await no_perms(interaction)

        # Validar que la URL sea de YouTube
        if "youtube.com" not in url and "youtu.be" not in url:
            return await send_error(
                interaction, "URL inválida",
                "Solo se aceptan URLs de YouTube.",
                "Ejemplo: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`"
            )

        # Validar que el usuario está en un canal de voz
        if not interaction.user.voice or not interaction.user.voice.channel:
            return await send_error(
                interaction, "No estás en voz",
                "Tenés que estar en un canal de voz para usar este comando.",
                "Entrá a un canal de voz y volvé a intentarlo."
            )

        voice_channel = interaction.user.voice.channel

        # Validar permisos del bot en ese canal
        bot_member = interaction.guild.me
        if not voice_channel.permissions_for(bot_member).connect:
            return await send_error(
                interaction, "Sin permisos",
                "El bot no tiene permiso para conectarse a ese canal de voz.",
                "Andá a los ajustes del canal de voz y agregale el permiso **Conectar** al rol Troller Bot."
            )
        if not voice_channel.permissions_for(bot_member).speak:
            return await send_error(
                interaction, "Sin permisos",
                "El bot no tiene permiso para hablar en ese canal de voz.",
                "Andá a los ajustes del canal de voz y agregale el permiso **Hablar** al rol Troller Bot."
            )

        await interaction.response.defer(ephemeral=False)

        # Descargar el audio con yt-dlp
        try:
            import yt_dlp

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(tempfile.gettempdir(), "troller_sound_%(id)s.%(ext)s"),
                "quiet": True,
                "no_warnings": True,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "opus",
                }],
                "noplaylist": True,
                "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
            }

            loop = asyncio.get_event_loop()
            info = None
            download_error = None

            def do_download(opts):
                return yt_dlp.YoutubeDL(opts).extract_info(url, download=True)

            # 1. Si existe cookies.txt (exportado por el usuario), usarlo primero
            cookies_txt = os.path.join(os.path.dirname(__file__), "cookies.txt")
            if os.path.exists(cookies_txt):
                opts = dict(ydl_opts)
                opts["cookiefile"] = cookies_txt
                try:
                    info = await loop.run_in_executor(None, do_download, opts)
                except Exception as e:
                    download_error = e

            # 2. Intentar sin cookies (player_client android funciona sin auth)
            if info is None:
                try:
                    info = await loop.run_in_executor(None, do_download, ydl_opts)
                except Exception as e:
                    download_error = e

            # 3. Si falló, probar con cookies de navegador
            if info is None:
                for browser in ["chrome", "edge", "firefox", "brave", "opera"]:
                    opts = dict(ydl_opts)
                    opts["cookiesfrombrowser"] = (browser,)
                    try:
                        info = await loop.run_in_executor(None, do_download, opts)
                        if info:
                            break
                    except Exception as e:
                        download_error = e
                        continue

            if info is None:
                error_msg = str(download_error) if download_error else "YouTube bloqueó la descarga"
                # Si el error es de bot-detection, dar instrucciones
                if "Sign in" in error_msg or "bot" in error_msg.lower():
                    return await interaction.followup.send(
                        "❌ **YouTube bloqueó la descarga.**\n\n"
                        "Para solucionarlo, **cerrá Opera GX** y ejecutá una sola vez:\n"
                        "`python export_cookies.py`\n\n"
                        "Después volvé a usar `/sound` y va a funcionar.",
                        ephemeral=True
                    )
                return await interaction.followup.send(f"❌ Error al descargar: `{error_msg}`", ephemeral=True)

            # Determinar la ruta del archivo descargado
            video_id = info["id"]
            # yt-dlp convierte a opus, así que buscamos .opus
            audio_path = os.path.join(tempfile.gettempdir(), f"troller_sound_{video_id}.opus")
            if not os.path.exists(audio_path):
                # Puede haber quedado con otra extensión
                for ext in ["opus", "webm", "m4a", "ogg"]:
                    candidate = os.path.join(tempfile.gettempdir(), f"troller_sound_{video_id}.{ext}")
                    if os.path.exists(candidate):
                        audio_path = candidate
                        break

            titulo = info.get("title", "Sin título")
            duracion = info.get("duration", 0)

        except Exception as e:
            return await interaction.followup.send(f"❌ Error al descargar el audio: `{e}`", ephemeral=True)

        # Conectarse al canal de voz y reproducir
        voice_client = None
        try:
            # Ver si ya está conectado en este server
            if interaction.guild.voice_client:
                # Si ya está en otro canal, moverse
                if interaction.guild.voice_client.channel != voice_channel:
                    await interaction.guild.voice_client.move_to(voice_channel)
                voice_client = interaction.guild.voice_client
            else:
                voice_client = await voice_channel.connect()

            # Si ya estaba reproduciendo algo, esperar
            if voice_client.is_playing():
                voice_client.stop()

            source = discord.FFmpegPCMAudio(audio_path)
            # Usar TransformSource para controlar volumen si es necesario
            source = discord.PCMVolumeTransformer(source, volume=1.0)

            voice_client.play(source)

            embed = discord.Embed(
                title="🔊 Reproduciendo sonido",
                description=f"**{titulo}**",
                color=discord.Color.green()
            )
            if duracion:
                mins, secs = divmod(duracion, 60)
                embed.add_field(name="Duración", value=f"{mins}:{secs:02d}")
            else:
                embed.add_field(name="Duración", value="Desconocida")
            embed.add_field(name="Canal", value=voice_channel.mention)
            embed.set_footer(text=f"Pedido por {interaction.user.display_name}")

            await interaction.followup.send(embed=embed)

            await log_action(interaction.guild, interaction.user, "sound",
                             details=f"título: {titulo} | url: {url}")

            # Esperar a que termine de reproducir y limpiar
            while voice_client.is_playing():
                await asyncio.sleep(1)

            # Limpiar archivo temporal
            try:
                os.remove(audio_path)
            except Exception:
                pass

        except Exception as e:
            await interaction.followup.send(f"❌ Error al reproducir: `{e}`", ephemeral=True)
            # Limpiar de todos modos
            try:
                os.remove(audio_path)
            except Exception:
                pass

    @bot.tree.command(name="stop", description="Detiene la reproducción de sonido y desconecta al bot de voz")
    async def stop_sound(interaction: discord.Interaction):
        if not await ensure_guild_context(interaction):
            return
        if not is_bot_admin(interaction.guild, interaction.user.id):
            return await no_perms(interaction)

        voice_client = interaction.guild.voice_client
        if not voice_client:
            return await send_error(interaction, "No conectado", "El bot no está en ningún canal de voz.")

        if voice_client.is_playing():
            voice_client.stop()

        await voice_client.disconnect()
        await interaction.response.send_message("⏹️ Reproducción detenida y desconectado del canal de voz.", ephemeral=True)

    @bot.tree.command(name="spamcall", description="Mueve al usuario entre canales de voz ratatata")
    async def spamcall(interaction: discord.Interaction, member: discord.Member, segundos: int = 30):
        if not await ensure_guild_context(interaction): return
        if not is_bot_admin(interaction.guild, interaction.user.id): return await no_perms(interaction)
        if not can_target(interaction.guild, interaction.user.id, member.id):
            return await send_error(interaction, "Objetivo protegido", f"No podés usar el bot contra **{member.display_name}**.")
        if member.id in spam_call_users:
            spam_call_users.discard(member.id)
            return await interaction.response.send_message(f"✅ Spam call detenido en {member.mention}", ephemeral=True)
        if not member.voice or not member.voice.channel:
            return await send_error(interaction, "Usuario no en voz", f"**{member.display_name}** no está en ningún canal de voz.")
        spam_call_users.add(member.id)
        await interaction.response.send_message(f"📞 Spam call activado en {member.mention} por {segundos}s", ephemeral=True)
        await log_action(interaction.guild, interaction.user, "spamcall", member, f"duración: {segundos}s")
        async def call_loop():
            end_time = asyncio.get_event_loop().time() + segundos
            while member.id in spam_call_users and asyncio.get_event_loop().time() < end_time:
                if not member.voice or not member.voice.channel:
                    break
                voice_channels = [c for c in interaction.guild.voice_channels if c != member.voice.channel]
                if not voice_channels:
                    break
                try:
                    await member.move_to(random.choice(voice_channels))
                except Exception as e:
                    print(f"❌ Error en spamcall: {e}")
                    break
                await asyncio.sleep(0.3)
            spam_call_users.discard(member.id)
        asyncio.create_task(call_loop())

    @bot.tree.command(name="lobotomy", description="Alterna mute/deafen para simular lag extremo")
    async def lobotomy(interaction: discord.Interaction, member: discord.Member, segundos: int = 20):
        if not await ensure_guild_context(interaction): return
        if not is_bot_admin(interaction.guild, interaction.user.id): return await no_perms(interaction)
        if not can_target(interaction.guild, interaction.user.id, member.id):
            return await send_error(interaction, "Objetivo protegido", f"No podés usar el bot contra **{member.display_name}**.")
        if not member.voice:
            return await send_error(interaction, "Usuario no en voz", f"**{member.display_name}** no está en ningún canal de voz.")
        await interaction.response.send_message(f"🧠 Lobotomy activado en {member.mention} por {segundos}s", ephemeral=True)
        await log_action(interaction.guild, interaction.user, "lobotomy", member, f"duración: {segundos}s")
        async def lobotomy_loop():
            end_time = asyncio.get_event_loop().time() + segundos
            state = True
            while asyncio.get_event_loop().time() < end_time:
                if not member.voice:
                    break
                try:
                    await member.edit(mute=state, deafen=state)
                    state = not state
                except Exception:
                    break
                await asyncio.sleep(random.uniform(0.2, 0.6))
        asyncio.create_task(lobotomy_loop())

    @bot.tree.command(name="paranoia", description="Envía mensajes perturbadores por MD")
    async def paranoia(interaction: discord.Interaction, member: discord.Member, mensajes: int = 5):
        if not await ensure_guild_context(interaction): return
        if not is_bot_admin(interaction.guild, interaction.user.id): return await no_perms(interaction)
        if not can_target(interaction.guild, interaction.user.id, member.id):
            return await send_error(interaction, "Objetivo protegido", f"No podés usar el bot contra **{member.display_name}**.")
        await interaction.response.send_message(f"👁️ Operación Paranoia iniciada contra {member.mention}", ephemeral=True)
        await log_action(interaction.guild, interaction.user, "paranoia", member, f"mensajes: {mensajes}")
        frases = [
            "Te esta viendo 👁️", "¿Por qué no cierras la ventana?", "El sabe que lo que hiciste.",
            "Hay alguien vigilandote ahora mismo.", "No te muevas.", "¿Escuchaste eso?",
            "No eres el único en tu habitación.", "No mires hacia arriba, o el te buscara", "Tus paredes tienen oídos.",
        ]
        async def paranoia_task():
            for _ in range(mensajes):
                try:
                    await member.send(random.choice(frases))
                    await asyncio.sleep(random.randint(60, 300))
                except Exception:
                    break
        asyncio.create_task(paranoia_task())
