import { RefObject, useLayoutEffect, useMemo, useState } from "react";
import useResizeObserver from "@react-hook/resize-observer";
import { Superclusterd, Viewport } from "superclusterd";
import { useClusteredMapData } from "superclusterd/react";
import { SmartForest } from "./types";
import { stringifyQuery } from "./state";

export type MapViewport = Viewport;

const supercluster = new Superclusterd(
  document.getElementById("MAP_APP")?.dataset.superclusterUrl
);

export const useFeatures = <T>(
  dimensions: DOMRectReadOnly,
  viewport: Viewport,
  getQuery: () => any,
  deps: unknown[] = []
) =>
  useClusteredMapData<SmartForest.MapItem>(
    supercluster,
    dimensions,
    viewport,
    useMemo(() => getFeaturesUrl(getQuery()), deps)
  );

export const useSize = (target: RefObject<HTMLElement>) => {
  const [size, setSize] = useState<DOMRectReadOnly>();

  useLayoutEffect(() => {
    setSize(target.current.getBoundingClientRect());
  }, [target]);

  // Where the magic happens
  useResizeObserver(target, (entry) => setSize(entry.contentRect));
  return size;
};

const getFeaturesUrl = (opts: { tag?: string }) => {
  const q = stringifyQuery({
    ...(opts.tag ? { tag: opts.tag } : {}),
  });

  return `${window.location.host}/api/v2/geo/${q}`;
};
