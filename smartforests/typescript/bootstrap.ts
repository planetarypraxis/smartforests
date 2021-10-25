import { useEffect, useRef } from "react"

export function useOffcanvas(offcanvasId: string) {
  const offcanvasElement = useRef<HTMLElement>()
  const offcanvas = useRef<bootstrap.Offcanvas>()

  useEffect(() => {
    offcanvasElement.current ??= document.getElementById(offcanvasId)
    // @ts-ignore
    offcanvas.current ??= new bootstrap.Offcanvas(offcanvasElement.current)

    return () => offcanvas.current?.dispose()
  }, [])

  return [offcanvas.current, offcanvasElement.current] as const
}