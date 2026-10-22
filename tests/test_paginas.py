"""tests/test_paginas.py — las páginas del editor de fotos (`paginas/`): solo cargan lo local, sus textos neutros son los
del servidor del estudio y su bloque de colores es el del kit común. Venían de las pruebas del estudio (Ruray,
estudio/tests/test_servidor.py y test_kit.py) y salieron con las páginas el 2026-10-21.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
from ruray.pruebas import UNANCHA, entorno  # noqa: F401 — `entorno` es un fixture

PAGINAS = Path(__file__).resolve().parents[1] / "paginas"


def test_editor_de_fotos_sin_recursos_externos():
    """foto.html y su marco cargan solo lo local (tema, íconos, miniPaint de vendor/): nada de CDN; el marco lo
    impone además con su Content-Security-Policy."""
    vendor = PAGINAS / "vendor" / "minipaint"
    assert "Permission is hereby granted, free of charge" in (vendor / "LICENSE").read_text(encoding="utf-8")   # MIT
    assert (vendor / "dist" / "bundle.js").is_file() and (vendor / "README.md").is_file()
    for nombre in ("foto.html", "foto-lienzo.html"):
        html = (PAGINAS / nombre).read_text(encoding="utf-8")
        refs = re.findall(r"""<(?:script|link|img|iframe)\b[^>]*\b(?:src|href)=["']([^"']+)""", html, re.I)
        assert refs, nombre
        externas = [r for r in refs if re.match(r"(?:[a-z]+:)?//", r, re.I)]
        assert externas == [], "%s carga recursos externos: %s" % (nombre, externas)
        assert not re.search(r"@import\s+url\(\s*['\"]?(?:https?:)?//", html), nombre
    lienzo = (PAGINAS / "foto-lienzo.html").read_text(encoding="utf-8")
    csp = re.search(r'Content-Security-Policy" content="([^"]+)"', lienzo).group(1)
    assert "default-src 'self'" in csp and "script-src 'self'" in csp and "connect-src 'self'" in csp


def test_textos_neutros_de_media_son_los_del_servidor(entorno):
    """Los neutros de los marcadores {{…}} de media.html son los del servidor del estudio (y los del editor de piezas y
    del kit, que vigila Ruray); y la página no nombra una región ni un cargo concretos."""
    _, srv = entorno
    texto = (PAGINAS / "media.html").read_text(encoding="utf-8")
    for k, v in srv.TEXTOS_NEUTROS.items():
        assert re.search(r'\b%s\s*:\s*"%s"' % (k, re.escape(v)), texto), k
    assert not re.search(r"Ayacucho|Huamanga|Huanta|SUTEP|DIPUTADO DE LA REPÚBLICA|CÁMARA DE DIPUTADOS", texto, re.I)


def test_el_bloque_de_colores_de_media_es_el_del_kit():
    """El bloque GENERADO de colores de media.html (`tokens-color:inicio … fin`) es el que hoy da el generador de Unancha
    (adaptadores/lib/web.py): si cambia un token, esta prueba lo avisa y el bloque se copia de Unancha."""
    if not (UNANCHA / "tokens").is_dir():
        pytest.skip("sin el kit común: UNANCHA_DIR")
    codigo = ("import json, sys; sys.path.insert(0, '.'); from adaptadores.lib import web as w; "
              "print(json.dumps({'marcas': w.MARCAS_CSS, 'bloque': w.bloque_css()}))")
    r = subprocess.run([sys.executable, "-c", codigo], cwd=UNANCHA, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-1500:]
    web = json.loads(r.stdout)
    texto = (PAGINAS / "media.html").read_text(encoding="utf-8")
    inicio, fin = web["marcas"]
    a, b = texto.find(inicio), texto.find(fin)
    assert a >= 0 and b > a, f"media.html no tiene las marcas {inicio} … {fin}"
    assert texto[a:b + len(fin)] == web["bloque"], "media.html: el bloque de tokens no es el que hoy da Unancha"
