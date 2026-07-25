# =========================
# CONFIG — Imports, constantes y bot
# =========================
import os
import re
import random
import asyncio
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "1391026661331435663"))

if not TOKEN:
    raise ValueError("❌ No se encontró DISCORD_TOKEN en el archivo .env")

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# CONSTANTES
# =========================
BOT_ROLE_NAME   = "Troller Bot"
PUNISH_ROLE_NAME = "Troleado"
SUGGEST_FILE    = Path("Sugerencias.txt")

RANDOM_NICKS = [
    "Amo a los gatitos 🐱", "Soy una patata 🥔", "Me gustan los pies",
    "Soy un NPC", "Jajaja no sé nada", "Bot de prueba 🤖", "Señor Cactus 🌵",
    "Troleable Premium", "Hola soy nuevo", "Mi IQ es -5", "Patata Frita 🍟",
    "Amo a Dora la Exploradora", "Soy el jefe aquí", "Bebé llorón 👶",
    "Experto en nada", "Campeón de perder", "Señor Misterioso 🕵️",
]

# Comandos disponibles sin premium (5 básicos)
BASIC_COMMANDS = ["help", "suggest", "historial", "sound", "stop", "claim", "premium"]

FALACIAS_MENSAJES = [
    "a veces me pregunto si los peces sueñan con el agua...",
    "¿y si las sillas tienen sentimientos? 🪑",
    "creo que el sol me está mirando fijamente hoy",
    "los lunes huelen a color azul",
    "mi gato me dijo que el universo es una simulación",
    "¿por qué los espejos no se ven a sí mismos?",
    "hoy vi una nube con forma de existencial crisis",
    "si te caes hacia arriba, ¿es volar?",
    "el wifi tiene sabor a martes",
    "a veces las paredes me escuchan demasiado bien",
    "creo que mi sombra tiene vida propia 👤",
    "¿los números impares se sienten solos?",
    "hoy el silencio sonó muy fuerte",
    "me pregunto si los semáforos se aburren de noche",
    "el olor a lluvia es básicamente la tierra estornudando",
]
