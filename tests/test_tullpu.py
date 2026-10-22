"""tests/test_tullpu.py — el editor de fotos (Tullpu; nació en Qillqa el 2026-10-20, editores E2a) sobre la base común de los
editores (Ruray): la cookie propia de cada editor, sus páginas (las suyas, de `paginas/`, y las comunes del estudio) y su
API bajo /api/fotos/, con las URL que emite el servidor del estudio llevando su prefijo, sin salir de sus carpetas ni
servir lo de otro editor; y su puente con la Mediateca por «medios.v2», aquí con una Mediateca falsa: el selector, la
foto materializada en el banco, su miniatura, lo exportado y lo subido, con la pieza de prensa de la sesión.

El servidor del estudio se carga con un perfil temporal (`ruray.pruebas.entorno`: banco, almacén, proyectos y salidas en
tmp_path): nada toca las carpetas del verde ni las de Unancha.
"""
import base64
import json
import sys
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from ruray import comun as estudio_comun
from ruray import mediateca as estudio_mediateca
from ruray.pruebas import PNG, SECRETO, MediatecaFalsa, entorno  # noqa: F401 — `entorno` es un fixture
from tiqsi import puertos

from tullpu import api as fotos


def _app(rol="asesor"):
    app = FastAPI()
    app.include_router(fotos.router)
    app.dependency_overrides[puertos.usuario_actual] = lambda: SimpleNamespace(id=7, rol=rol)
    return app


@pytest.fixture
def cliente(entorno):
    c = TestClient(_app())
    assert c.post("/api/fotos/sesion").status_code == 200
    return c


def test_la_carga_no_deja_al_estudio_delante_de_qillqa(entorno):
    """El servidor del estudio inserta sus carpetas en sys.path y registra «config», «lib» y «montaje»: la carga lo deshace."""
    raiz = str(estudio_comun.raiz())
    assert not any(p.startswith(raiz) for p in sys.path)
    del_estudio = [n for n in ("config", "lib", "lib.nucleo", "montaje")
                   if str(getattr(sys.modules.get(n), "__file__", "") or "").startswith(raiz)]
    assert not del_estudio
    _, srv = entorno
    assert srv.sys.executable == estudio_comun.python() and srv.sys.path is sys.path
    # shorts.py (que también inserta la raíz) se cargó dentro de la misma ventana: usarlo no la vuelve a meter.
    srv.api_video_config()
    assert not any(p.startswith(raiz) for p in sys.path)


def test_sin_cookie_no_hay_editor(entorno):
    c = TestClient(_app())
    assert c.get("/api/fotos/api/health").status_code == 401
    r = c.get("/api/fotos/foto.html", headers={"accept": "text/html"})
    assert r.status_code == 401 and "desde el sistema" in r.text


def test_la_cookie_es_del_editor_y_solo_de_su_prefijo(entorno):
    c = TestClient(_app())
    r = c.post("/api/fotos/sesion")
    galleta = r.headers["set-cookie"]
    assert "estudio_fotos=" in galleta and "Path=/api/fotos" in galleta and "HttpOnly" in galleta
    assert "SameSite=strict" in galleta and r.json()["pagina"] == "/api/fotos/foto.html"
    valor = c.cookies.get("estudio_fotos")
    assert estudio_comun.leer_sesion(fotos.EDITOR, valor)["sub"] == "7"
    # Otro editor (otro secreto derivado) no la acepta, ni la ficha de la API sirve de cookie.
    otro = estudio_comun.Editor(id="videos", nombre="Editor de videos", prefijo="/api/videos", inicio="video.html", paginas=())
    assert estudio_comun.leer_sesion(otro, valor) is None
    from tiqsi.minimo import firmar
    assert estudio_comun.leer_sesion(fotos.EDITOR, firmar({"sub": "7"}, SECRETO)) is None


def test_invitado_no_abre_el_editor(entorno):
    assert TestClient(_app("invitado")).post("/api/fotos/sesion").status_code == 403


def test_sin_secreto_no_hay_sesion(entorno, monkeypatch):
    monkeypatch.setattr(estudio_comun.config, "jwt_secret", "corto")
    monkeypatch.delenv("JWT_SECRET", raising=False)
    assert TestClient(_app()).post("/api/fotos/sesion").status_code == 503


def test_sirve_sus_paginas_y_nada_mas(cliente):
    for pagina in ("foto.html", "foto-lienzo.html", "media.html", "estudio-tema.css", "vendor/minipaint/dist/bundle.js"):
        r = cliente.get("/api/fotos/" + pagina)
        assert r.status_code == 200, pagina
        assert r.headers["x-frame-options"] == "SAMEORIGIN"
    assert cliente.get("/api/fotos/").headers["content-type"].startswith("text/html")
    # Las páginas de otros editores, el código del servidor y lo que sale de la carpeta: no.
    for ruta in ("servidor/servidor.py", "servidor/config.py", "../README.md",
                 "vendor/minipaint/..%2F..%2Fservidor%2Fservidor.py", "banco/..%2F..%2Fperfil.json",
                 "vendor/minipaint/..%2F..%2F..%2Ftullpu%2Fapi.py", "README.md"):   # ni su código ni su README
        assert cliente.get("/api/fotos/" + ruta).status_code in (403, 404), ruta


def test_las_rutas_de_otro_editor_no_estan(cliente):
    r = cliente.get("/api/fotos/api/video-config")
    assert r.status_code == 404 and r.json()["error"] == "Esto lo hace el editor de videos."
    assert cliente.post("/api/fotos/api/exportar-video", json={}).status_code == 404
    assert cliente.post("/api/fotos/api/imagenes", json={}).status_code == 404


def test_las_paginas_de_otro_editor_llevan_a_donde_esten(cliente, monkeypatch):
    # Solo, sin otros editores: una página que lo dice.
    r = cliente.get("/api/fotos/video.html", follow_redirects=False)
    assert r.status_code == 404 and "otro editor" in r.text
    # En Qillqa, al estudio aparte, con el medio del banco pasado a su prefijo.
    monkeypatch.setattr(estudio_comun.config, "estudio_otras_paginas", "/estudio/")
    r = cliente.get("/api/fotos/video.html?medio=/api/fotos/banco/a.mp4&tipo=video", follow_redirects=False)
    assert r.status_code == 307 and r.headers["location"] == "/estudio/video.html?medio=%2Festudio%2Fbanco%2Fa.mp4&tipo=video"
    assert cliente.get("/api/fotos/editor.html", follow_redirects=False).headers["location"] == "/estudio/editor.html"
    monkeypatch.setattr(estudio_comun.config, "estudio_otras_paginas", "//otro.sitio/")
    assert cliente.get("/api/fotos/editor.html", follow_redirects=False).status_code == 404


def test_las_url_que_emite_llevan_su_prefijo(cliente):
    media = cliente.get("/api/fotos/api/media").json()
    assert [x["url"] for x in media["imagenes"]] == ["/api/fotos/banco/actividad/plaza.png"]
    assert cliente.get("/api/fotos/banco/actividad/plaza.png").content == PNG
    assert cliente.get("/api/fotos/miniatura/actividad/plaza.png").status_code == 200
    diseno = cliente.get("/api/fotos/api/design").json()
    urls = json.dumps(diseno)
    assert "/plantillas/" not in urls.replace("/api/fotos/plantillas/", "")
    salud = cliente.get("/api/fotos/api/health").json()
    assert salud["ok"] and salud["editor"] == "fotos"


def test_subir_guardar_y_exportar(cliente, entorno):
    tmp, _ = entorno
    r = cliente.post("/api/fotos/api/subir", content=PNG, headers={"X-Nombre": "nueva%20foto.png", "Content-Type": "image/png"})
    assert r.json() == {"ok": True, "url": "/api/fotos/banco/subidas-editor/nueva%20foto.png", "esVideo": False, "esAudio": False}
    assert cliente.post("/api/fotos/api/subir", content=b"x", headers={"X-Nombre": "a.exe"}).status_code == 400
    # Proyectos (de fotos y de medios) y el almacén.
    assert cliente.post("/api/fotos/api/proyecto-foto", json={"nombre": "afiche", "datos": {"capas": 2}}).json()["ok"]
    assert [p["nombre"] for p in cliente.get("/api/fotos/api/proyectos-foto").json()] == ["afiche"]
    assert cliente.get("/api/fotos/api/proyecto-foto?nombre=afiche").json()["datos"] == {"capas": 2}
    assert cliente.get("/api/fotos/api/proyecto-foto?nombre=..%2F..%2Fperfil").status_code == 404
    assert cliente.post("/api/fotos/api/proyecto-media", json={"nombre": "m", "datos": {}}).json()["ok"]
    assert cliente.post("/api/fotos/api/almacen", json={"clave": "ajustes", "datos": {"a": 1}}).json()["ok"]
    assert cliente.get("/api/fotos/api/almacen").json()["claves"] == {"ajustes": {"a": 1}}
    assert cliente.post("/api/fotos/api/almacen", content="{}", headers={"Content-Type": "text/plain"}).status_code == 415
    # Exportar: a la salida del canal, con la URL bajo el prefijo.
    url = "data:image/png;base64," + base64.b64encode(PNG).decode()
    r = cliente.post("/api/fotos/api/exportar-foto", json={"nombre": "pieza.png", "canal": "facebook", "dataURL": url}).json()
    assert r["ok"] and r["url"].startswith("/api/fotos/redes/facebook/") and r["banco_url"].startswith("/api/fotos/banco/")
    assert (tmp / "salida" / "redes" / "facebook" / r["archivo"]).read_bytes() == PNG
    assert cliente.get(r["url"]).content == PNG


def test_analizar_acepta_su_prefijo_y_rechaza_lo_ajeno(cliente):
    # El origen llega del navegador con el prefijo del editor; fuera de sus carpetas, no vale.
    assert cliente.post("/api/fotos/api/analizar-foto", json={"origen": "/api/fotos/../../perfil.json"}).status_code == 400
    assert cliente.post("/api/fotos/api/mejorar-foto", json={"origen": "/etc/passwd"}).status_code == 400


# --- el puente con la Mediateca (E2b) --------------------------------------------------------------------------------


@pytest.fixture
def mediateca(entorno, monkeypatch):
    tmp, _ = entorno
    falsa = MediatecaFalsa(tmp / "mediateca")
    monkeypatch.setattr(estudio_mediateca, "ft", falsa)
    monkeypatch.setattr(estudio_mediateca, "con_mediateca", lambda: True)

    async def pieza_de(pid):
        return {"id": pid, "titular": "Obra en Huanta"} if pid == 9 else None

    monkeypatch.setattr(estudio_comun, "pieza_de", pieza_de)
    monkeypatch.setattr(estudio_comun, "_hay_piezas", lambda: True)
    c = TestClient(_app())
    r = c.post("/api/fotos/sesion", json={"pieza": 9}).json()
    assert r["pieza"] == {"id": 9, "titular": "Obra en Huanta"} and r["banco"] is True
    return c, falsa


def test_pieza_que_no_existe(mediateca):
    c, _ = mediateca
    assert c.post("/api/fotos/sesion", json={"pieza": 77}).status_code == 404


def test_el_selector_trae_la_mediateca_y_la_materializa(mediateca, entorno):
    c, _ = mediateca
    tmp, _ = entorno
    assert c.get("/api/fotos/api/health").json()["fototeca"] is True
    primera = c.get("/api/fotos/api/media").json()["imagenes"][0]
    assert primera == {"name": "Fototeca / Prensa / Visita (n.º 5)", "url": "/api/fotos/banco/fototeca/ft-5-0.jpg",
                       "credito": "", "carpeta": "Fototeca"}
    assert c.get(primera["url"]).content == PNG
    assert (tmp / "banco" / "fototeca" / "ft-5-0.jpg").is_file()
    assert c.get("/api/fotos/miniatura/fototeca/ft-5-0.jpg").content == PNG
    assert c.get("/api/fotos/banco/fototeca/ft-6-0.jpg").status_code == 404


def test_lo_exportado_va_a_la_mediateca_con_su_pieza(mediateca, entorno):
    c, falsa = mediateca
    tmp, _ = entorno
    url = "data:image/png;base64," + base64.b64encode(PNG).decode()
    r = c.post("/api/fotos/api/exportar-foto", json={"nombre": "2026-10-20-obra-post.png", "canal": "facebook",
                                                     "dataURL": url, "origen": "/api/fotos/banco/fototeca/ft-5-0.jpg"}).json()
    assert r["ok"] and r["url"] == "/api/fotos/mediateca/2026/20261020_120000.png" and r["banco_url"] == ""
    entrada = falsa.ingresos[-1]
    assert entrada["origen"] == 5 and entrada["usos"] == ["red:facebook", "pieza:9"] and entrada["tipo_uso"] == "prensa"
    meta = entrada["metadatos"]
    assert meta["ambito"] == "prensa" and meta["titulo"] == "Obra post" and "Facebook" in meta["etiquetas"]
    assert "«Obra en Huanta»" in meta["descripcion"]
    # Nada en la salida del canal: solo en la Mediateca, y se descarga desde ahí.
    assert not (tmp / "salida" / "redes" / "facebook").exists()
    assert c.get(r["url"]).content == PNG
    assert c.get("/api/fotos/mediateca/2026/../perfil.json").status_code == 404
    # «Guardar en la Fototeca».
    r = c.post("/api/fotos/api/fototeca-pieza", json={"dataURL": url, "titulo": "Afiche", "fotos": [5]}).json()
    assert r["ok"] and falsa.ingresos[-1]["origen"] == 5 and falsa.ingresos[-1]["metadatos"]["titulo"] == "Afiche"


def test_lo_subido_tambien_entra(mediateca):
    c, falsa = mediateca
    r = c.post("/api/fotos/api/subir", content=PNG, headers={"X-Nombre": "plaza.png", "Content-Type": "image/png"}).json()
    assert r["ok"] and r["fototeca"]["id"] == 41
    assert falsa.ingresos[-1]["etiquetas"] == ["Prensa"] and falsa.ingresos[-1]["usuario_id"] == 7


# --- lo que el proxy de Prensa hacía y pasó a la base (E5) ---------------------------------------------------------


def test_usar_en_prensa_trae_la_foto_al_banco_del_editor(mediateca, entorno):
    c, _ = mediateca
    tmp, _ = entorno
    r = c.post("/api/fotos/traer/5").json()
    assert r == {"ok": True, "url": "/api/fotos/banco/fototeca/ft-5-0.jpg", "nombre": "Visita"}
    assert (tmp / "banco" / "fototeca" / "ft-5-0.jpg").is_file()
    assert c.post("/api/fotos/traer/6").status_code == 404
    invitado = TestClient(_app("invitado"))
    assert invitado.post("/api/fotos/traer/5").status_code == 403


def test_la_cache_se_limpia_al_abrir_un_editor_y_no_pierde_lo_pendiente(mediateca, monkeypatch):
    import asyncio
    import os

    _, falsa = mediateca
    base = falsa.dir / "cache" / "prensa"
    pendiente = base / "salida" / "redes" / "tiktok" / "2026-10-01-101010.mp4"
    trabajo = base / "trabajo" / "mejoradas" / "mej_ab.jpg"
    for f in (pendiente, trabajo):
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(b"x")
        os.utime(f, (0, 0))
    monkeypatch.setitem(estudio_mediateca._limpieza, "ultima", 0.0)
    antes = len(falsa.ingresos)
    asyncio.run(estudio_mediateca.limpiar_cache(7, ahora=10_000_000.0))
    # El video que quedó en la salida entró a la Mediateca como pieza de su red antes de borrarse; lo demás, se borró.
    assert not pendiente.exists() and not trabajo.exists()
    assert len(falsa.ingresos) == antes + 1 and falsa.ingresos[-1]["usos"] == ["red:tiktok"]
    # Otra apertura enseguida no vuelve a recorrer la caché.
    pendiente.parent.mkdir(parents=True, exist_ok=True)
    pendiente.write_bytes(b"y")
    os.utime(pendiente, (0, 0))
    asyncio.run(estudio_mediateca.limpiar_cache(7, ahora=10_000_060.0))
    assert pendiente.exists()
