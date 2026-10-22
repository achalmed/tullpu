"""tests/test_tullpu_sola.py — el editor de fotos arranca SOLO, con el anfitrión mínimo de Tiqsi, sin Qillqa, sin base de
datos y sin Mediateca (tullpu/sola.py; nació en Qillqa el 2026-10-20, editores E2c): su perfil y sus carpetas en
TULLPU_DIR, su sesión y su cookie, y lo exportado a su salida.

Corre en un subproceso: el servidor del estudio se carga una vez por proceso, con el perfil de su entorno.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
UNANCHA = Path(os.environ.get("UNANCHA_DIR") or RAIZ.parent / "unancha")
SECRETO = "k" * 40


def _entorno(tmp_path) -> dict:
    return {"HOME": os.environ.get("HOME", "/tmp"), "PATH": os.environ.get("PATH", ""), "UNANCHA_DIR": str(UNANCHA),
            "TULLPU_DIR": str(tmp_path / "tullpu"), "JWT_SECRET": SECRETO}


def _correr(tmp_path, codigo: str, entorno: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-c", codigo], cwd=RAIZ, env=entorno or _entorno(tmp_path),
                          capture_output=True, text=True, timeout=180)


def test_solo_no_carga_nada_de_qillqa(tmp_path):
    r = _correr(tmp_path, "import sys, json; import tullpu.sola as m; "
                          "print(json.dumps({'ajenos': sorted(x for x in sys.modules if x == 'app' or x.startswith('app.')), "
                          "'informe': m.app.state.anfitrion.informe()}))")
    assert r.returncode == 0, r.stderr[-2000:]
    datos = json.loads(r.stdout.strip().splitlines()[-1])
    assert datos["ajenos"] == []                                    # nada de Qillqa
    assert datos["informe"] == [{"id": "fotos", "nombre": "Editor de fotos", "version": "0.1.0"}]


def test_solo_sin_su_carpeta_o_sin_secreto_no_arranca(tmp_path):
    for falta in ("TULLPU_DIR", "JWT_SECRET"):
        entorno = {k: v for k, v in _entorno(tmp_path).items() if k != falta}
        r = _correr(tmp_path, "import tullpu.sola", entorno)
        assert r.returncode != 0 and falta in r.stderr, falta


RECORRIDO = r'''
import base64, json
from fastapi.testclient import TestClient
from tiqsi.minimo import Cuentas
import os
Cuentas(os.environ["TULLPU_DIR"] + "/cuentas.json").crear("ana", "clave-de-prueba-larga", rol="asesor", nombre="Ana")
from tullpu.sola import app
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAAAAAA6fptVAAAACklEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII=")
with TestClient(app) as c:
    out = {"sin_sesion": c.get("/api/fotos/api/health").status_code}
    ficha = c.post("/api/auth/login", json={"usuario": "ana", "clave": "clave-de-prueba-larga"}).json()["token"]
    s = c.post("/api/fotos/sesion", json={"pieza": 3}, headers={"Authorization": "Bearer " + ficha}).json()
    out["sesion"] = {k: s[k] for k in ("banco", "pieza", "pagina")}
    out["salud"] = c.get("/api/fotos/api/health").json()
    out["subida"] = c.post("/api/fotos/api/subir", content=PNG, headers={"X-Nombre": "a.png", "Content-Type": "image/png"}).json()
    url = "data:image/png;base64," + base64.b64encode(PNG).decode()
    out["exportada"] = c.post("/api/fotos/api/exportar-foto", json={"nombre": "p.png", "canal": "x", "dataURL": url}).json()
    out["media"] = [i["url"] for i in c.get("/api/fotos/api/media").json()["imagenes"] if "subidas" in i["url"]]
    out["pagina"] = c.get("/api/fotos/foto.html").status_code
    out["perfil"] = json.load(open(os.environ["TULLPU_DIR"] + "/perfil.json"))["rutas"]["banco"]
print(json.dumps(out))
'''


def test_solo_abre_sube_y_exporta_a_su_salida(tmp_path):
    if not (UNANCHA / "tokens" / "colors.json").is_file():
        pytest.skip("sin Unancha en esta máquina")
    r = _correr(tmp_path, RECORRIDO)
    assert r.returncode == 0, r.stderr[-2000:]
    d = json.loads(r.stdout.strip().splitlines()[-1])
    carpeta = tmp_path / "tullpu"
    assert d["sin_sesion"] == 401 and d["pagina"] == 200
    # Sin quien resuelva piezas de prensa ni Mediateca: se abre sin pieza, y lo exportado va a su salida.
    assert d["sesion"] == {"banco": False, "pieza": None, "pagina": "/api/fotos/foto.html"}
    assert "fototeca" not in d["salud"] and "fototeca" not in d["subida"]
    assert d["subida"]["url"] == "/api/fotos/banco/subidas-editor/a.png" and d["media"] == [d["subida"]["url"]]
    assert d["exportada"]["url"].startswith("/api/fotos/redes/x/")
    assert (carpeta / "salida" / "redes" / "x" / d["exportada"]["archivo"]).is_file()
    assert d["perfil"] == str(carpeta / "banco") and (carpeta / "banco" / "subidas-editor" / "a.png").is_file()
