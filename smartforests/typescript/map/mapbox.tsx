import React from "react";
import MapGL, {
  MapContext,
  NavigationControl,
  GeolocateControl,
} from "@urbica/react-map-gl";
// import { WebMercatorViewport } from '@math.gl/web-mercator';
import MapboxGeocoder from "@mapbox/mapbox-gl-geocoder";
import mapboxgl from "mapbox-gl";
import "@mapbox/mapbox-gl-geocoder/dist/mapbox-gl-geocoder.css";
import "mapbox-gl/dist/mapbox-gl.css";
import { Fragment, useContext, useEffect, useRef, useState } from "react";
import { AtlasPagesMapLayer } from "./pages";

const MAPBOX_TOKEN = document.getElementById("MAP_APP")?.dataset.mapboxToken;

export function MapVisual() {
  const [viewport, setViewport] = useState({
    latitude: 0,
    longitude: 0,
    zoom: 2,
    bearing: 0,
    pitch: 0,
  });

  return (
    <Fragment>
      <MapGL
        accessToken={MAPBOX_TOKEN}
        mapStyle="mapbox://styles/smartforests/ckuquky9r2o3v18lkxddvri76/draft?v2"
        style={{ width: "100%", height: "100%" }}
        viewportChangeMethod="flyTo"
        {...viewport}
        onViewportChange={(viewport) =>
          setViewport({
            ...viewport,
            // no 3D controls
            bearing: 0,
            pitch: 0,
          })
        }
        minZoom={2}
        maxZoom={6}
      >
        {/* <NavigationControl showCompass showZoom position='top-left' /> */}
        {/* <GeolocateControl position='top-left' /> */}
        <GeocodeControl position="top-left" accessToken={MAPBOX_TOKEN} />
        <AtlasPagesMapLayer />
      </MapGL>
      {/* <div className='position-absolute bottom-0 end-0 me-3 mb-5 p-4 bg-white opacity-75'>
        <pre className='font-monospace mono monospace'>{JSON.stringify(results.data, null, 2)}</pre>
      </div> */}
    </Fragment>
  );
}

function GeocodeControl({
  position,
  accessToken,
}: {
  accessToken: string;
  position?: "top-left" | "top-right" | "bottom-left" | "bottom-right";
}) {
  const map: mapboxgl.Map = useContext(MapContext);

  useEffect(() => {
    const control = new MapboxGeocoder({
      accessToken,
      mapboxgl,
    });

    map?.addControl(control as any, position);

    return () => {
      map?.removeControl(control as any);
    };
  }, [map, position]);

  return null;
}
