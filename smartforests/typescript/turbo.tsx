import React, { createContext, FC, useContext, useEffect, useMemo, useRef, useState } from "react";
import qs, { ParsedQuery } from 'query-string'

export interface TurboFrameElement extends HTMLElement {
  src?: string;
  target?: string;
}

function getParams() {
  if (typeof window === 'undefined') return {}
  return qs.parseUrl(window.location.toString()).query
}

export const TurboURLParamsContext = createContext([
  getParams(),
  (query: object) => { }
] as const)

export function TurboURLParamsContextProvider({ children }) {
  const [params, _setParams] = useState(getParams())

  function updateParams() {
    _setParams(getParams())
  }

  useEffect(() => {
    window.addEventListener("turbo:visit", updateParams);
    return () => window.addEventListener("turbo:visit", updateParams);
  }, [])

  function setParams(query) {
    // @ts-ignore
    Turbo.visit(
      qs.stringifyUrl({
        url: window.location.toString(),
        query
      })
    )
  }

  const args = useMemo(() => [params, setParams], [params])

  return <TurboURLParamsContext.Provider value={args as any}>
    {children}
  </TurboURLParamsContext.Provider>
}

export function useTurboURLParams() {
  return useContext(TurboURLParamsContext)
}