import { atom, useAtom } from "jotai";
import { useEffect } from "react";

export const getLanguageCode = (): string => JSON.parse(document.getElementById('request-info')?.innerHTML)?.languageCode

export const languageCodeAtom = atom(getLanguageCode())

export function PageContext({ children }) {
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