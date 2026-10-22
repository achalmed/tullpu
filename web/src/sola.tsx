/**
 * El editor de fotos SOLO en el navegador (Tullpu): la cáscara mínima de Tiqsi con el módulo web del editor, contra el
 * anfitrión mínimo del backend (tullpu/sola.py). No importa nada de Qillqa. Se construye desde la raíz con
 * `npm run web:construir`.
 */
import { createRoot } from 'react-dom/client'
import { CascaronMinimo } from '@qillqa/tiqsi/minimo'
import { TULLPU } from './componentes/fotos/modulo'

createRoot(document.getElementById('root')!).render(<CascaronMinimo modulo={TULLPU} />)
