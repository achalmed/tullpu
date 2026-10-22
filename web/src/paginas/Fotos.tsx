/**
 * EL EDITOR DE FOTOS (proyecto Tullpu, editores E2c; fase 10.2b, 2026-10-20) — `foto.html` (capas, con miniPaint) o
 * `media.html` (revelar una foto con la plantilla de la marca) en un marco. Los sirve la API del módulo bajo /api/fotos/
 * con su cookie: el marco no puede mandar la ficha de la sesión, así que antes se pide la sesión del editor
 * (`POST /api/fotos/sesion`), que se renueva mientras la pantalla siga abierta.
 *
 * Sola, se abre en su ruta (`/fotos`; `?vista=media` para revelar; `?imagen=<url>` abre una foto). Dentro de Prensa
 * (Qillqa), Prensa la pinta en su marco (`sinMarco`) y le pasa la vista, la pieza de prensa para la que se abre (lo
 * exportado queda vinculado a ella), la foto y la base de video del recorte de `media.html` (que hace el editor de videos).
 */
import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router'
import { Alert, Box, Button, CircularProgress, Typography } from '@mui/material'
import { Marco, api } from '@qillqa/tiqsi'

interface Sesion {
  ok: boolean
  /** ¿Llegan las fotos de la Mediateca (y va a ella lo exportado)? */
  banco: boolean
  pieza: { id: number; titular: string } | null
  vence: string
}

type Estado = { tipo: 'cargando' } | { tipo: 'listo'; pieza: Sesion['pieza'] } | { tipo: 'error'; texto: string }

/** La cookie del editor vive 2 horas: se renueva cada media hora sin recargar el marco. */
const RENOVAR_MS = 30 * 60 * 1000
const PAGINAS = { foto: 'foto.html', media: 'media.html' } as const

export interface PropsFotos {
  /** Dentro de la página de otro (Prensa): sin el marco propio. */
  sinMarco?: boolean
  vista?: keyof typeof PAGINAS
  pieza?: number
  imagen?: string | null
  /** Dónde está el editor de videos (el recorte de un video en `media.html`): una carpeta del mismo sitio. */
  video?: string
  /** Al cerrar el aviso de la pieza (quien la pasó la quita). */
  alCerrarPieza?: () => void
}

export default function Fotos(props: PropsFotos) {
  const [consulta, setConsulta] = useSearchParams()
  const vista = props.vista ?? (consulta.get('vista') === 'media' ? 'media' : 'foto')
  const pieza = props.pieza ?? (Number(consulta.get('pieza')) || 0)
  const imagen = props.imagen !== undefined ? props.imagen : consulta.get('imagen')
  const video = props.video ?? consulta.get('video') ?? ''
  const [estado, setEstado] = useState<Estado>({ tipo: 'cargando' })
  const [intento, setIntento] = useState(0)

  useEffect(() => {
    let vivo = true
    const pedido = { method: 'POST', body: JSON.stringify(pieza ? { pieza } : {}) }
    api<Sesion>('/api/fotos/sesion', pedido)
      .then((s) => vivo && setEstado({ tipo: 'listo', pieza: s.pieza }))
      .catch((e) => vivo && setEstado({ tipo: 'error', texto: e instanceof Error ? e.message : 'No se pudo abrir el editor de fotos.' }))
    const reloj = window.setInterval(() => { api<Sesion>('/api/fotos/sesion', pedido).catch(() => {}) }, RENOVAR_MS)
    return () => {
      vivo = false
      window.clearInterval(reloj)
    }
  }, [intento, pieza])

  const params = new URLSearchParams()
  if (imagen) params.set('imagen', imagen)
  if (vista === 'media' && video) params.set('video', video)
  const src = `/api/fotos/${PAGINAS[vista]}${params.size ? `?${params}` : ''}`

  const quitarPieza = () => {
    if (props.alCerrarPieza) return props.alCerrarPieza()
    const c = new URLSearchParams(consulta)
    c.delete('pieza')
    setConsulta(c)
  }

  const contenido = (
    <>
      {estado.tipo === 'cargando' && (
        <Box sx={{ flex: 1, display: 'grid', placeItems: 'center' }}>
          <CircularProgress size={28} />
        </Box>
      )}
      {estado.tipo === 'error' && (
        <Box sx={{ p: { xs: 2, sm: 3 }, maxWidth: 720 }}>
          <Alert severity="error" action={
            <Button color="inherit" size="small" onClick={() => { setEstado({ tipo: 'cargando' }); setIntento((n) => n + 1) }}>Reintentar</Button>}>
            {estado.texto}
          </Alert>
        </Box>
      )}
      {estado.tipo === 'listo' && (
        <>
          {estado.pieza && (
            <Alert severity="info" sx={{ borderRadius: 0, py: 0, '& .MuiAlert-message': { minWidth: 0 } }} onClose={quitarPieza}>
              <Typography variant="body2" noWrap>Lo que exporte queda en la Mediateca, vinculado a «{estado.pieza.titular}».</Typography>
            </Alert>
          )}
          <Box
            component="iframe"
            key={src}
            title={vista === 'media' ? 'Editor de fotos: revelar' : 'Editor de fotos'}
            src={src}
            sx={{ flex: 1, width: '100%', border: 0, display: 'block', bgcolor: 'background.default' }}
          />
        </>
      )}
    </>
  )
  return props.sinMarco ? contenido : <Marco modulo="fotos">{contenido}</Marco>
}
