"""tullpu/api.py — el editor de fotos (Tullpu; nació en Qillqa el 2026-10-20, editores E2a, y salió a su repositorio el
2026-10-21).

Sus páginas viven en `paginas/` de este repositorio: `foto.html` (capas, con el motor miniPaint en `foto-lienzo.html` y
`vendor/minipaint/`) y `media.html` (revelar una foto suelta con la plantilla de la marca; Kuyuy la abre para recortar
un video suelto). Las sirve la base común de los editores (Ruray, `ruray.comun`) bajo `/api/fotos/`, con la API que
esas páginas piden en su carpeta: la común (kit, banco, almacén, salidas, el aspecto del estudio) y la suya (proyectos
de fotos y de medios, analizar, mejorar y exportar una foto).

- `POST /api/fotos/sesion` (con la ficha): la cookie del editor para su marco; `DELETE` la borra.
- `GET /api/fotos/` → `foto.html`; el resto, con la cookie.

Con la Mediateca (si el anfitrión ofrece «medios.v2»), su selector la incluye y lo exportado y lo subido entran a ella
(`ruray.mediateca`); solo, sin ella, lo exportado va a la salida de su canal, como en el servidor del estudio.
"""
from __future__ import annotations

from pathlib import Path

from ruray.comun import COMUNES, Editor, crear_router

PAGINAS = Path(__file__).resolve().parents[1] / "paginas"

EDITOR = Editor(
    id="fotos", nombre="Editor de fotos", prefijo="/api/fotos", inicio="foto.html",
    paginas=("foto.html", "foto-lienzo.html", "media.html", "estudio-tema.css", "estudio-iconos.js", "estudio-movil.js",
             "vendor/minipaint/"),
    rutas=COMUNES | {
        "GET api/proyectos-foto", "GET api/proyecto-foto", "POST api/proyecto-foto",
        "GET api/proyectos-media", "GET api/proyecto-media", "POST api/proyecto-media",
        "POST api/analizar-foto", "POST api/mejorar-foto", "POST api/exportar-foto", "POST api/fototeca-pieza",
    },
    carpeta=PAGINAS,
)

router = crear_router(EDITOR)
