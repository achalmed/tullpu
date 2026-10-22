/**
 * El módulo web del editor de fotos (proyecto Tullpu, editores E2c; fase 10.2b del contrato de Tiqsi, 2026-10-20): su
 * pantalla y su ruta. En Qillqa no tiene entrada propia en el menú: Prensa (Fotos y Formatos) carga su pantalla con
 * `TULLPU.cargar` y la pinta en su propio marco, sin importar nada más del módulo. Solo (src/tullpu_sola.tsx), la cáscara
 * mínima la monta en su ruta.
 *
 * Fotos por capas (`foto.html`, con miniPaint) y el revelado de una foto con la plantilla de la marca (`media.html`,
 * `?vista=media`), servidos por la API del módulo bajo /api/fotos/ con su cookie.
 */
import PhotoOutlinedIcon from '@mui/icons-material/PhotoOutlined'
import TuneOutlinedIcon from '@mui/icons-material/TuneOutlined'
import { definirModuloWeb } from '@qillqa/tiqsi'

export const TULLPU = definirModuloWeb({
  id: 'fotos',
  nombre: 'Editor de fotos',
  corto: 'Fotos',
  ruta: '/fotos',
  icono: PhotoOutlinedIcon,
  descripcion: 'Fotos por capas y el revelado con la plantilla de la marca.',
  opciones: [
    { etiqueta: 'Fotos', ruta: '/fotos', icono: PhotoOutlinedIcon, ayuda: 'Capas, retoque y texto, al estilo de Photoshop' },
    { etiqueta: 'Revelar', ruta: '/fotos?vista=media', icono: TuneOutlinedIcon, ayuda: 'Una foto con el marco y los formatos de la marca' },
  ],
  cargar: () => import('../../paginas/Fotos'),
})
