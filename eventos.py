# =========================
# EVENTOS — Handlers de voz, miembros y mensajes
# =========================
import random
import asyncio
import discord
from config import bot, FALACIAS_MENSAJES
from storage import (
    shhh_users, repetidor_users, fantasma_users,
    falacias_users, invertir_users,
    load_muted, load_deafened, load_voice_banned,
    load_forced_nicks,
)

# Mapeo de caracteres para el efecto "invertir" (letras volteadas)
UPSIDE_DOWN_MAP = {
    'a': 'ɐ', 'b': 'q', 'c': 'ɔ', 'd': 'p', 'e': 'ǝ',
    'f': 'ɟ', 'g': 'ƃ', 'h': 'ɥ', 'i': 'ı̣', 'j': 'ɾ̣',
    'k': 'ʞ', 'l': 'ן', 'm': 'ɯ', 'n': 'u', 'ñ': '̃u',
    'o': 'o', 'p': 'd', 'q': 'b', 'r': 'ɹ', 's': 's',
    't': 'ʇ', 'u': 'n', 'v': 'ʌ', 'w': 'ʍ', 'x': 'x',
    'y': 'ʎ', 'z': 'z',
    # Mayúsculas
    'A': '∀', 'B': 'ᗺ', 'C': 'Ɔ', 'D': 'ᗡ', 'E': 'Ǝ',
    'F': 'Ⅎ', 'G': '⅁', 'H': 'H', 'I': 'I', 'J': 'ſ',
    'K': '⋊', 'L': '˥', 'M': 'W', 'N': 'N', 'Ñ': '̃U',
    'O': 'O', 'P': 'Ԁ', 'Q': 'ᕈ', 'R': 'ᴚ', 'S': 'S',
    'T': '⊥', 'U': '∩', 'V': 'Λ', 'W': 'M', 'X': 'X',
    'Y': '⅄', 'Z': 'Z',
    # Dí­gitos
    '0': '0', '1': '⇂', '2': 'ᘔ', '3': 'Ɛ', '4': '߈',
    '5': 'ϛ', '6': '9', '7': 'Ɫ', '8': '8', '9': '6',
}


def invertir_texto(texto: str) -> str:
    """Invierte el texto aplicando el mapeo de caracteres volteados."""
    resultado = []
    for ch in reversed(texto):
        resultado.append(UPSIDE_DOWN_MAP.get(ch, ch))
    return ''.join(resultado)


def register_events():
    @bot.event
    async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild = member.guild
        muted       = load_muted(guild)
        deafened    = load_deafened(guild)
        voice_banned = load_voice_banned(guild)

        if member.id in voice_banned and after.channel is not None:
            await asyncio.sleep(0.5)
            try:
                await member.move_to(None)
            except Exception as e:
                print(f"❌ Error desconectando de voz: {e}")
            return

        if member.id in deafened and before.deaf and not after.deaf:
            await asyncio.sleep(0.3)
            try:
                await member.edit(deafen=True)
            except Exception as e:
                print(f"❌ Error re-ensordeciendo: {e}")

        if member.id in muted and before.mute and not after.mute:
            await asyncio.sleep(0.3)
            try:
                await member.edit(mute=True)
            except Exception as e:
                print(f"❌ Error re-silenciando: {e}")

    @bot.event
    async def on_member_update(before: discord.Member, after: discord.Member):
        guild = after.guild
        forced_nicks = load_forced_nicks(guild)
        if after.id not in forced_nicks:
            return
        forced_nick = forced_nicks[after.id]
        if after.nick != forced_nick:
            await asyncio.sleep(0.3)
            try:
                await after.edit(nick=forced_nick)
            except Exception as e:
                print(f"❌ Error reaplicando nick forzado: {e}")

    @bot.event
    async def on_member_join(member: discord.Member):
        guild = member.guild
        forced_nicks = load_forced_nicks(guild)
        if member.id in forced_nicks:
            nick = forced_nicks[member.id]
            await asyncio.sleep(1)
            try:
                await member.edit(nick=nick)
            except Exception as e:
                print(f"❌ Error aplicando nick al entrar: {e}")

    @bot.event
    async def on_message(message: discord.Message):
        if message.author == bot.user or not message.guild:
            return

        # Shhh — borrar mensajes
        if message.author.id in shhh_users:
            try:
                await message.delete()
            except Exception:
                pass
            return

        # Invertir mensajes con webhook
        if message.author.id in invertir_users and isinstance(message.channel, discord.TextChannel):
            try:
                await message.delete()
                webhooks = await message.channel.webhooks()
                webhook = next((w for w in webhooks if w.name == "TrollerBot-Invertir"), None)
                if not webhook:
                    webhook = await message.channel.create_webhook(name="TrollerBot-Invertir")

                texto_invertido = invertir_texto(message.content)

                await webhook.send(
                    content=texto_invertido or "​",
                    username=message.author.display_name,
                    avatar_url=str(message.author.display_avatar.url)
                )
            except Exception as e:
                print(f"❌ Error en invertir webhook: {e}")
            return

        # Fantasma — robar identidad con webhook
        if message.author.id in fantasma_users and isinstance(message.channel, discord.TextChannel):
            config = fantasma_users[message.author.id]
            try:
                await message.delete()
                webhooks = await message.channel.webhooks()
                webhook = next((w for w in webhooks if w.name == "TrollerBot"), None)
                if not webhook:
                    webhook = await message.channel.create_webhook(name="TrollerBot")
                await webhook.send(
                    content=message.content or "​",
                    username=config["name"],
                    avatar_url=config["avatar"]
                )
            except Exception as e:
                print(f"❌ Error en fantasma: {e}")
            return

        # Repetidor
        if message.author.id in repetidor_users:
            try:
                await message.channel.send(f"{message.author.mention} {message.content}")
            except Exception:
                pass

        # Falacias
        if message.author.id in falacias_users and isinstance(message.channel, discord.TextChannel):
            if random.random() < 0.4:
                try:
                    falacia = random.choice(FALACIAS_MENSAJES)
                    webhooks = await message.channel.webhooks()
                    webhook = next((w for w in webhooks if w.name == "TrollerBot"), None)
                    if not webhook:
                        webhook = await message.channel.create_webhook(name="TrollerBot")
                    await webhook.send(
                        content=falacia,
                        username=message.author.display_name,
                        avatar_url=message.author.display_avatar.url
                    )
                except Exception as e:
                    print(f"❌ Error en falacias: {e}")

        # Solo usamos slash commands, no procesamos prefijos
