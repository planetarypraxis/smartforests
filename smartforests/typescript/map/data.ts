import WebMercatorViewport from "@math.gl/web-mercator";
import {
  Ref,
  RefObject,
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { debounce } from "lodash";
import { Feature, FeatureCollection, Point } from "geojson";
import useResizeObserver from "@react-hook/resize-observer";
import { stringifyQuery } from "./state";

const SUPERCLUSTER_URL =
  document.getElementById("MAP_APP")?.dataset.superclusterUrl;

export interface MapViewport {
  latitude: number;
  longitude: number;
  zoom: number;
}

export interface Cluster {
  cluster: true;
  cluster_id: number;
  point_count: number;
}

type Clusterable<T> =
  | Cluster
  | (T & {
      cluster: false;
    });

export const useClusteredMapData = <T>(
  dimensions: DOMRectReadOnly,
  viewport: MapViewport,
  getUrl: () => string,
  deps: unknown[] = []
) => {
  const [state, setState] = useState<Feature<Point, Clusterable<T>>[]>();
  const url = useMemo(() => {
    const rawUrl = getUrl();

    const projection = new WebMercatorViewport({
      width: dimensions.width,
      height: dimensions.height,
      latitude: viewport.latitude,
      longitude: viewport.longitude,
      zoom: viewport.zoom,
    });

    const bounds = projection.getBounds();
    const bbox = JSON.stringify(
      [...bounds[0], ...bounds[1]].map((x) => round(x, 4))
    );

    const clusterQuery = `?bbox=${bbox}&zoom=${Math.round(projection.zoom)}`;

    const projectedUrl =
      SUPERCLUSTER_URL +
      "/cluster/" +
      encodeURIComponent(rawUrl) +
      clusterQuery;

    return projectedUrl;
  }, [...deps, dimensions, viewport]);

  const debouncedFetch = useMemo(
    () =>
      debounce(async (url: string) => {
        const res = await fetch(url);
        if (res.ok) {
          setState(await res.json());
        }
      }, 500),
    []
  );

  useEffect(() => {
    debouncedFetch(url);
  }, [url]);

  return state;
};

export const useSize = (target: RefObject<HTMLElement>) => {
  const [size, setSize] = useState<DOMRectReadOnly>();

  useLayoutEffect(() => {
    setSize(target.current.getBoundingClientRect());
  }, [target]);

  // Where the magic happens
  useResizeObserver(target, (entry) => setSize(entry.contentRect));
  return size;
};

const round = (x: number, precision: number) => {
  const factor = 10 ** precision;
  return Math.round(factor * x) / factor;
};
