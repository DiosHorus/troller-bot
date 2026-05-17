# 🤖 Troller Bot

Bot de moderación/troll para Discord.  
Creado por **+𝟝𝟠𝓵𝓸𝓬𝓸** (mas_58_loco) y **Sandia [🍉]** (prushkax)

---

## ⚙️ Instalación

1. Clona el repositorio
2. Copia `.env.example` a `.env` y coloca tu token de Discord
3. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Ejecuta:
   ```bash
   python Bot-main.py
   ```

---

## 📋 Comandos

El bot soporta **dos sistemas de comandos en paralelo**:
- **Slash commands** (`/comando`) — se muestran en el menú de Discord
- **Comandos con prefijo** (`t!comando`) — se escriben como mensajes normales

> **Nota:** Los comandos con prefijo requieren el intent `message_content` habilitado en el [Portal de Desarrolladores de Discord](https://discord.com/developers/applications).

### 🔨 Moderación (requiere ser admin del bot)

| Slash Command | Prefijo | Descripción |
|---|---|---|
| `/silenciar @usuario` | `t!silenciar @usuario` | 🔇 Silencia (mutea) a un usuario en voz |
| `/ensordecer @usuario` | `t!ensordecer @usuario` | 🔈 Ensordece a un usuario en voz |
| `/expulsar @usuario` | `t!expulsar @usuario` | 👢 Desconecta a un usuario del canal de voz |
| `/castigar @usuario` | `t!castigar @usuario` | 💀 Castigo completo: mute + deafen + ban de voz + desconectar |
| `/liberar @usuario` | `t!liberar @usuario` | ✅ Libera a un usuario de todos los castigos |

### 👑 Administración (solo dueño del bot)

| Slash Command | Prefijo | Descripción |
|---|---|---|
| `/addadmin @usuario` | `t!addadmin @usuario` | 👑 Agrega un admin del bot |
| `/removeadmin @usuario` | `t!removeadmin @usuario` | 🚫 Quita un admin del bot |
| `/admins` | `t!admins` | 📋 Lista de admins del bot |
| `/sync` | `t!sync` | 🔄 Sincroniza los slash commands en el servidor |

### 📜 Historial (requiere ser admin del bot)

| Slash Command | Prefijo | Descripción |
|---|---|---|
| `/historial [página]` | `t!historial [página]` | 📜 Muestra el historial de errores (paginado) |

### 🔊 Audio (requiere ser admin del bot)

| Slash Command | Prefijo | Descripción |
|---|---|---|
| `/audio random` | `t!audio random` | 🎲 Reproduce un audio aleatorio de la carpeta `audios/` |
| `/audio link <url>` | `t!audio <url>` | 🔗 Reproduce audio desde un enlace de YouTube (máx. 20s) |

---

## 📁 Estructura del proyecto

```
Discord/
├── Bot-main.py          # Punto de entrada principal
├── commands/
│   ├── moderation.py    # Comandos de moderación
│   ├── admin.py         # Sistema de administradores
│   ├── logs.py          # Historial de errores
│   └── audio.py         # Reproducción de audio
├── utils/
│   └── helpers.py       # Funciones auxiliares (logging, permisos)
├── data/
│   ├── admins/          # Listas de admins por servidor
│   └── logs/            # Logs de errores por servidor
├── audios/              # Archivos de audio para modo random
├── .env                 # Token del bot (no incluido en git)
├── .env.example         # Plantilla del archivo .env
├── requirements.txt     # Dependencias de Python
└── README.md
```

---

## 🔧 Requisitos

- Python 3.10+
- FFmpeg (para reproducción de audio)
- [discord.py](https://discordpy.readthedocs.io/) 2.3+
- Intent `message_content` habilitado en el portal de Discord

---

## 📝 Notas

- Los **slash commands** responden de forma efímera (solo visible para quien ejecuta).
- Los **comandos con prefijo** (`t!`) responden como mensajes normales visibles para todos.
- El bot re-aplica automáticamente mute/deafen si un usuario castigado intenta desmutear/desensordecerse.
- Los usuarios con ban de voz son desconectados automáticamente al unirse a cualquier canal.
