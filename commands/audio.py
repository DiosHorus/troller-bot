"""
audio.py - Comando de audio del Troller Bot
Comando: /audio (random o link de YouTube)
Requiere: discord.py[voice], yt-dlp, FFmpeg
Creado por +𝟝𝟠𝓵𝓸𝓬𝓸 (mas_58_loco) y Sandia [🍉] (prushkax)
"""

import os
import random
import asyncio
import discord
from discord import app_commands
from utils.helpers import (
    is_bot_admin,
    log_command,
    log_success,
    log_error,
    log_error_console,
    log_info,
)

# Carpeta de audios
AUDIOS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "audios")

# Extensiones de audio soportadas
AUDIO_EXTENSIONS = (".mp3", ".wav", ".ogg", ".m4a", ".flac", ".opus", ".webm")

# Duración máxima para descargas de YouTube (en segundos)
MAX_DURATION = 20

# Opciones de yt-dlp para descargar audio
YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "outtmpl": os.path.join(AUDIOS_DIR, "temp_%(id)s.%(ext)s"),
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",
    # Limitar a MAX_DURATION segundos
    "match_filter": f"duration <= {MAX_DURATION}",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
}

# Opciones de FFmpeg
FFMPEG_OPTIONS = {
    "options": "-vn",
}


def setup(
    bot: discord.Client,
    tree: app_commands.CommandTree,
    bot_admins: dict,
):
    """Registra el comando de audio en el árbol de comandos."""

    @tree.command(
        name="audio",
        description="🔊 Reproduce un audio en el canal de voz (random o desde YouTube)."
    )
    @app_commands.describe(
        modo="Elige el modo: 'random' para un audio aleatorio o 'link' para YouTube",
        url="URL de YouTube (solo si el modo es 'link')",
    )
    @app_commands.choices(
        modo=[
            app_commands.Choice(name="🎲 Random (audio aleatorio)", value="random"),
            app_commands.Choice(name="🔗 Link (YouTube)", value="link"),
        ]
    )
    async def audio(
        interaction: discord.Interaction,
        modo: app_commands.Choice[str],
        url: str = None,
    ):
        log_command(str(interaction.user), "audio", interaction.guild.name)

        # Verificar permisos
        if not is_bot_admin(interaction.user.id, interaction.guild_id, bot_admins):
            await interaction.response.send_message(
                "❌ No tienes permisos para usar este comando.", ephemeral=True
            )
            return

        # Verificar que el usuario está en un canal de voz
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message(
                "❌ Debes estar en un canal de voz para usar este comando.", ephemeral=True
            )
            return

        voice_channel = interaction.user.voice.channel

        # Defer la respuesta porque puede tardar
        await interaction.response.defer(ephemeral=True)

        audio_path = None
        temp_file = False  # Si es un archivo temporal que hay que borrar

        try:
            if modo.value == "random":
                # ─── Modo Random ───
                audio_path = _get_random_audio()
                if not audio_path:
                    await interaction.followup.send(
                        "❌ No hay archivos de audio en la carpeta `audios/`.", ephemeral=True
                    )
                    return
                log_info(f"Audio random seleccionado: {os.path.basename(audio_path)}")

            elif modo.value == "link":
                # ─── Modo Link (YouTube) ───
                if not url:
                    await interaction.followup.send(
                        "❌ Debes proporcionar una URL de YouTube cuando usas el modo 'link'.",
                        ephemeral=True,
                    )
                    return

                log_info(f"Descargando audio desde YouTube: {url}")
                audio_path = await _download_youtube(url)
                if not audio_path:
                    await interaction.followup.send(
                        f"❌ No se pudo descargar el audio. "
                        f"Verifica que el enlace sea válido y dure máximo {MAX_DURATION} segundos.",
                        ephemeral=True,
                    )
                    return
                temp_file = True
                log_success(f"Audio descargado: {os.path.basename(audio_path)}")

            # ─── Conectar al canal de voz y reproducir ───
            voice_client = await voice_channel.connect()

            try:
                source = discord.FFmpegPCMAudio(audio_path, **FFMPEG_OPTIONS)
                voice_client.play(source)

                # Esperar a que termine de reproducir
                while voice_client.is_playing():
                    await asyncio.sleep(0.5)

                await interaction.followup.send(
                    f"🔊 Audio reproducido exitosamente en **{voice_channel.name}**.",
                    ephemeral=True,
                )
                log_success(f"Audio reproducido en {voice_channel.name} ({interaction.guild.name})")

            finally:
                # Desconectar del canal
                if voice_client and voice_client.is_connected():
                    await voice_client.disconnect()

                # Borrar archivo temporal si es de YouTube
                if temp_file and audio_path and os.path.exists(audio_path):
                    try:
                        os.remove(audio_path)
                        log_info(f"Archivo temporal eliminado: {os.path.basename(audio_path)}")
                    except Exception as e:
                        log_error_console(f"No se pudo eliminar archivo temporal: {e}")

        except discord.ClientException as e:
            await interaction.followup.send(
                f"❌ Error de conexión de voz: {e}", ephemeral=True
            )
            log_error(interaction.guild_id, "audio", str(e))
        except Exception as e:
            await interaction.followup.send(
                f"❌ Ocurrió un error: {e}", ephemeral=True
            )
            log_error(interaction.guild_id, "audio", str(e))


def _get_random_audio() -> str | None:
    """
    Obtiene un archivo de audio aleatorio de la carpeta audios/.
    Retorna la ruta completa o None si no hay archivos.
    """
    os.makedirs(AUDIOS_DIR, exist_ok=True)
    archivos = [
        f for f in os.listdir(AUDIOS_DIR)
        if f.lower().endswith(AUDIO_EXTENSIONS) and not f.startswith("temp_")
    ]
    if not archivos:
        return None
    return os.path.join(AUDIOS_DIR, random.choice(archivos))


async def _download_youtube(url: str) -> str | None:
    """
    Descarga el audio de un video de YouTube usando yt-dlp.
    Retorna la ruta del archivo descargado o None si falla.
    Solo permite videos de máximo MAX_DURATION segundos.
    """
    try:
        import yt_dlp
    except ImportError:
        log_error_console("yt-dlp no está instalado. Instálalo con: pip install yt-dlp")
        return None

    os.makedirs(AUDIOS_DIR, exist_ok=True)

    try:
        loop = asyncio.get_event_loop()

        # Ejecutar la descarga en un thread para no bloquear el event loop
        def _download():
            with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=True)
                # Buscar el archivo descargado
                if info:
                    # yt-dlp con postprocessor cambia la extensión a mp3
                    filename = ydl.prepare_filename(info)
                    # Reemplazar la extensión original por .mp3
                    base, _ = os.path.splitext(filename)
                    mp3_path = base + ".mp3"
                    if os.path.exists(mp3_path):
                        return mp3_path
                    # Si no existe el .mp3, buscar el archivo original
                    if os.path.exists(filename):
                        return filename
                return None

        result = await loop.run_in_executor(None, _download)
        return result

    except Exception as e:
        log_error_console(f"Error descargando de YouTube: {e}")
        return None
