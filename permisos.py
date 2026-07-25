# =========================
# PERMISOS — Verificación de permisos y helpers de errores
# =========================
import discord
from config import OWNER_ID
from storage import ACCESS_MODES, ACCESS_ROLES, load_admins

# =========================
# PERMISOS
# =========================
def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID

def is_bot_admin(guild: discord.Guild, user_id: int) -> bool:
    if user_id == OWNER_ID:
        return True
    mode = ACCESS_MODES.get(guild.id, "admin_only")
    if mode == "everyone":
        return True
    if mode == "role":
        role_id = ACCESS_ROLES.get(guild.id)
        if role_id:
            member = guild.get_member(user_id)
            if member and any(r.id == role_id for r in member.roles):
                return True
        return False
    return user_id in load_admins(guild)

def can_target(guild: discord.Guild, actor_id: int, target_id: int) -> bool:
    admins = load_admins(guild)
    if target_id == OWNER_ID and actor_id != OWNER_ID:
        return False
    if actor_id != OWNER_ID and target_id in admins:
        return False
    return True

async def ensure_guild_context(interaction: discord.Interaction) -> bool:
    if interaction.guild is None:
        await send_error(interaction, "Contexto inválido", "Este comando solo funciona dentro de un servidor.")
        return False
    return True

# =========================
# HELPERS DE ERRORES
# =========================
async def send_error(interaction: discord.Interaction, title: str, description: str, solution: str = None):
    """Manda un embed de error rojo con título, descripción y solución opcional."""
    embed = discord.Embed(
        title=f"❌ {title}",
        description=description,
        color=discord.Color.red()
    )
    if solution:
        embed.add_field(name="💡 Cómo solucionarlo", value=solution, inline=False)
    embed.set_footer(text="Troller Bot — Sistema de errores")

    try:
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        print(f"❌ Error enviando embed de error: {e}")

async def no_perms(interaction: discord.Interaction):
    """Mensaje de sin permisos según el modo de acceso activo."""
    mode = ACCESS_MODES.get(interaction.guild.id, "admin_only")
    if mode == "admin_only":
        desc = "No tenés admin en el bot."
        sol  = "Pedíselo al owner para que te agregue con `/addadmin`."
    elif mode == "role":
        role_id = ACCESS_ROLES.get(interaction.guild.id)
        role = interaction.guild.get_role(role_id) if role_id else None
        role_name = f"**{role.name}**" if role else "el rol requerido"
        desc = f"No tenés el rol {role_name} para usar el bot."
        sol  = f"Pedile a un admin del servidor que te dé el rol {role_name}."
    else:
        desc = "No tenés permisos para usar este comando."
        sol  = None
    await send_error(interaction, "Sin permisos", desc, sol)

async def handle_forbidden(interaction: discord.Interaction, action: str, member: discord.Member = None):
    """Maneja errores 403 Forbidden con mensajes específicos."""
    bot_member = interaction.guild.me

    # Detectar si es problema de jerarquía
    if member and member.top_role >= bot_member.top_role:
        await send_error(
            interaction,
            "Error de jerarquía",
            f"No puedo {action} a **{member.display_name}** porque su rol más alto "
            f"(`{member.top_role.name}`) es igual o superior al mío (`{bot_member.top_role.name}`).",
            "Subí el rol **Troller Bot** por encima del rol del usuario en "
            "**Configuración del servidor → Roles**."
        )
    else:
        # Detectar qué permiso falta según la acción
        perm_map = {
            "silenciar":   ("Mute Members",   "Silenciar miembros"),
            "ensordecer":  ("Deafen Members",  "Ensordecer miembros"),
            "expulsar":    ("Kick Members",    "Expulsar miembros"),
            "mover":       ("Move Members",    "Mover miembros"),
            "nick":        ("Manage Nicknames","Gestionar apodos"),
            "rol":         ("Manage Roles",    "Gestionar roles"),
            "canal":       ("Manage Channels", "Gestionar canales"),
            "webhook":     ("Manage Webhooks", "Gestionar webhooks"),
            "mensaje":     ("Manage Messages", "Gestionar mensajes"),
        }
        perm_en, perm_es = perm_map.get(action, ("Administrator", "Administrador"))
        await send_error(
            interaction,
            "Sin permisos del bot",
            f"El bot no tiene el permiso **{perm_es}** para {action}.",
            f"Andá a **Configuración del servidor → Roles → Troller Bot** "
            f"y activá el permiso **{perm_en}**."
        )
