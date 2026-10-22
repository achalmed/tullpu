"""tullpu/manifiesto.py — el manifiesto del editor de fotos (Tullpu): el mismo dentro de Qillqa y solo.

El editor de fotos del estudio (foto.html y el revelado de media.html) como módulo: su API (`tullpu/api.py`) sobre la
base común de los editores (Ruray), que porta el servidor del estudio a FastAPI. Sin base de datos y sin necesitar nada
del anfitrión: la cuenta llega por «identidad.v1» y el kit común, de Unancha (UNANCHA_DIR). Aprovecha la Mediateca
(«medios.v2»: su selector, y lo exportado va a ella) y la referencia «piezas:pieza:N»; solo, sin ellas, trabaja con su
banco y su salida (`tullpu/sola.py`). Su web: `web/src/componentes/fotos/modulo.ts`.
"""
from __future__ import annotations

from tiqsi import Manifiesto

from tullpu import api as fotos

VERSION = "0.1.0"

MANIFIESTO = Manifiesto(
    id="fotos", nombre="Editor de fotos", version=VERSION, contrato="^0.1",
    routers=[fotos.router],
    # Los prefijos con que se apaga (los del registro de módulos encendibles de Qillqa).
    prefijos=("/api/fotos",),
)
