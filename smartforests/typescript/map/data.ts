import { RefObject, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import useResizeObserver from "@react-hook/resize-observer";
import type { ClusteredFeature, Viewport } from "superclusterd";
import { SmartForest } from "./types";
import { stringifyQuery } from "./state";
import Supercluster from 'supercluster'
import useSWR from "swr";
import WebMercatorViewport from "@math.gl/web-mercator";
import { FeatureCollection, Point } from "geojson";

export type MapViewport = Viewport;

export const useFeatures = <T>(
  dimensions: DOMRectReadOnly,
  viewport: Viewport,
  getQuery: () => any,
  deps: unknown[] = []
) =>
  useClusteredMapDataLocal<SmartForest.MapItem>(
    dimensions,
    viewport,
    useMemo(() => getFeaturesUrl(getQuery()), deps)
  );


function useClusteredMapDataLocal<T>(
  dimensions: {
    width: number
    height: number
  },
  viewport: Viewport,
  url: string
): ClusteredFeature<T>[] {
  const [state, setState] = useState<ClusteredFeature<T>[]>([])

  const data = useSWR(
    url,
    async (url) => {
      const data: FeatureCollection<Point, T> = await fetch(url).then((response) => response.json())
      const supercluster = new Supercluster<T>({
        map: (props) => {
          return {
            features: [props]
          }
        },
        reduce: (accumulated, props) => {
          accumulated.features = [...accumulated.features, ...props.features]
        },
      });
      supercluster.load(data.features)
      return {
        supercluster,
        data
      }
    },
    { revalidateOnFocus: false, revalidateOnReconnect: false }
  );

  useEffect(() => {
    // Calculate window
    const projection = new WebMercatorViewport({
      width: dimensions.width,
      height: dimensions.height,
      latitude: viewport.latitude,
      longitude: viewport.longitude,
      zoom: viewport.zoom,
    });

    const bounds = projection.getBounds();
    const bbox = [...bounds[0], ...bounds[1]] as any

    // Generate clusters
    const clusters = data.data?.supercluster?.getClusters(bbox, projection.zoom)
    setState(clusters)
  }, [
    data.data,
    dimensions.width,
    dimensions.height,
    viewport.latitude,
    viewport.longitude,
    viewport.zoom,
  ])

  return state
}

export const useSize = (target: RefObject<HTMLElement>) => {
  const [size, setSize] = useState<DOMRectReadOnly>();

  useLayoutEffect(() => {
    setSize(target.current.getBoundingClientRect());
  }, [target]);

  // Where the magic happens
  useResizeObserver(target, (entry) => setSize(entry.contentRect));
  return size;
};

const getFeaturesUrl = (opts: { tag?: string, languageCode?: string }) => {
  const q = stringifyQuery({
    ...(opts.tag ? { tag: opts.tag } : {}),
    ...(opts.languageCode ? { language_code: opts.languageCode } : {}),
  });

  return `${window.location.protocol}//${window.location.host}/api/v2/geo/${q}`;
};
