import React from "react";
import MapGL, {
  MapContext,
  NavigationControl,
  GeolocateControl,
} from "@urbica/react-map-gl";
// import { WebMercatorViewport } from '@math.gl/web-mercator';
import MapboxGeocoder from "@mapbox/mapbox-gl-geocoder";
import mapboxgl, { Evented } from "mapbox-gl";
import "@mapbox/mapbox-gl-geocoder/dist/mapbox-gl-geocoder.css";
import "mapbox-gl/dist/mapbox-gl.css";
import { Fragment, useContext, useEffect, useRef, useState } from "react";
import { AtlasPagesMapLayer } from "./pages";
import * as ReactDOM from 'react-dom'
import { useWagtailSearch } from "../wagtail";

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
        <FilterControl />
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
    // Docs: https://github.com/mapbox/mapbox-gl-geocoder/blob/master/API.md#mapboxgeocoder
    const control = new MapboxGeocoder({
      accessToken,
      mapboxgl,
      zoom: 14,
      placeholder: "Search by location",
      collapsed: true,
      marker: false,
      types: ['country', 'region', 'district', 'place', 'locality', 'neighborhood'].join(',')
    });

    map?.addControl(control as any, position);

    return () => {
      map?.removeControl(control as any);
    };
  }, [map, position]);

  return null;
}

class FilterControlRenderer extends Evented {
  private _map?: mapboxgl.Map;
  private _container?: HTMLElement;

  onAdd(map) {
    this._map = map;
    this._container = document.createElement('div');
    ReactDOM.render(
      <FilterPopover />,
      this._container
    )
    return this._container;
  }
}

function FilterIcon() {
  return <div className='mapboxgl-ctrl-geocoder mapboxgl-ctrl mapboxgl-ctrl-geocoder--collapsed p-1 py-2 text-center flex-column align-middle align-items-center'>
    <svg width="24" height="16" viewBox="0 0 24 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M9.33333 16H14.6667V13.3333H9.33333V16ZM0 0V2.66667H24V0H0ZM4 9.33333H20V6.66667H4V9.33333Z" fill="#043003" />
    </svg>
  </div>
}

function FilterOptions() {
  const tags = useWagtailSearch({ type: 'logbooks.AtlasTag' })
  return (
    <div>
      {tags.data?.items?.map(tag => {
        <div key={tag.id}>{tag.slug}</div>
      })}
    </div>
  )
  // We could actually just load filters.html as a turbo-frame
  // And then abstract the logic of filters.html out, perhaps using Stimulus?
  // Option 1: Click a tag will navigate to a URL (logbook index)
  // Option 2: Click a tag for map entries.
  //  The annoying thing is we've given up on URLs for the map, so we can't use the URL as an inter-app system.
  //  Another option we have is some kind of independent state, some object in memory that the map and the filter UI can be reactive to.
}

function FilterPopover() {
  const [open, setOpen] = useState(false)
  return (
    <Fragment>
      <div onClick={() => setOpen(o => !o)}>
        <FilterIcon />
      </div>
      {open && <FilterOptions />}
    </Fragment>
  )
}

export function FilterControl() {
  const map: mapboxgl.Map = useContext(MapContext);
  useEffect(() => {
    const control = new FilterControlRenderer();
    // @ts-ignore
    map?.addControl(control, 'top-left');
    return () => void map?.removeControl(control as any);
  }, [map]);
  return null;
}
