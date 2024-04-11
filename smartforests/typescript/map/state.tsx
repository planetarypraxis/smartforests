import WebMercatorViewport from "@math.gl/web-mercator";
import { atom, useAtom, WritableAtom } from "jotai";
import { atomFamily, useUpdateAtom } from "jotai/utils";
import { useEffect, useMemo, useRef, useState } from "react";
import { MapViewport, useSize } from "./data";

type FocusID = string | number;
export const focusIdAtom = atom<FocusID>("0");

type FocusType = string; // 'logbooks.LogbookPage' | 'logbooks.LogbookEntryPage' | 'logbooks.LogbookEntryPage'
export const focusTypeAtom = atom<FocusType | "">("");

type FocusSource = "list" | "map" | "url";
export const focusSourceAtom = atom<FocusSource | "">("url");

export const viewportAtom = atom<MapViewport>({
  latitude: 20,
  longitude: 0,
  zoom: 1.15,
});

export const isFocused = atomFamily((FocusId: FocusID) =>
  atom(
    (get) => get(focusIdAtom) === FocusId,
    (get, set, FocusId: FocusID | null) => set(focusIdAtom as any, FocusId)
  )
);

export const useFocusContext = (focusId: FocusID, type: FocusType) => {
  const [focusSource, setFocusSource] = useAtom(focusSourceAtom);
  const setFocusType = useUpdateAtom(focusTypeAtom);
  const [thisIsFocused, setFocusId] = useAtom(isFocused(focusId));
  return [
    thisIsFocused,
    (isFocusing: boolean, nextFocusSource: FocusSource, nextFocusId: FocusID = focusId) => {
      setFocusSource(nextFocusSource);
      setFocusType(type);
      setFocusId(isFocusing ? focusId : null);
    },
    focusSource,
  ] as const;
};

export const useQueryParams = () => {
  const [searchParams, setSearchParams] = useState(
    () => new URLSearchParams(window.location.search)
  );

  useEffect(() => {
    const listener = () => {
      setSearchParams(new URLSearchParams(window.location.search));
    };
    window.addEventListener("turbo:load", listener);
    return () => window.removeEventListener("turbo:load", listener);
  }, []);

  return searchParams;
};

export const useFilterParam = () => {
  return useQueryParams().get("filter");
};

export const stringifyQuery = (x: any) => {
  const queryString = new URLSearchParams(x).toString();
  return queryString ? "?" + queryString : "";
};
