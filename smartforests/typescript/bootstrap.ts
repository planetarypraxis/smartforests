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

export function useFrameSrc(id: string | HTMLElement) {
  const el = useMemo<any>(
    () => (typeof id === "string" ? document.getElementById(id) : id),
    [id]
  );
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
  if (a?.startsWith("/")) {
    a = window.location.protocol + "//" + window.location.host + a;
  }
  if (b?.startsWith("/")) {
    b = window.location.protocol + "//" + window.location.host + b;
  }
  return a?.replace(/\/$/, "") === b?.replace(/\/$/, "");
};
