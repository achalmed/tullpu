---
tipo: readme
estado: activo
---
# editor/vendor/minipaint/ — miniPaint, el motor de capas del editor de fotos (código de terceros, sin modificar)

Copia fija de la distribución ya compilada de **miniPaint** (editor de imágenes en el navegador: capas, selección,
pinceles, tampón de clonar, efectos, texto e historial), de Vilius L., con **licencia MIT** ([`LICENSE`](LICENSE)).
La usa [`../../foto.html`](../../foto.html) a través de [`../../foto-lienzo.html`](../../foto-lienzo.html), que la
carga en un marco y le pone el tema del estudio; **aquí no se edita nada**: el tema y la integración viven fuera.

| dato | valor |
|---|---|
| origen | <https://github.com/viliusle/miniPaint>, etiqueta `v4.14.3` (publicada el 2026-04-20) |
| archivo descargado | `https://codeload.github.com/viliusle/miniPaint/tar.gz/refs/tags/v4.14.3` |
| sha256 del tarball | `549e726d3dd3d9f1c4b20825631de5300ab545acbb4e23fd30bd4c443f64e83f` |
| sha256 de `dist/bundle.js` | `d084e2659fa7dc1c125663d08e354ccfab3c0cfb78281716ff83b0a6b9283356` |
| licencia | MIT (`MIT-LICENSE.txt` del tarball, copiado como `LICENSE`); las bibliotecas que el paquete incluye y sus avisos: `dist/bundle.js.LICENSE.txt` |
| incorporado | 2026-10-06, con autorización expresa de la jefatura de la oficina |

No está en npm (el paquete `minipaint` fue retirado del registro en 2021): se toma del tarball de la etiqueta, que ya
trae `dist/bundle.js` compilado; no se instala ni se compila nada.

## Qué se copió del tarball

| ruta | qué es |
|---|---|
| `dist/bundle.js`, `dist/bundle.js.LICENSE.txt`, `dist/bundle.js.map` | la aplicación compilada (JS + CSS) y los avisos de licencia de lo que incluye |
| `images/icons/`, `images/logo.svg`, `images/logo-colors.png` | íconos que el CSS del paquete pide con rutas relativas (`images/icons/…`) |
| `LICENSE` | la licencia MIT del proyecto |

No se copió el resto (`src/`, `examples/`, `tools/`, las vistas previas de `images/`, `index.html`): el marco
`foto-lienzo.html` reemplaza al `index.html` del paquete.

## Cómo se actualiza

```bash
V=v4.X.Y                                                   # la etiqueta nueva de github.com/viliusle/miniPaint/releases
curl -sL -o /tmp/miniPaint-$V.tar.gz https://codeload.github.com/viliusle/miniPaint/tar.gz/refs/tags/$V
sha256sum /tmp/miniPaint-$V.tar.gz                         # anotarlo en la tabla de arriba
tar xzf /tmp/miniPaint-$V.tar.gz -C /tmp && D=/tmp/miniPaint-${V#v}
head -3 $D/MIT-LICENSE.txt                                 # comprobar que sigue siendo MIT antes de copiar
cp $D/dist/bundle.js* editor/vendor/minipaint/dist/ && cp $D/images/icons/* editor/vendor/minipaint/images/icons/
cp $D/MIT-LICENSE.txt editor/vendor/minipaint/LICENSE
```

Luego abrir `foto.html` y repasar: abrir una foto, capa nueva, texto, niveles, exportar y guardar el proyecto.
`foto-lienzo.html` reproduce el esqueleto del `index.html` del paquete y llama a sus objetos globales
(`Layers`, `AppConfig`, `State`, `FileOpen`, `FileSave`): si una versión nueva cambia ese esqueleto o esos nombres,
hay que ajustar el marco y `foto.html`.
