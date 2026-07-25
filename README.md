# 🤖 Troller Bot

Bot de Discord en español para administrar, moderar y trolear usuarios en canales de voz y texto. Construido con `discord.py` usando slash commands (`/`).

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![discord.py](https://img.shields.io/badge/discord.py-2.x-5865F2)](https://discordpy.readthedocs.io/)
[![SQLite](https://img.shields.io/badge/SQLite-WAL%20mode-003B57)](https://sqlite.org/)

---

## ✨ Características

### 🛡️ Moderación por voz y texto
- **Silenciar / Ensordecer** — Mutea o ensordece usuarios en canales de voz. El bot **reaplica** el efecto automáticamente si el usuario intenta desactivarlo.
- **Castigar / Liberar** — Aplica mute + deafen + bloqueo de voz + rol `@Troleado` todo junto. `/liberar` quita todo de una vez.
- **Expulsar** — Kick con razón opcional.
- **FakeBan** — Oculta todos los canales del usuario y crea `#fuiste-baneado` para simular un baneo. `/unfakeban` restaura el acceso.

### 📛 Control de apodos
- **Forzar nick** — Impone un apodo que se reaplica automáticamente si el usuario lo cambia o se reconecta.
- **Random nick** — Cambia el apodo cada 5 minutos con frases aleatorias. Toggle on/off.
- **Nick spam** — Cambia el nick frenéticamente cada 0.8s durante X segundos.

### 😈 Troleo por texto
- **Shhh** 🤫 — Borra automáticamente todos los mensajes del usuario.
- **Fantasma** 👻 — Suplanta la identidad del usuario vía webhook (nombre y foto personalizados). Toggle.
- **Repetidor** 🔁 — El bot repite todo lo que escriba el usuario.
- **Falacias** 🌀 — 40% de probabilidad de reemplazar sus mensajes con frases pseudo-filosóficas absurdas.
- **Invertir** 🙃 — Invierte el texto de sus mensajes (`oʇɹǝʌuı oʇxǝʇ`).

### 🎙️ Voz y sonido
- **Sound** 🔊 — Descarga audio de YouTube con `yt-dlp` y lo reproduce en tu canal de voz vía FFmpeg.
- **SpamCall** 📞 — Mueve al usuario aleatoriamente entre canales de voz cada 0.3s.
- **Lobotomy** 🧠 — Alterna mute/deafen rápidamente simulando lag extremo.
- **Paranoia** 👁️ — Envía mensajes perturbadores por MD cada 1-5 minutos.

### ⭐ Sistema Premium
- Servidores **gratuitos**: 7 comandos básicos (`/help`, `/suggest`, `/historial`, `/sound`, `/stop`, `/claim`, `/premium`).
- Servidores **premium**: acceso a los **34 comandos**.
- Activación por **keys** (`TROLLER-XXXX-XXXX-XXXX`) con duraciones flexibles: 7d, 30d, 3m, 6m, 1y o permanente.
- Expiración automática chequeada en cada comando y al iniciar el bot.

### ⚙️ Gestión de permisos
- **Tres modos de acceso** por servidor:
  - `admin_only` — Solo admins designados por el owner.
  - `role` — Cualquiera con un rol específico del servidor.
  - `everyone` — Todos los miembros del servidor.
- El **owner** del bot siempre tiene acceso total (bypassea premium y restricciones).

### 📋 Registro de acciones
- **Doble log**: todas las acciones se guardan en base de datos SQLite **y** se envían como embed a un canal de logs configurable.
- **Historial** por usuario: `/historial <@usuario>` muestra las últimas 5 acciones recibidas y emitidas.
- Logs en archivo: `logs/commands.log` (todos) y `logs/premium.log` (solo comandos premium, con salida en consola).
- Sistema de **sugerencias**: `/suggest` guarda en archivo y manda DM al owner.

---

## 📦 Comandos (34)

| Categoría | Comandos |
|---|---|
| ⚙️ **Admin** | `/addadmin`, `/removeadmin`, `/admins`, `/accessmode`, `/log` |
| ⭐ **Premium** | `/claim`, `/premium`, `/genkey`, `/keys` |
| 🛡️ **Moderación** | `/silenciar`, `/ensordecer`, `/castigar`, `/liberar`, `/expulsar`, `/fakeban`, `/unfakeban` |
| 📛 **Nicks** | `/forcenick`, `/unforcenick`, `/randomnick`, `/nickspam` |
| 😈 **Troleo** | `/shhh`, `/fantasma`, `/unfantasma`, `/repetidor`, `/falacias`, `/invertir` |
| 🎙️ **Voz** | `/sound`, `/stop`, `/spamcall`, `/lobotomy`, `/paranoia` |
| 🧰 **Utilidades** | `/help`, `/suggest`, `/historial` |

> 🔒 = solo owner · 🛡️ = bot admin · 🌟 = requiere premium · 👤 = todos · ↻ = toggle

---

## 🚀 Instalación

```bash
# 1. Clonar
git clone <repo-url>
cd Trollerbot

# 2. Instalar dependencias
pip install discord.py python-dotenv yt-dlp

# 3. FFmpeg (necesario para /sound)
sudo apt install ffmpeg        # Linux
# winget install ffmpeg         # Windows
# brew install ffmpeg           # macOS

# 4. Configurar .env
cp .env.example .env
# Editar DISCORD_TOKEN y OWNER_ID

# 5. Ejecutar
python main.py
```

### Cookies de YouTube (para `/sound`)

Si YouTube bloquea las descargas:

```bash
# 1. Iniciar sesión en YouTube en Opera GX
# 2. Cerrar Opera GX completamente
python export_cookies.py
# 3. Reabrir Opera GX
```

---

## 🗄️ Arquitectura

```
Trollerbot/
├── main.py                  # Entry point, interacción premium, sync
├── config.py                # Bot, token, constantes, BASIC_COMMANDS
├── db.py                    # SQLite principal (trollerbot.db)
├── storage.py               # Estado en memoria + carga/guardado SQLite
├── permisos.py              # Autorización 3 niveles + helpers de error
├── roles.py                 # Roles Troller Bot y Troleado
├── eventos.py               # Eventos: voz, nicks, mensajes (toggles)
├── logger.py                # Logs: SQLite + embed + archivo + consola
├── premium_db.py            # SQLite secundario (premium.db)
├── premium.py               # Lógica de keys, claim, validación, expiración
├── export_cookies.py        # Utilidad standalone para cookies de YT
├── comandos_admin.py        # /addadmin, /removeadmin, /admins, /accessmode, /log
├── comandos_mod.py          # /silenciar, /ensordecer, /castigar, /liberar, /expulsar, /fakeban, /unfakeban
├── comandos_nick.py         # /forcenick, /unforcenick, /randomnick, /nickspam
├── comandos_troleo.py       # /shhh, /fantasma, /unfantasma, /repetidor, /falacias, /invertir
├── comandos_voz.py          # /sound, /stop, /spamcall, /lobotomy, /paranoia
├── comandos_util.py         # /suggest, /historial, /help
├── comandos_premium.py      # /claim, /genkey, /premium, /keys
├── Base de Datos/           # SQLite DBs (gitignored)
├── logs/                    # Archivos de log (gitignored)
└── backup/                  # Versión monolítica legacy
```

**Persistencia**: SQLite con WAL mode. Estado de toggles en memoria (efímero), configuración y castigos en BD (persiste entre reinicios).

**Validación premium**: `interaction_check` global en `main.py` — cada comando slash pasa por el gate antes de ejecutarse. Owner bypassea todo.

---

## 🔑 Sistema de Keys

| Formato | `TROLLER-XXXX-XXXX-XXXX` |
|---|---|
| Duraciones | `7d` · `30d` · `3m` · `6m` · `1y` · `permanent` |
| Generación | `/genkey <duración> [cantidad]` (owner only, máx 10) |
| Activación | `/claim <key>` (cualquier usuario) |
| Expiración automática | Se chequea en cada comando y al iniciar el bot |

---

## 📝 Licencia

MIT — hacé lo que quieras, el bot es para trolear.

---

## ⚠️ Disclaimer

Este bot está hecho para joder entre amigos. No me hago responsable del uso que le des. Si banean tu bot por usarlo para acosar, es tu problema.
