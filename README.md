<p align="center">
  <h1 align="center">🤖 Troller Bot</h1>
  <p align="center">
    <strong>Bot de control, gestión y troleo de usuarios para Discord</strong><br>
    Creado con ❤️ por <strong>+𝟝𝟠𝓵𝓸𝓬𝓸</strong> (mas_58_loco) y <strong>Sandia [🍉]</strong> (prushkax)
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/discord.py-2.3+-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="discord.py">
  <img src="https://img.shields.io/badge/FFmpeg-required-green?style=for-the-badge&logo=ffmpeg&logoColor=white" alt="FFmpeg">
  <img src="https://img.shields.io/badge/license-MIT-orange?style=for-the-badge" alt="License">
</p>

---

## 📖 Descripción

**Troller Bot** es un bot de Discord diseñado para el control y gestión de usuarios con fines de diversión y troleo en servidores. Permite silenciar, ensordecer, expulsar y castigar usuarios en canales de voz, además de reproducir audios aleatorios o desde YouTube directamente en los canales de voz.

El bot soporta **dos sistemas de comandos en paralelo**:
- 🔹 **Slash commands** (`/comando`) — se muestran en el menú autocompletado de Discord
- 🔹 **Comandos con prefijo** (`t!comando`) — se escriben como mensajes normales en el chat

---

## ✨ Características Principales

| Característica | Descripción |
|---|---|
| 🔨 **Sistema de Moderación** | Mute, deafen, kick y castigos completos en canales de voz |
| 👑 **Sistema de Administradores** | Gestión de permisos por servidor con persistencia en archivos |
| 🔊 **Reproducción de Audio** | Audio aleatorio desde carpeta local o desde YouTube en canales de voz |
| 📜 **Logs de Errores** | Registro automático de errores por servidor con historial paginado |
| ⚡ **Comandos Duales** | Todos los comandos disponibles como slash (`/`) y prefijo (`t!`) |
| 🔄 **Re-aplicación automática** | Los castigos se re-aplican si el usuario intenta desmutear/desensordecer |
| 🎨 **Consola con colores** | Salida en consola con colores usando colorama para mejor legibilidad |

---

## 📋 Requisitos

- 🐍 **Python 3.8** o superior
- 🎵 **FFmpeg** (necesario para reproducción de audio)
- 📦 Dependencias listadas en `requirements.txt`:
  - `discord.py[voice]>=2.3.0` — API wrapper de Discord con soporte de voz
  - `python-dotenv>=1.0.0` — Carga de variables de entorno
  - `yt-dlp>=2024.1.0` — Descarga de audio desde YouTube
  - `colorama>=0.4.6` — Colores en la consola
  - `PyNaCl>=1.5.0` — Criptografía para voz de Discord
- 🔑 **Intents** habilitados en el [Portal de Desarrolladores de Discord](https://discord.com/developers/applications):
  - ✅ Presence Intent
  - ✅ Server Members Intent
  - ✅ Message Content Intent

---

## 🚀 Instalación Paso a Paso

### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/troller-bot.git
cd troller-bot
```

### 2️⃣ Crear un entorno virtual (recomendado)

```bash
python -m venv venv

# En Linux/macOS:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

### 3️⃣ Instalar dependencias de Python

```bash
pip install -r requirements.txt
```

### 4️⃣ Instalar FFmpeg

FFmpeg es **obligatorio** para que el bot pueda reproducir audio en canales de voz.

**En Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg -y
```

**En macOS (con Homebrew):**
```bash
brew install ffmpeg
```

**En Windows:**
1. Descarga FFmpeg desde [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extrae el archivo y copia la carpeta `bin` a una ubicación fija
3. Agrega la ruta de la carpeta `bin` al PATH del sistema

Verifica la instalación:
```bash
ffmpeg -version
```

### 5️⃣ Configurar el archivo `.env`

```bash
cp .env.example .env
```

Abre el archivo `.env` y coloca tu token de Discord:

```env
DISCORD_TOKEN=tu_token_aqui
```

> ⚠️ **NUNCA** compartas tu token de Discord ni lo subas a repositorios públicos.

### 6️⃣ Configurar Intents en Discord Developer Portal

Ver la sección [Configuración del Bot de Discord](#-configuración-del-bot-de-discord) más abajo.

### 7️⃣ Ejecutar el bot

```bash
python Bot-main.py
```

Si todo está configurado correctamente, verás un mensaje de bienvenida con colores en la consola indicando que el bot está en línea. 🎉

---

## 🔧 Configuración del Bot de Discord

### Crear la aplicación

1. Ve al [Portal de Desarrolladores de Discord](https://discord.com/developers/applications)
2. Haz clic en **"New Application"** y dale un nombre (ej: `Troller Bot`)
3. Ve a la sección **"Bot"** en el menú lateral
4. Haz clic en **"Add Bot"** y confirma

### Activar los Intents necesarios

En la sección **"Bot"** → **"Privileged Gateway Intents"**, activa los siguientes:

| Intent | ¿Por qué es necesario? |
|---|---|
| ✅ **Presence Intent** | Para detectar el estado de los usuarios |
| ✅ **Server Members Intent** | Para acceder a la lista de miembros y gestionar permisos |
| ✅ **Message Content Intent** | **Obligatorio** para que funcionen los comandos con prefijo `t!` |

> ⚠️ **Importante:** Sin el **Message Content Intent**, los comandos con prefijo (`t!`) **no funcionarán**. Los slash commands (`/`) seguirán operando normalmente.

### Obtener el Token del Bot

1. En la sección **"Bot"**, haz clic en **"Reset Token"**
2. Copia el token generado
3. Pégalo en tu archivo `.env`:
   ```env
   DISCORD_TOKEN=tu_token_aqui
   ```

### Invitar al Bot a tu Servidor

1. Ve a la sección **"OAuth2"** → **"URL Generator"**
2. En **"Scopes"** selecciona:
   - ✅ `bot`
   - ✅ `applications.commands`
3. En **"Bot Permissions"** selecciona:
   - ✅ `Administrator` (recomendado para funcionamiento completo)
   
   O si prefieres permisos específicos:
   - ✅ Mute Members
   - ✅ Deafen Members
   - ✅ Move Members
   - ✅ Connect (canales de voz)
   - ✅ Speak (canales de voz)
   - ✅ Send Messages
   - ✅ Use Application Commands
4. Copia la URL generada y ábrela en tu navegador
5. Selecciona el servidor donde quieres agregar el bot y autoriza

---

## 🔊 Sistema de Audio (Detallado)

El bot tiene un sistema de audio completo que permite reproducir sonidos en canales de voz de dos maneras: **audio aleatorio** desde archivos locales o **audio desde YouTube**.

### 📂 La Carpeta `audios/`

```
Discord/
└── audios/
    ├── sonido1.mp3
    ├── risa.wav
    ├── efecto.ogg
    └── temp_*           ← archivos temporales (se borran automáticamente)
```

La carpeta `audios/` es donde se almacenan los archivos de audio para el modo **random**. El bot selecciona aleatoriamente un archivo de esta carpeta cuando se usa el comando.

### 🎵 Formatos Soportados

| Formato | Extensión |
|---|---|
| MP3 | `.mp3` |
| WAV | `.wav` |
| OGG | `.ogg` |
| M4A | `.m4a` |
| FLAC | `.flac` |
| Opus | `.opus` |
| WebM | `.webm` |

### ➕ Cómo Agregar Archivos de Audio Propios

1. Coloca tus archivos de audio en la carpeta `audios/` del proyecto
2. Asegúrate de que estén en uno de los formatos soportados
3. **No uses el prefijo `temp_`** en los nombres de archivo (esos se consideran temporales y pueden ser eliminados)
4. ¡Listo! El bot los detectará automáticamente cuando uses `t!audio random` o `/audio random`

```bash
# Ejemplo: agregar un audio
cp mi_sonido_gracioso.mp3 audios/
```

### 🎲 Modo Random (`t!audio random` / `/audio random`)

- Selecciona **aleatoriamente** un archivo de la carpeta `audios/`
- Ignora archivos que empiecen con `temp_` (son archivos temporales de YouTube)
- El bot se conecta al canal de voz del usuario, reproduce el audio y se desconecta automáticamente
- Si la carpeta está vacía, el bot mostrará un error

### 🔗 Modo Link (`t!audio <url>` / `/audio link <url>`)

- Descarga el audio de un **enlace de YouTube** usando `yt-dlp`
- El audio se convierte automáticamente a **MP3** con calidad de **192 kbps**
- ⏱️ **Limitación de 20 segundos**: solo se pueden reproducir videos de máximo 20 segundos de duración
- El archivo descargado se guarda temporalmente como `temp_*` en `audios/` y se **elimina automáticamente** después de reproducirlo
- Durante la descarga con prefijo (`t!`), se muestra el indicador de "escribiendo..." en Discord

```bash
# Ejemplo de uso:
t!audio https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### ⚙️ Requisitos del Sistema de Audio

| Requisito | Descripción |
|---|---|
| **FFmpeg** | Obligatorio para la reproducción de audio. Debe estar instalado y accesible en el PATH |
| **yt-dlp** | Necesario para descargar audio desde YouTube. Se instala con `pip install yt-dlp` |
| **PyNaCl** | Biblioteca de criptografía requerida por discord.py para la conexión de voz |

---

## 📜 Lista Completa de Comandos

### 🔨 Moderación (requiere ser admin del bot)

| Slash Command | Prefijo | Descripción | Permisos |
|---|---|---|---|
| `/silenciar @usuario` | `t!silenciar @usuario` | 🔇 Silencia (mutea) a un usuario en el canal de voz | Admin del bot |
| `/ensordecer @usuario` | `t!ensordecer @usuario` | 🔈 Ensordece a un usuario en el canal de voz | Admin del bot |
| `/expulsar @usuario` | `t!expulsar @usuario` | 👢 Desconecta a un usuario del canal de voz | Admin del bot |
| `/castigar @usuario` | `t!castigar @usuario` | 💀 Castigo completo: mute + deafen + ban de voz + desconectar | Admin del bot |
| `/liberar @usuario` | `t!liberar @usuario` | ✅ Libera a un usuario de todos los castigos activos | Admin del bot |

> **Nota sobre castigos:**
> - Los castigos son **persistentes en memoria**: si un usuario castigado intenta desmutear o desensordecer, el bot re-aplica automáticamente el castigo.
> - Los usuarios con ban de voz son **desconectados automáticamente** al intentar unirse a cualquier canal de voz.

### 👑 Administración (solo dueño del bot)

| Slash Command | Prefijo | Descripción | Permisos |
|---|---|---|---|
| `/addadmin @usuario` | `t!addadmin @usuario` | 👑 Agrega un usuario como admin del bot en el servidor | Solo dueño |
| `/removeadmin @usuario` | `t!removeadmin @usuario` | 🚫 Quita a un usuario de la lista de admins del bot | Solo dueño |
| `/admins` | `t!admins` | 📋 Muestra la lista paginada de admins del bot | Solo dueño |
| `/sync` | `t!sync` | 🔄 Sincroniza los slash commands en el servidor actual | Solo dueño |

> **Nota:** El dueño del bot (OWNER_ID) es siempre admin en todos los servidores y no puede ser removido.

### 📜 Historial

| Slash Command | Prefijo | Descripción | Permisos |
|---|---|---|---|
| `/historial [página]` | `t!historial [página]` | 📜 Muestra el historial de errores del servidor (paginado) | Admin del bot |

### 🔊 Audio

| Slash Command | Prefijo | Descripción | Permisos |
|---|---|---|---|
| `/audio random` | `t!audio random` | 🎲 Reproduce un audio aleatorio de la carpeta `audios/` | Admin del bot |
| `/audio link <url>` | `t!audio <url>` | 🔗 Reproduce audio desde YouTube (máx. 20 segundos) | Admin del bot |

---

## 📁 Estructura del Proyecto

```
Discord/
├── 🤖 Bot-main.py              # Punto de entrada principal del bot
├── 📂 commands/                 # Módulos de comandos
│   ├── __init__.py              # Inicializador del paquete
│   ├── moderation.py            # Comandos de moderación (mute, deafen, kick, etc.)
│   ├── admin.py                 # Gestión de administradores y sincronización
│   ├── logs.py                  # Historial de errores por servidor
│   └── audio.py                 # Reproducción de audio (random y YouTube)
├── 📂 utils/                    # Utilidades y funciones auxiliares
│   ├── __init__.py              # Inicializador del paquete
│   └── helpers.py               # Logging con colores, permisos, manejo de errores
├── 📂 data/                     # Datos persistentes (creado automáticamente)
│   ├── admins/                  # Listas de admins por servidor (guild_id.txt)
│   └── logs/                    # Logs de errores por servidor (guild_id.txt)
├── 📂 audios/                   # Archivos de audio para modo random
├── 📄 .env                      # Token del bot (NO incluido en git)
├── 📄 .env.example              # Plantilla del archivo .env
├── 📄 .gitignore                # Archivos ignorados por git
├── 📄 requirements.txt          # Dependencias de Python
└── 📄 README.md                 # Este archivo
```

### Descripción de cada módulo

| Archivo | Descripción |
|---|---|
| `Bot-main.py` | Inicializa el bot, carga token, configura intents, registra comandos slash y prefijo, maneja eventos (`on_ready`, `on_voice_state_update`), y ejecuta la consola interactiva |
| `commands/moderation.py` | Define los 5 comandos de moderación de voz (silenciar, ensordecer, expulsar, castigar, liberar) tanto en slash como en prefijo |
| `commands/admin.py` | Gestión de administradores del bot con persistencia en archivos. Funciones de carga/guardado de admins y comando de sincronización |
| `commands/logs.py` | Lectura y visualización paginada de errores registrados por servidor |
| `commands/audio.py` | Sistema de audio completo: selección aleatoria de archivos locales y descarga/reproducción desde YouTube con yt-dlp |
| `utils/helpers.py` | Funciones auxiliares: logging con colores (colorama), verificación de permisos (`is_owner`, `is_bot_admin`, `can_target`), registro de errores a archivo |

---

## 🖥️ Comandos de Consola

El bot incluye una **consola interactiva** que se ejecuta en la terminal donde fue iniciado. Puedes usar estos comandos directamente en la terminal:

| Comando | Descripción |
|---|---|
| `/test` | ✅ Verifica que el bot está funcionando correctamente. Muestra estado de usuarios muteados, ensordecidos y baneados de voz |
| `/stats` | 📊 Muestra estadísticas del bot: servidores conectados, usuarios totales y cantidad de admins |
| `/quit` | ⏏️ Apaga el bot de forma segura |

```bash
# Ejemplo de uso en la terminal mientras el bot está corriendo:
/test
# ────────────────────────────────
#   ✅ El bot está funcionando correctamente
#   🔇 Usuarios muteados: 0
#   🔈 Usuarios ensordecidos: 0
#   🚫 Usuarios con ban de voz: 0
# ────────────────────────────────
```

---

## 🔍 Troubleshooting (Solución de Problemas)

### ❓ Los slash commands no aparecen en Discord

**Solución:** Los comandos slash pueden tardar hasta 1 hora en sincronizarse globalmente. Para forzar la sincronización:
- Usa `t!sync` en el chat del servidor (requiere ser dueño del bot)
- O usa `/sync` si ya tienes acceso a los slash commands
- Reinicia Discord (Ctrl+R) para refrescar la caché de comandos

### 🔇 El bot no reproduce audio

**Posibles causas:**
1. **FFmpeg no está instalado:** Verifica con `ffmpeg -version` en la terminal
2. **PyNaCl no está instalado:** Ejecuta `pip install PyNaCl`
3. **El bot no tiene permisos de voz:** Asegúrate de que el bot tenga permisos de `Connect` y `Speak` en el canal de voz
4. **La carpeta `audios/` está vacía:** Agrega archivos de audio para usar el modo random

### ⛔ Permisos insuficientes

**Solución:**
- Verifica que el bot tenga el permiso de **Administrator** en el servidor, o al menos los permisos de:
  - `Mute Members`
  - `Deafen Members`
  - `Move Members`
  - `Connect`
  - `Speak`
- El rol del bot debe estar **por encima** del rol de los usuarios que quieres moderar en la jerarquía de roles

### 💬 Los comandos con prefijo (`t!`) no funcionan

**Solución:**
1. Ve al [Portal de Desarrolladores de Discord](https://discord.com/developers/applications)
2. Selecciona tu aplicación → **Bot** → **Privileged Gateway Intents**
3. Activa **Message Content Intent** ✅
4. Reinicia el bot

> Sin este intent, el bot no puede leer el contenido de los mensajes y los comandos con prefijo no se detectarán.

### 🎵 Error al descargar audio de YouTube

**Posibles causas:**
1. **yt-dlp no está instalado:** `pip install yt-dlp`
2. **yt-dlp desactualizado:** `pip install --upgrade yt-dlp`
3. **El video dura más de 20 segundos:** La limitación es intencional para evitar reproducir videos largos
4. **URL inválida:** Verifica que el enlace de YouTube sea correcto y público

### 🔄 El bot muestra "Error: No se encontró DISCORD_TOKEN"

**Solución:**
1. Copia `.env.example` a `.env`: `cp .env.example .env`
2. Edita el archivo `.env` y coloca tu token
3. Asegúrate de que no hay espacios alrededor del `=`

---

## 📝 Notas Importantes

- Los **slash commands** (`/`) responden de forma **efímera** (solo visible para quien ejecuta el comando).
- Los **comandos con prefijo** (`t!`) responden como **mensajes normales** visibles para todos en el canal.
- El bot **re-aplica automáticamente** mute/deafen si un usuario castigado intenta desmutear/desensordecerse.
- Los usuarios con **ban de voz** son desconectados automáticamente al unirse a cualquier canal de voz.
- Las listas de administradores son **persistentes** (se guardan en `data/admins/` por servidor).
- Los logs de errores se almacenan en `data/logs/` separados por servidor.

---

## 👥 Créditos

| Creador | Usuario |
|---|---|
| **+𝟝𝟠𝓵𝓸𝓬𝓸** | mas_58_loco |
| **Sandia [🍉]** | prushkax |

---

## 📄 Licencia

Este proyecto está bajo la licencia **MIT**. Puedes usar, modificar y distribuir el código libremente.

---

<p align="center">
  Hecho con 💀 y mucho troleo<br>
  <strong>Troller Bot</strong> — Porque a veces hay que divertirse 🎉
</p>
