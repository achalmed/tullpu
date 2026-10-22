# Tullpu — un editor de fotos por capas

Tullpu («tinte, color» en quechua) es un editor de fotos para el navegador: retoque por capas con el motor
[miniPaint](https://github.com/viliusle/miniPaint) (MIT) —selecciones, pinceles, clonar, niveles y curvas, filtros,
texto, marcos y logos de una marca— y el revelado de una foto suelta con la plantilla y los formatos por red social.
Es un módulo de [Tiqsi](https://github.com/achalmed/tiqsi) sobre [Ruray](https://github.com/achalmed/ruray), la base
común de los editores: funciona solo, con el anfitrión mínimo de Tiqsi, o dentro de una plataforma que lo monte por su
manifiesto (como Qillqa).

**Recorrido interactivo:** <https://achalmed.github.io/tullpu/> (el código del sitio está en [`sitio/`](sitio/)).

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt -e '.[pruebas,sola]'   # requiere tiqsi y ruray
.venv/bin/python -m pytest -q tests
npm install && npm run web:construir
TULLPU_DIR=/ruta/tullpu JWT_SECRET=<32 o más caracteres> TULLPU_WEB=web/dist .venv/bin/uvicorn tullpu.sola:app --port 8037
```

Los colores, la letra, los logos y los marcos salen de un kit de identidad (`UNANCHA_DIR`). Esta es una **versión de
demostración**. Licencia: AGPL-3.0 (`LICENSE`); miniPaint, MIT.
