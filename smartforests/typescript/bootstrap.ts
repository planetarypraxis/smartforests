import { useEffect, useMemo, useRef, useState } from "react";

export function useOffcanvas<T extends HTMLElement>(offcanvasId: string) {
  const offcanvasElement = useMemo(
    () => document.getElementById(offcanvasId),
    []
  );
  const offcanvas = useMemo(
    () =>
      // @ts-ignore
      bootstrap.Offcanvas.getInstance(offcanvasElement) ??
      // @ts-ignore
      new bootstrap.Offcanvas(offcanvasElement),
    [offcanvasElement]
  );

  return [offcanvas, offcanvasElement as T] as const;
}

export function useFrameSrc(id: string) {
  const el = useMemo<any>(() => document.getElementById(id), [id]);
  const [url, setUrl] = useState<string>(el.src);

  useEffect(() => {
    const listener = () => {
      setUrl(el.src);
    };
    el.addEventListener("turbo:frame-load", listener);

    return () => el.removeEventListener(listener);
  }, [el]);

  return url;
}

export const equalUrls = (a?: string, b?: string) => {
  return a?.replace(/\/$/, "") === b?.replace(/\/$/, "");
};
