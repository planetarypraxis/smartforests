import { atom, useAtom } from "jotai";
import { atomFamily } from "jotai/utils";
import { useEffect, useMemo } from "react";
import { TurboFrameElement } from "./turbo";

export const getLanguageCode = (): string => {
  return window.LANGUAGE_CODE || "en";
}

export const languageCodeAtom = atom(getLanguageCode())

export function LanguageContext({ children }) {
  const [languageCode, setLanguageCode] = useAtom(languageCodeAtom)

  async function loadRequestInfo(event) {
    setLanguageCode(getLanguageCode())
  }

  useEffect(() => {
    document.addEventListener("turbo:load", loadRequestInfo);
    return () => document.removeEventListener("turbo:load", loadRequestInfo)
  }, [])

  return children
}

export function TurboContext({ children }) {
  // Register Turbo Frames to track as atoms, identified by the DOM ID.
  // Access via the live atom via frameAtomFamily('#sidepanel-turboframe').
  useOffcanvasTurboFrameState("#sidepanel-turboframe", "#sidepanel-offcanvas")
  return children
}

export function useOffcanvasTurboFrameState(frameId: string, offcanvasId: string) {
  const frame = useMemo(() => document.querySelector<TurboFrameElement>(frameId), [])
  const offcanvas = useMemo(() => document.querySelector(offcanvasId), [])
  const [frameAtom, setFrameAtom] = useAtom(frameAtomFamily(frameId))

  useEffect(() => {
    const updateFrame = () => setFrameAtom({ ...frameAtom, src: frameAtom.el.src })
    frame.addEventListener("turbo:frame-load", updateFrame);

    const updateFrameIsClosed = () => setFrameAtom({ ...frameAtom, src: '' })
    offcanvas.addEventListener("hide.bs.offcanvas", updateFrameIsClosed)

    return () => {
      frame.removeEventListener("turbo:frame-load", updateFrame);
      offcanvas.removeEventListener("hide.bs.offcanvas", updateFrameIsClosed);
    }
  }, [frame, offcanvas]);

  return frameAtom;
}

export const frameAtomFamily = atomFamily((cssSelectorString: string) => {
  const frame = document.querySelector<TurboFrameElement>(cssSelectorString)
  return atom({ el: frame, src: frame.src })
})