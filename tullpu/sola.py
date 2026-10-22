"""tullpu/sola.py — el editor de fotos SOLO: sin Qillqa, con el anfitrión mínimo de Tiqsi (Tullpu). Sin base de datos y
sin Mediateca: su banco, su almacén, sus proyectos y su salida viven en su carpeta; el kit común (colores, fuentes,
logos, marcos), en Unancha.

    TULLPU_DIR=…  UNANCHA_DIR=…  JWT_SECRET=<32 o más caracteres> \\
      .venv/bin/uvicorn tullpu.sola:app --port 8037

Las cuentas viven en TULLPU_CUENTAS (por omisión <TULLPU_DIR>/cuentas.json). Sin IDENTIDAD_PERFIL, el perfil del editor
se escribe la primera vez en <TULLPU_DIR>/perfil.json, con sus carpetas dentro de TULLPU_DIR.
"""
from __future__ import annotations

import os
from pathlib import Path

from ruray.comun import perfil_propio
from tiqsi.minimo import crear_app

from tullpu.manifiesto import MANIFIESTO

carpeta = os.environ.get("TULLPU_DIR", "")
if not carpeta:
    raise SystemExit("El editor de fotos solo necesita su carpeta (su banco, sus proyectos y sus cuentas): TULLPU_DIR.")
secreto = os.environ.get("JWT_SECRET", "")
if len(secreto) < 32:
    raise SystemExit("El editor de fotos solo necesita su secreto: JWT_SECRET (32 caracteres o más; firma las sesiones).")
# El servidor del estudio lee el perfil al cargarse (la primera petición): va antes.
os.environ.setdefault("IDENTIDAD_PERFIL", str(perfil_propio(Path(carpeta), "editor de fotos")))

app = crear_app([MANIFIESTO], nombre="Editor de fotos", secreto=secreto,
                cuentas=os.environ.get("TULLPU_CUENTAS") or Path(carpeta) / "cuentas.json",
                web=os.environ.get("TULLPU_WEB") or None)
