# =========================
# export_cookies.py — Exporta cookies de YouTube de Opera GX a cookies.txt
# =========================
# Instrucciones:
#   1. CERRÁ Opera GX (importante, sino no se puede leer la base de datos)
#   2. Ejecutá: python export_cookies.py
#   3. Abrí Opera GX de nuevo
# =========================
import sqlite3
import os
import shutil
import tempfile
from pathlib import Path

COOKIES_DB = os.path.join(
    os.path.expandvars(r"%APPDATA%"),
    "Opera Software", "Opera GX Stable", "Default", "Network", "Cookies"
)
OUTPUT_FILE = Path(__file__).parent / "cookies.txt"

def export_cookies():
    if not os.path.exists(COOKIES_DB):
        print(f"❌ No se encontró la base de datos de cookies de Opera GX.")
        print(f"   Ruta esperada: {COOKIES_DB}")
        return False

    tmp = os.path.join(tempfile.gettempdir(), "opera_gx_cookies_export.db")

    try:
        # Intentar copiar el archivo
        shutil.copy2(COOKIES_DB, tmp)
        print(f"✅ Cookies copiadas ({os.path.getsize(tmp)} bytes)")
    except PermissionError:
        print(f"❌ No se pudo leer el archivo de cookies.")
        print(f"   Asegurate de CERRAR Opera GX completamente y volvé a intentar.")
        return False
    except Exception as e:
        print(f"❌ Error copiando cookies: {e}")
        return False

    try:
        conn = sqlite3.connect(tmp)
        cursor = conn.execute(
            "SELECT host_key, name, value, path, expires_utc, is_secure, is_httponly "
            "FROM cookies WHERE host_key LIKE '%youtube%' OR host_key LIKE '%google%'"
        )
        cookies = cursor.fetchall()
        conn.close()

        if not cookies:
            print("⚠️ No se encontraron cookies de YouTube/Google en Opera GX.")
            print("   Iniciá sesión en YouTube desde Opera GX y volvé a intentar.")
            return False

        # Escribir en formato Netscape (el que usa yt-dlp)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write("# Extraído de Opera GX para Troller Bot\n\n")
            for host_key, name, value, path, expires, secure, httponly in cookies:
                secure_flag = "TRUE" if secure else "FALSE"
                expires_val = str(int(expires / 1000000)) if expires and expires > 0 else "0"
                f.write(f"{host_key}\tTRUE\t{path}\t{secure_flag}\t{expires_val}\t{name}\t{value}\n")

        print(f"✅ {len(cookies)} cookies exportadas a: {OUTPUT_FILE}")
        return True

    except Exception as e:
        print(f"❌ Error procesando cookies: {e}")
        return False
    finally:
        try:
            os.remove(tmp)
        except Exception:
            pass

if __name__ == "__main__":
    print("=" * 50)
    print("  Troller Bot — Exportador de Cookies")
    print("=" * 50)
    if export_cookies():
        print("\n✅ Listo. Ya podés usar /sound en Discord.")
    else:
        print("\n❌ Falló la exportación. Revisá los errores arriba.")
