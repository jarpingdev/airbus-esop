#!/usr/bin/env python3
"""
Sincroniza y genera las versiones standalone de Airbus ESOP desde index.html.
index.html ya es 100% autónomo (Tailwind CSS compilado, SVG Lucide inline, cero CDN).
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INDEX_PATH = BASE_DIR / "index.html"
OUT_DESKTOP = Path.home() / "Desktop" / "Airbus_ESOP.html"
OUT_DEV = BASE_DIR / "Airbus_ESOP_Standalone.html"
OUT_DEV_ALIAS = BASE_DIR / "airbus_esop.html"

def main():
    if not INDEX_PATH.exists():
        raise FileNotFoundError(f"No se encontró index.html en {INDEX_PATH}")

    content = INDEX_PATH.read_text(encoding="utf-8")

    # Guardar en Desktop si es accesible
    try:
        OUT_DESKTOP.write_text(content, encoding="utf-8")
        print(f"  1. {OUT_DESKTOP} ({len(content)} bytes)")
    except Exception as e:
        print(f"  Nota: No se pudo escribir en el Escritorio: {e}")

    # Guardar en la carpeta del repositorio
    OUT_DEV.write_text(content, encoding="utf-8")
    print(f"  2. {OUT_DEV}")

    OUT_DEV_ALIAS.write_text(content, encoding="utf-8")
    print(f"  3. {OUT_DEV_ALIAS}")

    print("✅ Archivos standalone sincronizados correctamente desde index.html.")

if __name__ == "__main__":
    main()
