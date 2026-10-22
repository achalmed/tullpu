---
tipo: readme
estado: activo
---
# paginas/ — las páginas del editor de fotos

Las sirve la base común de los editores (Ruray) bajo `/api/fotos/` (`Editor.carpeta` de `tullpu/api.py`): primero de
aquí y, lo común del estudio (`estudio-tema.css`, `estudio-iconos.js`, `estudio-movil.js`), desde Ruray. Piden todo
relativo a su carpeta (`api("api/x")` → `/api/fotos/api/x`); no se reescriben para el servidor.

| archivo | para qué | manual |
|---|---|---|
| [`media.html`](media.html) | fotos y videos de actividades: plantilla, formato, revelado, recorte en tramos, mejora de fotos, MP4 | `editor-de-medios.md` (en los docs de Unancha) |
| [`foto.html`](foto.html) | retoque de fotos con capas (motor miniPaint): selección por rectángulo, elipse, lazo, lazo poligonal y varita (sumar, restar, calado) que limita ajustes, filtros y pinceles; pinceles, tampón de clonar, recorte, niveles y curvas por canal, filtros, texto, formatos de redes, paleta, marcos y logos; guarda en la Fototeca, en la salida de redes o como proyecto con capas | [`vendor/minipaint/README.md`](vendor/minipaint/README.md) |

| archivo | qué es |
|---|---|
| `foto-lienzo.html`, `vendor/minipaint/` | marco del editor de fotos y el motor miniPaint v4.14.3 (MIT, de terceros, sin modificar; origen, sha256 y actualización en su README) |