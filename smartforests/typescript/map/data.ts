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
import { FeatureCollection, Point } from "geojson";
import useResizeObserver from "@react-hook/resize-observer";

export interface MapViewport {
  latitude: number;
  longitude: number;
  zoom: number;
}

export const useMapData = <T>(
  dimensions: DOMRectReadOnly,
  viewport: MapViewport,
  getUrl: () => string,
  deps: unknown[] = []
) => {
  const [state, setState] = useState<FeatureCollection<Point, T>>();
  const url = useMemo(getUrl, deps);

  useEffect(() => {
    const projection = new WebMercatorViewport({
      ...dimensions,
      ...viewport,
    });

    console.log(projection.zoom, projection.getBounds());

    fetch(url).then(async (res) => {
      setState(await res.json());
    });
  }, [dimensions, viewport, url]);

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
