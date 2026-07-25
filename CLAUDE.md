# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Troller Bot is a Spanish-language Discord bot for trolling and moderating users in voice and text channels. Built with `discord.py` using slash commands (`app_commands`). This is the modular version split across `main.py` + `config.py` + individual `comandos_*.py` files. A legacy monolithic version is archived at `backup/Bot-main.py`.

## Running the bot

```bash
python main.py          # modular version (recommended)
# python Bot-main.py    # monolithic version — archived at backup/Bot-main.py
```

There is no virtual environment, requirements file, or dependency manager. Install dependencies manually:

```bash
pip install discord.py python-dotenv yt-dlp
```

FFmpeg must be installed on the system for the `/sound` command. YouTube downloads may fail unless cookies are exported first (see below).

**YouTube cookies setup** (needed for `/sound`):
1. Log into YouTube in Opera GX
2. Close Opera GX completely
3. Run `python export_cookies.py` — this creates `cookies.txt`
4. Reopen Opera GX

`export_cookies.py` is a standalone utility (not imported by the bot). It copies Opera GX's SQLite cookie database to a temp file, queries for YouTube/Google cookies, and writes them in Netscape format to `cookies.txt` for yt-dlp.

## Environment

Copy `.env` and fill in:
- `DISCORD_TOKEN` — the bot token
- `OWNER_ID` — the Discord user ID of the bot owner (has full control)

## Architecture

### Entry point and bot lifecycle (`main.py`)

`main.py` is the entry point. It:
1. Imports `bot` and `TOKEN` from `config.py`
2. Registers event handlers via `eventos.register_events()`
3. Registers slash commands via each `comandos_*.py` module's `setup()` function
4. Sets a global `on_app_command_error` handler for permission/cooldown errors
5. On `on_ready`: loads per-guild persisted state from disk, ensures the bot has its identity role (`Troller Bot`), syncs slash commands to each guild individually (not globally), and prints synced command names

### Core modules

**`config.py`** — Bot instance (`commands.Bot` with `!` prefix), token (hardcoded — `.env` fallback exists for `OWNER_ID` but not token), intents (members, voice_states, message_content), and shared constant lists (`RANDOM_NICKS`, `FALACIAS_MENSAJES`).

**`db.py`** — SQLite connection management. Singleton WAL-mode connection (`Base de Datos/trollerbot.db`), `init_db()` creates tables on first run, `execute()`/`executemany()` convenience helpers.

**`storage.py`** — All state management:
- **Session-only (in-memory, lost on restart):** `shhh_users`, `repetidor_users`, `fantasma_users`, `random_nick_users`, `spam_call_users`, `falacias_users`, `invertir_users`, `ACCESS_MODES`, `ACCESS_ROLES` — active toggle effects and access config cached in memory
- **Persisted (SQLite, survives restarts):** `load_*`/`save_*` functions query `trollerbot.db` using `guild.id` as key (not guild name). Tables: `admins`, `muted`, `deafened`, `voice_banned`, `forced_nicks`, `guild_settings` (log channel + access config).
- `run_migration(bot)` — one-time migration from old `.txt` files to SQLite. Called automatically in `on_ready` before loading state. Deletes migrated txt files on success.

**`permisos.py`** — Three-tier authorization:
1. `is_owner()` — checks against `OWNER_ID`
2. `is_bot_admin()` — owner, or admin list, or role-based, or everyone (depending on `ACCESS_MODES[guild_id]`)
3. `can_target()` — prevents targeting owner or other admins

Plus error/solution helpers (`send_error`, `no_perms`, `handle_forbidden` for 403 errors).

**`roles.py`** — Creates and assigns the `Troller Bot` role on guild join (gives the bot a visible identity). Also manages the `Troleado` role used by `/castigar`.

**`eventos.py`** — Event handlers registered via `register_events()`:
- `on_voice_state_update` — enforces mute/deafen/voice-ban (re-applies if user tries to undo)
- `on_member_update` — re-applies forced nicknames
- `on_member_join` — applies forced nick on join
- `on_message` — processes text toggles before `bot.process_commands()`: delete messages (shhh), echo (repetidor), webhook impersonation (fantasma), upside-down text (invertir), random weird messages at 40% chance (falacias)

**`logger.py`** — Dual logging: inserts into `action_logs` table in SQLite, and sends a rich embed to the configured log channel. Color and emoji per command type.

### Command modules

Each module exposes a `setup()` function that registers slash commands on the global `bot.tree`:

| Module | Commands |
|---|---|
| `comandos_admin.py` | `/addadmin`, `/removeadmin`, `/admins`, `/accessmode`, `/log` |
| `comandos_mod.py` | `/silenciar`, `/ensordecer`, `/castigar`, `/liberar`, `/expulsar`, `/fakeban`, `/unfakeban` |
| `comandos_nick.py` | `/forcenick`, `/unforcenick`, `/randomnick`, `/nickspam` |
| `comandos_troleo.py` | `/shhh`, `/fantasma`, `/unfantasma`, `/repetidor`, `/falacias`, `/invertir` |
| `comandos_voz.py` | `/sound`, `/stop`, `/spamcall`, `/lobotomy`, `/paranoia` |
| `comandos_util.py` | `/suggest`, `/historial`, `/help` |
| `comandos_premium.py` | `/claim`, `/genkey`, `/premium`, `/keys` |

All moderation/trolling commands require `is_bot_admin()` and `can_target()` checks. Commands use `interaction.response.send_message(embed=..., ephemeral=True)` for feedback and call `log_action()` afterward.

### Premium system

**`premium_db.py`** — Separate SQLite database (`Base de Datos/premium.db`) for premium state. Tables: `premium_keys` (activation codes with duration, usage status, creation metadata) and `premium_servers` (per-guild premium status with expiration).

**`premium.py`** — Core premium logic: key generation (`TROLLER-XXXX-XXXX-XXXX` format), key claiming with validation, premium status checks with in-memory cache for fast lookups, auto-expiry on every check (cleans up DB on expiration), and startup mass-expiry sweep.

**Premium validation** — A `bot.tree.interaction_check` in `main.py` runs before every slash command. Non-premium servers are restricted to 5 basic commands (defined in `config.py` as `BASIC_COMMANDS`): `/help`, `/suggest`, `/historial`, `/sound`, `/stop`, plus the premium commands themselves (`/claim`, `/premium`). The owner always bypasses all checks. Rejected commands get an ephemeral embed explaining how to upgrade.

### Persistent data pattern

All per-guild state is stored in `trollerbot.db` (SQLite) keyed by `guild.id`. The DB file is auto-created on first run. The old flat `.txt` file system is auto-migrated on first startup and files are deleted.

`Sugerencias.txt` remains a plain text file (global suggestion inbox, only appended to, never read by the bot).

The `.gitignore` excludes: `.env`/`.env.*`, `__pycache__/`, `Base de Datos/` (the SQLite DB), old `*_*.txt` and `log-*.txt` data files, `cookies.txt`, and `Sugerencias.txt`.

`temp.py` is a meme/joke file — not imported by the bot, safe to ignore.

## Backup

The legacy monolithic version is archived at `backup/Bot-main.py` (~1300 lines). It uses the old txt-file persistence and should not be run — it's kept only for reference.

## Key patterns

- **SQLite persistence** — `trollerbot.db` with WAL mode, `check_same_thread=False` for thread safety
- **Blocking DB I/O in async context** — `load_*`/`save_*` functions use synchronous SQLite calls; acceptable because Discord API latency dominates
- **Guild-scoped commands** — commands are synced per-guild with `bot.tree.sync(guild=guild)`, not globally
- **Toggle pattern** — most trolling commands toggle on/off: calling again with the same target removes the effect
- **Webhook impersonation** — `fantasma`, `invertir`, and `falacias` delete the user's original message and re-send it through a webhook with custom name/avatar
- **Re-apply loops** — mute/deafen/voice-ban/nick enforcement uses `on_voice_state_update`/`on_member_update` events, not timers
- **save_* delete+insert pattern** — set-based saves do `DELETE FROM table WHERE guild_id=?` + batch `INSERT`, all in one transaction
- **Migration on startup** — `run_migration()` in `on_ready` handles old txt→DB migration and deletes migrated files
- **Premium check** — `interaction_check` gates every slash command; `BASIC_COMMANDS` list defines the 5 free commands + premium commands. Owner always bypasses.
- **Premium cache** — `_premium_cache` dict in `premium.py` avoids SQLite queries on every command; populated at startup via `load_all_premium()` and updated on claim/expiry
